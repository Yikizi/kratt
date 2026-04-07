#include "driver/i2c_master.h"
#include "driver/i2s_tdm.h"
#include "driver/sdmmc_host.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_app_desc.h"
#include "esp_check.h"
#include "esp_codec_dev.h"
#include "esp_codec_dev_defaults.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "esp_vfs_fat.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdmmc_cmd.h"

#include <frontend.h>
#include <frontend_util.h>
#include <tensorflow/lite/core/c/common.h>
#include <tensorflow/lite/micro/micro_allocator.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/micro/micro_mutable_op_resolver.h>
#include <tensorflow/lite/micro/micro_resource_variable.h>
#include <tensorflow/lite/schema/schema_generated.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdarg>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <dirent.h>
#include <memory>
#include <string>
#include <sys/stat.h>
#include <unistd.h>

namespace {

constexpr char TAG[] = "ww_logger";

// Buttons (ESP32-S3-Korvo-2 resistor ladder on GPIO5 / ADC1 channel 4)
constexpr adc_channel_t BUTTON_ADC_CHANNEL = ADC_CHANNEL_4;
constexpr int BTN_NONE_MIN = 4000;
constexpr int BTN_REC_CENTER = 2805;
constexpr int BTN_REC_TOLERANCE = 180;
constexpr int BTN_MUTE_CENTER = 2285;
constexpr int BTN_MUTE_TOLERANCE = 140;
constexpr int BTN_SET_CENTER = 1895;
constexpr int BTN_SET_TOLERANCE = 140;
constexpr int BTN_PLAY_CENTER = 1254;
constexpr int BTN_PLAY_TOLERANCE = 120;
constexpr size_t BUTTON_BURST_SAMPLE_COUNT = 5;
constexpr TickType_t BUTTON_BURST_SAMPLE_DELAY_TICKS = pdMS_TO_TICKS(2);
constexpr int BUTTON_DEBOUNCE_SAMPLES = 3;

// SD card (SDMMC 1-bit mode)
constexpr gpio_num_t SD_CMD_PIN = GPIO_NUM_7;
constexpr gpio_num_t SD_CLK_PIN = GPIO_NUM_15;
constexpr gpio_num_t SD_D0_PIN = GPIO_NUM_4;
constexpr char MOUNT_POINT[] = "/sdcard";

// I2C and I2S for ES7210 on Korvo-2
constexpr gpio_num_t I2C_SDA_PIN = GPIO_NUM_17;
constexpr gpio_num_t I2C_SCL_PIN = GPIO_NUM_18;
constexpr gpio_num_t I2S_MCLK_PIN = GPIO_NUM_16;
constexpr gpio_num_t I2S_BCLK_PIN = GPIO_NUM_9;
constexpr gpio_num_t I2S_LRCLK_PIN = GPIO_NUM_45;
constexpr gpio_num_t I2S_DIN_PIN = GPIO_NUM_10;

constexpr int SAMPLE_RATE = 16000;
constexpr int MIC_GAIN_DB = 30;
constexpr int TDM_SLOTS = 4;
constexpr size_t I2S_READ_SAMPLES_PER_SLOT = 256;
constexpr size_t I2S_READ_SAMPLE_COUNT = I2S_READ_SAMPLES_PER_SLOT * TDM_SLOTS;
constexpr size_t MONO_BUFFER_CAPACITY = 1600;
constexpr size_t MODEL_INPUT_FEATURES = 40;

// Korvo-2 v3.1 physical mics map to TDM slots 0 and 2.
constexpr size_t MIC1_SLOT = 0;
constexpr uint16_t CODEC_MIC_SELECTION = ES7210_SEL_MIC1 | ES7210_SEL_MIC2 | ES7210_SEL_MIC3;

constexpr float DETECTION_THRESHOLD = 0.97f;
constexpr size_t SLIDING_WINDOW_SIZE = 5;
constexpr size_t TENSOR_ARENA_SIZE = 45000;
constexpr size_t VARIABLE_ARENA_SIZE = 1024;
constexpr uint32_t WAKE_WORD_TASK_STACK_SIZE = 24576;
constexpr UBaseType_t WAKE_WORD_TASK_PRIORITY = 5;
constexpr uint8_t MIN_SLICES_BEFORE_DETECTION = 100;
constexpr uint8_t FEATURE_DURATION_MS = 30;
constexpr uint8_t FEATURE_STEP_MS = 10;
constexpr uint8_t FEATURE_SIZE = 40;

constexpr float FILTERBANK_LOWER_BAND_LIMIT = 125.0f;
constexpr float FILTERBANK_UPPER_BAND_LIMIT = 7500.0f;
constexpr uint8_t NOISE_REDUCTION_SMOOTHING_BITS = 10;
constexpr float NOISE_REDUCTION_EVEN_SMOOTHING = 0.025f;
constexpr float NOISE_REDUCTION_ODD_SMOOTHING = 0.06f;
constexpr float NOISE_REDUCTION_MIN_SIGNAL_REMAINING = 0.05f;
constexpr bool PCAN_GAIN_CONTROL_ENABLE_PCAN = true;
constexpr float PCAN_GAIN_CONTROL_STRENGTH = 0.95f;
constexpr float PCAN_GAIN_CONTROL_OFFSET = 80.0f;
constexpr uint8_t PCAN_GAIN_CONTROL_GAIN_BITS = 21;
constexpr bool LOG_SCALE_ENABLE_LOG = true;
constexpr uint8_t LOG_SCALE_SCALE_SHIFT = 6;

enum class Button {
  NONE,
  REC,
  MUTE,
  PLAY,
  SET,
};

struct DetectionInfo {
  bool detected{false};
  uint8_t max_probability{0};
  uint8_t average_probability{0};
};

struct SessionState {
  bool active{false};
  int session_number{0};
  int detection_count{0};
  int64_t start_us{0};
  FILE *log_file{nullptr};
  std::string path;
};

struct ButtonDebounceState {
  Button last_observed{Button::NONE};
  Button stable{Button::NONE};
  int repeat_count{0};
};

static i2s_chan_handle_t g_rx_chan = nullptr;
static sdmmc_card_t *g_sd_card = nullptr;
static bool g_sd_mounted = false;
static int64_t g_last_i2s_timeout_log_us = 0;
static int64_t g_last_sd_retry_us = 0;
static int g_next_session_number = 1;

static constexpr uint8_t quantize_probability(float value) {
  const float clamped = value < 0.0f ? 0.0f : (value > 1.0f ? 1.0f : value);
  return static_cast<uint8_t>(clamped * 255.0f + 0.5f);
}

static float dequantize_probability(uint8_t value) { return static_cast<float>(value) / 255.0f; }

class WakeWordModel {
 public:
  explicit WakeWordModel(const uint8_t *model_data)
      : model_data_(model_data),
        probability_cutoff_(quantize_probability(DETECTION_THRESHOLD)),
        recent_probabilities_{} {
    this->register_ops_();
    this->reset_probabilities();
  }

