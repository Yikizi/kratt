#include "driver/i2c_master.h"
#include "driver/i2s_tdm.h"
#include "driver/sdmmc_host.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_check.h"
#include "esp_codec_dev.h"
#include "esp_codec_dev_defaults.h"
#include "esp_event.h"
#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_netif.h"
#include "esp_vfs_fat.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "lwip/inet.h"
#include "nvs_flash.h"
#include "sdmmc_cmd.h"
#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

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
// Verify with logger firmware if values don't match your board revision
#define BTN_NONE_MIN 4000
#define BTN_REC_MIN 2650
#define BTN_REC_MAX 2950
#define BTN_MUTE_MIN 2100
#define BTN_MUTE_MAX 2400
#define BTN_PLAY_MIN 1100
#define BTN_PLAY_MAX 1400
#define BTN_SET_MIN 1750
#define BTN_SET_MAX 2050

// ── WiFi AP config ──
#define WIFI_SSID "Kratt-Recorder"
#define WIFI_MAX_CONN 2

// ── HTTP config ──
#define FILE_BUF_SIZE 4096
#define SSE_WORKER_STACK 4096

static const char *TAG = "recorder";
static i2s_chan_handle_t rx_chan = NULL;

// ── Buttons ──

typedef enum {
  BTN_NONE,
  BTN_REC,  // positive data
  BTN_MUTE, // stop recording
  BTN_PLAY, // negative data
  BTN_SET,  // ambient data
} button_t;

// Recording type determines filename prefix
typedef enum {
  REC_POSITIVE, // rec_NNNN_mic*.wav
  REC_NEGATIVE, // neg_NNNN_mic*.wav
  REC_AMBIENT,  // amb_NNNN_mic*.wav
} rec_type_t;

// Recording type prefixes (must be defined before find_next_rec_number)
static const char *rec_prefix[] = {"rec", "neg", "amb"};
static const char *rec_type_name[] = {"positive", "negative", "ambient"};

// ── Command queue (HTTP → main loop) ──
typedef enum { CMD_REC_START, CMD_REC_STOP } cmd_type_t;
typedef struct {
  cmd_type_t type;
  rec_type_t rec_type;
} recorder_cmd_t;
static QueueHandle_t cmd_queue = NULL;

// ── Event group (main loop → SSE) ──
#define EVT_STATE_CHANGED BIT0
static EventGroupHandle_t state_events = NULL;

// ── Shared state (written only by main loop, read by HTTP handlers) ──
// On Xtensa (ESP32-S3), 32-bit aligned reads/writes are atomic.
// Single writer (app_main) + multiple readers (HTTP handlers) is safe.
static volatile bool g_recording = false;
static volatile rec_type_t g_rec_type = REC_POSITIVE;
static volatile int g_rec_num = 0;
static volatile bool g_sd_mounted = false;

// ── SSE async worker ──
typedef esp_err_t (*httpd_req_handler_t)(httpd_req_t *req);
typedef struct {
  httpd_req_t *req;
  httpd_req_handler_t handler;
} httpd_async_req_t;
static QueueHandle_t sse_queue = NULL;
static SemaphoreHandle_t sse_worker_ready = NULL;

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

static sdmmc_card_t *sd_card = NULL;

static void unmount_sd(void) {
  if (!g_sd_mounted)
    return;
  esp_vfs_fat_sdcard_unmount(MOUNT_POINT, sd_card);
  sd_card = NULL;
  g_sd_mounted = false;
  ESP_LOGW(TAG, "SD card unmounted");
}

