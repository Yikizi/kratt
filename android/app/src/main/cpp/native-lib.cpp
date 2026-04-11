// JNI wrapper for tflite-micro MicroFrontend, vendored from
// hardware/esp32/firmware/.../esp_micro_speech_features.
//
// Matches pymicro-features defaults used by microWakeWord training:
//   sample_rate       = 16000
//   window_size_ms    = 30
//   window_step_ms    = 20
//   num_channels      = 40
//   upper_band_limit  = 7500
//   lower_band_limit  = 125
//   smoothing_bits    = 10
//   even_smoothing    = 0.025
//   odd_smoothing     = 0.06
//   min_signal_remaining = 0.05
//   enable_pcan       = true
//   pcan_strength     = 0.95
//   pcan_offset       = 80.0
//   gain_bits         = 21
//   enable_log        = true
//   scale_shift       = 6

#include <android/log.h>
#include <jni.h>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <mutex>

extern "C" {
#include "frontend.h"
#include "frontend_util.h"
}

#define LOG_TAG "KrattFrontend"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO,  LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

namespace {

struct FrontendHandle {
    FrontendState state{};
    bool populated = false;
    int num_channels = 40;
};

std::mutex g_handles_mutex;

FrontendHandle* HandleFromPtr(jlong ptr) {
    return reinterpret_cast<FrontendHandle*>(ptr);
}

}  // namespace

extern "C" JNIEXPORT jlong JNICALL
Java_ee_taltech_kratt_falselog_audio_MicroFrontendJNI_nativeCreate(
        JNIEnv* /*env*/, jclass /*clazz*/,
        jint sample_rate,
        jint window_size_ms,
        jint window_step_ms,
        jint num_channels,
        jfloat upper_band_limit,
        jfloat lower_band_limit,
        jboolean enable_pcan) {

    FrontendHandle* h = new FrontendHandle();
    h->num_channels = num_channels;

    FrontendConfig cfg{};
    FrontendFillConfigWithDefaults(&cfg);

    cfg.window.size_ms = window_size_ms;
    cfg.window.step_size_ms = window_step_ms;

    cfg.filterbank.num_channels = num_channels;
    cfg.filterbank.lower_band_limit = lower_band_limit;
    cfg.filterbank.upper_band_limit = upper_band_limit;
    cfg.filterbank.output_scale_shift = 7;

    cfg.noise_reduction.smoothing_bits = 10;
    cfg.noise_reduction.even_smoothing = 0.025f;
    cfg.noise_reduction.odd_smoothing = 0.06f;
    cfg.noise_reduction.min_signal_remaining = 0.05f;

    cfg.pcan_gain_control.enable_pcan = enable_pcan ? 1 : 0;
    cfg.pcan_gain_control.strength = 0.95f;
    cfg.pcan_gain_control.offset = 80.0f;
    cfg.pcan_gain_control.gain_bits = 21;

    cfg.log_scale.enable_log = 1;
    cfg.log_scale.scale_shift = 6;

    if (!FrontendPopulateState(&cfg, &h->state, sample_rate)) {
        LOGE("FrontendPopulateState failed");
        delete h;
        return 0;
    }
    h->populated = true;
    LOGI("MicroFrontend created: sr=%d window=%dms step=%dms nch=%d pcan=%d",
         sample_rate, window_size_ms, window_step_ms, num_channels, (int) enable_pcan);
    return reinterpret_cast<jlong>(h);
}

extern "C" JNIEXPORT void JNICALL
Java_ee_taltech_kratt_falselog_audio_MicroFrontendJNI_nativeDestroy(
        JNIEnv* /*env*/, jclass /*clazz*/, jlong ptr) {
    std::lock_guard<std::mutex> lock(g_handles_mutex);
    FrontendHandle* h = HandleFromPtr(ptr);
    if (h == nullptr) return;
    if (h->populated) {
        FrontendFreeStateContents(&h->state);
    }
    delete h;
}

extern "C" JNIEXPORT void JNICALL
Java_ee_taltech_kratt_falselog_audio_MicroFrontendJNI_nativeReset(
        JNIEnv* /*env*/, jclass /*clazz*/, jlong ptr) {
    FrontendHandle* h = HandleFromPtr(ptr);
    if (h == nullptr || !h->populated) return;
    FrontendReset(&h->state);
}

// Processes all the samples it can.
// Input: pcm is int16 audio.
// Output: returns a flat int array where each group of `num_channels` entries is one feature frame.
extern "C" JNIEXPORT jintArray JNICALL
Java_ee_taltech_kratt_falselog_audio_MicroFrontendJNI_nativeProcess(
        JNIEnv* env, jclass /*clazz*/, jlong ptr, jshortArray pcm) {
    FrontendHandle* h = HandleFromPtr(ptr);
    if (h == nullptr || !h->populated) {
        return env->NewIntArray(0);
    }

    jsize input_len = env->GetArrayLength(pcm);
    if (input_len <= 0) {
        return env->NewIntArray(0);
    }

    jshort* input_ptr = env->GetShortArrayElements(pcm, nullptr);
    if (input_ptr == nullptr) {
        return env->NewIntArray(0);
    }

    const int num_channels = h->num_channels;
    // Worst-case frames: one per step_ms's worth of samples.
    // We collect dynamically; for MVP allocate a generous scratch (2 * max expected).
    // Typical: 320 samples in -> 0-1 feature frame out.
    // Use std::vector.
    const int max_possible_frames = (input_len / (h->state.window.step / 1) ) + 4;
    (void) max_possible_frames;

    // We'll collect features into a growing buffer.
    // Use heap-alloc; in MVP we cap at a safe upper bound.
    constexpr int kMaxFramesPerCall = 4096;
    int32_t* feats = static_cast<int32_t*>(malloc(kMaxFramesPerCall * num_channels * sizeof(int32_t)));
    if (feats == nullptr) {
        env->ReleaseShortArrayElements(pcm, input_ptr, JNI_ABORT);
        return env->NewIntArray(0);
    }
    int frame_count = 0;

    size_t remaining = static_cast<size_t>(input_len);
    const int16_t* cursor = reinterpret_cast<const int16_t*>(input_ptr);

    while (remaining > 0) {
        size_t num_read = 0;
        FrontendOutput out = FrontendProcessSamples(
                &h->state,
                cursor,
                remaining,
                &num_read);
        if (num_read == 0) {
            break;
        }
        cursor += num_read;
        remaining -= num_read;

        if (out.size > 0 && out.values != nullptr) {
            if (frame_count >= kMaxFramesPerCall) {
                LOGE("feature buffer overflow; truncating");
                break;
            }
            const int n = static_cast<int>(out.size);
            const int copy_n = n < num_channels ? n : num_channels;
            int32_t* dst = feats + frame_count * num_channels;
            for (int i = 0; i < copy_n; ++i) {
                dst[i] = static_cast<int32_t>(out.values[i]);
            }
            for (int i = copy_n; i < num_channels; ++i) {
                dst[i] = 0;
            }
            frame_count += 1;
        }
    }

    env->ReleaseShortArrayElements(pcm, input_ptr, JNI_ABORT);

    jintArray result = env->NewIntArray(frame_count * num_channels);
    if (result != nullptr && frame_count > 0) {
        env->SetIntArrayRegion(result, 0, frame_count * num_channels, feats);
    }
    free(feats);
    return result;
}
