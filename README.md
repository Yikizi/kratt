# Kratt

Kratt is a research prototype for Estonian Home Assistant voice control: a
**"Kuule Kratt"** ESPHome wake-word model plus modular Estonian STT/TTS
components for Home Assistant Assist.

> Status: `v0.1.0-alpha` research prototype. The `v16c` wake-word model is a
> stable demo/baseline model, not a production-proven detector. Later thesis
> experiments showed unresolved prefix/confusable phrase-selectivity risks.

## Components

| Component | Path | Notes |
|---|---|---|
| Kuule Kratt wake word (`v16c`) | `wake-word/models/kuule-kratt-v16c/` | ESPHome `micro_wake_word` TFLite model + manifest. |
| Kiirkirjutaja STT add-on | `kratt-kiirkirjutaja-stt/` | Local Estonian Wyoming STT on port `10300`. |
| Neurokõne TTS add-on | `kratt-neurokone-tts/` | Estonian Wyoming TTS on port `10301`; calls external TartuNLP API. |
| ESPHome examples | `hardware/esp32/esphome/` | ESP32-S3/Korvo-2 voice satellite examples. |
| Docker Compose stack | `docker/kratt-stack.yml` | Optional non-Supervisor service deployment. |

## Home Assistant quickstart

Add this repository in Home Assistant:

```text
Settings → Add-ons → Add-on Store → ⋮ → Repositories
https://github.com/Yikizi/kratt
```

Install whichever add-ons you need:

- **Kratt Kiirkirjutaja STT** — local Estonian speech-to-text.
- **Kratt Neurokõne TTS** — Estonian text-to-speech through Neurokõne.

For the wake word, add the public ESPHome model manifest to an ESPHome voice
satellite:

```yaml
micro_wake_word:
  models:
    - model: github://Yikizi/kratt/wake-word/models/kuule-kratt-v16c/kuule_kratt_v16c.json@main
      id: kuule_kratt_model
```

See `docs/user-guide/home-assistant-quickstart.md` and `home-assistant/README.md`.

## Privacy

Wake-word detection runs locally on the ESP32-S3 class device. The Kiirkirjutaja
STT add-on processes audio locally after downloading upstream model files. The
Neurokõne TTS add-on sends synthesis text to the external TartuNLP API; use
Piper or another local TTS if a fully offline stack is required.

No raw participant audio, user-test WAV files, private Home Assistant logs,
Wi-Fi credentials, or local training datasets are published in this repository.
See `PRIVACY.md`.

## Evaluation and model caveats

The thesis work behind this repository found that clip-level wake-word accuracy
is not enough for real deployment. Models must be evaluated together on:

- streaming false accepts per hour (FAPH),
- real/unseen-speaker recall,
- hard-negative, prefix, and confusable phrase rejection.

The `v16c` model is published as a baseline/demo artifact. It should not be
marketed as a production-ready Estonian wake-word detector. See:

- `wake-word/models/kuule-kratt-v16c/NOTES.md`
- `wake-word/docs/MODEL_LINEAGE.md`
- `docs/evaluation.md`

## License

Kratt-owned code, configuration, documentation, and wake-word model artifacts are
published under the Apache License 2.0 unless otherwise noted. Third-party
components and downloaded model files remain under their upstream licenses. See
`LICENSE` and `NOTICE`.
