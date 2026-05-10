#include "ble_wiz_bridge.h"
#include "wiz_udp_bridge.h"

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "esp_log.h"

#if CONFIG_BT_NIMBLE_ENABLED

#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "freertos/task.h"

#include "host/ble_gap.h"
#include "host/ble_hs.h"
#include "host/ble_hs_mbuf.h"
#include "host/ble_uuid.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "services/gap/ble_svc_gap.h"
#include "services/gatt/ble_svc_gatt.h"

#endif  // CONFIG_BT_NIMBLE_ENABLED

static const char *TAG = "ble_wiz_bridge";

#if CONFIG_BT_NIMBLE_ENABLED

// UUIDs are stored in NimBLE little-endian format.
static const ble_uuid128_t g_wiz_bridge_service_uuid = BLE_UUID128_INIT(
    0x50, 0x4a, 0x3b, 0x2c, 0x1d, 0x0f, 0x5d, 0x8f,
    0x4b, 0x6d, 0x2d, 0x6b, 0xf5, 0xf8, 0xd6, 0xc6);
static const ble_uuid128_t g_wiz_bridge_char_uuid = BLE_UUID128_INIT(
    0x11, 0x2a, 0x4b, 0x0c, 0x8d, 0x9f, 0xf7, 0xb6,
    0x2a, 0x4f, 0x4b, 0x57, 0xc2, 0xa7, 0xa1, 0xad);

static uint8_t g_ble_addr_type;
static uint16_t g_wiz_char_handle;
static uint16_t g_ble_conn_handle = 0xffff;
static bool g_ble_enabled;
static bool g_ble_advertising;
static bool g_ble_connected;
static bool g_ble_notify_enabled;
static char g_wiz_last_ble_response[WIZ_UDP_STATUS_JSON_MAX_LEN] =
    "{\"ok\":false,\"message\":\"no command yet\"}";

typedef struct {
  uint16_t frame_len;
  uint8_t frame[WIZ_BRIDGE_MAX_FRAME_LEN];
} wiz_ble_job_t;

static QueueHandle_t g_wiz_job_queue;
static SemaphoreHandle_t g_wiz_response_lock;
static TaskHandle_t g_wiz_worker_task;

void ble_store_config_init(void);

static int gatt_access_cb(uint16_t conn_handle, uint16_t attr_handle,
                          struct ble_gatt_access_ctxt *ctxt, void *arg);
static int on_gap_event(struct ble_gap_event *event, void *arg);
static int start_advertising_if_needed(void);
static void on_reset(int reason);
static void on_sync(void);
static void host_task(void *arg);
static void notify_ble_ack(bool ok);
static void wiz_ble_worker_task(void *arg);
static esp_err_t ensure_worker_started(void);
static void set_last_response(const char *response);

static const struct ble_gatt_svc_def g_wiz_gatt_svcs[] = {
    {
        .type = BLE_GATT_SVC_TYPE_PRIMARY,
        .uuid = &g_wiz_bridge_service_uuid.u,
        .characteristics =
            (struct ble_gatt_chr_def[]){
                {
                    .uuid = &g_wiz_bridge_char_uuid.u,
                    .access_cb = gatt_access_cb,
                    .flags = BLE_GATT_CHR_F_WRITE | BLE_GATT_CHR_F_WRITE_NO_RSP |
                             BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_NOTIFY,
                    .val_handle = &g_wiz_char_handle,
                },
                {0},
            },
    },
    {0},
};

static void set_last_response(const char *response) {
  if (!response) {
    return;
  }
  if (g_wiz_response_lock) {
    xSemaphoreTake(g_wiz_response_lock, portMAX_DELAY);
  }
  strlcpy(g_wiz_last_ble_response, response, sizeof(g_wiz_last_ble_response));
  if (g_wiz_response_lock) {
    xSemaphoreGive(g_wiz_response_lock);
  }
}

