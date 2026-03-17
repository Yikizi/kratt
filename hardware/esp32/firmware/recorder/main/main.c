#include "driver/i2c_master.h"
#include "driver/i2s_tdm.h"
#include "driver/sdmmc_host.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_check.h"
#include "esp_codec_dev.h"
#include "esp_codec_dev_defaults.h"
#include "esp_log.h"
#include "esp_vfs_fat.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdmmc_cmd.h"
#include <dirent.h>
#include <errno.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ── Pin definitions (ESP32-S3-Korvo-2 v3.1) ──

// Buttons (all on one ADC pin via resistor ladder)
#define BUTTON_ADC_CHANNEL ADC_CHANNEL_4 // GPIO5

// SD card (SDMMC 1-bit mode)
#define SD_CMD_PIN GPIO_NUM_7
#define SD_CLK_PIN GPIO_NUM_15
#define SD_D0_PIN GPIO_NUM_4
#define MOUNT_POINT "/sdcard"

// I2C (shared bus for ES7210 + ES8311)
#define I2C_SDA_PIN 17
#define I2C_SCL_PIN 18

// I2S (ES7210 mic array, TDM mode)
#define I2S_MCLK_PIN 16
#define I2S_BCLK_PIN 9
#define I2S_LRCLK_PIN 45
#define I2S_DIN_PIN 10

// ── Audio config ──
#define SAMPLE_RATE 48000
#define MIC_GAIN 30         // dB
#define NUM_MICS 2          // MIC1, MIC2 (Korvo-2 v3.1 has 2 physical mics)
#define TDM_SLOTS 4         // TDM always has 4 slots
#define I2S_BUF_SAMPLES 256 // samples per TDM read (per slot)

// ES7210 TDM slot mapping (with MIC1+MIC2 enabled, MIC3 disabled):
//   ADC pair 1: MIC1 → slot 0, MIC2 → slot 2
//   ADC pair 2: (disabled) → slots 1, 3 empty
// Note: "RMNM" mapping from board_def.h only applies when MIC3 is also enabled
#define MIC1_SLOT 0
#define MIC2_SLOT 2

// ── Button ADC thresholds ──
#define BTN_NONE_MIN 4000
#define BTN_REC_MIN 2650
#define BTN_REC_MAX 2950
#define BTN_MUTE_MIN 2100
#define BTN_MUTE_MAX 2400

static const char *TAG = "recorder";
static i2s_chan_handle_t rx_chan = NULL;

// ── WAV header ──

typedef struct __attribute__((packed)) {
  char riff[4];       // "RIFF"
  uint32_t file_size; // file size - 8
  char wave[4];       // "WAVE"
  char fmt[4];        // "fmt "
  uint32_t fmt_size;  // 16
  uint16_t format;    // 1 = PCM
  uint16_t channels;  // 1
  uint32_t sample_rate;
  uint32_t byte_rate;   // sample_rate * channels * bits/8
  uint16_t block_align; // channels * bits/8
  uint16_t bits;        // 16
  char data[4];         // "data"
  uint32_t data_size;   // raw audio size
} wav_header_t;

static wav_header_t make_wav_header(uint32_t data_size) {
  wav_header_t h = {
      .riff = "RIFF",
      .file_size = data_size + sizeof(wav_header_t) - 8,
      .wave = "WAVE",
      .fmt = "fmt ",
      .fmt_size = 16,
      .format = 1,
      .channels = 1,
      .sample_rate = SAMPLE_RATE,
      .byte_rate = SAMPLE_RATE * 1 * 2,
      .block_align = 1 * 2,
      .bits = 16,
      .data = "data",
      .data_size = data_size,
  };
  return h;
}

// ── SD card ──

static esp_err_t init_sd_card(void) {
  esp_vfs_fat_sdmmc_mount_config_t mount_config = {
      .format_if_mount_failed = false,
      .max_files = 5, // 2 WAV files + headroom
  };

  sdmmc_host_t host = SDMMC_HOST_DEFAULT();
  sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();
  slot_config.width = 1;
  slot_config.clk = SD_CLK_PIN;
  slot_config.cmd = SD_CMD_PIN;
  slot_config.d0 = SD_D0_PIN;
  slot_config.flags |= SDMMC_SLOT_FLAG_INTERNAL_PULLUP;

  sdmmc_card_t *card;
  esp_err_t ret = esp_vfs_fat_sdmmc_mount(MOUNT_POINT, &host, &slot_config,
                                          &mount_config, &card);
  if (ret != ESP_OK) {
    ESP_LOGE(TAG, "SD mount failed: %s", esp_err_to_name(ret));
    return ret;
  }

  ESP_LOGI(TAG, "SD card mounted");
  sdmmc_card_print_info(stdout, card);
  return ESP_OK;
}

