#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "esp_adc/adc_oneshot.h"
#include "esp_bt.h"
#include "esp_err.h"
#include "esp_event.h"
#include "esp_gap_ble_api.h"
#include "esp_hid_common.h"
#include "esp_hid_gap.h"
#include "esp_hidd.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs_flash.h"

#define TAG "slideshow_clicker"

// Korvo-2 button ladder on GPIO5 / ADC1 channel 4
#define BUTTON_ADC_CHANNEL ADC_CHANNEL_4

#define BTN_NONE_MIN 4000
#define BTN_REC_MIN 2650
#define BTN_REC_MAX 2950
#define BTN_MUTE_MIN 2100
#define BTN_MUTE_MAX 2400
#define BTN_PLAY_MIN 1100
#define BTN_PLAY_MAX 1400
#define BTN_SET_MIN 1750
#define BTN_SET_MAX 2050

#define POLL_INTERVAL_MS 20
#define DEBOUNCE_SAMPLES 3

#define HID_KEY_LEFT_ARROW  0x50
#define HID_KEY_RIGHT_ARROW 0x4F

typedef enum {
    BTN_NONE = 0,
    BTN_REC,
    BTN_MUTE,
    BTN_PLAY,
    BTN_SET,
} button_t;

typedef struct {
    esp_hidd_dev_t *dev;
    bool connected;
} hid_state_t;

static hid_state_t s_hid = {0};

static const unsigned char keyboard_report_map[] = {
    0x05, 0x01,
    0x09, 0x06,
    0xA1, 0x01,
    0x85, 0x01,
    0x05, 0x07,
    0x19, 0xE0,
    0x29, 0xE7,
    0x15, 0x00,
    0x25, 0x01,
    0x75, 0x01,
    0x95, 0x08,
    0x81, 0x02,
    0x95, 0x01,
    0x75, 0x08,
    0x81, 0x03,
    0x95, 0x05,
    0x75, 0x01,
    0x05, 0x08,
    0x19, 0x01,
    0x29, 0x05,
    0x91, 0x02,
    0x95, 0x01,
    0x75, 0x03,
    0x91, 0x03,
    0x95, 0x05,
    0x75, 0x08,
    0x15, 0x00,
    0x25, 0x65,
    0x05, 0x07,
    0x19, 0x00,
    0x29, 0x65,
    0x81, 0x00,
    0xC0,
};

static esp_hid_raw_report_map_t ble_report_maps[] = {
    {
        .data = keyboard_report_map,
        .len = sizeof(keyboard_report_map),
    },
};

static esp_hid_device_config_t ble_hid_config = {
    .vendor_id = 0x16C0,
    .product_id = 0x05DF,
    .version = 0x0100,
    .device_name = "Kratt Clicker",
    .manufacturer_name = "Mattias",
    .serial_number = "kratt-clicker-1",
    .report_maps = ble_report_maps,
    .report_maps_len = 1,
};

static const char *button_name(button_t button) {
    switch (button) {
    case BTN_REC:
        return "REC";
    case BTN_MUTE:
        return "MUTE";
    case BTN_PLAY:
        return "PLAY";
    case BTN_SET:
        return "SET";
    case BTN_NONE:
    default:
        return "NONE";
    }
}

static button_t read_button(adc_oneshot_unit_handle_t adc) {
    int raw = 0;
    if (adc_oneshot_read(adc, BUTTON_ADC_CHANNEL, &raw) != ESP_OK) {
        return BTN_NONE;
    }

    if (raw >= BTN_NONE_MIN) {
        return BTN_NONE;
    }
    if (raw >= BTN_REC_MIN && raw <= BTN_REC_MAX) {
        return BTN_REC;
    }
    if (raw >= BTN_MUTE_MIN && raw <= BTN_MUTE_MAX) {
        return BTN_MUTE;
    }
    if (raw >= BTN_PLAY_MIN && raw <= BTN_PLAY_MAX) {
        return BTN_PLAY;
    }
    if (raw >= BTN_SET_MIN && raw <= BTN_SET_MAX) {
        return BTN_SET;
    }
    return BTN_NONE;
}

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
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc_handle, BUTTON_ADC_CHANNEL, &chan_cfg));

    return adc_handle;
}

static void send_keyboard_usage(uint8_t usage) {
    if (!s_hid.connected || s_hid.dev == NULL) {
        ESP_LOGW(TAG, "Ignoring key 0x%02X, host not connected", usage);
        return;
    }

    uint8_t report[8] = {0};
    report[2] = usage;
    esp_hidd_dev_input_set(s_hid.dev, 0, 1, report, sizeof(report));
    vTaskDelay(pdMS_TO_TICKS(30));
    memset(report, 0, sizeof(report));
    esp_hidd_dev_input_set(s_hid.dev, 0, 1, report, sizeof(report));
}