static esp_err_t ensure_worker_started(void) {
  if (!g_wiz_response_lock) {
    g_wiz_response_lock = xSemaphoreCreateMutex();
    if (!g_wiz_response_lock) {
      return ESP_ERR_NO_MEM;
    }
  }

  if (!g_wiz_job_queue) {
    g_wiz_job_queue = xQueueCreate(4, sizeof(wiz_ble_job_t *));
    if (!g_wiz_job_queue) {
      return ESP_ERR_NO_MEM;
    }
  }

  if (!g_wiz_worker_task) {
    BaseType_t ok = xTaskCreate(wiz_ble_worker_task, "wiz_ble_worker", 8192,
                                NULL, 5, &g_wiz_worker_task);
    if (ok != pdPASS) {
      g_wiz_worker_task = NULL;
      return ESP_ERR_NO_MEM;
    }
  }

  return ESP_OK;
}

static void wiz_ble_worker_task(void *arg) {
  (void)arg;
  while (true) {
    wiz_ble_job_t *job = NULL;
    if (xQueueReceive(g_wiz_job_queue, &job, portMAX_DELAY) != pdTRUE || !job) {
      continue;
    }

    char *summary = calloc(1, WIZ_UDP_STATUS_JSON_MAX_LEN);
    esp_err_t err = ESP_ERR_NO_MEM;
    if (summary) {
      err = wiz_udp_bridge_send_frame(job->frame, job->frame_len, summary,
                                      WIZ_UDP_STATUS_JSON_MAX_LEN);
      if (summary[0] == '\0') {
        wiz_udp_bridge_get_status_json(summary, WIZ_UDP_STATUS_JSON_MAX_LEN);
      }
      set_last_response(summary);
    } else {
      set_last_response("{\"ok\":false,\"message\":\"no memory\"}");
    }

    notify_ble_ack(err == ESP_OK);
    free(summary);
    free(job);
  }
}

static void notify_ble_ack(bool ok) {
  if (!g_ble_connected || !g_ble_notify_enabled || g_ble_conn_handle == 0xffff) {
    return;
  }

  char note[96];
  snprintf(note, sizeof(note), "{\"ok\":%s,\"read\":true}", ok ? "true" : "false");
  struct os_mbuf *om = ble_hs_mbuf_from_flat(note, strlen(note));
  if (!om) {
    return;
  }

  int rc = ble_gattc_notify_custom(g_ble_conn_handle, g_wiz_char_handle, om);
  if (rc != 0) {
    ESP_LOGW(TAG, "BLE notify failed: rc=%d", rc);
  }
}

static int start_advertising_if_needed(void) {
  struct ble_hs_adv_fields fields = {0};
  fields.flags = BLE_HS_ADV_F_DISC_GEN | BLE_HS_ADV_F_BREDR_UNSUP;
  fields.tx_pwr_lvl_is_present = 1;
  fields.tx_pwr_lvl = BLE_HS_ADV_TX_PWR_LVL_AUTO;
  fields.name = (uint8_t *)WIZ_BRIDGE_DEVICE_NAME;
  fields.name_len = strlen(WIZ_BRIDGE_DEVICE_NAME);
  fields.name_is_complete = 1;

  int rc = ble_gap_adv_set_fields(&fields);
  if (rc != 0) {
    return rc;
  }

  // The 128-bit service UUID plus complete device name does not fit in the
  // legacy 31-byte advertising payload; place the UUID in scan response data.
  struct ble_hs_adv_fields rsp_fields = {0};
  rsp_fields.uuids128 = &g_wiz_bridge_service_uuid;
  rsp_fields.num_uuids128 = 1;
  rsp_fields.uuids128_is_complete = 1;
  rc = ble_gap_adv_rsp_set_fields(&rsp_fields);
  if (rc != 0) {
    return rc;
  }

  struct ble_gap_adv_params adv_params = {
      .conn_mode = BLE_GAP_CONN_MODE_UND,
      .disc_mode = BLE_GAP_DISC_MODE_GEN,
  };

  rc = ble_gap_adv_start(g_ble_addr_type, NULL, BLE_HS_FOREVER, &adv_params,
                         on_gap_event, NULL);
  if (rc == 0) {
    g_ble_advertising = true;
    ESP_LOGI(TAG, "BLE advertising started as '%s'", WIZ_BRIDGE_DEVICE_NAME);
  }
  return rc;
}