  ~WakeWordModel() { this->unload(); }

  void reset_probabilities() {
    recent_probabilities_.fill(0);
    current_stride_step_ = 0;
    last_n_index_ = 0;
    ignore_windows_ = -static_cast<int>(MIN_SLICES_BEFORE_DETECTION);
    unprocessed_probability_ = false;
  }

  void hard_reset() {
    this->unload();
    this->reset_probabilities();
  }

  bool perform_inference(const int8_t features[MODEL_INPUT_FEATURES]) {
    if (!loaded_ && !this->load_()) {
      return false;
    }

    TfLiteTensor *input = interpreter_->input(0);
    const uint8_t stride = interpreter_->input(0)->dims->data[1];
    current_stride_step_ = current_stride_step_ % stride;

    std::memmove(tflite::GetTensorData<int8_t>(input) + MODEL_INPUT_FEATURES * current_stride_step_, features,
                 MODEL_INPUT_FEATURES);
    ++current_stride_step_;

    if (current_stride_step_ >= stride) {
      if (interpreter_->Invoke() != kTfLiteOk) {
        ESP_LOGE(TAG, "TFLite invoke failed");
        return false;
      }

      TfLiteTensor *output = interpreter_->output(0);
      recent_probabilities_[last_n_index_] = output->data.uint8[0];
      last_n_index_ = (last_n_index_ + 1) % recent_probabilities_.size();
      unprocessed_probability_ = true;
    }

    const size_t latest_index =
        (last_n_index_ + recent_probabilities_.size() - 1) % recent_probabilities_.size();
    if (recent_probabilities_[latest_index] < probability_cutoff_) {
      ignore_windows_ = std::min(ignore_windows_ + 1, 0);
    }
    return true;
  }

  bool has_unprocessed_probability() const { return unprocessed_probability_; }

  DetectionInfo determine_detection() {
    DetectionInfo info;
    if (ignore_windows_ < 0) {
      unprocessed_probability_ = false;
      return info;
    }

    uint32_t sum = 0;
    for (uint8_t prob : recent_probabilities_) {
      info.max_probability = std::max(info.max_probability, prob);
      sum += prob;
    }
    info.average_probability = static_cast<uint8_t>(sum / recent_probabilities_.size());
    info.detected = sum > probability_cutoff_ * recent_probabilities_.size();
    unprocessed_probability_ = false;
    return info;
  }

