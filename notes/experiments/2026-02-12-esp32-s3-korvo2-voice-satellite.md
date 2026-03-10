# ESP32-S3 Korvo-2 Voice Satellite + microWakeWord (Kratt) - Initial Experiment

Date: 2026-02-12 to 2026-02-13

## Goal

Validate an ESP32-S3 Korvo-2 mic-array board as a Home Assistant voice satellite using:

- ESPHome `voice_assistant`
- On-device wake word via ESPHome `micro_wake_word`
- A custom microWakeWord model for the wake word "kratt"

## Hardware

- Board: ESP32-S3 Korvo-2 (Espressif)
- USB ports used:
  - `USB-to-UART` for flashing/logs (CP2102N)
  - `USB Power` for stable power

Notes:
- With only one cable connected, macOS did not enumerate the UART serial device.
- With both cables connected and the board power switch set to ON, the UART enumerated as `/dev/cu.usbserial-130`.

## Software / Repo Artifacts

- ESPHome venv: `/Users/mattias/kratt/.venv-esphome`
- microWakeWord training venv: `/Users/mattias/kratt/wake-word/.venv-microwakeword`
- ESPHome Korvo-2 config:
  - `/Users/mattias/kratt/hardware/esp32/esphome/voice-satellite-esp32-s3-korvo2.yaml`
- microWakeWord model manifest (text, commit-safe):
  - `/Users/mattias/kratt/hardware/esp32/esphome/models/kratt.json`
- Trained TFLite model (binary, gitignored):
  - `/Users/mattias/kratt/hardware/esp32/esphome/models/kratt.tflite`

## ESPHome Configuration Summary (Korvo-2)

Mic input (ES7210 ADC over I2C + I2S):
- I2C: SDA `GPIO17`, SCL `GPIO18`
- I2S (mic): MCLK `GPIO16`, BCLK `GPIO9`, LRCLK `GPIO45`, DIN `GPIO10`
- Sample rate: 16 kHz, 16-bit

Wake word:
- `micro_wake_word` enabled with:
  - Built-in `okay_nabu` model
  - Custom `kratt` model (local JSON manifest)
- Added debug helpers in YAML:
  - Binary sensor: `Listening`
  - Text sensor: `Last Wake Word`
  - Button: `Start Assist (PTT)`
  - Button: `Restart Wake Word`
- Ensure wake word starts on boot via `esphome.on_boot -> micro_wake_word.start`.

Speaker output (ES8311 DAC over I2C + I2S):
- ES8311 (I2C, default address `0x18`)
- I2S DOUT (to ES8311 DSDIN): `GPIO8`
- Added `voice_assistant.speaker: spk` so HA responses can be played on-device.

## Home Assistant Integration

Device added via ESPHome.

Observed:
- Device IP: `192.168.0.131`
- mDNS hostname: `kratt-korvo2.local`

Entities used for debugging:
- `... Last Wake Word` (shows "Okay Nabu" when that model triggers)
- `... Listening` (ON while capturing)
- `... Start Assist (PTT)` (manual start; validates mic + pipeline independent of wake word)

## Results

1. UART + flashing
- Successful flash via CP2102N UART once the serial port enumerated.

2. WiFi
- Korvo-2 did not connect to the 5 GHz SSID (`TP-Link_C8F0_5G`).
- Switching to the 2.4 GHz SSID (`TP-Link_C8F0`) worked reliably.

3. Wake word: "Okay Nabu"
- Works (wake events observed; `Last Wake Word` updates to "Okay Nabu").

4. Wake word: "kratt" (custom model)
- Did not trigger in initial tests, even after reducing:
  - `probability_cutoff` to 0.70
  - `sliding_window_size` to 3

5. "Responding" state / audio output
- Earlier, the satellite could get stuck in a "responding" state when no speaker was configured.
- Adding ES8311 + I2S speaker output unblocked end-to-end response playback (speaker initialized in logs).

## Key Takeaways / Hypotheses

- The custom "kratt" model is likely suffering from domain mismatch:
  - positives were generated via TTS (clean, near-field, no room acoustics)
  - Korvo-2 is far-field + room acoustics + mic-array frequency response
- The fact that `okay_nabu` works confirms the on-device wake word pipeline and microphone capture path are functional.

## Next Steps

1. Collect real Korvo-2 recordings for "kratt"
- Multiple speakers, distances, rooms, and background noise levels.

2. Retrain microWakeWord with real positives
- Re-export streaming INT8 TFLite and re-package into ESPHome local manifest.

3. Evaluate false positives / sensitivity tradeoff
- Tune `probability_cutoff` and `sliding_window_size` after real-data training.

4. Optional: add a visible "wake detected" indicator (LED) in ESPHome
- Useful for debugging without watching logs.

