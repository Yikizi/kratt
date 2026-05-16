# Home Assistant packaging validation

Validation performed in the working tree on 2026-05-12 and refreshed after packaging corrections on 2026-05-16.

## 2026-05-15/16 correction

The old `kratt-neurokone-tts` add-on called the external TartuNLP Neurokõne API. Because Neurokõne asks integrators to contact them before application integration, that wrapper was removed from the active add-on path.

The corrected public/default TTS direction is now a **local** wrapper around TartuNLP `text-to-speech-worker`, which is already present in this project and used by the demo path:

- upstream: <https://github.com/TartuNLP/text-to-speech-worker>
- local checkout: `tools/text-to-speech-worker/`
- checked version: `v3.1.0`, commit `14d47bf9af4e562829ccafcc757d93abb2a6412f`
- model release: <https://github.com/TartuNLP/text-to-speech-worker/releases/tag/v3.1.0>
- local demo wrapper: `tools/tts-server/server.py`

Also, ESPHome `micro_wake_word` models are firmware-time configuration. A Home Assistant add-on cannot automatically inject `Kuule Kratt` into arbitrary already-flashed ESP32 devices. The preferred user-facing validation path is a ready firmware image for the supported board(s), starting with ESP32-S3-Korvo-2; the YAML/manifest path remains the reproducible developer path.

Implemented correction:

- `kratt-neurokone-tts/` now contains a local Wyoming wrapper around TartuNLP `text-to-speech-worker` instead of the external API wrapper.
- `kratt build-esphome-firmware` builds/copies a prebuilt ESPHome firmware artifact.

See `home-assistant/README.md` for the user-facing install path.

## Static validation

```bash
ruby -e 'require "yaml"; ARGV.each { |p| YAML.load_file(p); puts "yaml-ok #{p}" }' \
  repository.yaml \
  kratt-kiirkirjutaja-stt/config.yaml \
  kratt-neurokone-tts/config.yaml \
  docker/kratt-stack.yml

python3 -m py_compile \
  kratt-kiirkirjutaja-stt/main.py \
  kratt-kiirkirjutaja-stt/asr.py \
  kratt-kiirkirjutaja-stt/wyoming_handler.py \
  kratt-neurokone-tts/wyoming_tartunlp_local.py

bash -n \
  kratt-kiirkirjutaja-stt/run.sh \
  kratt-neurokone-tts/run.sh \
  scripts/deployment/build_esphome_firmware.sh \
  cli/commands/kratt-build-esphome-firmware

docker compose -f docker/kratt-stack.yml --profile ha --profile stt --profile tartunlp --profile piper config

docker manifest inspect ghcr.io/tartunlp/text-to-speech-worker:3.1.0
```

Result: passed for YAML parsing, Python syntax, shell syntax, Docker Compose config, and TartuNLP image manifest inspection. The TartuNLP upstream image manifest currently exposes `linux/amd64` only.

## Docker build/start smoke test

Earlier 2026-05-12 local smoke tests covered the old STT image and old API-based TTS wrapper. After the 2026-05-15/16 correction:

- STT add-on still needs a final HA Supervisor install/start check.
- Local TartuNLP TTS add-on syntax/config is validated, and the upstream image manifest resolves for `linux/amd64`.
- A local `docker build --platform linux/amd64 -t kratt-tartunlp-tts-addon:dev kratt-neurokone-tts` was started, but the upstream base image contains a ~7.26GB layer and did not finish within the local timeout. Treat runtime TTS add-on build/start as **not yet validated**.

## ESPHome validation

2026-05-16 firmware artifact build:

```bash
./scripts/setup/install_esphome.sh
./cli/kratt build-esphome-firmware --model v16c --cutoff 0.996
```

Result: compile succeeded and wrote:

```text
output/firmware/esphome/kratt-korvo2-v16c-20260516T142909Z/
├── firmware.bin
├── firmware.factory.bin
├── firmware.ota.bin
├── kratt-model-manifest.json
├── README.md
├── SHA256SUMS.txt
└── source-config.yaml
```

Factory image SHA-256: `7447d7e07c0c09ec869b092e223dc0b61f2786bfb8f28a6f52fcb32da1242d0d`.

Accepted warnings: GPIO45 strapping pin; captive portal enabled without Wi-Fi AP.

```bash
.venv-esphome/bin/esphome config hardware/esp32/esphome/voice-satellite-esp32-s3-korvo2.yaml
.venv-esphome/bin/esphome config hardware/esp32/esphome/voice-satellite-esp32-s3-korvo2-demo.yaml
.venv-esphome/bin/esphome config hardware/esp32/esphome/voice-satellite-esp32-s3.yaml
```

Result: all three configs were valid after changing the Kratt model manifest references from absolute `/Users/...` paths to relative `models/kratt.json`.

Warnings observed and accepted:

- ESPHome warns that GPIO45 is a strapping pin on Korvo-2.
- ESPHome warns that captive portal is enabled without a Wi-Fi AP block.

## Not yet validated

- Installation through Home Assistant Supervisor UI from the public GitHub URL. This requires the repository/branch to be publicly reachable with the new add-on folders committed.
- Home Assistant Supervisor build/start of the corrected local TartuNLP TTS add-on (`amd64`).
- ARM/aarch64 TTS image support; upstream TartuNLP worker image currently exposes `amd64` only.
- Full end-to-end Assist pipeline with real HA UI, ESPHome wake trigger, STT, intent, and local TartuNLP TTS.
- Flashing the generated `firmware.factory.bin` to an ESP32-S3-Korvo-2 and confirming boot/wake logs.
