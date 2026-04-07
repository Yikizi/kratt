#pragma once

#include "driver/gpio.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
  gpio_num_t i2c_sda;
  gpio_num_t i2c_scl;
  gpio_num_t i2s_mclk;
  gpio_num_t i2s_bclk;
  gpio_num_t i2s_lrck;
  gpio_num_t i2s_dout;
  gpio_num_t i2s_din;
  gpio_num_t speaker_pa_enable;
  gpio_num_t buttons_adc_gpio;
} kratt_korvo2_audio_pins_t;

const kratt_korvo2_audio_pins_t *kratt_korvo2_audio_pins(void);

void kratt_korvo2_log_board_overview(const char *tag);

#ifdef __cplusplus
}
#endif