// Find the next recording number by scanning existing files
static int find_next_rec_number(void) {
  DIR *dir = opendir(MOUNT_POINT);
  if (!dir)
    return 1;

  int max_num = 0;
  struct dirent *entry;
  while ((entry = readdir(dir)) != NULL) {
    int num;
    if (sscanf(entry->d_name, "rec_%d", &num) == 1) {
      if (num > max_num)
        max_num = num;
    }
  }
  closedir(dir);
  return max_num + 1;
}

// ── I2S + ES7210 mic ──

static esp_err_t init_i2s(void) {
  i2s_chan_config_t chan_cfg =
      I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
  ESP_RETURN_ON_ERROR(i2s_new_channel(&chan_cfg, NULL, &rx_chan), TAG,
                      "new channel failed");

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
              .dout = -1,
              .din = I2S_DIN_PIN,
          },
  };
  ESP_RETURN_ON_ERROR(i2s_channel_init_tdm_mode(rx_chan, &tdm_cfg), TAG,
                      "init tdm failed");

  ESP_LOGI(TAG, "I2S TDM initialized");
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
  ESP_RETURN_ON_ERROR(i2c_new_master_bus(&i2c_cfg, &i2c_bus), TAG,
                      "i2c bus failed");

  audio_codec_i2c_cfg_t codec_i2c_cfg = {
      .port = I2C_NUM_0,
      .addr = ES7210_CODEC_DEFAULT_ADDR,
      .bus_handle = i2c_bus,
  };
  const audio_codec_ctrl_if_t *ctrl_if =
      audio_codec_new_i2c_ctrl(&codec_i2c_cfg);

  audio_codec_i2s_cfg_t codec_i2s_cfg = {
      .port = I2S_NUM_0,
      .rx_handle = rx_chan,
      .tx_handle = NULL,
  };
  const audio_codec_data_if_t *data_if =
      audio_codec_new_i2s_data(&codec_i2s_cfg);

  es7210_codec_cfg_t es7210_cfg = {
      .ctrl_if = ctrl_if,
      .master_mode = false,
      .mic_selected = ES7210_SEL_MIC1 | ES7210_SEL_MIC2,
      .mclk_src = ES7210_MCLK_FROM_PAD,
      .mclk_div = I2S_MCLK_MULTIPLE_384,
  };
  const audio_codec_if_t *es7210_if = es7210_codec_new(&es7210_cfg);

  esp_codec_dev_cfg_t dev_cfg = {
      .dev_type = ESP_CODEC_DEV_TYPE_IN,
      .codec_if = es7210_if,
      .data_if = data_if,
  };
  esp_codec_dev_handle_t handle = esp_codec_dev_new(&dev_cfg);

  esp_codec_dev_sample_info_t sample_cfg = {
      .bits_per_sample = I2S_DATA_BIT_WIDTH_32BIT,
      .channel = TDM_SLOTS,
      .channel_mask = 0x000F, // all 4 TDM slots for correct BCLK calculation
      .sample_rate = SAMPLE_RATE,
  };
  ESP_RETURN_ON_ERROR(esp_codec_dev_open(handle, &sample_cfg), TAG,
                      "codec open failed");
  ESP_RETURN_ON_ERROR(esp_codec_dev_set_in_gain(handle, MIC_GAIN), TAG,
                      "set gain failed");

  ESP_LOGI(TAG, "ES7210 codec initialized");
  return ESP_OK;
}

// ── Buttons ──

typedef enum {
  BTN_NONE,
  BTN_REC,
  BTN_MUTE,
} button_t;

static button_t read_button(adc_oneshot_unit_handle_t adc) {
  int raw;
  if (adc_oneshot_read(adc, BUTTON_ADC_CHANNEL, &raw) != ESP_OK)
    return BTN_NONE;
  if (raw >= BTN_NONE_MIN)
    return BTN_NONE;
  if (raw >= BTN_REC_MIN && raw <= BTN_REC_MAX)
    return BTN_REC;
  if (raw >= BTN_MUTE_MIN && raw <= BTN_MUTE_MAX)
    return BTN_MUTE;
  return BTN_NONE;
}

// ── ADC init ──

static adc_oneshot_unit_handle_t init_buttons(void) {
  adc_oneshot_unit_handle_t adc_handle;
  adc_oneshot_unit_init_cfg_t init_cfg = {
      .unit_id = ADC_UNIT_1,
  };
  ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_cfg, &adc_handle));

  adc_oneshot_chan_cfg_t chan_cfg = {
      .atten = ADC_ATTEN_DB_12,
      .bitwidth = ADC_BITWIDTH_DEFAULT,
  };
  ESP_ERROR_CHECK(
      adc_oneshot_config_channel(adc_handle, BUTTON_ADC_CHANNEL, &chan_cfg));

  return adc_handle;
}

// ── Main ──