static void try_mount_sd(void) {
  if (g_sd_mounted)
    return;

  esp_vfs_fat_sdmmc_mount_config_t mount_config = {
      .format_if_mount_failed = false,
      .max_files = 7,
  };

  sdmmc_host_t host = SDMMC_HOST_DEFAULT();
  sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();
  slot_config.width = 1;
  slot_config.clk = SD_CLK_PIN;
  slot_config.cmd = SD_CMD_PIN;
  slot_config.d0 = SD_D0_PIN;
  slot_config.flags |= SDMMC_SLOT_FLAG_INTERNAL_PULLUP;

  // Suppress noisy driver logs during retry
  esp_log_level_set("sdmmc_common", ESP_LOG_NONE);
  esp_log_level_set("vfs_fat_sdmmc", ESP_LOG_NONE);
  esp_err_t ret = esp_vfs_fat_sdmmc_mount(MOUNT_POINT, &host, &slot_config,
                                          &mount_config, &sd_card);
  esp_log_level_set("sdmmc_common", ESP_LOG_WARN);
  esp_log_level_set("vfs_fat_sdmmc", ESP_LOG_WARN);

  if (ret == ESP_OK) {
    g_sd_mounted = true;
    ESP_LOGI(TAG, "SD card mounted");
    sdmmc_card_print_info(stdout, sd_card);
  }
}

// Find the next recording number by scanning all prefixes
static int find_next_rec_number(void) {
  DIR *dir = opendir(MOUNT_POINT);
  if (!dir)
    return 1;

  int max_num = 0;
  struct dirent *entry;
  while ((entry = readdir(dir)) != NULL) {
    int num;
    for (int p = 0; p < 3; p++) {
      char fmt[16];
      snprintf(fmt, sizeof(fmt), "%s_%%d", rec_prefix[p]);
      if (sscanf(entry->d_name, fmt, &num) == 1) {
        if (num > max_num)
          max_num = num;
      }
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
  if (raw >= BTN_PLAY_MIN && raw <= BTN_PLAY_MAX)
    return BTN_PLAY;
  if (raw >= BTN_SET_MIN && raw <= BTN_SET_MAX)
    return BTN_SET;
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

// ── WiFi AP ──

static void wifi_event_handler(void *arg, esp_event_base_t event_base,
                               int32_t event_id, void *event_data) {
  if (event_id == WIFI_EVENT_AP_STACONNECTED) {
    wifi_event_ap_staconnected_t *event =
        (wifi_event_ap_staconnected_t *)event_data;
    ESP_LOGI(TAG, "Client connected: " MACSTR, MAC2STR(event->mac));
  } else if (event_id == WIFI_EVENT_AP_STADISCONNECTED) {
    wifi_event_ap_stadisconnected_t *event =
        (wifi_event_ap_stadisconnected_t *)event_data;
    ESP_LOGI(TAG, "Client disconnected: " MACSTR, MAC2STR(event->mac));
  }
}

static void wifi_init_softap(void) {
  esp_netif_create_default_wifi_ap();

  wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
  ESP_ERROR_CHECK(esp_wifi_init(&cfg));

  ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID,
                                             &wifi_event_handler, NULL));

  wifi_config_t wifi_config = {
      .ap =
          {
              .ssid = WIFI_SSID,
              .ssid_len = strlen(WIFI_SSID),
              .max_connection = WIFI_MAX_CONN,
              .authmode = WIFI_AUTH_OPEN,
          },
  };

  ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
  ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_config));
  ESP_ERROR_CHECK(esp_wifi_start());

  esp_netif_ip_info_t ip_info;
  esp_netif_get_ip_info(esp_netif_get_handle_from_ifkey("WIFI_AP_DEF"),
                        &ip_info);
  char ip_addr[16];
  inet_ntoa_r(ip_info.ip.addr, ip_addr, 16);
  ESP_LOGI(TAG, "WiFi AP started: SSID=%s, IP=%s", WIFI_SSID, ip_addr);
}

// ── HTTP handlers ──

// Build JSON status string into buf, return length
static int build_status_json(char *buf, size_t bufsize) {
  return snprintf(buf, bufsize,
                  "{\"recording\":%s,\"type\":\"%s\",\"num\":%d,\"sd\":%s}",
                  g_recording ? "true" : "false", rec_type_name[g_rec_type],
                  g_rec_num, g_sd_mounted ? "true" : "false");
}

// GET / — serve embedded HTML
static esp_err_t root_handler(httpd_req_t *req) {
  extern const char index_html_start[] asm("_binary_index_html_start");
  extern const char index_html_end[] asm("_binary_index_html_end");
  httpd_resp_set_type(req, "text/html");
  httpd_resp_send(req, index_html_start, index_html_end - index_html_start);
  return ESP_OK;
}

