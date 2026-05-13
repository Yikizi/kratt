# home-assistant/

Home Assistant voice pipeline integration.

## Status

A modular v0.1 add-on/install path exists:

- repo-root Home Assistant add-on repository metadata: `repository.yaml`
- `kratt-kiirkirjutaja-stt/`: Wyoming STT add-on for local Estonian Kiirkirjutaja INT8
- `kratt-neurokone-tts/`: Wyoming TTS add-on wrapping the Tartu Neurokõne API
- `home-assistant/README.md`: user-facing modular install guide
- ESPHome wake-word install remains the primary Kratt wake-word path (see `hardware/esp32/esphome/` and the v16c manifest in `wake-word/models/kuule-kratt-v16c/`).

## Current integration path

```
ESP32-S3 (microWakeWord, Kuule Kratt v16c)
    → Home Assistant Assist pipeline
    → Kiirkirjutaja STT add-on (Wyoming TCP:10300)
    → HA Conversation / intent / action
    → Piper or Neurokõne TTS add-on (Wyoming TCP:10301)
```

The stack is intentionally modular: users may install only STT, only TTS, only the ESPHome wake-word model, or combine them into a full Estonian Assist pipeline.
