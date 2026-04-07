#include "bsp/esp-bsp.h"
#include "driver/gpio.h"
#include "esp_check.h"
#include "esp_codec_dev.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "kratt_korvo2_board.h"
#include "kratt_korvo2_buttons.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include <inttypes.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SAMPLE_RATE_HZ 16000
#define BITS_PER_SAMPLE I2S_DATA_BIT_WIDTH_16BIT
#define PLAYBACK_CHANNELS 2
#define DEFAULT_VOLUME 15
#define VOLUME_STEP 5
#define BUTTON_POLL_MS 50
#define STARTUP_DELAY_MS 750
#define BUTTON_QUEUE_LEN 8
#define PI_F 3.14159265358979323846f
#define BUTTON_NONE (-1)

typedef struct {
  const char *label;
  int frequency_hz;
  int duration_ms;
  float amplitude;
} tone_step_t;

static const tone_step_t kStartupPattern[] = {
    {.label = "tone-a4", .frequency_hz = 440, .duration_ms = 180, .amplitude = 0.35f},
    {.label = "tone-a5", .frequency_hz = 880, .duration_ms = 180, .amplitude = 0.30f},
    {.label = "tone-e6", .frequency_hz = 1320, .duration_ms = 220, .amplitude = 0.25f},
};

static const char *TAG = "korvo2-spk";
static esp_codec_dev_handle_t g_speaker = NULL;
static QueueHandle_t g_button_queue = NULL;
static bool g_muted = false;
static int g_last_nonzero_volume = DEFAULT_VOLUME;
static kratt_korvo2_button_id_t g_last_button_id = BUTTON_NONE;

static esp_err_t open_playback_stream(void) {
  esp_codec_dev_sample_info_t sample_info = {
      .sample_rate = SAMPLE_RATE_HZ,
      .channel = PLAYBACK_CHANNELS,
      .channel_mask = 0x03,
      .bits_per_sample = BITS_PER_SAMPLE,
  };

  ESP_LOGI(TAG, "Opening speaker stream: sample_rate=%d channel=%d bits=%d", sample_info.sample_rate,
           sample_info.channel, sample_info.bits_per_sample);
  return esp_codec_dev_open(g_speaker, &sample_info);
}

static esp_err_t play_pcm_blocking(int16_t *samples, size_t sample_count,
                                   const char *label) {
  const size_t bytes = sample_count * PLAYBACK_CHANNELS * sizeof(int16_t);
  const uint32_t nominal_duration_ms =
      (uint32_t)((1000ULL * sample_count) / SAMPLE_RATE_HZ);
  const int64_t started_us = esp_timer_get_time();

  ESP_LOGI(TAG, "Playback start: label=%s frames=%u bytes=%u nominal_ms=%" PRIu32, label,
           (unsigned)sample_count, (unsigned)bytes, nominal_duration_ms);
  ESP_RETURN_ON_ERROR(open_playback_stream(), TAG, "speaker open failed");

  const esp_err_t write_ret = esp_codec_dev_write(g_speaker, samples, bytes);
  const esp_err_t close_ret = esp_codec_dev_close(g_speaker);
  const int64_t elapsed_ms = (esp_timer_get_time() - started_us) / 1000;

  if (write_ret != ESP_OK) {
    ESP_LOGE(TAG, "Playback write failed for %s: %s", label, esp_err_to_name(write_ret));
    return write_ret;
  }
  if (close_ret != ESP_OK) {
    ESP_LOGE(TAG, "Speaker close failed for %s: %s", label, esp_err_to_name(close_ret));
    return close_ret;
  }

  ESP_LOGI(TAG, "Playback done: label=%s elapsed_ms=%" PRIi64, label, elapsed_ms);
  return ESP_OK;
}

static size_t duration_to_samples(int duration_ms) {
  return (size_t)(((uint64_t)SAMPLE_RATE_HZ * (uint64_t)duration_ms) / 1000ULL);
}

static void render_tone(int16_t *samples, size_t sample_count, const tone_step_t *step) {
  const float phase_increment =
      (2.0f * PI_F * (float)step->frequency_hz) / (float)SAMPLE_RATE_HZ;
  const float peak = 32767.0f * step->amplitude;
  float phase = 0.0f;
  for (size_t i = 0; i < sample_count; ++i) {
    const int16_t sample = (int16_t)(sinf(phase) * peak);
    samples[i * PLAYBACK_CHANNELS] = sample;
    samples[i * PLAYBACK_CHANNELS + 1] = sample;
    phase += phase_increment;
    if (phase >= (2.0f * PI_F)) {
      phase -= 2.0f * PI_F;
    }
  }
}