 private:
  bool load_() {
    if (tensor_arena_ == nullptr) {
      tensor_arena_ = static_cast<uint8_t *>(
          heap_caps_malloc(TENSOR_ARENA_SIZE, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
      if (tensor_arena_ == nullptr) {
        tensor_arena_ = static_cast<uint8_t *>(heap_caps_malloc(TENSOR_ARENA_SIZE, MALLOC_CAP_8BIT));
      }
      if (tensor_arena_ == nullptr) {
        ESP_LOGE(TAG, "Failed to allocate tensor arena (%u bytes)", static_cast<unsigned>(TENSOR_ARENA_SIZE));
        return false;
      }
    }

    if (variable_arena_ == nullptr) {
      variable_arena_ = static_cast<uint8_t *>(heap_caps_malloc(VARIABLE_ARENA_SIZE, MALLOC_CAP_8BIT));
      if (variable_arena_ == nullptr) {
        ESP_LOGE(TAG, "Failed to allocate variable arena");
        return false;
      }
      allocator_ = tflite::MicroAllocator::Create(variable_arena_, VARIABLE_ARENA_SIZE);
      resource_variables_ = tflite::MicroResourceVariables::Create(allocator_, 20);
    }

    const tflite::Model *model = tflite::GetModel(model_data_);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
      ESP_LOGE(TAG, "Unsupported TFLite schema version: %d", model->version());
      return false;
    }

    interpreter_ = std::make_unique<tflite::MicroInterpreter>(model, op_resolver_, tensor_arena_, TENSOR_ARENA_SIZE,
                                                              resource_variables_);
    if (interpreter_->AllocateTensors() != kTfLiteOk) {
      ESP_LOGE(TAG, "AllocateTensors failed");
      interpreter_.reset();
      return false;
    }

    TfLiteTensor *input = interpreter_->input(0);
    if (input->dims->size != 3 || input->dims->data[0] != 1 || input->dims->data[2] != MODEL_INPUT_FEATURES ||
        input->type != kTfLiteInt8) {
      ESP_LOGE(TAG, "Unexpected model input tensor");
      interpreter_.reset();
      return false;
    }

    TfLiteTensor *output = interpreter_->output(0);
    if (output->dims->size != 2 || output->dims->data[0] != 1 || output->dims->data[1] != 1 ||
        output->type != kTfLiteUInt8) {
      ESP_LOGE(TAG, "Unexpected model output tensor");
      interpreter_.reset();
      return false;
    }

    loaded_ = true;
    ESP_LOGI(TAG, "Wake-word model loaded, stride=%d", input->dims->data[1]);
    return true;
  }

  void unload() {
    interpreter_.reset();
    if (tensor_arena_ != nullptr) {
      heap_caps_free(tensor_arena_);
      tensor_arena_ = nullptr;
    }
    if (variable_arena_ != nullptr) {
      heap_caps_free(variable_arena_);
      variable_arena_ = nullptr;
    }
    allocator_ = nullptr;
    resource_variables_ = nullptr;
    loaded_ = false;
  }

  void register_ops_() {
    auto add_op = [&](TfLiteStatus status, const char *name) {
      if (status != kTfLiteOk) {
        ESP_LOGE(TAG, "Failed to register op: %s", name);
      }
    };

    add_op(op_resolver_.AddCallOnce(), "CallOnce");
    add_op(op_resolver_.AddVarHandle(), "VarHandle");
    add_op(op_resolver_.AddReshape(), "Reshape");
    add_op(op_resolver_.AddReadVariable(), "ReadVariable");
    add_op(op_resolver_.AddStridedSlice(), "StridedSlice");
    add_op(op_resolver_.AddConcatenation(), "Concatenation");
    add_op(op_resolver_.AddAssignVariable(), "AssignVariable");
    add_op(op_resolver_.AddConv2D(), "Conv2D");
    add_op(op_resolver_.AddMul(), "Mul");
    add_op(op_resolver_.AddAdd(), "Add");
    add_op(op_resolver_.AddMean(), "Mean");
    add_op(op_resolver_.AddFullyConnected(), "FullyConnected");
    add_op(op_resolver_.AddLogistic(), "Logistic");
    add_op(op_resolver_.AddQuantize(), "Quantize");
    add_op(op_resolver_.AddDepthwiseConv2D(), "DepthwiseConv2D");
    add_op(op_resolver_.AddAveragePool2D(), "AveragePool2D");
    add_op(op_resolver_.AddMaxPool2D(), "MaxPool2D");
    add_op(op_resolver_.AddPad(), "Pad");
    add_op(op_resolver_.AddPack(), "Pack");
    add_op(op_resolver_.AddSplitV(), "SplitV");
  }

  const uint8_t *model_data_;
  uint8_t probability_cutoff_;
  tflite::MicroMutableOpResolver<20> op_resolver_;
  std::array<uint8_t, SLIDING_WINDOW_SIZE> recent_probabilities_;
  std::unique_ptr<tflite::MicroInterpreter> interpreter_;
  tflite::MicroAllocator *allocator_{nullptr};
  tflite::MicroResourceVariables *resource_variables_{nullptr};
  uint8_t *tensor_arena_{nullptr};
  uint8_t *variable_arena_{nullptr};
  bool loaded_{false};
  bool unprocessed_probability_{false};
  uint8_t current_stride_step_{0};
  size_t last_n_index_{0};
  int ignore_windows_{0};
};

static Button decode_button_from_raw(int raw) {
  if (raw >= BTN_NONE_MIN) {
    return Button::NONE;
  }

  struct Candidate {
    Button button;
    int center;
    int tolerance;
  };

  constexpr std::array<Candidate, 4> candidates{{
      {Button::REC, BTN_REC_CENTER, BTN_REC_TOLERANCE},
      {Button::MUTE, BTN_MUTE_CENTER, BTN_MUTE_TOLERANCE},
      {Button::SET, BTN_SET_CENTER, BTN_SET_TOLERANCE},
      {Button::PLAY, BTN_PLAY_CENTER, BTN_PLAY_TOLERANCE},
  }};

  Button best_button = Button::NONE;
  int best_distance = INT32_MAX;
  for (const Candidate &candidate : candidates) {
    const int distance = std::abs(raw - candidate.center);
    if (distance <= candidate.tolerance && distance < best_distance) {
      best_distance = distance;
      best_button = candidate.button;
    }
  }

  return best_button;
}

static Button read_button_once(adc_oneshot_unit_handle_t adc_handle, int &raw_out) {
  raw_out = 0;
  if (adc_oneshot_read(adc_handle, BUTTON_ADC_CHANNEL, &raw_out) != ESP_OK) {
    return Button::NONE;
  }
  return decode_button_from_raw(raw_out);
}

static Button read_button_stable(adc_oneshot_unit_handle_t adc_handle, int &raw_out) {
  std::array<int, BUTTON_BURST_SAMPLE_COUNT> raw_samples{};
  std::array<Button, BUTTON_BURST_SAMPLE_COUNT> decoded_samples{};

  for (size_t i = 0; i < BUTTON_BURST_SAMPLE_COUNT; ++i) {
    decoded_samples[i] = read_button_once(adc_handle, raw_samples[i]);
    if (i + 1 < BUTTON_BURST_SAMPLE_COUNT) {
      vTaskDelay(BUTTON_BURST_SAMPLE_DELAY_TICKS);
    }
  }

  std::array<int, BUTTON_BURST_SAMPLE_COUNT> sorted_raw = raw_samples;
  std::sort(sorted_raw.begin(), sorted_raw.end());
  raw_out = sorted_raw[sorted_raw.size() / 2];

  const Button median_button = decode_button_from_raw(raw_out);
  if (median_button == Button::NONE) {
    return Button::NONE;
  }

  int matching_samples = 0;
  for (Button sample : decoded_samples) {
    if (sample == median_button) {
      ++matching_samples;
    }
  }

  return matching_samples >= static_cast<int>((BUTTON_BURST_SAMPLE_COUNT / 2) + 1) ? median_button : Button::NONE;
}

static adc_oneshot_unit_handle_t init_buttons() {
  adc_oneshot_unit_handle_t adc_handle;
  adc_oneshot_unit_init_cfg_t init_cfg{};
  init_cfg.unit_id = ADC_UNIT_1;
  ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_cfg, &adc_handle));

