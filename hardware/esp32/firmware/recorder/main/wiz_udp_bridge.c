#include "wiz_udp_bridge.h"

#include "esp_log.h"
#include "esp_netif.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "lwip/inet.h"
#include "lwip/sockets.h"

#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <unistd.h>

#define WIZ_AP_NETIF_KEY "WIFI_AP_DEF"
#define WIZ_PAYLOAD_MAX_LEN (WIZ_BRIDGE_MAX_FRAME_LEN - WIZ_BRIDGE_FRAME_HEADER_LEN)
#define WIZ_LAST_COMMAND_LEN 192
#define WIZ_LAST_RESPONSE_LEN 256
#define WIZ_LAST_METHOD_LEN 24
#define WIZ_TARGET_MODE_LEN 20

static const char *TAG = "wiz_udp";

typedef struct {
  bool udp_sent;
  bool response_ok;
  int last_errno;
  uint32_t commands_sent;
  uint32_t responders;
  int64_t last_command_ms;
  int64_t last_response_ms;
  char target_mode[WIZ_TARGET_MODE_LEN];
  char last_method[WIZ_LAST_METHOD_LEN];
  char last_command[WIZ_LAST_COMMAND_LEN];
  char last_ip[16];
  char last_response[WIZ_LAST_RESPONSE_LEN];
  bool state_valid;
  bool state;
  int dimming;
  int temp;
  int r;
  int g;
  int b;
  int rssi;
} wiz_status_t;

static SemaphoreHandle_t g_wiz_lock;
static uint32_t g_wiz_learned_ip;
static wiz_status_t g_wiz_status = {
    .udp_sent = false,
    .response_ok = false,
    .last_errno = 0,
    .commands_sent = 0,
    .responders = 0,
    .last_command_ms = 0,
    .last_response_ms = 0,
    .target_mode = "auto/broadcast",
    .last_method = "",
    .last_command = "",
    .last_ip = "",
    .last_response = "",
    .state_valid = false,
    .state = false,
    .dimming = -1,
    .temp = -1,
    .r = -1,
    .g = -1,
    .b = -1,
    .rssi = 0,
};

static int64_t now_ms(void) { return esp_timer_get_time() / 1000; }

static void ensure_lock(void) {
  if (!g_wiz_lock) {
    g_wiz_lock = xSemaphoreCreateMutex();
  }
}

esp_err_t wiz_udp_bridge_init(void) {
  ensure_lock();
  if (!g_wiz_lock) {
    return ESP_ERR_NO_MEM;
  }
  return ESP_OK;
}

static void lock_status(void) {
  ensure_lock();
  if (g_wiz_lock) {
    xSemaphoreTake(g_wiz_lock, portMAX_DELAY);
  }
}

static void unlock_status(void) {
  if (g_wiz_lock) {
    xSemaphoreGive(g_wiz_lock);
  }
}

static void copy_truncated(char *dst, size_t dst_len, const char *src,
                           size_t src_len) {
  if (!dst || dst_len == 0) {
    return;
  }
  size_t n = src_len;
  if (n >= dst_len) {
    n = dst_len - 1;
  }
  if (n > 0 && src) {
    memcpy(dst, src, n);
  }
  dst[n] = '\0';
}

static void extract_method(const char *json, char *method, size_t method_len) {
  if (!method || method_len == 0) {
    return;
  }
  method[0] = '\0';
  if (!json) {
    return;
  }

  const char *p = strstr(json, "\"method\"");
  if (!p) {
    return;
  }
  p = strchr(p, ':');
  if (!p) {
    return;
  }
  p++;
  while (*p == ' ' || *p == '\t') {
    p++;
  }
  if (*p != '"') {
    return;
  }
  p++;
  const char *end = strchr(p, '"');
  if (!end || end <= p) {
    return;
  }
  copy_truncated(method, method_len, p, (size_t)(end - p));
}

static bool json_find_bool(const char *json, const char *key, bool *out) {
  char pattern[32];
  snprintf(pattern, sizeof(pattern), "\"%s\":", key);
  const char *p = strstr(json, pattern);
  if (!p) {
    return false;
  }
  p += strlen(pattern);
  while (*p == ' ' || *p == '\t') {
    p++;
  }
  if (strncmp(p, "true", 4) == 0) {
    *out = true;
    return true;
  }
  if (strncmp(p, "false", 5) == 0) {
    *out = false;
    return true;
  }
  return false;
}

