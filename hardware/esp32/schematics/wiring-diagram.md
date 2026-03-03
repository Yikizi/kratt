# ESP32-S3 Audio Wiring Notes

This project uses ESPHome with `i2s_audio` + `microphone` + `micro_wake_word`.

There is no single "correct" wiring because ESP32-S3 voice boards vary:

- Simple I2S mic (e.g. INMP441 / SPH0645)
  - Typically needs `BCLK`, `LRCLK/WS`, `DIN`, plus `3V3` and `GND`.
- Boards with an audio ADC (e.g. ES7210, ES7243E)
  - Usually require I2S pins plus I2C pins for codec configuration.
- PDM mic arrays
  - May need `pdm: true` in ESPHome and different pin mapping.

Use your board's schematic or product page to fill:
- `mic_bclk_pin`
- `mic_lrclk_pin`
- `mic_din_pin`
- optional I2C pins if you use `audio_adc:`

Config lives in:
- `/Users/mattias/kratt/hardware/esp32/esphome/voice-satellite-esp32-s3.yaml`

