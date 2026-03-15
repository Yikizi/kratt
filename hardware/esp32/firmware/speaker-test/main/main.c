#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "driver/i2s_std.h"
#include "esp_codec_dev.h"
#include "esp_codec_dev_defaults.h"
#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

// I2C (shared bus for ES8311 + ES7210)
#define I2C_SDA_PIN GPIO_NUM_17
#define I2C_SCL_PIN GPIO_NUM_18

// I2S (shared between ES8311 speaker and ES7210 mic)
#define I2S_MCLK_PIN GPIO_NUM_16
#define I2S_BCLK_PIN GPIO_NUM_9
#define I2S_LRCLK_PIN GPIO_NUM_45
#define I2S_DOUT_PIN GPIO_NUM_8
#define I2S_DIN_PIN GPIO_NUM_10

// Speaker power amplifier enable
#define PA_ENABLE_PIN GPIO_NUM_48

#define SAMPLE_RATE 16000
#define MCLK_MULTIPLE 256
#define BEEP_FREQ 1000 // 1kHz beep
#define BEEP_DURATION_MS 200
#define BEEP_VOLUME 60 // 0-100

static const char *TAG = "speaker-test";
static i2s_chan_handle_t tx_handle = NULL;
static i2s_chan_handle_t rx_handle = NULL;
static esp_codec_dev_handle_t codec_handle = NULL;

static esp_err_t init_i2s(void) {
  i2s_chan_config_t chan_cfg =
      I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
  chan_cfg.auto_clear = true;
  ESP_RETURN_ON_ERROR(i2s_new_channel(&chan_cfg, &tx_handle, &rx_handle), TAG,
                      "new channel failed");

  i2s_std_config_t std_cfg = {
      .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
      .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT,
                                                      I2S_SLOT_MODE_STEREO),
      .gpio_cfg =
          {
              .mclk = I2S_MCLK_PIN,
              .bclk = I2S_BCLK_PIN,
              .ws = I2S_LRCLK_PIN,
              .dout = I2S_DOUT_PIN,
              .din = I2S_DIN_PIN,
          },
  };
  std_cfg.clk_cfg.mclk_multiple = MCLK_MULTIPLE;

  ESP_RETURN_ON_ERROR(i2s_channel_init_std_mode(tx_handle, &std_cfg), TAG,
                      "init tx failed");
  ESP_RETURN_ON_ERROR(i2s_channel_init_std_mode(rx_handle, &std_cfg), TAG,
                      "init rx failed");
  ESP_RETURN_ON_ERROR(i2s_channel_enable(tx_handle), TAG, "enable tx failed");
  ESP_RETURN_ON_ERROR(i2s_channel_enable(rx_handle), TAG, "enable rx failed");

  ESP_LOGI(TAG, "I2S initialized");
  return ESP_OK;
}

static esp_err_t init_codec(void) {
  // I2C bus
  i2c_master_bus_handle_t i2c_bus = NULL;
  i2c_master_bus_config_t i2c_cfg = {
      .i2c_port = I2C_NUM_0,
      .sda_io_num = I2C_SDA_PIN,
      .scl_io_num = I2C_SCL_PIN,
      .clk_source = I2C_CLK_SRC_DEFAULT,
      .glitch_ignore_cnt = 7,
      .flags.enable_internal_pullup = true,
  };
  ESP_RETURN_ON_ERROR(i2c_new_master_bus(&i2c_cfg, &i2c_bus), TAG,
                      "i2c bus failed");

  // ES8311 control interface (I2C)
  audio_codec_i2c_cfg_t codec_i2c_cfg = {
      .port = I2C_NUM_0,
      .addr = ES8311_CODEC_DEFAULT_ADDR,
      .bus_handle = i2c_bus,
  };
  const audio_codec_ctrl_if_t *ctrl_if =
      audio_codec_new_i2c_ctrl(&codec_i2c_cfg);

  // ES8311 data interface (I2S)
  audio_codec_i2s_cfg_t codec_i2s_cfg = {
      .port = I2S_NUM_0,
      .rx_handle = rx_handle,
      .tx_handle = tx_handle,
  };
  const audio_codec_data_if_t *data_if =
      audio_codec_new_i2s_data(&codec_i2s_cfg);

  // ES8311 codec
  const audio_codec_gpio_if_t *gpio_if = audio_codec_new_gpio();
  es8311_codec_cfg_t es8311_cfg = {
      .ctrl_if = ctrl_if,
      .gpio_if = gpio_if,
      .codec_mode = ESP_CODEC_DEV_WORK_MODE_DAC, // speaker only
      .master_mode = false,
      .use_mclk = true,
      .pa_pin = PA_ENABLE_PIN,
      .pa_reverted = false,
      .hw_gain =
          {
              .pa_voltage = 5.0,
              .codec_dac_voltage = 3.3,
          },
      .mclk_div = MCLK_MULTIPLE,
  };
  const audio_codec_if_t *es8311_if = es8311_codec_new(&es8311_cfg);

  // Top-level codec device
  esp_codec_dev_cfg_t dev_cfg = {
      .dev_type = ESP_CODEC_DEV_TYPE_OUT,
      .codec_if = es8311_if,
      .data_if = data_if,
  };
  codec_handle = esp_codec_dev_new(&dev_cfg);

  // Open with sample config
  esp_codec_dev_sample_info_t sample_cfg = {
      .bits_per_sample = 16,
      .channel = 2,
      .channel_mask = 0x03,
      .sample_rate = SAMPLE_RATE,
  };
  ESP_RETURN_ON_ERROR(esp_codec_dev_open(codec_handle, &sample_cfg), TAG,
                      "codec open failed");
  ESP_RETURN_ON_ERROR(esp_codec_dev_set_out_vol(codec_handle, BEEP_VOLUME), TAG,
                      "set volume failed");

  ESP_LOGI(TAG, "ES8311 codec initialized");
  return ESP_OK;
}

// Generate and play a sine wave beep
static void play_beep(int freq_hz, int duration_ms) {
  int total_samples = SAMPLE_RATE * duration_ms / 1000;
  // Stereo: 2 channels, 16-bit per sample
  int buf_size = total_samples * 2 * sizeof(int16_t);
  int16_t *buf = malloc(buf_size);
  if (!buf) {
    ESP_LOGE(TAG, "No memory for beep buffer");
    return;
  }

  for (int i = 0; i < total_samples; i++) {
    int16_t sample =
        (int16_t)(16000.0 * sin(2.0 * M_PI * freq_hz * i / SAMPLE_RATE));
    buf[i * 2] = sample;     // left
    buf[i * 2 + 1] = sample; // right
  }

  size_t bytes_written = 0;
  i2s_channel_write(tx_handle, buf, buf_size, &bytes_written, portMAX_DELAY);

  free(buf);
}

void app_main(void) {
  // Force PA enable
  gpio_set_direction(PA_ENABLE_PIN, GPIO_MODE_OUTPUT);
  gpio_set_level(PA_ENABLE_PIN, 1);

  ESP_ERROR_CHECK(init_i2s());
  ESP_ERROR_CHECK(init_codec());

  ESP_LOGI(TAG, "Playing single beep...");
  play_beep(BEEP_FREQ, BEEP_DURATION_MS);
  vTaskDelay(pdMS_TO_TICKS(500));

  ESP_LOGI(TAG, "Playing double beep...");
  play_beep(BEEP_FREQ, BEEP_DURATION_MS);
  vTaskDelay(pdMS_TO_TICKS(100));
  play_beep(BEEP_FREQ, BEEP_DURATION_MS);

  ESP_LOGI(TAG, "Done!");
}