static esp_err_t play_sweep(void) {
  const int duration_ms = 1800;
  const int start_hz = 250;
  const int stop_hz = 3000;
  const size_t sample_count =
      (size_t)(((uint64_t)SAMPLE_RATE_HZ * (uint64_t)duration_ms) / 1000ULL);
  int16_t *samples = calloc(sample_count * PLAYBACK_CHANNELS, sizeof(int16_t));
  if (samples == NULL) {
    ESP_LOGE(TAG, "Out of memory while preparing sweep");
    return ESP_ERR_NO_MEM;
  }

  float phase = 0.0f;
  for (size_t i = 0; i < sample_count; ++i) {
    const float progress = (float)i / (float)(sample_count - 1);
    const float frequency_hz =
        (float)start_hz + ((float)(stop_hz - start_hz) * progress);
    phase += (2.0f * PI_F * frequency_hz) / (float)SAMPLE_RATE_HZ;
    if (phase >= (2.0f * PI_F)) {
      phase -= 2.0f * PI_F;
    }
    const int16_t sample = (int16_t)(sinf(phase) * 6000.0f);
    samples[i * PLAYBACK_CHANNELS] = sample;
    samples[i * PLAYBACK_CHANNELS + 1] = sample;
  }

  ESP_LOGI(TAG, "Generated diagnostic sweep: %dHz -> %dHz in %dms", start_hz, stop_hz,
           duration_ms);
  const esp_err_t ret = play_pcm_blocking(samples, sample_count, "diag-sweep");
  free(samples);
  return ret;
}

static esp_err_t play_startup_pattern(void) {
  const int gap_ms = 70;
  size_t total_samples = 0;
  for (size_t i = 0; i < (sizeof(kStartupPattern) / sizeof(kStartupPattern[0])); ++i) {
    total_samples += duration_to_samples(kStartupPattern[i].duration_ms);
    if (i + 1 < (sizeof(kStartupPattern) / sizeof(kStartupPattern[0]))) {
      total_samples += duration_to_samples(gap_ms);
    }
  }

  int16_t *samples = calloc(total_samples * PLAYBACK_CHANNELS, sizeof(int16_t));
  if (samples == NULL) {
    ESP_LOGE(TAG, "Out of memory while preparing startup pattern");
    return ESP_ERR_NO_MEM;
  }

  size_t offset = 0;
  for (size_t i = 0; i < (sizeof(kStartupPattern) / sizeof(kStartupPattern[0])); ++i) {
    const size_t tone_samples = duration_to_samples(kStartupPattern[i].duration_ms);
    ESP_LOGI(TAG, "Pattern segment: label=%s freq=%dHz duration=%dms amplitude=%.2f",
             kStartupPattern[i].label, kStartupPattern[i].frequency_hz,
             kStartupPattern[i].duration_ms, (double)kStartupPattern[i].amplitude);
    render_tone(samples + offset, tone_samples, &kStartupPattern[i]);
    offset += tone_samples;

    if (i + 1 < (sizeof(kStartupPattern) / sizeof(kStartupPattern[0]))) {
      offset += duration_to_samples(gap_ms);
    }
  }

  ESP_LOGI(TAG, "Composed startup pattern: segments=%u total_samples=%u total_ms=%u",
           (unsigned)(sizeof(kStartupPattern) / sizeof(kStartupPattern[0])),
           (unsigned)total_samples,
           (unsigned)((1000ULL * total_samples) / SAMPLE_RATE_HZ));
  const esp_err_t ret = play_pcm_blocking(samples, total_samples, "startup-pattern");
  free(samples);
  return ret;
}

static void dump_runtime_status(void) {
  int volume = -1;
  const esp_err_t vol_ret = esp_codec_dev_get_out_vol(g_speaker, &volume);
  if (vol_ret != ESP_OK) {
    ESP_LOGW(TAG, "Could not read speaker volume: %s", esp_err_to_name(vol_ret));
  }

  ESP_LOGI(TAG, "Runtime status: volume=%d muted=%s sample_rate=%d bits=%d last_button=%s",
           volume, g_muted ? "true" : "false", SAMPLE_RATE_HZ, BITS_PER_SAMPLE,
           kratt_korvo2_button_name(g_last_button_id));
  ESP_LOGI(TAG, "Button actions via Espressif ADC-button path: PLAY/SET=startup pattern, REC=sweep, MUTE=toggle mute");
}

static esp_err_t set_volume(int new_volume, const char *reason) {
  if (new_volume < 0) {
    new_volume = 0;
  } else if (new_volume > 100) {
    new_volume = 100;
  }

  ESP_RETURN_ON_ERROR(esp_codec_dev_set_out_vol(g_speaker, new_volume), TAG,
                      "set volume failed");
  if (new_volume > 0) {
    g_last_nonzero_volume = new_volume;
    g_muted = false;
  } else {
    g_muted = true;
  }

  ESP_LOGI(TAG, "Volume updated: reason=%s value=%d", reason, new_volume);
  return ESP_OK;
}

static esp_err_t change_volume(int delta, const char *reason) {
  int current_volume = DEFAULT_VOLUME;
  ESP_RETURN_ON_ERROR(esp_codec_dev_get_out_vol(g_speaker, &current_volume), TAG,
                      "get volume failed");
  return set_volume(current_volume + delta, reason);
}

