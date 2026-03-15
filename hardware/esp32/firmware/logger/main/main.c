#include "esp_adc/adc_oneshot.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdio.h>

#define BUTTON_ADC_CHANNEL ADC_CHANNEL_4

static const char *TAG = "buttons";

void app_main(void) {
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

  int raw = 0;
  while (true) {
    ESP_ERROR_CHECK(adc_oneshot_read(adc_handle, BUTTON_ADC_CHANNEL, &raw));
    ESP_LOGI(TAG, "ADC raw: %d", raw);
    vTaskDelay(pdMS_TO_TICKS(200));
  }
}