  adc_oneshot_chan_cfg_t chan_cfg{};
  chan_cfg.atten = ADC_ATTEN_DB_12;
  chan_cfg.bitwidth = ADC_BITWIDTH_DEFAULT;
  ESP_ERROR_CHECK(adc_oneshot_config_channel(adc_handle, BUTTON_ADC_CHANNEL, &chan_cfg));
  return adc_handle;
}

static esp_err_t init_i2s() {
  const i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
  ESP_RETURN_ON_ERROR(i2s_new_channel(&chan_cfg, nullptr, &g_rx_chan), TAG, "new channel failed");

  i2s_tdm_config_t tdm_cfg{};
  tdm_cfg.clk_cfg.clk_src = I2S_CLK_SRC_DEFAULT;
  tdm_cfg.clk_cfg.sample_rate_hz = SAMPLE_RATE;
  tdm_cfg.clk_cfg.mclk_multiple = I2S_MCLK_MULTIPLE_256;
  tdm_cfg.slot_cfg = I2S_TDM_PHILIPS_SLOT_DEFAULT_CONFIG(
      I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO,
      static_cast<i2s_tdm_slot_mask_t>(I2S_TDM_SLOT0 | I2S_TDM_SLOT1 | I2S_TDM_SLOT2 | I2S_TDM_SLOT3));
  tdm_cfg.gpio_cfg.mclk = I2S_MCLK_PIN;
  tdm_cfg.gpio_cfg.bclk = I2S_BCLK_PIN;
  tdm_cfg.gpio_cfg.ws = I2S_LRCLK_PIN;
  tdm_cfg.gpio_cfg.dout = GPIO_NUM_NC;
  tdm_cfg.gpio_cfg.din = I2S_DIN_PIN;

  ESP_RETURN_ON_ERROR(i2s_channel_init_tdm_mode(g_rx_chan, &tdm_cfg), TAG, "tdm init failed");
  ESP_LOGI(TAG, "I2S initialized @ %d Hz", SAMPLE_RATE);
  return ESP_OK;
}

static esp_err_t init_codec() {
  i2c_master_bus_handle_t i2c_bus = nullptr;
  i2c_master_bus_config_t i2c_cfg{};
  i2c_cfg.i2c_port = I2C_NUM_0;
  i2c_cfg.sda_io_num = I2C_SDA_PIN;
  i2c_cfg.scl_io_num = I2C_SCL_PIN;
  i2c_cfg.clk_source = I2C_CLK_SRC_DEFAULT;
  i2c_cfg.glitch_ignore_cnt = 7;
  i2c_cfg.flags.enable_internal_pullup = true;
  ESP_RETURN_ON_ERROR(i2c_new_master_bus(&i2c_cfg, &i2c_bus), TAG, "i2c bus failed");

  audio_codec_i2c_cfg_t codec_i2c_cfg{};
  codec_i2c_cfg.port = I2C_NUM_0;
  codec_i2c_cfg.addr = ES7210_CODEC_DEFAULT_ADDR;
  codec_i2c_cfg.bus_handle = i2c_bus;
  const audio_codec_ctrl_if_t *ctrl_if = audio_codec_new_i2c_ctrl(&codec_i2c_cfg);

  audio_codec_i2s_cfg_t codec_i2s_cfg{};
  codec_i2s_cfg.port = I2S_NUM_0;
  codec_i2s_cfg.rx_handle = g_rx_chan;
  codec_i2s_cfg.tx_handle = nullptr;
  const audio_codec_data_if_t *data_if = audio_codec_new_i2s_data(&codec_i2s_cfg);

  es7210_codec_cfg_t es7210_cfg{};
  es7210_cfg.ctrl_if = ctrl_if;
  es7210_cfg.master_mode = false;
  es7210_cfg.mic_selected = CODEC_MIC_SELECTION;
  es7210_cfg.mclk_src = ES7210_MCLK_FROM_PAD;
  es7210_cfg.mclk_div = I2S_MCLK_MULTIPLE_256;
  const audio_codec_if_t *codec_if = es7210_codec_new(&es7210_cfg);

  esp_codec_dev_cfg_t dev_cfg{};
  dev_cfg.dev_type = ESP_CODEC_DEV_TYPE_IN;
  dev_cfg.codec_if = codec_if;
  dev_cfg.data_if = data_if;
  esp_codec_dev_handle_t handle = esp_codec_dev_new(&dev_cfg);

  esp_codec_dev_sample_info_t sample_cfg{};
  sample_cfg.bits_per_sample = I2S_DATA_BIT_WIDTH_16BIT;
  sample_cfg.channel = TDM_SLOTS;
  sample_cfg.channel_mask = CODEC_MIC_SELECTION;
  sample_cfg.sample_rate = SAMPLE_RATE;
  ESP_RETURN_ON_ERROR(esp_codec_dev_open(handle, &sample_cfg), TAG, "codec open failed");
  ESP_RETURN_ON_ERROR(esp_codec_dev_set_in_gain(handle, MIC_GAIN_DB), TAG, "set gain failed");

  i2s_chan_info_t chan_info{};
  ESP_RETURN_ON_ERROR(i2s_channel_get_info(g_rx_chan, &chan_info), TAG, "channel info failed");
  if (!chan_info.is_enabled) {
    ESP_LOGW(TAG, "RX channel was not enabled by codec open, enabling manually");
    ESP_RETURN_ON_ERROR(i2s_channel_enable(g_rx_chan), TAG, "manual channel enable failed");
    ESP_RETURN_ON_ERROR(i2s_channel_get_info(g_rx_chan, &chan_info), TAG, "channel info after enable failed");
  }
  ESP_LOGI(TAG, "I2S RX enabled=%s", chan_info.is_enabled ? "true" : "false");
  ESP_LOGI(TAG, "ES7210 initialized");
  return ESP_OK;
}

