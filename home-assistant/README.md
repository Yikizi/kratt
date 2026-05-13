# Kratt for Home Assistant

Kratt is packaged for Home Assistant as a **modular** stack. You can install only the parts you need:

| Component | Install path | Required? | Notes |
|---|---|---:|---|
| Kuule Kratt wake word (`v16c`) | ESPHome `micro_wake_word` model manifest | Optional but core Kratt feature | Runs on ESP32-S3 class voice satellites. |
| Kiirkirjutaja STT | `Kratt Kiirkirjutaja STT` add-on | Optional | Local Estonian Wyoming STT on `10300`. |
| Neurokõne TTS | `Kratt Neurokõne TTS` add-on | Optional | Estonian Wyoming TTS on `10301`; currently calls external TartuNLP API. |
| Piper TTS | Official Wyoming Piper add-on/container | Optional | Prefer this for a fully local TTS path if an Estonian voice is sufficient. |
| Demo pipeline | `kratt demo` / `tools/demo-pipeline` | No | Maintainer/demo tooling, not the normal Home Assistant install path. |

## Add-on repository

The monorepo root is also a Home Assistant add-on repository. Add this URL in Home Assistant:

```text
https://github.com/Yikizi/kratt
```

Then install the add-ons you want:

- **Kratt Kiirkirjutaja STT** — local Estonian speech-to-text.
- **Kratt Neurokõne TTS** — Estonian text-to-speech through Neurokõne.

Both add-ons use Wyoming discovery. If discovery does not appear, open each add-on's **Network** section, map the container port to the same host port, restart the add-on, and add the Wyoming integrations manually using your Home Assistant host/IP:

- STT: container `10300` → host `10300`
- TTS: container `10301` → host `10301`

## Wake word: ESPHome install like `hey_jarvis`

For ESPHome/microWakeWord devices, add the Kratt model manifest just like a built-in model:

```yaml
micro_wake_word:
  models:
    - model: github://Yikizi/kratt/wake-word/models/kuule-kratt-v16c/kuule_kratt_v16c.json@main
      id: kuule_kratt_model
```

Alternative raw URL:

```yaml
micro_wake_word:
  models:
    - model: https://raw.githubusercontent.com/Yikizi/kratt/main/wake-word/models/kuule-kratt-v16c/kuule_kratt_v16c.json
      id: kuule_kratt_model
```

Changing an ESPHome wake word requires recompiling/flashing the ESPHome device. It is firmware configuration, not a runtime Home Assistant option.

## Docker Compose alternative

For users not running Home Assistant OS/Supervisor add-ons, `docker/kratt-stack.yml` provides the same services as opt-in Compose profiles:

```bash
docker compose -f docker/kratt-stack.yml --profile stt --profile piper up -d
docker compose -f docker/kratt-stack.yml --profile stt --profile neurokone up -d
```

## Full example pipeline

A practical Estonian Assist pipeline can be:

```text
ESPHome voice satellite with Kuule Kratt v16c
  → Home Assistant Assist pipeline
  → Kiirkirjutaja STT add-on
  → Home Assistant conversation/intent handling
  → Piper or Neurokõne TTS
```

## Validation

See `home-assistant/VALIDATION.md` for the current static checks, Docker build/start smoke tests, and ESPHome config validation.

## Status and limitations

This is a research-prototype release path for the thesis project. `v16c` is the stable demo/baseline wake-word model, not a production-proven detector. Later experiments showed unresolved prefix/confusable phrase-selectivity risks; see `wake-word/docs/MODEL_LINEAGE.md` and `wake-word/models/kuule-kratt-v16c/NOTES.md`.
