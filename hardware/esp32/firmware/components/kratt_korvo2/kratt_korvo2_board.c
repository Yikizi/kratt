#include "kratt_korvo2_board.h"

#include "esp_log.h"

static const kratt_korvo2_audio_pins_t kAudioPins = {
    .i2c_sda = GPIO_NUM_17,
    .i2c_scl = GPIO_NUM_18,
    .i2s_mclk = GPIO_NUM_16,
    .i2s_bclk = GPIO_NUM_9,
    .i2s_lrck = GPIO_NUM_45,
    .i2s_dout = GPIO_NUM_8,
    .i2s_din = GPIO_NUM_10,
    .speaker_pa_enable = GPIO_NUM_48,
    .buttons_adc_gpio = GPIO_NUM_5,
};

const kratt_korvo2_audio_pins_t *kratt_korvo2_audio_pins(void) {
  return &kAudioPins;
}

void kratt_korvo2_log_board_overview(const char *tag) {
  const char *log_tag = (tag != NULL) ? tag : "korvo2-board";

  ESP_LOGI(log_tag,
           "Korvo-2 v3.1 audio path: ESP32-S3 I2S -> ES8311 DAC -> NS4150 PA -> speaker");
  ESP_LOGI(log_tag,
           "Korvo-2 v3.1 mic path: left/right mics -> ES7210 ADC -> ESP32-S3 I2S");
  ESP_LOGI(log_tag,
           "Documented pins: I2C SDA=%d SCL=%d | I2S MCLK=%d BCLK=%d LRCK=%d DOUT=%d DIN=%d | PA=%d",
           kAudioPins.i2c_sda, kAudioPins.i2c_scl, kAudioPins.i2s_mclk,
           kAudioPins.i2s_bclk, kAudioPins.i2s_lrck, kAudioPins.i2s_dout,
           kAudioPins.i2s_din, kAudioPins.speaker_pa_enable);
  ESP_LOGI(log_tag,
           "Buttons: ADC ladder on GPIO%d / ADC1_CH4 with calibrated millivolt windows",
           kAudioPins.buttons_adc_gpio);
  ESP_LOGI(log_tag,
           "AEC note: MIC3 is the echo-reference path sourced from ES8311 DAC by default on v3.1");
}
