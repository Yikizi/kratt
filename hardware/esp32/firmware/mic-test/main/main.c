#include "driver/i2c_master.h"
#include "driver/i2s_tdm.h"
#include "esp_check.h"
#include "esp_codec_dev.h"
#include "esp_codec_dev_defaults.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <math.h>
#include <string.h>

// I2C (ES7210 configuration bus)
#define I2C_SDA_PIN 17
#define I2C_SCL_PIN 18

// I2S (ES7210 audio data)
#define I2S_MCLK_PIN 16
#define I2S_BCLK_PIN 9
#define I2S_LRCLK_PIN 45
#define I2S_DIN_PIN 10

// ES7210 config
#define SAMPLE_RATE 16000
#define CHAN_NUM 3  // MIC1 + MIC2 + MIC3
#define MIC_GAIN 30 // dB

static const char *TAG = "mic-test";

static i2s_chan_handle_t init_i2s(void) {
  i2s_chan_handle_t rx_chan = NULL;
  i2s_chan_config_t chan_cfg =
      I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
  ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, NULL, &rx_chan));

  // ES7210 uses TDM mode to multiplex multiple mics
  i2s_tdm_config_t tdm_cfg = {
      .slot_cfg = I2S_TDM_PHILIPS_SLOT_DEFAULT_CONFIG(
          I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO,
          I2S_TDM_SLOT0 | I2S_TDM_SLOT1 | I2S_TDM_SLOT2 | I2S_TDM_SLOT3),
      .clk_cfg =
          {
              .clk_src = I2S_CLK_SRC_DEFAULT,
              .sample_rate_hz = SAMPLE_RATE,
              .mclk_multiple = I2S_MCLK_MULTIPLE_256,
          },
      .gpio_cfg =
          {
              .mclk = I2S_MCLK_PIN,
              .bclk = I2S_BCLK_PIN,
              .ws = I2S_LRCLK_PIN,
              .dout = -1, // ES7210 is ADC only, no output
              .din = I2S_DIN_PIN,
          },
  };
  ESP_ERROR_CHECK(i2s_channel_init_tdm_mode(rx_chan, &tdm_cfg));

  ESP_LOGI(TAG, "I2S TDM initialized");
  return rx_chan;
}

static esp_codec_dev_handle_t init_codec(i2s_chan_handle_t rx_chan) {
  // I2C bus for ES7210 configuration
  i2c_master_bus_handle_t i2c_bus = NULL;
  i2c_master_bus_config_t i2c_cfg = {
      .i2c_port = I2C_NUM_0,
      .sda_io_num = I2C_SDA_PIN,
      .scl_io_num = I2C_SCL_PIN,
      .clk_source = I2C_CLK_SRC_DEFAULT,
      .glitch_ignore_cnt = 7,
      .flags.enable_internal_pullup = true,
  };
  ESP_ERROR_CHECK(i2c_new_master_bus(&i2c_cfg, &i2c_bus));

  // ES7210 control interface (I2C)
  audio_codec_i2c_cfg_t codec_i2c_cfg = {
      .port = I2C_NUM_0,
      .addr = ES7210_CODEC_DEFAULT_ADDR,
      .bus_handle = i2c_bus,
  };
  const audio_codec_ctrl_if_t *ctrl_if =
      audio_codec_new_i2c_ctrl(&codec_i2c_cfg);

  // ES7210 data interface (I2S)
  audio_codec_i2s_cfg_t codec_i2s_cfg = {
      .port = I2S_NUM_0,
      .rx_handle = rx_chan,
      .tx_handle = NULL,
  };
  const audio_codec_data_if_t *data_if =
      audio_codec_new_i2s_data(&codec_i2s_cfg);

  // ES7210 codec config
  es7210_codec_cfg_t es7210_cfg = {
      .ctrl_if = ctrl_if,
      .master_mode = false,
      .mic_selected = ES7210_SEL_MIC1 | ES7210_SEL_MIC2 | ES7210_SEL_MIC3,
      .mclk_src = ES7210_MCLK_FROM_PAD,
      .mclk_div = I2S_MCLK_MULTIPLE_256,
  };
  const audio_codec_if_t *es7210_if = es7210_codec_new(&es7210_cfg);

  // Top-level codec device
  esp_codec_dev_cfg_t dev_cfg = {
      .dev_type = ESP_CODEC_DEV_TYPE_IN,
      .codec_if = es7210_if,
      .data_if = data_if,
  };
  esp_codec_dev_handle_t handle = esp_codec_dev_new(&dev_cfg);

  // Open with sample config
  esp_codec_dev_sample_info_t sample_cfg = {
      .bits_per_sample = I2S_DATA_BIT_WIDTH_16BIT,
      .channel = 4, // TDM always reads 4 slots
      .channel_mask = ES7210_SEL_MIC1 | ES7210_SEL_MIC2 | ES7210_SEL_MIC3,
      .sample_rate = SAMPLE_RATE,
  };
  ESP_ERROR_CHECK(esp_codec_dev_open(handle, &sample_cfg));
  ESP_ERROR_CHECK(esp_codec_dev_set_in_gain(handle, MIC_GAIN));

  ESP_LOGI(TAG, "ES7210 codec initialized");
  return handle;
}

void app_main(void) {
  i2s_chan_handle_t rx_chan = init_i2s();
  init_codec(rx_chan);

  // Read audio and print RMS levels
  // (codec_dev_open already enables the I2S channel)
  int16_t buf[1024]; // 256 samples x 4 channels
  while (true) {
    size_t bytes_read = 0;
    esp_err_t ret =
        i2s_channel_read(rx_chan, buf, sizeof(buf), &bytes_read, portMAX_DELAY);
    if (ret != ESP_OK) {
      ESP_LOGE(TAG, "Read failed: %s", esp_err_to_name(ret));
      continue;
    }

    // Calculate RMS for mic 1 (every 4th sample in TDM interleaved data)
    int64_t sum = 0;
    int count = 0;
    for (int i = 0; i < (int)(bytes_read / sizeof(int16_t)); i += 4) {
      int32_t s = buf[i];
      sum += s * s;
      count++;
    }
    if (count > 0) {
      int rms = (int)sqrt((double)sum / count);
      ESP_LOGI(TAG, "MIC1 RMS: %d", rms);
    }

    vTaskDelay(pdMS_TO_TICKS(200));
  }
}
