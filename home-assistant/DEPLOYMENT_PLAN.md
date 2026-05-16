# Kratt Home Assistant deployment plan — corrected packaging story

Last updated: 2026-05-15

## 1. Wake word: ship a ready firmware image

Best user-facing path for `Kuule Kratt` wake-word installation is **not** “ask the user to paste YAML”. The wake word runs inside ESPHome/microWakeWord firmware on the ESP32-S3 voice satellite, so the practical low-friction path is:

1. keep the YAML/package path for developers and reproducibility;
2. build a ready firmware image for the supported board(s), starting with ESP32-S3-Korvo-2;
3. publish the firmware artifact with exact model/threshold provenance;
4. let users flash that image via ESPHome / ESPHome Web / `esptool`, rather than hand-editing the wake-word model block.

Validation artifact should record:

- board target, e.g. ESP32-S3-Korvo-2;
- source config, e.g. `hardware/esp32/esphome/voice-satellite-esp32-s3-korvo2.yaml`;
- wake-word model, e.g. `wake-word/models/kuule-kratt-v16c/kuule_kratt_v16c.json`;
- threshold/cutoff in the manifest;
- commit hash;
- produced firmware binary path/checksum;
- flash method and boot log.

This is more honest than claiming a Home Assistant add-on can automatically make a microWakeWord model appear on arbitrary already-flashed ESPHome devices. A future server-side wake-word add-on could appear as a Home Assistant wake-word engine, but that is a different architecture and not the current ESP32-S3/microWakeWord path.

## 2. TTS: use local TartuNLP text-to-speech-worker, not the public Neurokõne API

The current `kratt-neurokone-tts` add-on wraps the external API endpoint. That should not be the public/default validation path.

The project already contains a local TartuNLP TTS checkout and model assets used by the demo path:

- Upstream repository: <https://github.com/TartuNLP/text-to-speech-worker>
- Local checkout: `tools/text-to-speech-worker/`
- Checked version: `v3.1.0`, commit `14d47bf9af4e562829ccafcc757d93abb2a6412f`
- License in upstream checkout: MIT, copyright University of Tartu
- Model release used locally: <https://github.com/TartuNLP/text-to-speech-worker/releases/tag/v3.1.0>
- Local model files:
  - `tools/text-to-speech-worker/models/multispeaker.zip`
  - `tools/text-to-speech-worker/models/multispeaker/config.yaml`
  - `tools/text-to-speech-worker/models/multispeaker/model_weights.hdf5`
- Demo HTTP wrapper: `tools/tts-server/server.py` (`POST /synthesize`, `GET /speakers`)

Implemented HA packaging direction:

1. `kratt-neurokone-tts/` now contains a local Wyoming TTS wrapper (`wyoming_tartunlp_local.py`) that loads `tts_worker.synthesizer.Synthesizer` directly, analogous to `tools/tts-server/server.py`.
2. The add-on is based on TartuNLP's published container: `ghcr.io/tartunlp/text-to-speech-worker:3.1.0`.
3. `run.sh` downloads `multispeaker.zip` from the TartuNLP GitHub release on first start into `/data/models` instead of bundling large model weights in this repository/image.
4. TartuNLP / University of Tartu attribution is included in the add-on README and Wyoming `Info`.

Validation caveat: the upstream published container is currently `amd64`; ARM/aarch64 support needs separate validation before enabling Raspberry Pi add-on installs.

Important distinction:

- **Allowed/defensible local path:** user runs the TartuNLP model on their own machine/container; synthesis text stays local after model download.
- **Problematic path:** Kratt sends synthesis requests to the public Neurokõne API without explicit integration permission.

## 3. Thesis/demo wording

Defensible wording:

> The prototype uses local Estonian STT and a local TartuNLP neural TTS model packaged or wrapped for the demo environment. Wake-word detection runs on ESPHome firmware using a prebuilt ESP32-S3 firmware image containing the `v16c` microWakeWord model.

Avoid:

- “TTS is local” if using the API wrapper;
- “the HA add-on automatically installs the wake word” for ESPHome microWakeWord;
- “zero-config install” until prebuilt firmware artifacts and a tested flash path exist.