static void unmount_sd(const char *reason = nullptr) {
  if (g_sd_card != nullptr) {
    esp_vfs_fat_sdcard_unmount(MOUNT_POINT, g_sd_card);
  }
  g_sd_card = nullptr;
  g_sd_mounted = false;
  g_next_session_number = 1;
  if (reason != nullptr) {
    ESP_LOGW(TAG, "SD card unmounted: %s", reason);
  } else {
    ESP_LOGW(TAG, "SD card unmounted");
  }
}

static bool check_sd_health() {
  if (!g_sd_mounted || g_sd_card == nullptr) {
    g_sd_mounted = false;
    g_sd_card = nullptr;
    return false;
  }

  const esp_err_t ret = sdmmc_get_status(g_sd_card);
  if (ret != ESP_OK) {
    ESP_LOGW(TAG, "SD card no longer available: %s", esp_err_to_name(ret));
    unmount_sd("health check failed");
    return false;
  }
  return true;
}

static bool parse_session_number(const char *name, int &num_out) {
  if (name == nullptr) {
    return false;
  }
  char trailing = '\0';
  int num = 0;
  if (std::sscanf(name, "faph_%d.jsonl%c", &num, &trailing) != 1) {
    return false;
  }
  if (num <= 0) {
    return false;
  }
  num_out = num;
  return true;
}

static int find_next_session_number() {
  DIR *dir = opendir(MOUNT_POINT);
  if (dir == nullptr) {
    return 1;
  }

  int max_num = 0;
  struct dirent *entry = nullptr;
  while ((entry = readdir(dir)) != nullptr) {
    int num = 0;
    if (parse_session_number(entry->d_name, num)) {
      max_num = std::max(max_num, num);
    }
  }
  closedir(dir);
  return max_num + 1;
}

static void try_mount_sd(bool force_remount = false) {
  if (force_remount && (g_sd_mounted || g_sd_card != nullptr)) {
    unmount_sd("forced remount");
    vTaskDelay(pdMS_TO_TICKS(50));
  } else if (g_sd_mounted) {
    if (check_sd_health()) {
      return;
    }
  }

  esp_vfs_fat_sdmmc_mount_config_t mount_config{};
  mount_config.format_if_mount_failed = false;
  mount_config.max_files = 7;

  sdmmc_host_t host = SDMMC_HOST_DEFAULT();
  sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();
  slot_config.width = 1;
  slot_config.clk = SD_CLK_PIN;
  slot_config.cmd = SD_CMD_PIN;
  slot_config.d0 = SD_D0_PIN;
  slot_config.flags |= SDMMC_SLOT_FLAG_INTERNAL_PULLUP;

  esp_log_level_set("sdmmc_common", ESP_LOG_NONE);
  esp_log_level_set("vfs_fat_sdmmc", ESP_LOG_NONE);
  const esp_err_t ret =
      esp_vfs_fat_sdmmc_mount(MOUNT_POINT, &host, &slot_config, &mount_config, &g_sd_card);
  esp_log_level_set("sdmmc_common", ESP_LOG_WARN);
  esp_log_level_set("vfs_fat_sdmmc", ESP_LOG_WARN);

  if (ret == ESP_OK) {
    g_sd_mounted = true;
    g_next_session_number = find_next_session_number();
    ESP_LOGI(TAG, "SD card mounted");
    sdmmc_card_print_info(stdout, g_sd_card);
    ESP_LOGI(TAG, "Next FAPH session: #%04d", g_next_session_number);
  } else {
    g_sd_card = nullptr;
    g_sd_mounted = false;
    g_next_session_number = 1;
    ESP_LOGW(TAG, "SD mount failed: %s", esp_err_to_name(ret));
  }
}

