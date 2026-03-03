# ESP32 (ESPHome) Voice Satellite

This folder contains ESPHome configurations for an ESP32-based voice satellite with on-device wake word
detection (microWakeWord) and Home Assistant Assist streaming.

## Quick Start (macOS / Linux)

1. Create secrets file:

   - Copy `secrets.yaml.example` to `secrets.yaml`
   - Fill in Wi-Fi credentials

2. Install ESPHome CLI (recommended via a venv in this repo):

   ```bash
   cd /Users/mattias/kratt
   ./scripts/setup/install_esphome.sh
   ```

3. Configure the board + microphone pins:

   Edit `voice-satellite-esp32-s3.yaml` substitutions:
   - `board` (e.g. `esp32-s3-devkitc-1`, `esp32-s3-box-3`, ...)
   - `mic_bclk_pin`, `mic_lrclk_pin`, `mic_din_pin`
   - If your board uses an audio ADC (ES7210/ES7243E) you may need to enable the `audio_adc:` block.

4. Flash over USB and watch logs:

   ```bash
   cd /Users/mattias/kratt
   ./scripts/deployment/esphome_run.sh /Users/mattias/kratt/hardware/esp32/esphome/voice-satellite-esp32-s3.yaml
   ```

## Custom Wake Word ("Kratt")

ESPHome `micro_wake_word` models are defined by a JSON manifest that references a `.tflite` file.
For local testing you can keep both files on disk and point ESPHome at the JSON via an absolute path.

1. Put your trained `.tflite` somewhere on disk.
2. Create a JSON manifest (see `models/kratt.example.json`) and update:
   - `wake_word`
   - `model` (path to the `.tflite`)
   - `probability_cutoff`, `sliding_window_size`, `tensor_arena_size`
3. Update `voice-satellite-esp32-s3.yaml` to reference your JSON.

If you want to (re)train the model from the repo dataset:
  - `/Users/mattias/kratt/wake-word/training/scripts/train_microwakeword.sh`

Notes:
- This repo intentionally does not commit trained model binaries (see `.gitignore`).