static void handle_button_press(button_t button) {
    switch (button) {
    case BTN_PLAY:
        ESP_LOGI(TAG, "PLAY -> next slide");
        send_keyboard_usage(HID_KEY_RIGHT_ARROW);
        break;
    case BTN_SET:
        ESP_LOGI(TAG, "SET -> previous slide");
        send_keyboard_usage(HID_KEY_LEFT_ARROW);
        break;
    case BTN_REC:
    case BTN_MUTE:
        ESP_LOGI(TAG, "%s pressed (no action)", button_name(button));
        break;
    case BTN_NONE:
    default:
        break;
    }
}

void ble_hid_task_start_up(void) {
    // The borrowed GAP helper expects this symbol, but button polling runs
    // independently in button_task, so nothing needs to be started here.
}

static void button_task(void *arg) {
    adc_oneshot_unit_handle_t adc = init_buttons();
    button_t last_raw = BTN_NONE;
    button_t stable = BTN_NONE;
    int stable_count = 0;

    ESP_LOGI(TAG, "Button task started: PLAY=next, SET=previous");

    while (true) {
        button_t raw = read_button(adc);

        if (raw == last_raw) {
            if (stable_count < DEBOUNCE_SAMPLES) {
                stable_count++;
            }
        } else {
            stable_count = 1;
            last_raw = raw;
        }

        if (stable_count >= DEBOUNCE_SAMPLES && raw != stable) {
            button_t previous = stable;
            stable = raw;
            if (previous == BTN_NONE && stable != BTN_NONE) {
                handle_button_press(stable);
            }
        }

        vTaskDelay(pdMS_TO_TICKS(POLL_INTERVAL_MS));
    }
}

static void ble_hidd_event_callback(void *handler_args, esp_event_base_t base, int32_t id, void *event_data) {
    (void)handler_args;
    (void)base;
    esp_hidd_event_t event = (esp_hidd_event_t)id;
    esp_hidd_event_data_t *param = (esp_hidd_event_data_t *)event_data;

    switch (event) {
    case ESP_HIDD_START_EVENT:
        ESP_LOGI(TAG, "HID start event");
        esp_hid_ble_gap_adv_start();
        break;
    case ESP_HIDD_CONNECT_EVENT:
        s_hid.connected = true;
        ESP_LOGI(TAG, "BLE host connected");
        break;
    case ESP_HIDD_PROTOCOL_MODE_EVENT:
        ESP_LOGI(TAG, "Protocol mode: %s", param->protocol_mode.protocol_mode ? "REPORT" : "BOOT");
        break;
    case ESP_HIDD_CONTROL_EVENT:
        ESP_LOGI(TAG, "Control event: %s suspend", param->control.control ? "exit" : "enter");
        break;
    case ESP_HIDD_OUTPUT_EVENT:
        ESP_LOGI(TAG, "Output report id=%u len=%d", param->output.report_id, param->output.length);
        break;
    case ESP_HIDD_FEATURE_EVENT:
        ESP_LOGI(TAG, "Feature report id=%u len=%d", param->feature.report_id, param->feature.length);
        break;
    case ESP_HIDD_DISCONNECT_EVENT:
        s_hid.connected = false;
        ESP_LOGI(TAG, "BLE host disconnected: %s",
                 esp_hid_disconnect_reason_str(esp_hidd_dev_transport_get(param->disconnect.dev),
                                               param->disconnect.reason));
        esp_hid_ble_gap_adv_start();
        break;
    case ESP_HIDD_STOP_EVENT:
        s_hid.connected = false;
        ESP_LOGI(TAG, "HID stopped");
        break;
    default:
        break;
    }
}

void app_main(void) {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    ESP_LOGI(TAG, "Initializing BLE HID slideshow clicker");
    ESP_ERROR_CHECK(esp_hid_gap_init(HID_DEV_MODE));
    ESP_ERROR_CHECK(esp_hid_ble_gap_adv_init(ESP_HID_APPEARANCE_KEYBOARD, ble_hid_config.device_name));
    ESP_ERROR_CHECK(esp_ble_gatts_register_callback(esp_hidd_gatts_event_handler));
    ESP_ERROR_CHECK(esp_hidd_dev_init(&ble_hid_config, ESP_HID_TRANSPORT_BLE, ble_hidd_event_callback, &s_hid.dev));

    xTaskCreate(button_task, "button_task", 4096, NULL, 5, NULL);
    ESP_LOGI(TAG, "Ready. Pair '%s' on the Mac and use PLAY/SET buttons.", ble_hid_config.device_name);
}
