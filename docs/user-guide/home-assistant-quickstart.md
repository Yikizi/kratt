# Kratt Home Assistant quickstart

This guide installs Kratt as modular Home Assistant components. You can use only the parts you need.

## 1. Add the Kratt add-on repository

In Home Assistant:

1. **Settings → Add-ons → Add-on Store**
2. Open **⋮ → Repositories**
3. Add:

```text
https://github.com/Yikizi/kratt
```

Install the local STT add-on:

- **Kratt Kiirkirjutaja STT** — local Estonian speech-to-text, Wyoming port `10300`.

TTS note:

- Install **Kratt TartuNLP Local TTS** for Estonian text-to-speech using TartuNLP `text-to-speech-worker` (`v3.1.0`, local checkout `tools/text-to-speech-worker/`, upstream <https://github.com/TartuNLP/text-to-speech-worker>). Initial add-on target is `amd64`; ARM/aarch64 needs separate validation.

If Home Assistant does not auto-discover the services, open the add-on **Network** section, map the container port to the same host port (`10300` or `10301`), restart the add-on, and add the **Wyoming Protocol** integration manually with your Home Assistant host/IP and the mapped port.

## 2. Install Kuule Kratt wake word firmware

Best user path: flash a ready ESPHome firmware image for the supported voice-satellite board, starting with ESP32-S3-Korvo-2. This avoids asking normal users to hand-edit YAML. Build/rebuild the artifact with:

```bash
./cli/kratt build-esphome-firmware --model v16c --cutoff 0.996
```

The build writes firmware binaries and checksums under `output/firmware/esphome/`.

Developer/reproducible path: for an ESPHome voice satellite, use the public v16c manifest:

```yaml
micro_wake_word:
  models:
    - model: github://Yikizi/kratt/wake-word/models/kuule-kratt-v16c/kuule_kratt_v16c.json@main
      id: kuule_kratt_model
```

Then compile and flash the ESPHome device. This step is required: ESPHome `micro_wake_word` models are firmware-time configuration, so a Home Assistant add-on cannot automatically install the wake word into an already flashed ESP32 device.

For a full Korvo-2 example, see:

- `hardware/esp32/esphome/voice-satellite-esp32-s3-korvo2.yaml`
- `hardware/esp32/esphome/README.md`

## 3. Configure an Assist pipeline

Create or edit an Assist pipeline:

- Wake word: ESPHome satellite using `kuule_kratt_model`
- Speech-to-text: Kiirkirjutaja / Wyoming STT
- Conversation agent: Home Assistant
- Text-to-speech: Kratt TartuNLP Local TTS / Wyoming TTS
- Language: Estonian (`et` / `et-EE`)

## Notes

- The wake-word model `v16c` is a research-prototype baseline, not a production-proven detector.
- STT runs locally after the model files are downloaded.
- The active TTS add-on path is local TartuNLP `text-to-speech-worker` + `multispeaker` model release; see `home-assistant/VALIDATION.md` for current validation status.