static const char *button_name(Button button) {
  switch (button) {
    case Button::REC:
      return "rec";
    case Button::MUTE:
      return "mute";
    case Button::PLAY:
      return "play";
    case Button::SET:
      return "set";
    case Button::NONE:
    default:
      return "none";
  }
}

static void format_duration_hms(int64_t duration_us, char *buffer, size_t buffer_size) {
  const int64_t total_ms = duration_us >= 0 ? duration_us / 1000 : 0;
  const int64_t hours = total_ms / 3600000;
  const int64_t minutes = (total_ms / 60000) % 60;
  const int64_t seconds = (total_ms / 1000) % 60;
  const int64_t millis = total_ms % 1000;
  std::snprintf(buffer, buffer_size, "%02lld:%02lld:%02lld.%03lld", static_cast<long long>(hours),
                static_cast<long long>(minutes), static_cast<long long>(seconds), static_cast<long long>(millis));
}

static void flush_and_sync_log(FILE *file) {
  if (file == nullptr) {
    return;
  }

  std::fflush(file);
  const int fd = fileno(file);
  if (fd < 0) {
    ESP_LOGW(TAG, "fileno() failed while syncing session log");
    return;
  }
  if (fsync(fd) != 0) {
    ESP_LOGW(TAG, "fsync() failed while syncing session log");
  }
}

static void append_session_event(FILE *file, int session_number, int64_t session_start_us, int64_t now_us, const char *event,
                                 const char *extra_fmt = nullptr, ...) {
  if (file == nullptr) {
    return;
  }

  char uptime_hms[32];
  char session_hms[32];
  format_duration_hms(now_us, uptime_hms, sizeof(uptime_hms));
  const int64_t session_us = session_start_us > 0 ? (now_us - session_start_us) : 0;
  format_duration_hms(session_us, session_hms, sizeof(session_hms));

  std::fprintf(file,
               "{\"event\":\"%s\",\"session\":%d,\"uptime_ms\":%lld,\"uptime_hms\":\"%s\","
               "\"session_ms\":%lld,\"session_hms\":\"%s\"",
               event, session_number, static_cast<long long>(now_us / 1000), uptime_hms,
               static_cast<long long>(session_us / 1000), session_hms);

  if (extra_fmt != nullptr && extra_fmt[0] != '\0') {
    std::fputc(',', file);
    va_list args;
    va_start(args, extra_fmt);
    std::vfprintf(file, extra_fmt, args);
    va_end(args);
  }

  std::fputs("}\n", file);
  flush_and_sync_log(file);
}

static void close_session(SessionState &session, int64_t now_us) {
  if (!session.active || session.log_file == nullptr) {
    session.active = false;
    session.log_file = nullptr;
    return;
  }
  const double elapsed_h = static_cast<double>(now_us - session.start_us) / 3600000000.0;
  const double faph = elapsed_h > 0.0 ? static_cast<double>(session.detection_count) / elapsed_h : 0.0;
  append_session_event(session.log_file, session.session_number, session.start_us, now_us, "session_end",
                       "\"detections\":%d,\"elapsed_s\":%.3f,\"faph\":%.3f", session.detection_count,
                       (now_us - session.start_us) / 1000000.0, faph);
  std::fclose(session.log_file);
  ESP_LOGI(TAG, "Stopped session %d, detections=%d, FAPH=%.2f, log=%s", session.session_number,
           session.detection_count, faph, session.path.c_str());
  session = {};
}

static bool open_session(SessionState &session) {
  check_sd_health();
  try_mount_sd();
  if (!g_sd_mounted) {
    ESP_LOGW(TAG, "Cannot start FAPH session without SD card");
    return false;
  }

  session.session_number = g_next_session_number;
  char path[64];
  std::snprintf(path, sizeof(path), "%s/faph_%04d.jsonl", MOUNT_POINT, session.session_number);
  session.log_file = std::fopen(path, "a");
  if (session.log_file == nullptr) {
    ESP_LOGE(TAG, "Failed to open session log: %s", path);
    unmount_sd("open session log failed");
    return false;
  }

  session.active = true;
  session.detection_count = 0;
  session.start_us = esp_timer_get_time();
  session.path = path;
  const esp_app_desc_t *app_desc = esp_app_get_description();
  append_session_event(
      session.log_file, session.session_number, session.start_us, session.start_us, "session_start",
      "\"threshold\":%.3f,\"threshold_q\":%u,\"sliding_window\":%u,\"sample_rate\":%d,"
      "\"model_input_features\":%u,\"firmware\":\"%s\",\"version\":\"%s\",\"build_date\":\"%s\",\"build_time\":\"%s\"",
      DETECTION_THRESHOLD, quantize_probability(DETECTION_THRESHOLD), static_cast<unsigned>(SLIDING_WINDOW_SIZE),
      SAMPLE_RATE, static_cast<unsigned>(MODEL_INPUT_FEATURES), app_desc->project_name, app_desc->version,
      app_desc->date, app_desc->time);
  g_next_session_number += 1;
  ESP_LOGI(TAG, "Started session %d -> %s", session.session_number, path);
  return true;
}

