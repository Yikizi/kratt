#pragma once

#include "esp_err.h"
#include <stddef.h>

// Stable BLE UUIDs for the WiZ bridge GATT interface.
// These values are mirrored in tools/ble-wiz-bridge/bridge.py.
#define WIZ_BRIDGE_DEVICE_NAME "Kratt-BLE-Bridge"
#define WIZ_BRIDGE_SERVICE_UUID "c6d6f8f5-6b2d-6d4b-8f5d-0f1d2c3b4a50"
#define WIZ_BRIDGE_CHAR_UUID    "ada1a7c2-574b-4f2a-b6f7-9f8d0c4b2a11"

/**
 * Initialize BLE GATT bridge. Forwards all writes to BLE command characteristic
 * as UDP frames on the AP subnet.
 *
 * Safe to call even when NimBLE is disabled; returns ESP_ERR_NOT_SUPPORTED
 * without side effects in that case.
 */
esp_err_t init_ble_wiz_bridge(void);

/** Return BLE bridge diagnostics as a JSON object string. */
void ble_wiz_bridge_get_status_json(char *buf, size_t buf_len);