static esp_err_t toggle_mute(void) {
  int current_volume = DEFAULT_VOLUME;
  ESP_RETURN_ON_ERROR(esp_codec_dev_get_out_vol(g_speaker, &current_volume), TAG,
                      "get volume failed");

  if (!g_muted && current_volume > 0) {
    g_last_nonzero_volume = current_volume;
    return set_volume(0, "mute");
  }

  const int restore_volume = (g_last_nonzero_volume > 0) ? g_last_nonzero_volume : DEFAULT_VOLUME;
  return set_volume(restore_volume, "unmute");
}

static esp_err_t init_buttons(void) {
  g_button_queue = xQueueCreate(BUTTON_QUEUE_LEN, sizeof(kratt_korvo2_button_id_t));
  if (g_button_queue == NULL) {
    return ESP_ERR_NO_MEM;
  }
  return kratt_korvo2_buttons_init(g_button_queue);
}

static esp_err_t init_audio(void) {
  const kratt_korvo2_audio_pins_t *pins = kratt_korvo2_audio_pins();
  const i2s_std_config_t i2s_cfg = {
      .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE_HZ),
      .slot_cfg = I2S_STD_PHILIP_SLOT_DEFAULT_CONFIG(BITS_PER_SAMPLE, I2S_SLOT_MODE_MONO),
      .gpio_cfg =
          {
              .mclk = pins->i2s_mclk,
              .bclk = pins->i2s_bclk,
              .ws = pins->i2s_lrck,
              .dout = pins->i2s_dout,
              .din = pins->i2s_din,
              .invert_flags =
                  {
                      .mclk_inv = false,
                      .bclk_inv = false,
                      .ws_inv = false,
                  },
          },
  };

  ESP_LOGI(TAG, "Initializing I2C explicitly before BSP audio init");
  gpio_reset_pin(pins->speaker_pa_enable);
  ESP_RETURN_ON_ERROR(gpio_set_direction(pins->speaker_pa_enable, GPIO_MODE_OUTPUT), TAG,
                      "pa gpio direction failed");
  ESP_RETURN_ON_ERROR(gpio_set_level(pins->speaker_pa_enable, 1), TAG, "pa gpio set failed");
  ESP_RETURN_ON_ERROR(bsp_i2c_init(), TAG, "i2c init failed");
  ESP_RETURN_ON_ERROR(bsp_audio_init(&i2s_cfg), TAG, "bsp audio init failed");

  g_speaker = bsp_audio_codec_speaker_init();
  if (g_speaker == NULL) {
    return ESP_FAIL;
  }

  ESP_RETURN_ON_ERROR(gpio_set_level(pins->speaker_pa_enable, 1), TAG,
                      "pa gpio set after codec failed");
  ESP_LOGI(TAG, "PA forced on via GPIO%d for speaker diagnostics", pins->speaker_pa_enable);
  ESP_RETURN_ON_ERROR(set_volume(DEFAULT_VOLUME, "boot"), TAG, "initial volume failed");
  return ESP_OK;
}

static void handle_button_event(kratt_korvo2_button_id_t button_index) {
  g_last_button_id = button_index;
  ESP_LOGI(TAG, "Button pressed: %s (%d)", kratt_korvo2_button_name(button_index),
           button_index);
  switch (button_index) {
  case KRATT_KORVO2_BUTTON_PLAY:
  case KRATT_KORVO2_BUTTON_SET:
    dump_runtime_status();
    ESP_ERROR_CHECK(play_startup_pattern());
    break;
  case KRATT_KORVO2_BUTTON_REC:
    ESP_ERROR_CHECK(play_sweep());
    break;
  case KRATT_KORVO2_BUTTON_MUTE:
    ESP_ERROR_CHECK(toggle_mute());
    break;
  case KRATT_KORVO2_BUTTON_VOLDOWN:
    ESP_ERROR_CHECK(change_volume(-VOLUME_STEP, "vol-down"));
    break;
  case KRATT_KORVO2_BUTTON_VOLUP:
    ESP_ERROR_CHECK(change_volume(VOLUME_STEP, "vol-up"));
    break;
  default:
    ESP_LOGI(TAG, "No speaker action mapped for %s",
             kratt_korvo2_button_name(button_index));
    break;
  }
}

void app_main(void) {
  kratt_korvo2_log_board_overview(TAG);

  ESP_ERROR_CHECK(init_audio());
  ESP_ERROR_CHECK(init_buttons());
  dump_runtime_status();

  ESP_LOGI(TAG, "Startup delay: %dms before entering low-volume standby", STARTUP_DELAY_MS);
  vTaskDelay(pdMS_TO_TICKS(STARTUP_DELAY_MS));
  ESP_LOGI(TAG, "Standby: no automatic playback. Press PLAY for low-volume test pattern.");

  while (true) {
    kratt_korvo2_button_id_t button_index = BUTTON_NONE;
    if (xQueueReceive(g_button_queue, &button_index, pdMS_TO_TICKS(BUTTON_POLL_MS)) == pdTRUE) {
      handle_button_event(button_index);
    }
  }
}