static size_t generate_features(FrontendState &frontend_state, int16_t *audio_samples, size_t samples_available,
                                int8_t features_out[MODEL_INPUT_FEATURES], bool &has_features) {
  size_t processed_samples = 0;
  const FrontendOutput frontend_output =
      FrontendProcessSamples(&frontend_state, audio_samples, samples_available, &processed_samples);

  has_features = frontend_output.size == MODEL_INPUT_FEATURES;
  if (!has_features) {
    return processed_samples;
  }

  for (size_t i = 0; i < frontend_output.size; ++i) {
    constexpr int32_t value_scale = 256;
    constexpr int32_t value_div = 666;
    int32_t value = ((frontend_output.values[i] * value_scale) + (value_div / 2)) / value_div;
    value += INT8_MIN;
    value = std::clamp(value, static_cast<int32_t>(INT8_MIN), static_cast<int32_t>(INT8_MAX));
    features_out[i] = static_cast<int8_t>(value);
  }
  return processed_samples;
}

static bool poll_button_press(adc_oneshot_unit_handle_t adc_handle, ButtonDebounceState &state, Button &pressed_button,
                              int &raw_out) {
  const Button observed = read_button_stable(adc_handle, raw_out);

  if (observed == state.last_observed) {
    if (state.repeat_count < BUTTON_DEBOUNCE_SAMPLES) {
      ++state.repeat_count;
    }
  } else {
    state.last_observed = observed;
    state.repeat_count = 1;
  }

  if (state.repeat_count >= BUTTON_DEBOUNCE_SAMPLES && observed != state.stable) {
    const Button previous = state.stable;
    state.stable = observed;
    if (previous == Button::NONE && observed != Button::NONE) {
      pressed_button = observed;
      return true;
    }
  }

  return false;
}

}  // namespace