static bool json_find_int(const char *json, const char *key, int *out) {
  char pattern[32];
  snprintf(pattern, sizeof(pattern), "\"%s\":", key);
  const char *p = strstr(json, pattern);
  if (!p) {
    return false;
  }
  p += strlen(pattern);
  while (*p == ' ' || *p == '\t') {
    p++;
  }
  char *end = NULL;
  long value = strtol(p, &end, 10);
  if (!end || end == p) {
    return false;
  }
  *out = (int)value;
  return true;
}

static void json_escape(char *dst, size_t dst_len, const char *src) {
  if (!dst || dst_len == 0) {
    return;
  }
  size_t j = 0;
  if (!src) {
    dst[0] = '\0';
    return;
  }
  for (size_t i = 0; src[i] != '\0' && j + 1 < dst_len; i++) {
    unsigned char c = (unsigned char)src[i];
    if (c == '"' || c == '\\') {
      if (j + 2 >= dst_len) {
        break;
      }
      dst[j++] = '\\';
      dst[j++] = (char)c;
    } else if (c < 0x20) {
      dst[j++] = ' ';
    } else {
      dst[j++] = (char)c;
    }
  }
  dst[j] = '\0';
}

static void learned_ip_string_locked(char *buf, size_t buf_len) {
  if (!buf || buf_len == 0) {
    return;
  }
  if (g_wiz_learned_ip == 0) {
    buf[0] = '\0';
    return;
  }
  inet_ntoa_r(g_wiz_learned_ip, buf, buf_len);
}

static void parse_wiz_response_locked(const char *response) {
  bool state;
  int value;

  if (json_find_bool(response, "state", &state)) {
    g_wiz_status.state_valid = true;
    g_wiz_status.state = state;
  }
  if (json_find_int(response, "dimming", &value)) {
    g_wiz_status.dimming = value;
  }
  if (json_find_int(response, "temp", &value)) {
    g_wiz_status.temp = value;
  }
  if (json_find_int(response, "r", &value)) {
    g_wiz_status.r = value;
  }
  if (json_find_int(response, "g", &value)) {
    g_wiz_status.g = value;
  }
  if (json_find_int(response, "b", &value)) {
    g_wiz_status.b = value;
  }
  if (json_find_int(response, "rssi", &value)) {
    g_wiz_status.rssi = value;
  }
}

static void build_status_json_locked(char *buf, size_t buf_len) {
  if (!buf || buf_len == 0) {
    return;
  }

  char learned_ip[16] = {0};
  char escaped_command[WIZ_LAST_COMMAND_LEN * 2] = {0};
  char escaped_response[WIZ_LAST_RESPONSE_LEN * 2] = {0};
  learned_ip_string_locked(learned_ip, sizeof(learned_ip));
  json_escape(escaped_command, sizeof(escaped_command), g_wiz_status.last_command);
  json_escape(escaped_response, sizeof(escaped_response), g_wiz_status.last_response);

  int64_t t_now = now_ms();
  long long response_age =
      g_wiz_status.last_response_ms > 0 ? (long long)(t_now - g_wiz_status.last_response_ms) : -1;
  long long command_age =
      g_wiz_status.last_command_ms > 0 ? (long long)(t_now - g_wiz_status.last_command_ms) : -1;

  snprintf(buf, buf_len,
           "{\"ok\":%s,\"udp_sent\":%s,\"response_ok\":%s,"
           "\"responders\":%lu,\"commands_sent\":%lu,\"target_mode\":\"%s\","
           "\"learned_ip\":\"%s\",\"last_ip\":\"%s\",\"last_method\":\"%s\","
           "\"state_valid\":%s,\"state\":%s,\"dimming\":%d,\"temp\":%d,"
           "\"r\":%d,\"g\":%d,\"b\":%d,\"rssi\":%d,"
           "\"last_errno\":%d,\"last_command_age_ms\":%lld,"
           "\"last_response_age_ms\":%lld,\"last_command\":\"%s\","
           "\"last_response\":\"%s\"}",
           g_wiz_status.udp_sent ? "true" : "false",
           g_wiz_status.udp_sent ? "true" : "false",
           g_wiz_status.response_ok ? "true" : "false",
           (unsigned long)g_wiz_status.responders,
           (unsigned long)g_wiz_status.commands_sent, g_wiz_status.target_mode,
           learned_ip, g_wiz_status.last_ip, g_wiz_status.last_method,
           g_wiz_status.state_valid ? "true" : "false",
           g_wiz_status.state ? "true" : "false", g_wiz_status.dimming,
           g_wiz_status.temp, g_wiz_status.r, g_wiz_status.g, g_wiz_status.b,
           g_wiz_status.rssi, g_wiz_status.last_errno, command_age, response_age,
           escaped_command, escaped_response);
}