// GET /api/status — JSON status
static esp_err_t status_handler(httpd_req_t *req) {
  char buf[128];
  int len = build_status_json(buf, sizeof(buf));
  httpd_resp_set_type(req, "application/json");
  httpd_resp_send(req, buf, len);
  return ESP_OK;
}

// GET /api/record?type=positive|negative|ambient
static esp_err_t record_handler(httpd_req_t *req) {
  if (g_recording) {
    httpd_resp_set_status(req, "409 Conflict");
    httpd_resp_sendstr(req, "{\"error\":\"already recording\"}");
    return ESP_OK;
  }
  if (!g_sd_mounted) {
    httpd_resp_set_status(req, "503 Service Unavailable");
    httpd_resp_sendstr(req, "{\"error\":\"no SD card\"}");
    return ESP_OK;
  }

  // Parse type query param
  char query[64] = {0};
  char type_str[16] = {0};
  rec_type_t rtype = REC_POSITIVE;

  if (httpd_req_get_url_query_str(req, query, sizeof(query)) == ESP_OK) {
    httpd_query_key_value(query, "type", type_str, sizeof(type_str));
  }

  if (strcmp(type_str, "negative") == 0) {
    rtype = REC_NEGATIVE;
  } else if (strcmp(type_str, "ambient") == 0) {
    rtype = REC_AMBIENT;
  } else {
    rtype = REC_POSITIVE;
  }

  recorder_cmd_t cmd = {.type = CMD_REC_START, .rec_type = rtype};
  if (xQueueSend(cmd_queue, &cmd, pdMS_TO_TICKS(100)) != pdTRUE) {
    httpd_resp_set_status(req, "503 Service Unavailable");
    httpd_resp_sendstr(req, "{\"error\":\"busy\"}");
    return ESP_OK;
  }

  httpd_resp_set_type(req, "application/json");
  httpd_resp_sendstr(req, "{\"ok\":true}");
  return ESP_OK;
}

// GET /api/stop
static esp_err_t stop_handler(httpd_req_t *req) {
  if (!g_recording) {
    httpd_resp_set_status(req, "409 Conflict");
    httpd_resp_sendstr(req, "{\"error\":\"not recording\"}");
    return ESP_OK;
  }

  recorder_cmd_t cmd = {.type = CMD_REC_STOP};
  if (xQueueSend(cmd_queue, &cmd, pdMS_TO_TICKS(100)) != pdTRUE) {
    httpd_resp_set_status(req, "503 Service Unavailable");
    httpd_resp_sendstr(req, "{\"error\":\"busy\"}");
    return ESP_OK;
  }

  httpd_resp_set_type(req, "application/json");
  httpd_resp_sendstr(req, "{\"ok\":true}");
  return ESP_OK;
}

// GET /api/files — JSON array of files
static esp_err_t files_handler(httpd_req_t *req) {
  if (!g_sd_mounted) {
    httpd_resp_set_type(req, "application/json");
    httpd_resp_sendstr(req, "[]");
    return ESP_OK;
  }

  DIR *dir = opendir(MOUNT_POINT);
  if (!dir) {
    httpd_resp_set_type(req, "application/json");
    httpd_resp_sendstr(req, "[]");
    return ESP_OK;
  }

  httpd_resp_set_type(req, "application/json");
  httpd_resp_sendstr_chunk(req, "[");

  struct dirent *entry;
  struct stat st;
  char path[288]; // MOUNT_POINT + "/" + d_name(255)
  char item[320];
  bool first = true;

  while ((entry = readdir(dir)) != NULL) {
    // Only list .wav files
    size_t nlen = strlen(entry->d_name);
    if (nlen < 5 || strcasecmp(entry->d_name + nlen - 4, ".wav") != 0)
      continue;

    snprintf(path, sizeof(path), MOUNT_POINT "/%s", entry->d_name);
    long size = 0;
    if (stat(path, &st) == 0)
      size = st.st_size;

    int len = snprintf(item, sizeof(item), "%s{\"name\":\"%s\",\"size\":%ld}",
                       first ? "" : ",", entry->d_name, size);
    httpd_resp_send_chunk(req, item, len);
    first = false;
  }
  closedir(dir);

  httpd_resp_sendstr_chunk(req, "]");
  httpd_resp_sendstr_chunk(req, NULL);
  return ESP_OK;
}