static void wake_word_task(void *unused) {
  (void)unused;
  extern const uint8_t kratt_tflite_start[] asm("_binary_kratt_tflite_start");

  ESP_ERROR_CHECK(init_i2s());
  ESP_ERROR_CHECK(init_codec());
  adc_oneshot_unit_handle_t adc_handle = init_buttons();
  try_mount_sd();
  vTaskDelay(pdMS_TO_TICKS(100));

  FrontendConfig frontend_config{};
  frontend_config.window.size_ms = FEATURE_DURATION_MS;
  frontend_config.window.step_size_ms = FEATURE_STEP_MS;
  frontend_config.filterbank.num_channels = FEATURE_SIZE;
  frontend_config.filterbank.lower_band_limit = FILTERBANK_LOWER_BAND_LIMIT;
  frontend_config.filterbank.upper_band_limit = FILTERBANK_UPPER_BAND_LIMIT;
  frontend_config.noise_reduction.smoothing_bits = NOISE_REDUCTION_SMOOTHING_BITS;
  frontend_config.noise_reduction.even_smoothing = NOISE_REDUCTION_EVEN_SMOOTHING;
  frontend_config.noise_reduction.odd_smoothing = NOISE_REDUCTION_ODD_SMOOTHING;
  frontend_config.noise_reduction.min_signal_remaining = NOISE_REDUCTION_MIN_SIGNAL_REMAINING;
  frontend_config.pcan_gain_control.enable_pcan = PCAN_GAIN_CONTROL_ENABLE_PCAN;
  frontend_config.pcan_gain_control.strength = PCAN_GAIN_CONTROL_STRENGTH;
  frontend_config.pcan_gain_control.offset = PCAN_GAIN_CONTROL_OFFSET;
  frontend_config.pcan_gain_control.gain_bits = PCAN_GAIN_CONTROL_GAIN_BITS;
  frontend_config.log_scale.enable_log = LOG_SCALE_ENABLE_LOG;
  frontend_config.log_scale.scale_shift = LOG_SCALE_SCALE_SHIFT;

  FrontendState frontend_state;
  if (!FrontendPopulateState(&frontend_config, &frontend_state, SAMPLE_RATE)) {
    ESP_LOGE(TAG, "FrontendPopulateState failed");
    return;
  }

  WakeWordModel model(kratt_tflite_start);
  SessionState session;

  std::array<int16_t, I2S_READ_SAMPLE_COUNT> tdm_read_buffer{};
  std::array<int16_t, MONO_BUFFER_CAPACITY> mono_buffer{};
  size_t mono_samples = 0;
  std::array<int8_t, MODEL_INPUT_FEATURES> features{};

  ButtonDebounceState button_state;

  ESP_LOGI(TAG,
           "Wake-word logger ready. REC=start FAPH session, MUTE=stop. threshold=%.2f window=%u tensor_arena=%u",
           DETECTION_THRESHOLD, static_cast<unsigned>(SLIDING_WINDOW_SIZE), static_cast<unsigned>(TENSOR_ARENA_SIZE));

  while (true) {
    if (g_sd_mounted && !session.active) {
      check_sd_health();
    }

    if (!g_sd_mounted && !session.active) {
      const int64_t now_us = esp_timer_get_time();
      if ((now_us - g_last_sd_retry_us) >= 5000000) {
        g_last_sd_retry_us = now_us;
        try_mount_sd();
      }
    }

    int button_raw = 0;
    Button current_button = Button::NONE;
    if (poll_button_press(adc_handle, button_state, current_button, button_raw)) {
      ESP_LOGI(TAG, "Button %s raw=%d", button_name(current_button), button_raw);
      if (current_button == Button::REC) {
        if (!session.active) {
          model.reset_probabilities();
          mono_samples = 0;
          open_session(session);
        }
      } else if (current_button == Button::MUTE) {
        if (session.active) {
          const int64_t now_us = esp_timer_get_time();
          append_session_event(session.log_file, session.session_number, session.start_us, now_us, "button_press",
                               "\"button\":\"%s\",\"action\":\"stop_session\"", button_name(current_button));
        }
        close_session(session, esp_timer_get_time());
      } else if (current_button == Button::PLAY) {
        check_sd_health();
        ESP_LOGI(TAG, "Status: session=%s sd=%s detections=%d", session.active ? "active" : "idle",
                 g_sd_mounted ? "mounted" : "missing", session.detection_count);
        ESP_LOGI(TAG, "Next FAPH session: #%04d", g_next_session_number);
        if (session.active) {
          const int64_t now_us = esp_timer_get_time();
          append_session_event(
              session.log_file, session.session_number, session.start_us, now_us, "button_press",
              "\"button\":\"%s\",\"action\":\"status\",\"sd_mounted\":%s,\"detections\":%d",
              button_name(current_button), g_sd_mounted ? "true" : "false", session.detection_count);
        }
      } else if (current_button == Button::SET) {
        if (session.active) {
          ESP_LOGW(TAG, "Cannot remount SD while session is active");
          const int64_t now_us = esp_timer_get_time();
          append_session_event(session.log_file, session.session_number, session.start_us, now_us, "button_press",
                               "\"button\":\"%s\",\"action\":\"remount_blocked\",\"sd_mounted\":%s",
                               button_name(current_button), g_sd_mounted ? "true" : "false");
        } else {
          try_mount_sd(true);
          ESP_LOGI(TAG, "SET pressed: SD %s", g_sd_mounted ? "mounted" : "not available");
        }
      }
    }

    size_t bytes_read = 0;
    const esp_err_t ret =
        i2s_channel_read(g_rx_chan, tdm_read_buffer.data(), sizeof(tdm_read_buffer), &bytes_read, 50);
    if (ret != ESP_OK) {
      if (ret != ESP_ERR_TIMEOUT) {
        ESP_LOGW(TAG, "I2S read failed: %s", esp_err_to_name(ret));
      } else {
        const int64_t now_us = esp_timer_get_time();
        if ((now_us - g_last_i2s_timeout_log_us) >= 2000000) {
          g_last_i2s_timeout_log_us = now_us;
          ESP_LOGW(TAG, "I2S read timing out");
        }
      }
      vTaskDelay(pdMS_TO_TICKS(10));
      continue;
    }

    const size_t tdm_samples = bytes_read / sizeof(int16_t);
    for (size_t i = MIC1_SLOT; i < tdm_samples; i += TDM_SLOTS) {
      if (mono_samples < mono_buffer.size()) {
        mono_buffer[mono_samples++] = tdm_read_buffer[i];
      } else {
        std::memmove(mono_buffer.data(), mono_buffer.data() + 1, (mono_buffer.size() - 1) * sizeof(int16_t));
        mono_buffer.back() = tdm_read_buffer[i];
      }
    }

    while (mono_samples > 0) {
      bool have_features = false;
      const size_t processed =
          generate_features(frontend_state, mono_buffer.data(), mono_samples, features.data(), have_features);

      if (processed > 0 && processed <= mono_samples) {
        const size_t remaining = mono_samples - processed;
        if (remaining > 0) {
          std::memmove(mono_buffer.data(), mono_buffer.data() + processed, remaining * sizeof(int16_t));
        }
        mono_samples = remaining;
      }

      if (!have_features) {
        if (processed == 0) {
          break;
        }
        continue;
      }

      if (!model.perform_inference(features.data())) {
        ESP_LOGE(TAG, "Inference failed, resetting model");
        model.hard_reset();
        break;
      }

      if (!model.has_unprocessed_probability()) {
        continue;
      }

      const DetectionInfo info = model.determine_detection();
      if (!info.detected) {
        continue;
      }

      const int64_t now_us = esp_timer_get_time();
      const double elapsed_s = session.active ? static_cast<double>(now_us - session.start_us) / 1000000.0 : 0.0;

      ESP_LOGI(TAG, "DETECTED avg=%.3f max=%.3f session=%s", dequantize_probability(info.average_probability),
               dequantize_probability(info.max_probability), session.active ? "active" : "idle");

      if (session.active) {
        session.detection_count += 1;
        const double elapsed_h = elapsed_s / 3600.0;
        const double faph = elapsed_h > 0.0 ? static_cast<double>(session.detection_count) / elapsed_h : 0.0;
        append_session_event(
            session.log_file, session.session_number, session.start_us, now_us, "detection",
            "\"count\":%d,\"elapsed_s\":%.3f,\"avg_prob\":%.4f,\"max_prob\":%.4f,"
            "\"avg_prob_q\":%u,\"max_prob_q\":%u,\"faph\":%.3f,\"threshold\":%.3f,\"threshold_q\":%u",
            session.detection_count, elapsed_s, dequantize_probability(info.average_probability),
            dequantize_probability(info.max_probability), info.average_probability, info.max_probability, faph,
            DETECTION_THRESHOLD, quantize_probability(DETECTION_THRESHOLD));
      }

      model.reset_probabilities();
    }
  }
}

extern "C" void app_main(void) {
  BaseType_t task_created = xTaskCreatePinnedToCore(wake_word_task, "wake_word", WAKE_WORD_TASK_STACK_SIZE, nullptr,
                                                    WAKE_WORD_TASK_PRIORITY, nullptr, tskNO_AFFINITY);
  ESP_ERROR_CHECK(task_created == pdPASS ? ESP_OK : ESP_FAIL);
}
