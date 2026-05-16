# home-assistant/

Home Assistant voice pipeline integration.

## Status

A modular v0.1 add-on/install path exists:

- repo-root Home Assistant add-on repository metadata: `repository.yaml`
- `kratt-kiirkirjutaja-stt/`: Wyoming STT add-on for local Estonian Kiirkirjutaja INT8
- `kratt-neurokone-tts/`: older Wyoming TTS add-on wrapping the external Tartu Neurokõne API; supersede with local TartuNLP `text-to-speech-worker` path before public/default claims
- `tools/text-to-speech-worker/`: local TartuNLP TTS checkout used by the demo (`v3.1.0`, commit `14d47bf`); source/provenance for the local TTS path
- `home-assistant/README.md`: user-facing modular install guide
- ESPHome wake-word install remains the primary Kratt wake-word path; normal-user UX should be a ready firmware image, while YAML/manifests remain the developer/reproducibility path.

## Current integration path

```
ESP32-S3 firmware image (microWakeWord, Kuule Kratt v16c)
    → Home Assistant Assist pipeline
    → Kiirkirjutaja STT add-on (Wyoming TCP:10300)
    → HA Conversation / intent / action
    → local TartuNLP TTS Wyoming wrapper (planned replacement for API wrapper)
```

The stack is intentionally modular: users may install only STT, only TTS, only the ESPHome wake-word firmware, or combine them into a full Estonian Assist pipeline. Do not claim that an HA add-on can automatically install ESPHome microWakeWord models into already-flashed devices.