// GET /files/<filename> — download file
static esp_err_t download_handler(httpd_req_t *req) {
  // Extract filename from URI (skip "/files/")
  const char *filename = req->uri + 7; // strlen("/files/") == 7
  if (strlen(filename) == 0 || strlen(filename) > 63 ||
      strstr(filename, "..") || strstr(filename, "/")) {
    httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "Invalid filename");
    return ESP_OK;
  }
  if (!g_sd_mounted) {
    httpd_resp_set_status(req, "503 Service Unavailable");
    httpd_resp_sendstr(req, "No SD card");
    return ESP_OK;
  }

  char path[80]; // safe: MOUNT_POINT(7) + "/" + filename(max 63) + NUL
  snprintf(path, sizeof(path), MOUNT_POINT "/%s", filename);

  FILE *f = fopen(path, "rb");
  if (!f) {
    httpd_resp_send_err(req, HTTPD_404_NOT_FOUND, "File not found");
    return ESP_OK;
  }

  httpd_resp_set_type(req, "audio/wav");
  char hdr[96];
  snprintf(hdr, sizeof(hdr), "attachment; filename=\"%s\"", filename);
  httpd_resp_set_hdr(req, "Content-Disposition", hdr);

  char *buf = malloc(FILE_BUF_SIZE);
  if (!buf) {
    fclose(f);
    httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "No memory");
    return ESP_OK;
  }

  size_t read_bytes;
  do {
    read_bytes = fread(buf, 1, FILE_BUF_SIZE, f);
    if (read_bytes > 0) {
      if (httpd_resp_send_chunk(req, buf, read_bytes) != ESP_OK) {
        fclose(f);
        free(buf);
        httpd_resp_sendstr_chunk(req, NULL);
        return ESP_OK;
      }
    }
  } while (read_bytes > 0);

  fclose(f);
  free(buf);
  httpd_resp_send_chunk(req, NULL, 0);
  return ESP_OK;
}

// GET /api/delete?file=name.wav
static esp_err_t delete_handler(httpd_req_t *req) {
  if (!g_sd_mounted) {
    httpd_resp_set_status(req, "503 Service Unavailable");
    httpd_resp_sendstr(req, "{\"error\":\"no SD card\"}");
    return ESP_OK;
  }

  char query[128] = {0};
  char filename[64] = {0};
  if (httpd_req_get_url_query_str(req, query, sizeof(query)) != ESP_OK ||
      httpd_query_key_value(query, "file", filename, sizeof(filename)) !=
          ESP_OK) {
    httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "Missing file param");
    return ESP_OK;
  }

  // Security: reject path traversal and non-wav files
  if (strstr(filename, "..") || strstr(filename, "/") || strlen(filename) < 5 ||
      strcasecmp(filename + strlen(filename) - 4, ".wav") != 0) {
    httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "Invalid filename");
    return ESP_OK;
  }

  // Don't delete files being recorded right now
  if (g_recording) {
    char cur_prefix[16];
    snprintf(cur_prefix, sizeof(cur_prefix), "%s_%04d_", rec_prefix[g_rec_type],
             g_rec_num);
    if (strncmp(filename, cur_prefix, strlen(cur_prefix)) == 0) {
      httpd_resp_set_status(req, "409 Conflict");
      httpd_resp_sendstr(req, "{\"error\":\"file is being recorded\"}");
      return ESP_OK;
    }
  }

  char path[80];
  snprintf(path, sizeof(path), MOUNT_POINT "/%s", filename);
  if (unlink(path) != 0) {
    httpd_resp_send_err(req, HTTPD_404_NOT_FOUND, "File not found");
    return ESP_OK;
  }

  httpd_resp_set_type(req, "application/json");
  httpd_resp_sendstr(req, "{\"ok\":true}");
  return ESP_OK;
}

// ── SSE (Server-Sent Events) via async handler ──

