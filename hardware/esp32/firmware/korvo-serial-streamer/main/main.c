#include "driver/i2c_master.h"
#include "driver/i2s_tdm.h"
#include "driver/uart.h"
#include "esp_check.h"
#include "esp_codec_dev.h"
#include "esp_codec_dev_defaults.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include <stdint.h>
#include <string.h>

// ESP32-S3-Korvo-2 v3.1 ES7210 microphone pins.
#define I2C_SDA_PIN GPIO_NUM_17
#define I2C_SCL_PIN GPIO_NUM_18
#define I2S_MCLK_PIN GPIO_NUM_16
#define I2S_BCLK_PIN GPIO_NUM_9
#define I2S_LRCLK_PIN GPIO_NUM_45
#define I2S_DIN_PIN GPIO_NUM_10

#define SAMPLE_RATE 16000
#define STREAM_BAUD 921600
#define MIC_GAIN_DB 30
#define TDM_SLOTS 4
#define FRAME_SAMPLES 160 // 10 ms @ 16 kHz, matching the host micro-frontend step.
#define STREAM_CHANNELS 2 // Send both physical mics; host chooses mic1/mic2/mix.

// With MIC1+MIC2 enabled on Korvo-2 v3.1, physical mics appear in slots 0 and 2.
#define MIC1_SLOT 0
#define MIC2_SLOT 2

static const char *TAG = "korvo_pcm";
static i2s_chan_handle_t rx_chan = NULL;

#pragma pack(push, 1)
typedef struct {
  char magic[4];
  uint16_t version;
  uint16_t header_size;
  uint32_t seq;
  uint32_t sample_rate;
  uint32_t payload_bytes;
  uint16_t channels;
  uint16_t bits_per_sample;
} pcm_frame_header_t;
#pragma pack(pop)

_Static_assert(sizeof(pcm_frame_header_t) == 24, "KPCM header must stay 24 bytes");

static esp_err_t init_stream_uart(void) {
  uart_config_t cfg = {
      .baud_rate = STREAM_BAUD,
      .data_bits = UART_DATA_8_BITS,
      .parity = UART_PARITY_DISABLE,
      .stop_bits = UART_STOP_BITS_1,
      .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
      .rx_flow_ctrl_thresh = 0,
      .source_clk = UART_SCLK_DEFAULT,
  };

  esp_err_t ret = uart_driver_install(UART_NUM_0, 8192, 0, 0, NULL, 0);
  if (ret != ESP_OK && ret != ESP_ERR_INVALID_STATE) {
    return ret;
  }
  ESP_RETURN_ON_ERROR(uart_param_config(UART_NUM_0, &cfg), TAG, "uart param config failed");
  ESP_RETURN_ON_ERROR(
      uart_set_pin(UART_NUM_0, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE),
      TAG, "uart set pin failed");
  ESP_RETURN_ON_ERROR(uart_set_baudrate(UART_NUM_0, STREAM_BAUD), TAG, "uart baud failed");
  return ESP_OK;
}

static void uart_write_all(const void *data, size_t len) {
  const uint8_t *ptr = (const uint8_t *)data;
  while (len > 0) {
    int written = uart_write_bytes(UART_NUM_0, ptr, len);
    if (written > 0) {
      ptr += written;
      len -= (size_t)written;
    } else {
      vTaskDelay(pdMS_TO_TICKS(1));
    }
  }
}

static esp_err_t init_i2s(void) {
  i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
  ESP_RETURN_ON_ERROR(i2s_new_channel(&chan_cfg, NULL, &rx_chan), TAG, "new channel failed");

  i2s_tdm_config_t tdm_cfg = {
      .slot_cfg = I2S_TDM_PHILIPS_SLOT_DEFAULT_CONFIG(
          I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_STEREO,
          I2S_TDM_SLOT0 | I2S_TDM_SLOT1 | I2S_TDM_SLOT2 | I2S_TDM_SLOT3),
      .clk_cfg =
          {
              .clk_src = I2S_CLK_SRC_DEFAULT,
              .sample_rate_hz = SAMPLE_RATE,
              .mclk_multiple = I2S_MCLK_MULTIPLE_384,
          },
      .gpio_cfg =
          {
              .mclk = I2S_MCLK_PIN,
              .bclk = I2S_BCLK_PIN,
              .ws = I2S_LRCLK_PIN,
              .dout = GPIO_NUM_NC,
              .din = I2S_DIN_PIN,
          },
  };
  ESP_RETURN_ON_ERROR(i2s_channel_init_tdm_mode(rx_chan, &tdm_cfg), TAG, "tdm init failed");
  return ESP_OK;
}