void wiz_udp_bridge_get_status_json(char *buf, size_t buf_len) {
  lock_status();
  build_status_json_locked(buf, buf_len);
  unlock_status();
}

void wiz_udp_bridge_get_learned_ip(char *buf, size_t buf_len) {
  lock_status();
  learned_ip_string_locked(buf, buf_len);
  unlock_status();
}

void wiz_udp_bridge_clear_learned_ip(void) {
  lock_status();
  g_wiz_learned_ip = 0;
  strlcpy(g_wiz_status.target_mode, "auto/broadcast",
          sizeof(g_wiz_status.target_mode));
  unlock_status();
  ESP_LOGI(TAG, "Cleared learned WiZ IP");
}

esp_err_t wiz_udp_bridge_send_payload(uint32_t dest_ip, uint16_t dest_port,
                                      const char *payload, size_t payload_len,
                                      char *summary_json,
                                      size_t summary_json_len) {
  if (!payload || payload_len == 0 || payload_len > WIZ_PAYLOAD_MAX_LEN ||
      dest_port == 0) {
    return ESP_ERR_INVALID_ARG;
  }

  char payload_copy[WIZ_PAYLOAD_MAX_LEN + 1] = {0};
  copy_truncated(payload_copy, sizeof(payload_copy), payload, payload_len);

  lock_status();

  bool auto_target = (dest_ip == 0);
  // Reliability-first demo behavior: auto mode broadcasts every command on the
  // ESP32 AP subnet. The previous learned-IP unicast optimization could
  // blackhole commands after the WiZ bulb rejoined DHCP with a new address.
  bool learned_target = false;
  bool broadcast_target = auto_target;

  g_wiz_status.commands_sent++;
  g_wiz_status.responders = 0;
  g_wiz_status.udp_sent = false;
  g_wiz_status.response_ok = false;
  g_wiz_status.last_errno = 0;
  g_wiz_status.last_command_ms = now_ms();
  copy_truncated(g_wiz_status.last_command, sizeof(g_wiz_status.last_command),
                 payload_copy, strlen(payload_copy));
  extract_method(payload_copy, g_wiz_status.last_method,
                 sizeof(g_wiz_status.last_method));
  strlcpy(g_wiz_status.target_mode,
          broadcast_target ? "auto/broadcast" : (learned_target ? "auto/unicast" : "unicast"),
          sizeof(g_wiz_status.target_mode));

  struct sockaddr_in dest_addr = {0};
  dest_addr.sin_family = AF_INET;
  dest_addr.sin_port = htons(dest_port);
  dest_addr.sin_addr.s_addr = dest_ip;

  int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
  if (sock < 0) {
    g_wiz_status.last_errno = errno;
    ESP_LOGE(TAG, "socket() failed: %s", strerror(errno));
    if (summary_json && summary_json_len > 0) {
      build_status_json_locked(summary_json, summary_json_len);
    }
    unlock_status();
    return ESP_FAIL;
  }

  if (broadcast_target) {
    int yes = 1;
    if (setsockopt(sock, SOL_SOCKET, SO_BROADCAST, &yes, sizeof(yes)) != 0) {
      ESP_LOGW(TAG, "setsockopt(SO_BROADCAST) failed: %s", strerror(errno));
    }
  }

  esp_netif_t *ap_netif = esp_netif_get_handle_from_ifkey(WIZ_AP_NETIF_KEY);
  if (ap_netif) {
    esp_netif_ip_info_t ip_info = {0};
    if (esp_netif_get_ip_info(ap_netif, &ip_info) == ESP_OK &&
        ip_info.ip.addr != 0) {
      struct sockaddr_in source_addr = {0};
      source_addr.sin_family = AF_INET;
      source_addr.sin_port = 0;
      source_addr.sin_addr.s_addr = ip_info.ip.addr;
      if (bind(sock, (struct sockaddr *)&source_addr, sizeof(source_addr)) != 0) {
        char source_ip_str[16] = {0};
        inet_ntoa_r(ip_info.ip.addr, source_ip_str, sizeof(source_ip_str));
        ESP_LOGW(TAG, "UDP bind(source=%s) failed: %s", source_ip_str,
                 strerror(errno));
      }

      if (broadcast_target) {
        dest_addr.sin_addr.s_addr =
            (ip_info.ip.addr & ip_info.netmask.addr) | ~ip_info.netmask.addr;
      }
    }
  }

  if (broadcast_target && dest_addr.sin_addr.s_addr == 0) {
    dest_addr.sin_addr.s_addr = 0xffffffffUL;
  }

  char dest_ip_str[16] = {0};
  inet_ntoa_r(dest_addr.sin_addr.s_addr, dest_ip_str, sizeof(dest_ip_str));

  ssize_t sent = sendto(sock, payload, payload_len, 0,
                        (struct sockaddr *)&dest_addr, sizeof(dest_addr));
  if (sent < 0 || (size_t)sent != payload_len) {
    g_wiz_status.last_errno = errno;
    ESP_LOGE(TAG, "sendto %s:%u failed. payload=%u sent=%ld errno=%d",
             dest_ip_str, dest_port, (unsigned)payload_len, (long)sent, errno);
    close(sock);
    if (summary_json && summary_json_len > 0) {
      build_status_json_locked(summary_json, summary_json_len);
    }
    unlock_status();
    return ESP_FAIL;
  }

  g_wiz_status.udp_sent = true;
  int preview_len = (payload_len > 64) ? 64 : (int)payload_len;
  ESP_LOGI(TAG,
           "Forwarded WiZ target=%s:%u auto=%s learned=%s payload=%u first=%.*s",
           dest_ip_str, dest_port, auto_target ? "yes" : "no",
           learned_target ? "yes" : "no", (unsigned)payload_len, preview_len,
           payload);

  struct timeval recv_timeout = {
      .tv_sec = 0,
      .tv_usec = 300000,
  };
  if (setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &recv_timeout,
                 sizeof(recv_timeout)) != 0) {
    ESP_LOGW(TAG, "setsockopt(SO_RCVTIMEO) failed: %s", strerror(errno));
  }

  while (true) {
    char response[WIZ_LAST_RESPONSE_LEN] = {0};
    struct sockaddr_in from_addr = {0};
    socklen_t from_len = sizeof(from_addr);
    ssize_t got = recvfrom(sock, response, sizeof(response) - 1, 0,
                           (struct sockaddr *)&from_addr, &from_len);
    if (got <= 0) {
      break;
    }

    g_wiz_status.responders++;
    g_wiz_status.response_ok = true;
    g_wiz_status.last_response_ms = now_ms();
    g_wiz_learned_ip = from_addr.sin_addr.s_addr;
    inet_ntoa_r(from_addr.sin_addr.s_addr, g_wiz_status.last_ip,
                sizeof(g_wiz_status.last_ip));
    response[got] = '\0';
    copy_truncated(g_wiz_status.last_response, sizeof(g_wiz_status.last_response),
                   response, (size_t)got);
    parse_wiz_response_locked(response);

    int response_preview_len = (got > 100) ? 100 : (int)got;
    ESP_LOGI(TAG, "WiZ UDP response from %s:%u bytes=%ld first=%.*s",
             g_wiz_status.last_ip, ntohs(from_addr.sin_port), (long)got,
             response_preview_len, response);
  }

  if (auto_target && g_wiz_status.responders == 0) {
    g_wiz_learned_ip = 0;
    ESP_LOGW(TAG, "No WiZ UDP response observed for auto/broadcast target");
  }

  close(sock);

  if (summary_json && summary_json_len > 0) {
    build_status_json_locked(summary_json, summary_json_len);
  }
  unlock_status();
  return ESP_OK;
}