static int on_gap_event(struct ble_gap_event *event, void *arg) {
  (void)arg;
  if (!event) {
    return 0;
  }

  switch (event->type) {
  case BLE_GAP_EVENT_CONNECT:
    if (event->connect.status != 0) {
      g_ble_connected = false;
      ESP_LOGW(TAG, "BLE connect failed: status=%d", event->connect.status);
      start_advertising_if_needed();
    } else {
      g_ble_conn_handle = event->connect.conn_handle;
      g_ble_connected = true;
      g_ble_advertising = false;
      ESP_LOGI(TAG, "BLE central connected");
    }
    break;
  case BLE_GAP_EVENT_DISCONNECT:
    ESP_LOGI(TAG, "BLE disconnected: reason=%d", event->disconnect.reason);
    g_ble_conn_handle = 0xffff;
    g_ble_connected = false;
    g_ble_notify_enabled = false;
    start_advertising_if_needed();
    break;
  case BLE_GAP_EVENT_SUBSCRIBE:
    if (event->subscribe.attr_handle == g_wiz_char_handle) {
      g_ble_notify_enabled = event->subscribe.cur_notify;
      ESP_LOGI(TAG, "BLE notify subscription: %s",
               g_ble_notify_enabled ? "enabled" : "disabled");
    }
    break;
  default:
    break;
  }

  return 0;
}

static int gatt_access_cb(uint16_t conn_handle, uint16_t attr_handle,
                          struct ble_gatt_access_ctxt *ctxt, void *arg) {
  (void)conn_handle;
  (void)attr_handle;
  (void)arg;

  if (ctxt->op == BLE_GATT_ACCESS_OP_READ_CHR) {
    if (g_wiz_response_lock) {
      xSemaphoreTake(g_wiz_response_lock, portMAX_DELAY);
    }
    size_t len = strlen(g_wiz_last_ble_response);
    int rc = os_mbuf_append(ctxt->om, g_wiz_last_ble_response, len);
    if (g_wiz_response_lock) {
      xSemaphoreGive(g_wiz_response_lock);
    }
    return rc == 0 ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;
  }

  if (ctxt->op != BLE_GATT_ACCESS_OP_WRITE_CHR) {
    return BLE_ATT_ERR_WRITE_NOT_PERMITTED;
  }

  uint16_t frame_len = OS_MBUF_PKTLEN(ctxt->om);
  if (frame_len < WIZ_BRIDGE_FRAME_HEADER_LEN ||
      frame_len > WIZ_BRIDGE_MAX_FRAME_LEN) {
    return BLE_ATT_ERR_INVALID_ATTR_VALUE_LEN;
  }

  // Do not perform WiFi/UDP work inside the NimBLE host callback. The callback
  // must return quickly; otherwise CoreBluetooth/NimBLE can time out or drop the
  // connection while the ESP32 waits for a WiZ UDP response. Copy the frame and
  // let a worker task forward it asynchronously.
  if (ensure_worker_started() != ESP_OK) {
    return BLE_ATT_ERR_INSUFFICIENT_RES;
  }

  wiz_ble_job_t *job = calloc(1, sizeof(*job));
  if (!job) {
    return BLE_ATT_ERR_INSUFFICIENT_RES;
  }
  job->frame_len = frame_len;
  if (os_mbuf_copydata(ctxt->om, 0, frame_len, job->frame) != 0) {
    free(job);
    return BLE_ATT_ERR_UNLIKELY;
  }

  set_last_response("{\"ok\":true,\"queued\":true}");
  if (xQueueSend(g_wiz_job_queue, &job, 0) != pdTRUE) {
    free(job);
    set_last_response("{\"ok\":false,\"queued\":false,\"message\":\"queue full\"}");
    return BLE_ATT_ERR_INSUFFICIENT_RES;
  }

  return 0;
}

