#include "kratt_korvo2_buttons.h"

#include "button_adc.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_check.h"
#include "esp_log.h"
#include "iot_button.h"
#include <stdint.h>

static const char *TAG = "korvo2-buttons";
static QueueHandle_t s_event_queue = NULL;
static adc_oneshot_unit_handle_t s_adc_handle = NULL;
static button_handle_t s_buttons[6] = {0};

// Voltage windows mirror Espressif's official esp32_s3_korvo_2 BSP and are
// interpreted by espressif/button as calibrated millivolts, not raw ADC codes.
static const kratt_korvo2_button_range_t kButtonRanges[] = {
    {.button_id = KRATT_KORVO2_BUTTON_REC, .min_mv = 2310, .max_mv = 2510},
    {.button_id = KRATT_KORVO2_BUTTON_MUTE, .min_mv = 1880, .max_mv = 2080},
    {.button_id = KRATT_KORVO2_BUTTON_PLAY, .min_mv = 1550, .max_mv = 1750},
    {.button_id = KRATT_KORVO2_BUTTON_SET, .min_mv = 1010, .max_mv = 1210},
    {.button_id = KRATT_KORVO2_BUTTON_VOLDOWN, .min_mv = 720, .max_mv = 920},
    {.button_id = KRATT_KORVO2_BUTTON_VOLUP, .min_mv = 280, .max_mv = 480},
};

const char *kratt_korvo2_button_name(kratt_korvo2_button_id_t button_id) {
  switch (button_id) {
  case KRATT_KORVO2_BUTTON_REC:
    return "REC";
  case KRATT_KORVO2_BUTTON_MUTE:
    return "MUTE";
  case KRATT_KORVO2_BUTTON_PLAY:
    return "PLAY";
  case KRATT_KORVO2_BUTTON_SET:
    return "SET";
  case KRATT_KORVO2_BUTTON_VOLDOWN:
    return "VOL-";
  case KRATT_KORVO2_BUTTON_VOLUP:
    return "VOL+";
  case KRATT_KORVO2_BUTTON_MAIN:
    return "MAIN";
  default:
    return "UNKNOWN";
  }
}

const kratt_korvo2_button_range_t *kratt_korvo2_button_ranges(size_t *count) {
  if (count != NULL) {
    *count = sizeof(kButtonRanges) / sizeof(kButtonRanges[0]);
  }
  return kButtonRanges;
}

static void button_press_down_cb(void *arg, void *user_data) {
  (void)arg;
  const kratt_korvo2_button_id_t button_id =
      (kratt_korvo2_button_id_t)(intptr_t)user_data;
  if (s_event_queue != NULL) {
    xQueueSend(s_event_queue, &button_id, 0);
  }
}

esp_err_t kratt_korvo2_buttons_init(QueueHandle_t event_queue) {
  const button_config_t btn_cfg = {0};

  ESP_RETURN_ON_FALSE(event_queue != NULL, ESP_ERR_INVALID_ARG, TAG,
                      "event queue is required");
  if (s_event_queue != NULL) {
    ESP_LOGW(TAG, "Buttons already initialized");
    return ESP_OK;
  }

  adc_oneshot_unit_init_cfg_t init_cfg = {
      .unit_id = ADC_UNIT_1,
  };
  ESP_RETURN_ON_ERROR(adc_oneshot_new_unit(&init_cfg, &s_adc_handle), TAG,
                      "adc unit init failed");

  const adc_oneshot_chan_cfg_t chan_cfg = {
      .atten = ADC_ATTEN_DB_12,
      .bitwidth = ADC_BITWIDTH_DEFAULT,
  };
  ESP_RETURN_ON_ERROR(adc_oneshot_config_channel(s_adc_handle, ADC_CHANNEL_4, &chan_cfg),
                      TAG, "adc channel init failed");

  s_event_queue = event_queue;
  ESP_LOGI(TAG, "Initializing documented Korvo-2 ADC buttons on GPIO5");

  for (size_t i = 0; i < (sizeof(kButtonRanges) / sizeof(kButtonRanges[0])); ++i) {
    const button_adc_config_t adc_cfg = {
        .adc_handle = &s_adc_handle,
        .unit_id = ADC_UNIT_1,
        .adc_channel = ADC_CHANNEL_4,
        .button_index = kButtonRanges[i].button_id,
        .min = kButtonRanges[i].min_mv,
        .max = kButtonRanges[i].max_mv,
    };
    ESP_RETURN_ON_ERROR(iot_button_new_adc_device(&btn_cfg, &adc_cfg, &s_buttons[i]), TAG,
                        "create adc button failed");
#if BUTTON_VER_MAJOR >= 4
    ESP_RETURN_ON_ERROR(
        iot_button_register_cb(s_buttons[i], BUTTON_PRESS_DOWN, NULL, button_press_down_cb,
                               (void *)(intptr_t)kButtonRanges[i].button_id),
        TAG, "register callback failed");
#else
    ESP_RETURN_ON_ERROR(iot_button_register_cb(s_buttons[i], BUTTON_PRESS_DOWN,
                                               button_press_down_cb,
                                               (void *)(intptr_t)kButtonRanges[i].button_id),
                        TAG, "register callback failed");
#endif
    ESP_LOGI(TAG, "ADC button mapped: %-5s => %u-%u mV",
             kratt_korvo2_button_name(kButtonRanges[i].button_id),
             (unsigned)kButtonRanges[i].min_mv, (unsigned)kButtonRanges[i].max_mv);
  }

  return ESP_OK;
}
