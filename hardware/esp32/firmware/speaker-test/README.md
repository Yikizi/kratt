# Korvo-2 v3.1 Speaker Diagnostic Firmware

This firmware is the dedicated speaker-side diagnostic target for the ESP32-S3-Korvo-2 v3.1 board.
It follows Espressif's documented audio path instead of treating the board like a generic devkit.

## Architecture

- Playback path: `ESP32-S3 I2S peripheral -> ES8311 mono DAC -> NS4150 power amplifier -> speaker JST`
- Control path: `BSP-selected I2C bus on GPIO17/GPIO18` configures ES8311 and the ES7210 microphone ADC
- Board-specific pins and PA control come from the official `espressif/esp32_s3_korvo_2` BSP
- The firmware uses mono PCM because Espressif documents ES8311 on this board as a mono codec
- The board's AEC reference comes back through ES7210 MIC3, so MIC3 is not a third user microphone

## Runtime behavior

- Boots, initializes I2C + BSP audio + ES8311 speaker codec, then plays a three-tone startup pattern
- `PLAY` replays the startup pattern
- `REC` plays a frequency sweep for checking the full speaker path
- `VOL+` / `VOL-` adjust output volume
- `MUTE` toggles mute by driving codec volume to zero and restoring the previous level
- `SET` dumps runtime status and the current audio configuration to the serial log
- Buttons are read directly from the documented ADC resistor ladder on `GPIO5`, avoiding the BSP helper path that also tries to initialize the optional TT21100 touch controller

## Build and flash

```sh
source /Users/mattias/esp/esp-idf/export.sh
cd /Users/mattias/kratt/hardware/esp32/firmware/speaker-test
idf.py set-target esp32s3
idf.py -p /dev/cu.usbserial-130 flash monitor
```

## Primary sources

- Espressif Korvo-2 v3.1 user guide: <https://docs.espressif.com/projects/esp-adf/en/latest/design-guide/dev-boards/user-guide-esp32-s3-korvo-2.html>
- Espressif Korvo-2 v3.1 schematic: <https://dl.espressif.com/dl/schematics/SCH_ESP32-S3-Korvo-2_V3.1.2_20240116.pdf>
- Espressif Korvo-2 BSP/API: <https://components.espressif.com/components/espressif/esp32_s3_korvo_2>