// Actual SSE streaming — runs on async worker task
static esp_err_t sse_stream(httpd_req_t *req) {
  httpd_resp_set_type(req, "text/event-stream");
  httpd_resp_set_hdr(req, "Cache-Control", "no-cache");
  httpd_resp_set_hdr(req, "Connection", "keep-alive");

  // Send current state immediately so browser doesn't wait for first event
  char buf[192];
  char json[128];
  build_status_json(json, sizeof(json));
  int len = snprintf(buf, sizeof(buf), "data: %s\n\n", json);
  if (httpd_resp_send_chunk(req, buf, len) != ESP_OK)
    goto done;

  while (true) {
    // Wait for state change or timeout (keepalive every 3s).
    // Short timeout so we detect dead connections quickly — otherwise
    // the worker stays blocked for 15s after client disconnects,
    // causing "SSE worker busy" spam when browser reconnects.
    EventBits_t bits = xEventGroupWaitBits(
        state_events, EVT_STATE_CHANGED, pdTRUE, pdFALSE, pdMS_TO_TICKS(3000));

    if (bits & EVT_STATE_CHANGED) {
      build_status_json(json, sizeof(json));
      len = snprintf(buf, sizeof(buf), "data: %s\n\n", json);
      if (httpd_resp_send_chunk(req, buf, len) != ESP_OK)
        break;
    } else {
      // Keepalive comment (also probes if connection is still alive)
      if (httpd_resp_send_chunk(req, ": keepalive\n\n", 14) != ESP_OK)
        break;
    }
  }

done:
  httpd_resp_send_chunk(req, NULL, 0);
  return ESP_OK;
}

// SSE async worker task — holds the long-lived SSE connection
static void sse_worker_task(void *arg) {
  ESP_LOGI(TAG, "SSE worker started");
  while (true) {
    xSemaphoreGive(sse_worker_ready);
    httpd_async_req_t async_req;
    if (xQueueReceive(sse_queue, &async_req, portMAX_DELAY)) {
      ESP_LOGI(TAG, "SSE client connected");
      async_req.handler(async_req.req);
      ESP_LOGI(TAG, "SSE client disconnected");
      if (httpd_req_async_handler_complete(async_req.req) != ESP_OK) {
        ESP_LOGE(TAG, "Failed to complete async SSE req");
      }
    }
  }
}

// GET /api/events — SSE entry point, queues to async worker
static esp_err_t events_handler(httpd_req_t *req) {
  // Check worker availability BEFORE async_handler_begin, because after
  // that call the original req is invalidated and can't be used for responses
  if (xSemaphoreTake(sse_worker_ready, 0) == pdFALSE) {
    ESP_LOGW(TAG, "SSE worker busy");
    httpd_resp_set_status(req, "503 Service Unavailable");
    httpd_resp_sendstr(req, "SSE slot busy");
    return ESP_OK;
  }

  httpd_req_t *copy = NULL;
  esp_err_t err = httpd_req_async_handler_begin(req, &copy);
  if (err != ESP_OK) {
    xSemaphoreGive(sse_worker_ready); // return the semaphore we took
    return err;
  }

  httpd_async_req_t async_req = {.req = copy, .handler = sse_stream};
  if (xQueueSend(sse_queue, &async_req, pdMS_TO_TICKS(100)) == pdFALSE) {
    ESP_LOGE(TAG, "SSE queue full");
    httpd_req_async_handler_complete(copy);
    xSemaphoreGive(sse_worker_ready);
    return ESP_FAIL;
  }

  return ESP_OK;
}

// ── Start HTTP server ──

static void start_sse_worker(void) {
  sse_worker_ready = xSemaphoreCreateCounting(1, 0);
  sse_queue = xQueueCreate(1, sizeof(httpd_async_req_t));
  xTaskCreate(sse_worker_task, "sse_worker", SSE_WORKER_STACK, NULL, 5, NULL);
}