static void on_sync(void) {
  int rc = ble_hs_id_infer_auto(0, &g_ble_addr_type);
  if (rc != 0) {
    ESP_LOGE(TAG, "ble_hs_id_infer_auto failed: %d", rc);
    return;
  }

  rc = start_advertising_if_needed();
  if (rc != 0) {
    ESP_LOGE(TAG, "Failed to start advertising: %d", rc);
  }
}

static void on_reset(int reason) { ESP_LOGW(TAG, "BLE host reset: %d", reason); }

static void host_task(void *arg) {
  (void)arg;
  nimble_port_run();
  nimble_port_freertos_deinit();
}

#endif  // CONFIG_BT_NIMBLE_ENABLED

esp_err_t init_ble_wiz_bridge(void) {
#if CONFIG_BT_NIMBLE_ENABLED
  ESP_ERROR_CHECK_WITHOUT_ABORT(wiz_udp_bridge_init());
  esp_err_t worker_err = ensure_worker_started();
  if (worker_err != ESP_OK) {
    ESP_LOGE(TAG, "Failed to start BLE WiZ worker: %s", esp_err_to_name(worker_err));
    return worker_err;
  }

  int rc = nimble_port_init();
  if (rc != 0) {
    ESP_LOGE(TAG, "nimble_port_init failed: %d", rc);
    return ESP_FAIL;
  }

  ble_hs_cfg.reset_cb = on_reset;
  ble_hs_cfg.sync_cb = on_sync;

  ble_svc_gap_init();
  ble_svc_gap_device_name_set(WIZ_BRIDGE_DEVICE_NAME);
  ble_svc_gatt_init();

  rc = ble_gatts_count_cfg(g_wiz_gatt_svcs);
  if (rc != 0) {
    ESP_LOGE(TAG, "ble_gatts_count_cfg failed: %d", rc);
    return ESP_FAIL;
  }

  rc = ble_gatts_add_svcs(g_wiz_gatt_svcs);
  if (rc != 0) {
    ESP_LOGE(TAG, "ble_gatts_add_svcs failed: %d", rc);
    return ESP_FAIL;
  }

  ble_store_config_init();
  nimble_port_freertos_init(host_task);

  g_ble_enabled = true;
  ESP_LOGI(TAG, "NimBLE initialized: service=%s char=%s", WIZ_BRIDGE_SERVICE_UUID,
           WIZ_BRIDGE_CHAR_UUID);
  return ESP_OK;
#else
  ESP_LOGW(TAG, "NimBLE disabled in Kconfig; WiZ BLE bridge not started");
  return ESP_ERR_NOT_SUPPORTED;
#endif
}

void ble_wiz_bridge_get_status_json(char *buf, size_t buf_len) {
  if (!buf || buf_len == 0) {
    return;
  }
#if CONFIG_BT_NIMBLE_ENABLED
  snprintf(buf, buf_len,
           "{\"enabled\":%s,\"advertising\":%s,\"connected\":%s,"
           "\"notify\":%s,\"device_name\":\"%s\"}",
           g_ble_enabled ? "true" : "false",
           g_ble_advertising ? "true" : "false",
           g_ble_connected ? "true" : "false",
           g_ble_notify_enabled ? "true" : "false", WIZ_BRIDGE_DEVICE_NAME);
#else
  snprintf(buf, buf_len,
           "{\"enabled\":false,\"advertising\":false,\"connected\":false,"
           "\"notify\":false,\"device_name\":\"%s\"}",
           WIZ_BRIDGE_DEVICE_NAME);
#endif
}
