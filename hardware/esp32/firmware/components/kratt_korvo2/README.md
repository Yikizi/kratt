# kratt_korvo2

Shared Korvo-2 v3.1 board support used by multiple Kratt firmware targets.

## Source of truth

This component is intentionally aligned to Espressif's official documentation and
reference implementations:

- Korvo-2 user guide:
  [ESP32-S3-Korvo-2 V3.1](https://docs.espressif.com/projects/esp-adf/en/latest/design-guide/dev-boards/user-guide-esp32-s3-korvo-2.html)
- Button component docs:
  [ESP-IoT-Solution Button](https://docs.espressif.com/projects/esp-iot-solution/en/release-v2.0/input_device/button.html)
- Official BSP package:
  [espressif/esp32_s3_korvo_2](https://components.espressif.com/components/espressif/esp32_s3_korvo_2/versions/4.2.0/readme)

## Architecture

`kratt_korvo2` owns board-specific facts that should not be reimplemented inside
application firmware:

- documented audio and control pinout for Korvo-2 v3.1
- button ADC ladder setup on `GPIO5 / ADC1_CH4`
- official calibrated millivolt windows for the six side buttons
- high-signal board logging that explains the audio and AEC signal paths

Application firmware should own only product logic:

- what each button press does
- which audio pipelines are opened
- how state is persisted
- which diagnostics are emitted on top of the shared board logs

## Current modules

- `kratt_korvo2_board.[ch]`
  - exposes documented Korvo-2 pin assignments
  - logs the board-level speaker, microphone, button, and AEC topology
- `kratt_korvo2_buttons.[ch]`
  - creates ADC buttons using Espressif's `button` component
  - uses calibrated millivolt ranges, not raw ADC counts
  - avoids `bsp_iot_button_create()` so speaker-only firmware does not pull in
    touch/LCD button initialization

## Button ranges

These values match Espressif's official Korvo-2 BSP:

- `REC`: `2310-2510 mV`
- `MUTE`: `1880-2080 mV`
- `PLAY`: `1550-1750 mV`
- `SET`: `1010-1210 mV`
- `VOL-`: `720-920 mV`
- `VOL+`: `280-480 mV`

## Design rules

- Do not decode Korvo-2 side buttons from raw ADC values.
- Do not duplicate Korvo-2 pin constants inside firmware apps unless there is a
  deliberate board fork.
- Prefer extending this component when multiple firmware targets need the same
  board-specific behavior.
