# Home Assistant packaging validation

Validation performed in the working tree on 2026-05-12.

## Static validation

```bash
ruby -e 'require "yaml"; ARGV.each { |p| YAML.load_file(p); puts "yaml-ok #{p}" }' \
  repository.yaml \
  kratt-kiirkirjutaja-stt/config.yaml \
  kratt-kiirkirjutaja-stt/build.yaml \
  kratt-neurokone-tts/config.yaml \
  kratt-neurokone-tts/build.yaml \
  docker/kratt-stack.yml

python3 -m py_compile \
  kratt-kiirkirjutaja-stt/main.py \
  kratt-kiirkirjutaja-stt/asr.py \
  kratt-kiirkirjutaja-stt/wyoming_handler.py \
  kratt-neurokone-tts/wyoming_neurokone.py

shellcheck \
  kratt-kiirkirjutaja-stt/run.sh \
  kratt-neurokone-tts/run.sh \
  scripts/setup/install_esphome.sh \
  cli/commands/kratt-prepare-esphome-model \
  cli/commands/kratt-flash

docker compose -f docker/kratt-stack.yml --profile ha --profile stt --profile neurokone --profile piper config
```

Result: passed.

## Docker build/start smoke test

Docker daemon was started temporarily with Colima for local validation and stopped afterwards.

```bash
docker build -t kratt-kiirkirjutaja-stt-addon:dev kratt-kiirkirjutaja-stt
docker build -t kratt-neurokone-tts-addon:dev kratt-neurokone-tts
```

Result: both images built successfully for the local `linux/arm64` environment.

Startup smoke:

- STT add-on downloaded `encoder.int8.onnx`, `decoder.int8.onnx`, `joiner.int8.onnx`, and `tokens.txt` into `/data/models/sherpa-int8`, loaded the INT8 model, and logged `Starting Wyoming server on tcp://0.0.0.0:10300`.
- TTS add-on started and logged `Starting Wyoming Neurokõne TTS server on tcp://0.0.0.0:10301`.

## ESPHome validation

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
- Cross-architecture builds for `amd64`; local validation was `linux/arm64`.
- Full end-to-end Assist pipeline with real HA UI, ESPHome wake trigger, STT, intent, and TTS.
