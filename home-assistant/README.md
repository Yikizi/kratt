# Kratt for Home Assistant

Kratt is packaged for Home Assistant as a **modular** stack. You can install only the parts you need:

| Component | Install path | Required? | Notes |
|---|---|---:|---|
| Kuule Kratt wake word (`v16c`) | Prebuilt ESPHome firmware image / ESPHome config | Optional but core Kratt feature | Best user path is a ready firmware image for supported ESP32-S3 voice-satellite boards; YAML remains the reproducible developer path. |
| Kiirkirjutaja STT | `Kratt Kiirkirjutaja STT` add-on | Optional | Local Estonian Wyoming STT on `10300`. |
| Local TartuNLP TTS | `Kratt TartuNLP Local TTS` add-on | Optional | Estonian TTS using TartuNLP `text-to-speech-worker` (`v3.1.0`). Initial add-on target is `amd64` because the upstream image is `amd64` only. |
| Demo pipeline | `kratt demo` / `tools/demo-pipeline` | No | Maintainer/demo tooling, not the normal Home Assistant install path. |

## Add-on repository

The monorepo root is also a Home Assistant add-on repository. Add this URL in Home Assistant:

```text
https://github.com/Yikizi/kratt
```

Install the local add-on first:

- **Kratt Kiirkirjutaja STT** — local Estonian speech-to-text.

TTS path:

- **Kratt TartuNLP Local TTS** — local Estonian text-to-speech using TartuNLP `text-to-speech-worker` (`v3.1.0`, local checkout `tools/text-to-speech-worker/`, upstream <https://github.com/TartuNLP/text-to-speech-worker>).

The add-ons use Wyoming discovery. If discovery does not appear, open each add-on's **Network** section, map the container port to the same host port, restart the add-on, and add the Wyoming integrations manually using your Home Assistant host/IP:

- STT: container `10300` → host `10300`
- TTS: container `10301` → host `10301`

## Wake word: prebuilt ESPHome firmware image

For ESPHome/microWakeWord devices, the wake-word model is part of the ESPHome firmware configuration. A Home Assistant add-on cannot silently inject a new microWakeWord model into an already flashed ESP32 device. The best user-facing path is a ready firmware image for supported devices, starting with ESP32-S3-Korvo-2. The build script writes local artifacts under `output/firmware/esphome/`.

The YAML/manifest form remains the reproducible developer path. Add the Kratt model manifest like a built-in model:

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

Changing an ESPHome wake word requires recompiling/flashing the ESPHome device. It is firmware configuration, not a runtime Home Assistant add-on option. After the firmware includes the model, Home Assistant/ESPHome can expose the device's configured wake-word behavior, but the add-on repository alone cannot make `Kuule Kratt` appear as a selectable model on arbitrary existing devices.

See `home-assistant/VALIDATION.md` for the current validation status.

## Docker Compose alternative

For users not running Home Assistant OS/Supervisor add-ons, `docker/kratt-stack.yml` provides the same services as opt-in Compose profiles:

```bash
docker compose -f docker/kratt-stack.yml --profile stt up -d
docker compose -f docker/kratt-stack.yml --profile stt --profile tartunlp up -d
```

## Full example pipeline

A practical Estonian Assist pipeline can be:

```text
ESPHome voice satellite with Kuule Kratt v16c
  → Home Assistant Assist pipeline
  → Kiirkirjutaja STT add-on
  → Home Assistant conversation/intent handling
  → local TartuNLP TTS Wyoming wrapper
```

## Validation

See `home-assistant/VALIDATION.md` for the current static checks, Docker build/start smoke tests, and ESPHome config validation.

## Status and limitations

This is a research-prototype release path for the thesis project. `v16c` is the stable demo/baseline wake-word model, not a production-proven detector. Later experiments showed unresolved prefix/confusable phrase-selectivity risks; see `wake-word/docs/MODEL_LINEAGE.md` and `wake-word/models/kuule-kratt-v16c/NOTES.md`.

For thesis/demo references, cite the local TartuNLP `text-to-speech-worker` path with attribution to TartuNLP / University of Tartu and the pinned upstream release.
