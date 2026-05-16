# ESP32 (ESPHome) Voice Satellite

ESPHome configurations for an ESP32-S3 voice satellite with on-device Kratt wake-word detection (`micro_wake_word`) and Home Assistant Assist streaming.

## Recommended user path: prebuilt firmware image

For normal users, the best install UX is a ready firmware image for a supported board, starting with ESP32-S3-Korvo-2. This avoids asking users to hand-edit YAML just to install the wake word.

Build a firmware artifact from this repo:

```bash
./cli/kratt build-esphome-firmware --model v16c --cutoff 0.996
```

The script compiles ESPHome, copies `firmware*.bin` files into `output/firmware/esphome/...`, and writes checksum/provenance files. Publish/use the factory image for first-time flashing when available.

## Developer path: use Kratt v16c like a built-in wake word

In an existing ESPHome voice-satellite YAML, add the public v16c manifest under `micro_wake_word.models`:

```yaml
micro_wake_word:
  models:
    - model: github://Yikizi/kratt/wake-word/models/kuule-kratt-v16c/kuule_kratt_v16c.json@main
      id: kuule_kratt_model
```

Raw URL alternative:

```yaml
micro_wake_word:
  models:
    - model: https://raw.githubusercontent.com/Yikizi/kratt/main/wake-word/models/kuule-kratt-v16c/kuule_kratt_v16c.json
      id: kuule_kratt_model
```

Then compile/flash the ESPHome device. This is the closest equivalent to using a built-in model such as `hey_jarvis`.

> Status: `v16c` is the stable demo/baseline model, not a production-proven detector. See `wake-word/models/kuule-kratt-v16c/NOTES.md`.

## Option B: local development from this repository

1. Create secrets file:

   ```bash
   cp hardware/esp32/esphome/secrets.yaml.example hardware/esp32/esphome/secrets.yaml
   ```

   Fill in Wi-Fi credentials and `api_encryption_key`.

2. Install ESPHome CLI (recommended via the repo venv):

   ```bash
   ./scripts/setup/install_esphome.sh
   ```

3. Prepare the local Kratt model copy:

   ```bash
   ./cli/kratt prepare-esphome-model v16c --cutoff 0.996
   ```

   This copies `wake-word/models/kuule-kratt-v16c/kuule_kratt_v16c.tflite` to the ignored local ESPHome artifact `hardware/esp32/esphome/models/kratt.tflite` and updates `models/kratt.json`.

4. Configure board and microphone pins if you use the generic config:

   Edit `voice-satellite-esp32-s3.yaml` substitutions:
   - `board` (for example `esp32-s3-devkitc-1` or another ESP32-S3 board);
   - `mic_bclk_pin`, `mic_lrclk_pin`, `mic_din_pin`;
   - enable/configure `audio_adc:` if your board uses an ES7210/ES7243E-style audio ADC.

   For ESP32-S3-Korvo-2, start with `voice-satellite-esp32-s3-korvo2.yaml`.

5. Validate/flash:

   ```bash
   ./.venv-esphome/bin/esphome config hardware/esp32/esphome/voice-satellite-esp32-s3-korvo2.yaml
   ./.venv-esphome/bin/esphome run hardware/esp32/esphome/voice-satellite-esp32-s3-korvo2.yaml
   ```

## Included configs

- `voice-satellite-esp32-s3-korvo2.yaml` — full Korvo-2 Home Assistant Assist satellite.
- `voice-satellite-esp32-s3-korvo2-demo.yaml` — wake-word-only serial/log demo for Korvo-2.
- `voice-satellite-esp32-s3.yaml` — generic ESP32-S3 skeleton with configurable pins.
- `models/kratt.json` — local development manifest; expects ignored `models/kratt.tflite`.

## Home Assistant pipeline

Use this ESPHome device as the wake-word satellite, then choose whichever backend components you need:

- local Estonian STT: `Kratt Kiirkirjutaja STT` add-on (`10300`);
- TTS: local TartuNLP TTS add-on / Wyoming wrapper (`10301`);
- conversation agent: Home Assistant.
