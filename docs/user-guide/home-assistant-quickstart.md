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

Install one or both add-ons:

- **Kratt Kiirkirjutaja STT** — local Estonian speech-to-text, Wyoming port `10300`.
- **Kratt Neurokõne TTS** — Estonian TTS, Wyoming port `10301`, uses the external TartuNLP API.

If Home Assistant does not auto-discover the services, open the add-on **Network** section, map the container port to the same host port (`10300` or `10301`), restart the add-on, and add the **Wyoming Protocol** integration manually with your Home Assistant host/IP and the mapped port.

## 2. Add Kuule Kratt wake word to ESPHome

For an ESPHome voice satellite, use the public v16c manifest:

```yaml
micro_wake_word:
  models:
    - model: github://Yikizi/kratt/wake-word/models/kuule-kratt-v16c/kuule_kratt_v16c.json@main
      id: kuule_kratt_model
```

Then compile and flash the ESPHome device.

For a full Korvo-2 example, see:

- `hardware/esp32/esphome/voice-satellite-esp32-s3-korvo2.yaml`
- `hardware/esp32/esphome/README.md`

## 3. Configure an Assist pipeline

Create or edit an Assist pipeline:

- Wake word: ESPHome satellite using `kuule_kratt_model`
- Speech-to-text: Kiirkirjutaja / Wyoming STT
- Conversation agent: Home Assistant
- Text-to-speech: Piper, Neurokõne, or another Wyoming TTS service
- Language: Estonian (`et` / `et-EE`)

## Notes

- The wake-word model `v16c` is a research-prototype baseline, not a production-proven detector.
- STT runs locally after the model files are downloaded.
- Neurokõne TTS currently sends synthesis text to the TartuNLP API. Use Piper or another local TTS if you require a fully offline stack.