static esp_err_t init_codec(void) {
  i2c_master_bus_handle_t i2c_bus = NULL;
  i2c_master_bus_config_t i2c_cfg = {
      .i2c_port = I2C_NUM_0,
      .sda_io_num = I2C_SDA_PIN,
      .scl_io_num = I2C_SCL_PIN,
      .clk_source = I2C_CLK_SRC_DEFAULT,
      .glitch_ignore_cnt = 7,
      .flags.enable_internal_pullup = true,
  };
  ESP_RETURN_ON_ERROR(i2c_new_master_bus(&i2c_cfg, &i2c_bus), TAG, "i2c bus failed");

  audio_codec_i2c_cfg_t codec_i2c_cfg = {
      .port = I2C_NUM_0,
      .addr = ES7210_CODEC_DEFAULT_ADDR,
      .bus_handle = i2c_bus,
  };
  const audio_codec_ctrl_if_t *ctrl_if = audio_codec_new_i2c_ctrl(&codec_i2c_cfg);

  audio_codec_i2s_cfg_t codec_i2s_cfg = {
      .port = I2S_NUM_0,
      .rx_handle = rx_chan,
      .tx_handle = NULL,
  };
  const audio_codec_data_if_t *data_if = audio_codec_new_i2s_data(&codec_i2s_cfg);

  es7210_codec_cfg_t es7210_cfg = {
      .ctrl_if = ctrl_if,
      .master_mode = false,
      .mic_selected = ES7210_SEL_MIC1 | ES7210_SEL_MIC2,
      .mclk_src = ES7210_MCLK_FROM_PAD,
      .mclk_div = I2S_MCLK_MULTIPLE_384,
  };
  const audio_codec_if_t *codec_if = es7210_codec_new(&es7210_cfg);

  esp_codec_dev_cfg_t dev_cfg = {
      .dev_type = ESP_CODEC_DEV_TYPE_IN,
      .codec_if = codec_if,
      .data_if = data_if,
  };
  esp_codec_dev_handle_t handle = esp_codec_dev_new(&dev_cfg);

  esp_codec_dev_sample_info_t sample_cfg = {
      .bits_per_sample = I2S_DATA_BIT_WIDTH_32BIT,
      .channel = TDM_SLOTS,
      .channel_mask = 0x000F, // all TDM slots so BCLK is computed correctly
      .sample_rate = SAMPLE_RATE,
  };
  ESP_RETURN_ON_ERROR(esp_codec_dev_open(handle, &sample_cfg), TAG, "codec open failed");
  ESP_RETURN_ON_ERROR(esp_codec_dev_set_in_gain(handle, MIC_GAIN_DB), TAG, "set gain failed");

  i2s_chan_info_t info = {0};
  ESP_RETURN_ON_ERROR(i2s_channel_get_info(rx_chan, &info), TAG, "get channel info failed");
  if (!info.is_enabled) {
    ESP_RETURN_ON_ERROR(i2s_channel_enable(rx_chan), TAG, "enable channel failed");
  }
  return ESP_OK;
}

static int16_t sample_to_i16(int32_t left_justified_sample) {
  int32_t sample = left_justified_sample >> 16;
  if (sample > INT16_MAX) {
    sample = INT16_MAX;
  } else if (sample < INT16_MIN) {
    sample = INT16_MIN;
  }
  return (int16_t)sample;
}

void app_main(void) {
  ESP_ERROR_CHECK(init_stream_uart());
  ESP_ERROR_CHECK(init_i2s());
  ESP_ERROR_CHECK(init_codec());

  // From here on, UART0 is a binary stream. Keep logs out of the audio path.
  esp_log_level_set("*", ESP_LOG_ERROR);

  const char ready[] = "KRATT_PCM_STREAM_READY v=1 sample_rate=16000 channels=2 bits=16 mic=mic1+mic2 baud=921600\n";
  uart_write_all(ready, strlen(ready));

  int32_t i2s_buf[FRAME_SAMPLES * TDM_SLOTS];
  int16_t pcm_buf[FRAME_SAMPLES * STREAM_CHANNELS];
  uint32_t seq = 0;

  while (true) {
    size_t bytes_read = 0;
    esp_err_t ret = i2s_channel_read(rx_chan, i2s_buf, sizeof(i2s_buf), &bytes_read, portMAX_DELAY);
    if (ret != ESP_OK) {
      vTaskDelay(pdMS_TO_TICKS(1));
      continue;
    }

    size_t samples = bytes_read / (TDM_SLOTS * sizeof(int32_t));
    if (samples == 0) {
      continue;
    }
    if (samples > FRAME_SAMPLES) {
      samples = FRAME_SAMPLES;
    }

    for (size_t i = 0; i < samples; ++i) {
      const size_t base = i * TDM_SLOTS;
      pcm_buf[i * STREAM_CHANNELS + 0] = sample_to_i16(i2s_buf[base + MIC1_SLOT]);
      pcm_buf[i * STREAM_CHANNELS + 1] = sample_to_i16(i2s_buf[base + MIC2_SLOT]);
    }

    pcm_frame_header_t header = {
        .magic = {'K', 'P', 'C', 'M'},
        .version = 1,
        .header_size = sizeof(pcm_frame_header_t),
        .seq = seq++,
        .sample_rate = SAMPLE_RATE,
        .payload_bytes = (uint32_t)(samples * STREAM_CHANNELS * sizeof(int16_t)),
        .channels = STREAM_CHANNELS,
        .bits_per_sample = 16,
    };

    uart_write_all(&header, sizeof(header));
    uart_write_all(pcm_buf, header.payload_bytes);
  }
}
