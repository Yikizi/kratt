#pragma once

#include "esp_err.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
  KRATT_KORVO2_BUTTON_REC = 0,
  KRATT_KORVO2_BUTTON_MUTE,
  KRATT_KORVO2_BUTTON_PLAY,
  KRATT_KORVO2_BUTTON_SET,
  KRATT_KORVO2_BUTTON_VOLDOWN,
  KRATT_KORVO2_BUTTON_VOLUP,
  KRATT_KORVO2_BUTTON_MAIN,
  KRATT_KORVO2_BUTTON_NUM,
} kratt_korvo2_button_id_t;

typedef struct {
  kratt_korvo2_button_id_t button_id;
  uint16_t min_mv;
  uint16_t max_mv;
} kratt_korvo2_button_range_t;

esp_err_t kratt_korvo2_buttons_init(QueueHandle_t event_queue);

const char *kratt_korvo2_button_name(kratt_korvo2_button_id_t button_id);

const kratt_korvo2_button_range_t *kratt_korvo2_button_ranges(size_t *count);

#ifdef __cplusplus
}
#endif