static httpd_handle_t start_webserver(void) {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.lru_purge_enable = true;
  config.max_open_sockets = 5; // 1 SSE + browser parallel requests
  config.max_uri_handlers = 8;
  config.uri_match_fn = httpd_uri_match_wildcard;
  config.stack_size = 8192;

  httpd_handle_t server = NULL;
  if (httpd_start(&server, &config) != ESP_OK) {
    ESP_LOGE(TAG, "Failed to start HTTP server");
    return NULL;
  }

  const httpd_uri_t routes[] = {
      {.uri = "/", .method = HTTP_GET, .handler = root_handler},
      {.uri = "/api/status", .method = HTTP_GET, .handler = status_handler},
      {.uri = "/api/events", .method = HTTP_GET, .handler = events_handler},
      {.uri = "/api/record", .method = HTTP_GET, .handler = record_handler},
      {.uri = "/api/stop", .method = HTTP_GET, .handler = stop_handler},
      {.uri = "/api/files", .method = HTTP_GET, .handler = files_handler},
      {.uri = "/api/delete", .method = HTTP_GET, .handler = delete_handler},
      {.uri = "/files/*", .method = HTTP_GET, .handler = download_handler},
  };

  for (int i = 0; i < sizeof(routes) / sizeof(routes[0]); i++) {
    httpd_register_uri_handler(server, &routes[i]);
  }

  ESP_LOGI(TAG, "HTTP server started on port 80");
  return server;
}

// ── Main ──

