# Research: Home Assistant add-on packaging + Wyoming examples + ESPHome micro_wake_word models

## Summary
Build a minimal Wyoming wake-word add-on as a normal Home Assistant add-on repository: root `repository.yaml`, one add-on folder with `config.yaml`, `Dockerfile`, and executable `run.sh`. For a Wyoming TCP service, follow the official voice add-ons: `startup: services`, `boot: auto`, `init: false`, `discovery: [wyoming]`, no ingress, and a declared Wyoming port such as `10400/tcp`. ESPHome `micro_wake_word` custom models are installed by adding a built-in model name or a JSON manifest URL/path to `micro_wake_word.models` and recompiling/flashing the device firmware.

## Findings
1. **Repository shape is small.** A Home Assistant add-on repository is a Git repository with root metadata (`repository.yaml`) and one folder per add-on; each add-on needs add-on config plus build files. Keep root `repository.yaml` with `name`, `url`, and `maintainer`; keep each add-on folder self-contained. [HA add-on repository docs](https://developers.home-assistant.io/docs/add-ons/repository/) [HA add-on tutorial](https://developers.home-assistant.io/docs/add-ons/tutorial/)
2. **Minimal `config.yaml` should declare identity, supported architectures, lifecycle, discovery, ports, options, and schema.** The add-on configuration reference documents keys such as `name`, `version`, `slug`, `description`, `url`, `arch`, `startup`, `boot`, `init`, `ports`, `ports_description`, `options`, and `schema`. [HA add-on configuration docs](https://developers.home-assistant.io/docs/add-ons/configuration/)
3. **For a Wyoming wake-word server, copy the official voice add-on pattern.** Official Home Assistant add-ons for Piper, Whisper, and openWakeWord are concrete examples of Wyoming services: they expose a TCP Wyoming protocol port, set Wyoming discovery, and are service-style background add-ons rather than web-ingress add-ons. [openWakeWord add-on](https://github.com/home-assistant/addons/tree/master/openwakeword) [Whisper add-on](https://github.com/home-assistant/addons/tree/master/whisper) [Piper add-on](https://github.com/home-assistant/addons/tree/master/piper) [Wyoming integration](https://www.home-assistant.io/integrations/wyoming/)
4. **Use `startup: services`, `boot: auto`, `init: false`, and no ingress.** Voice/Wyoming add-ons are long-running services that should be available for Home Assistant voice pipelines; they do not need Supervisor ingress because the UI is not a web app. `init: false` is the common Home Assistant add-on/base-image pattern for these service containers. [HA config reference](https://developers.home-assistant.io/docs/add-ons/configuration/) [openWakeWord example](https://github.com/home-assistant/addons/tree/master/openwakeword)
5. **Declare the container Wyoming port; avoid unnecessary host exposure by default.** Official Wyoming add-ons use well-known internal ports: Piper `10200/tcp`, Whisper `10300/tcp`, openWakeWord `10400/tcp`. Use `ports_description` so the Supervisor UI labels the port. A wake-word add-on should usually listen on `tcp://0.0.0.0:10400` inside the container and declare `10400/tcp`; set the default host mapping to `null` unless users need LAN access. [Piper add-on](https://github.com/home-assistant/addons/tree/master/piper) [Whisper add-on](https://github.com/home-assistant/addons/tree/master/whisper) [openWakeWord add-on](https://github.com/home-assistant/addons/tree/master/openwakeword)
6. **Architecture strings are Home Assistant Supervisor architecture names.** Use only architectures you build and test: `aarch64` for Raspberry Pi 5 / 64-bit ARM, `amd64` for x86_64, optionally `armv7`; avoid advertising `armhf`/`i386` unless dependencies are proven. Docker build inputs normally come from `ARG BUILD_FROM` plus `build.yaml` per-arch base images, or from an `image: .../{arch}...` published-image template. [HA add-on build docs](https://developers.home-assistant.io/docs/add-ons/configuration/#build) [HA add-on configuration docs](https://developers.home-assistant.io/docs/add-ons/configuration/)
7. **Options must be mirrored by `schema`.** Keep add-on options minimal and validate every user-editable option. For a wake-word server this is likely `model`, `threshold`, optional `trigger_level`, optional `debug_logging`, and maybe `uri`/`port` only if you truly need user configurability. [HA add-on configuration docs](https://developers.home-assistant.io/docs/add-ons/configuration/)
8. **ESPHome `micro_wake_word` accepts built-in names and external manifest files.** Users can install built-ins such as `hey_jarvis` by adding `- model: hey_jarvis` under `micro_wake_word.models`. Custom models are referenced by a local JSON manifest path, an HTTPS raw manifest URL, or ESPHome's GitHub shorthand such as `github://owner/repo/path/to/model.json@ref`; the manifest points to the `.tflite` model file. [ESPHome micro_wake_word docs](https://esphome.io/components/micro_wake_word/) [micro-wake-word models repo](https://github.com/esphome/micro-wake-word-models) [hey_jarvis manifest](https://github.com/esphome/micro-wake-word-models/blob/main/models/v2/hey_jarvis.json)
9. **Do not give users GitHub `blob` URLs for ESPHome manifests.** Use raw HTTPS (`https://raw.githubusercontent.com/.../model.json`) or `github://...@ref`; keep the `.json` manifest and referenced `.tflite` together so relative paths resolve cleanly. The upstream `hey_jarvis.json` is the concrete format to mirror. [hey_jarvis manifest](https://github.com/esphome/micro-wake-word-models/blob/main/models/v2/hey_jarvis.json) [ESPHome micro_wake_word docs](https://esphome.io/components/micro_wake_word/)

## Implementation checklist

### Home Assistant add-on repository
- [ ] Add root `repository.yaml`:
  ```yaml
  name: Kratt add-ons
  url: https://github.com/<owner>/<repo>
  maintainer: Mattias <email-or-github>
  ```
- [ ] Create one add-on folder, e.g. `kratt-wyoming/`, containing at minimum:
  - `config.yaml`
  - `Dockerfile`
  - `run.sh` with executable bit
  - optional but recommended: `README.md`, `DOCS.md`, `CHANGELOG.md`, `build.yaml`

### Minimal `config.yaml` for a Wyoming wake-word add-on
```yaml
name: Kratt Wyoming Wake Word
version: 0.1.0
slug: kratt_wyoming_wake_word
description: Wyoming wake-word server for Kuule Kratt
url: https://github.com/<owner>/<repo>/tree/main/kratt-wyoming
arch:
  - aarch64
  - amd64
  - armv7
startup: services
boot: auto
init: false
discovery:
  - wyoming
ports:
  10400/tcp: null
ports_description:
  10400/tcp: Wyoming protocol
options:
  model: kuule_kratt
  threshold: 0.5
  debug_logging: false
schema:
  model: str
  threshold: float(0,1)
  debug_logging: bool
```
Notes: omit `ingress`; do not set `panel_icon`, `ingress_port`, or web UI keys unless a web UI is added. Add `audio: true`, device mappings, or `host_network: true` only if the add-on actually captures audio locally; a pure Wyoming server usually only needs TCP.

### `Dockerfile` / `run.sh` pattern
- [ ] Use Home Assistant base images and `ARG BUILD_FROM` so the builder can select the right architecture.
- [ ] Keep the process in the foreground and `exec` it from `run.sh`.

```dockerfile
ARG BUILD_FROM
FROM ${BUILD_FROM}

COPY run.sh /run.sh
RUN chmod a+x /run.sh

CMD ["/run.sh"]
```

```bash
#!/usr/bin/with-contenv bashio
set -euo pipefail

MODEL="$(bashio::config 'model')"
THRESHOLD="$(bashio::config 'threshold')"

exec kratt-wyoming \
  --uri 'tcp://0.0.0.0:10400' \
  --model "${MODEL}" \
  --threshold "${THRESHOLD}"
```

### Architecture/build mapping
- [ ] Start with `aarch64` and `amd64`; add `armv7` only if dependencies and performance are tested.
- [ ] Example `build.yaml` mapping:
  ```yaml
  build_from:
    aarch64: ghcr.io/home-assistant/aarch64-base:latest
    amd64: ghcr.io/home-assistant/amd64-base:latest
    armv7: ghcr.io/home-assistant/armv7-base:latest
  ```
- [ ] If publishing prebuilt images, use an `image:` template in `config.yaml` such as `ghcr.io/<owner>/{arch}-addon-kratt-wyoming` and publish matching per-arch tags/images.

### ESPHome `micro_wake_word` custom model install
- [ ] For built-in `hey_jarvis`:
  ```yaml
  micro_wake_word:
    models:
      - model: hey_jarvis
  ```
- [ ] For a custom Kuule Kratt model using GitHub shorthand:
  ```yaml
  micro_wake_word:
    models:
      - model: github://<owner>/<repo>/path/to/kuule_kratt.json@main
  ```
- [ ] For a raw HTTPS manifest:
  ```yaml
  micro_wake_word:
    models:
      - model: https://raw.githubusercontent.com/<owner>/<repo>/main/path/to/kuule_kratt.json
  ```
- [ ] Mirror the upstream manifest style: JSON manifest includes metadata, `type: micro`, wake-word name, `model` pointing to the `.tflite`, version, and a `micro` section with probability cutoff, sliding window, feature step size, tensor arena size, and minimum ESPHome version.
- [ ] Tell users that changing ESPHome wake words requires editing YAML and recompiling/flashing the ESPHome device; it is firmware configuration, not a Home Assistant add-on option.

## Sources
- Kept: Home Assistant add-on repository docs (https://developers.home-assistant.io/docs/add-ons/repository/) — root repository structure and metadata.
- Kept: Home Assistant add-on configuration docs (https://developers.home-assistant.io/docs/add-ons/configuration/) — authoritative config key reference for `config.yaml`, lifecycle, ports, options/schema, build settings.
- Kept: Home Assistant add-on tutorial (https://developers.home-assistant.io/docs/add-ons/tutorial/) — minimal `Dockerfile`/`run.sh` pattern.
- Kept: openWakeWord official add-on (https://github.com/home-assistant/addons/tree/master/openwakeword) — closest Wyoming wake-word service example.
- Kept: Piper official add-on (https://github.com/home-assistant/addons/tree/master/piper) — Wyoming TTS service pattern and port example.
- Kept: Whisper official add-on (https://github.com/home-assistant/addons/tree/master/whisper) — Wyoming STT service pattern and port example.
- Kept: Home Assistant Wyoming integration (https://www.home-assistant.io/integrations/wyoming/) — confirms Wyoming is the HA protocol/integration used by voice services.
- Kept: ESPHome micro_wake_word docs (https://esphome.io/components/micro_wake_word/) — authoritative ESPHome YAML model configuration.
- Kept: ESPHome micro-wake-word models repo (https://github.com/esphome/micro-wake-word-models) — canonical model manifests and built-ins.
- Kept: `hey_jarvis` manifest (https://github.com/esphome/micro-wake-word-models/blob/main/models/v2/hey_jarvis.json) — concrete custom/built-in manifest example.
- Dropped: Blog/forum posts about Wyoming and ESPHome voice devices — useful for anecdotes but less authoritative than official docs and repositories.
- Dropped: Generic Docker/Compose packaging guides — not specific to Supervisor add-on requirements.

## Gaps
- I could not live-verify line-level current contents from the linked GitHub files in this tool session; before implementation, open the three official add-on `config.yaml` files and copy their exact current conventions for `discovery`, `ports`, and `build.yaml` pinning.
- Confirm the exact ESPHome version targeted by the Kratt model and set `minimum_esphome_version` in the manifest accordingly.
