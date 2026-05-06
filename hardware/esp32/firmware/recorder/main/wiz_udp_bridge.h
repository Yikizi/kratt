#pragma once

#include "esp_err.h"
#include <stddef.h>
#include <stdint.h>

#define WIZ_UDP_DEFAULT_PORT 38899
#define WIZ_BRIDGE_FRAME_HEADER_LEN 6
#define WIZ_BRIDGE_MAX_FRAME_LEN 512
#define WIZ_UDP_STATUS_JSON_MAX_LEN 1024

/** Initialize shared WiZ UDP bridge state. Safe to call more than once. */
esp_err_t wiz_udp_bridge_init(void);

/**
 * Send a WiZ JSON payload over UDP from the ESP32 AP interface.
 *
 * dest_ip is in network byte order. dest_ip == 0 means auto mode: use the
 * learned bulb IP when available, otherwise broadcast on the AP subnet.
 */
esp_err_t wiz_udp_bridge_send_payload(uint32_t dest_ip, uint16_t dest_port,
                                      const char *payload, size_t payload_len,
                                      char *summary_json,
                                      size_t summary_json_len);

/** Send a BLE-format frame: [4-byte IPv4][2-byte port][JSON payload]. */
esp_err_t wiz_udp_bridge_send_frame(const uint8_t *frame, uint16_t frame_len,
                                    char *summary_json,
                                    size_t summary_json_len);

/** Send a WiZ JSON payload in auto mode to the default WiZ UDP port. */
esp_err_t wiz_udp_bridge_send_json_auto(const char *payload,
                                        char *summary_json,
                                        size_t summary_json_len);

/** Clear the cached learned WiZ bulb IP, returning auto mode to broadcast. */
void wiz_udp_bridge_clear_learned_ip(void);

/** Copy the learned WiZ IP string, or "" when none is cached. */
void wiz_udp_bridge_get_learned_ip(char *buf, size_t buf_len);

/** Return current cached WiZ bridge status as a JSON object string. */
void wiz_udp_bridge_get_status_json(char *buf, size_t buf_len);