esp_err_t wiz_udp_bridge_send_frame(const uint8_t *frame, uint16_t frame_len,
                                    char *summary_json,
                                    size_t summary_json_len) {
  if (!frame || frame_len < WIZ_BRIDGE_FRAME_HEADER_LEN ||
      frame_len > WIZ_BRIDGE_MAX_FRAME_LEN) {
    return ESP_ERR_INVALID_ARG;
  }

  uint32_t dest_ip = 0;
  memcpy(&dest_ip, frame, sizeof(dest_ip));
  uint16_t dest_port = (uint16_t)((frame[4] << 8) | frame[5]);
  const char *payload = (const char *)(frame + WIZ_BRIDGE_FRAME_HEADER_LEN);
  size_t payload_len = frame_len - WIZ_BRIDGE_FRAME_HEADER_LEN;

  return wiz_udp_bridge_send_payload(dest_ip, dest_port, payload, payload_len,
                                     summary_json, summary_json_len);
}

esp_err_t wiz_udp_bridge_send_json_auto(const char *payload,
                                        char *summary_json,
                                        size_t summary_json_len) {
  if (!payload) {
    return ESP_ERR_INVALID_ARG;
  }
  return wiz_udp_bridge_send_payload(0, WIZ_UDP_DEFAULT_PORT, payload,
                                     strlen(payload), summary_json,
                                     summary_json_len);
}