void app_main(void) {
  // NVS (required by WiFi)
  ESP_ERROR_CHECK(nvs_flash_init());

  // Network stack
  ESP_ERROR_CHECK(esp_netif_init());
  ESP_ERROR_CHECK(esp_event_loop_create_default());

  // Init audio and buttons (required)
  ESP_ERROR_CHECK(init_i2s());
  ESP_ERROR_CHECK(init_codec());
  adc_oneshot_unit_handle_t adc = init_buttons();

  // Try SD card (optional — will retry in main loop)
  try_mount_sd();
  if (!g_sd_mounted)
    ESP_LOGW(TAG, "No SD card. Insert one and it will be detected.");

  int rec_num = g_sd_mounted ? find_next_rec_number() : 1;
  g_rec_num = rec_num;

  // IPC primitives
  cmd_queue = xQueueCreate(4, sizeof(recorder_cmd_t));
  state_events = xEventGroupCreate();

  // WiFi AP
  wifi_init_softap();

  // HTTP server + SSE worker
  start_sse_worker();
  start_webserver();

  ESP_LOGI(TAG, "Ready. Open http://192.168.4.1 or use buttons.");
  ESP_LOGI(TAG, "REC=positive, PLAY=negative, SET=ambient, MUTE=stop");

  // I2S read buffer: TDM_SLOTS channels interleaved, 32-bit per slot
  int32_t i2s_buf[I2S_BUF_SAMPLES * TDM_SLOTS];
  // Per-mic mono buffers for deinterleaving (downconverted to 16-bit)
  int16_t mic_buf[NUM_MICS][I2S_BUF_SAMPLES];

  bool recording = false;
  rec_type_t rec_type = REC_POSITIVE;
  FILE *wav_files[NUM_MICS] = {NULL};
  uint32_t data_written = 0;
  button_t prev_btn = BTN_NONE;
  bool debug_printed = false;

  while (true) {
    // Poll button (edge detection)
    button_t btn = read_button(adc);
    bool btn_pressed = (btn != BTN_NONE && prev_btn == BTN_NONE);
    prev_btn = btn;

    // ── Check HTTP commands (non-blocking) ──
    recorder_cmd_t cmd;
    bool cmd_start = false;
    bool cmd_stop = false;
    rec_type_t cmd_rec_type = REC_POSITIVE;

    if (xQueueReceive(cmd_queue, &cmd, 0) == pdTRUE) {
      if (cmd.type == CMD_REC_START && !recording && g_sd_mounted) {
        cmd_start = true;
        cmd_rec_type = cmd.rec_type;
      } else if (cmd.type == CMD_REC_STOP && recording) {
        cmd_stop = true;
      }
    }

    // ── Try mounting SD every ~2 seconds if not yet available ──
    static int sd_retry_counter = 0;
    if (!g_sd_mounted && !recording && ++sd_retry_counter >= 100) {
      sd_retry_counter = 0;
      try_mount_sd();
      if (g_sd_mounted) {
        rec_num = find_next_rec_number();
        g_rec_num = rec_num;
        ESP_LOGI(TAG, "SD ready. Next recording: #%04d", rec_num);
        xEventGroupSetBits(state_events, EVT_STATE_CHANGED);
      }
    }

    // ── Start recording (button or HTTP command) ──
    bool start_from_btn = btn_pressed && !recording &&
                          (btn == BTN_REC || btn == BTN_PLAY || btn == BTN_SET);
    if ((start_from_btn || cmd_start) && !recording) {
      if (!g_sd_mounted) {
        ESP_LOGW(TAG, "No SD card — cannot record");
        goto skip;
      }
      if (start_from_btn) {
        rec_type = (btn == BTN_REC)    ? REC_POSITIVE
                   : (btn == BTN_PLAY) ? REC_NEGATIVE
                                       : REC_AMBIENT;
      } else {
        rec_type = cmd_rec_type;
      }
      ESP_LOGI(TAG, ">>> %s START #%04d", rec_prefix[rec_type], rec_num);

      // Open WAV files (one per mic)
      for (int m = 0; m < NUM_MICS; m++) {
        char path[64];
        snprintf(path, sizeof(path), MOUNT_POINT "/%s_%04d_mic%d.wav",
                 rec_prefix[rec_type], rec_num, m + 1);
        wav_files[m] = fopen(path, "wb");
        if (!wav_files[m]) {
          ESP_LOGE(TAG, "Failed to open %s: %s", path, strerror(errno));
          for (int j = 0; j < m; j++) {
            fclose(wav_files[j]);
            wav_files[j] = NULL;
          }
          unmount_sd(); // SD likely removed — will retry mounting
          xEventGroupSetBits(state_events, EVT_STATE_CHANGED);
          goto skip;
        }
        // Write placeholder header (will update at end)
        wav_header_t hdr = make_wav_header(0);
        fwrite(&hdr, sizeof(hdr), 1, wav_files[m]);
      }

      recording = true;
      g_recording = true;
      g_rec_type = rec_type;
      data_written = 0;
      xEventGroupSetBits(state_events, EVT_STATE_CHANGED);
    }

    // ── Stop recording (button or HTTP command) ──
    bool stop_from_btn = btn_pressed && btn == BTN_MUTE && recording;
    if ((stop_from_btn || cmd_stop) && recording) {
      ESP_LOGI(TAG, "<<< %s STOP #%04d (%lu bytes per mic)",
               rec_prefix[rec_type], rec_num, (unsigned long)data_written);

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
      g_recording = false;
      rec_num++;
      g_rec_num = rec_num;
      xEventGroupSetBits(state_events, EVT_STATE_CHANGED);
      ESP_LOGI(TAG,
               "Ready. REC=positive, PLAY=negative, SET=ambient, MUTE=stop");
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
      // Korvo-2 mapping: MIC1=slot0, MIC2=slot2
      // Downconvert 32-bit to 16-bit: ES7210 outputs 24-bit left-justified
      // in 32 bits (0xXXXXXX00), so >> 16 takes the top 16 of 24 bits
      int samples = bytes_read / (TDM_SLOTS * sizeof(int32_t));
      for (int i = 0; i < samples; i++) {
        mic_buf[0][i] = (int16_t)(i2s_buf[i * TDM_SLOTS + MIC1_SLOT] >> 16);
        mic_buf[1][i] = (int16_t)(i2s_buf[i * TDM_SLOTS + MIC2_SLOT] >> 16);
      }

      // Write each mic to its file
      size_t mono_bytes = samples * sizeof(int16_t);
      bool write_ok = true;
      for (int m = 0; m < NUM_MICS; m++) {
        if (wav_files[m]) {
          if (fwrite(mic_buf[m], 1, mono_bytes, wav_files[m]) != mono_bytes) {
            write_ok = false;
          }
        }
      }
      if (!write_ok) {
        ESP_LOGE(TAG, "SD write failed — stopping recording");
        for (int m = 0; m < NUM_MICS; m++) {
          if (wav_files[m]) {
            fclose(wav_files[m]);
            wav_files[m] = NULL;
          }
        }
        recording = false;
        g_recording = false;
        rec_num++;
        g_rec_num = rec_num;
        unmount_sd();
        xEventGroupSetBits(state_events, EVT_STATE_CHANGED);
        continue;
      }
      data_written += mono_bytes;
    } else {
      // Not recording, just poll slowly
      vTaskDelay(pdMS_TO_TICKS(20));
    }
  }
}