void app_main(void) {
  // Init all peripherals
  ESP_ERROR_CHECK(init_sd_card());
  ESP_ERROR_CHECK(init_i2s());
  ESP_ERROR_CHECK(init_codec());
  adc_oneshot_unit_handle_t adc = init_buttons();

  int rec_num = find_next_rec_number();
  ESP_LOGI(TAG, "Next recording number: %d", rec_num);
  ESP_LOGI(TAG, "Ready. Press REC to start, MUTE to stop.");

  // I2S read buffer: TDM_SLOTS channels interleaved, 32-bit per slot
  int32_t i2s_buf[I2S_BUF_SAMPLES * TDM_SLOTS];
  // Per-mic mono buffers for deinterleaving (downconverted to 16-bit)
  int16_t mic_buf[NUM_MICS][I2S_BUF_SAMPLES];

  bool recording = false;
  FILE *wav_files[NUM_MICS] = {NULL};
  uint32_t data_written = 0;
  button_t prev_btn = BTN_NONE;
  bool debug_printed = false;

  while (true) {
    // Poll button (edge detection)
    button_t btn = read_button(adc);
    bool btn_pressed = (btn != BTN_NONE && prev_btn == BTN_NONE);
    prev_btn = btn;

    // ── Start recording ──
    if (btn_pressed && btn == BTN_REC && !recording) {
      ESP_LOGI(TAG, ">>> REC START #%04d", rec_num);

      // Open WAV files (one per mic)
      for (int m = 0; m < NUM_MICS; m++) {
        char path[64];
        snprintf(path, sizeof(path), MOUNT_POINT "/rec_%04d_mic%d.wav", rec_num,
                 m + 1);
        wav_files[m] = fopen(path, "wb");
        if (!wav_files[m]) {
          ESP_LOGE(TAG, "Failed to open %s: %s", path, strerror(errno));
          // Close any already opened
          for (int j = 0; j < m; j++) {
            fclose(wav_files[j]);
            wav_files[j] = NULL;
          }
          goto skip;
        }
        // Write placeholder header (will update at end)
        wav_header_t hdr = make_wav_header(0);
        fwrite(&hdr, sizeof(hdr), 1, wav_files[m]);
      }

      recording = true;
      data_written = 0;
    }

    // ── Stop recording ──
    if (btn_pressed && btn == BTN_MUTE && recording) {
      ESP_LOGI(TAG, "<<< REC STOP #%04d (%d bytes per mic)", rec_num,
               data_written);

      // Update WAV headers with actual size and close files
      for (int m = 0; m < NUM_MICS; m++) {
        if (wav_files[m]) {
          fseek(wav_files[m], 0, SEEK_SET);
          wav_header_t hdr = make_wav_header(data_written);
          fwrite(&hdr, sizeof(hdr), 1, wav_files[m]);
          fclose(wav_files[m]);
          wav_files[m] = NULL;
        }
      }

      recording = false;
      rec_num++;
      ESP_LOGI(TAG, "Ready. Press REC to start, MUTE to stop.");
    }

  skip:
    // ── Record audio ──
    if (recording) {
      size_t bytes_read = 0;
      esp_err_t ret = i2s_channel_read(rx_chan, i2s_buf, sizeof(i2s_buf),
                                       &bytes_read, portMAX_DELAY);
      if (ret != ESP_OK) {
        ESP_LOGE(TAG, "I2S read failed: %s", esp_err_to_name(ret));
        continue;
      }

      // Debug: print first 8 int32_t values (2 TDM frames) to verify layout
      if (!debug_printed) {
        ESP_LOGI(TAG, "I2S buf (%d bytes). First 2 frames (8 slots):",
                 (int)bytes_read);
        for (int d = 0; d < 8 && d < (int)(bytes_read / sizeof(int32_t)); d++) {
          ESP_LOGI(TAG, "  [%d] slot%d = %ld (0x%08lX)", d, d % TDM_SLOTS,
                   (long)i2s_buf[d], (unsigned long)i2s_buf[d]);
        }
        debug_printed = true;
      }

      // Deinterleave: 32-bit TDM data [S0,S1,S2,S3, S0,S1,S2,S3, ...]
      // Korvo-2 mapping: MIC1=slot1, MIC2=slot3
      // Downconvert 32-bit to 16-bit: ES7210 outputs 24-bit left-justified
      // in 32 bits (0xXXXXXX00), so >> 16 takes the top 16 of 24 bits
      int samples = bytes_read / (TDM_SLOTS * sizeof(int32_t));
      for (int i = 0; i < samples; i++) {
        mic_buf[0][i] = (int16_t)(i2s_buf[i * TDM_SLOTS + MIC1_SLOT] >> 16);
        mic_buf[1][i] = (int16_t)(i2s_buf[i * TDM_SLOTS + MIC2_SLOT] >> 16);
      }

      // Write each mic to its file
      size_t mono_bytes = samples * sizeof(int16_t);
      for (int m = 0; m < NUM_MICS; m++) {
        if (wav_files[m]) {
          fwrite(mic_buf[m], 1, mono_bytes, wav_files[m]);
        }
      }
      data_written += mono_bytes;
    } else {
      // Not recording, just poll slowly
      vTaskDelay(pdMS_TO_TICKS(20));
    }
  }
}
