# home-assistant/

Home Assistant voice pipeline integration — planned but not yet implemented.

## Status

Blueprint only. The actual wake word runs via ESPHome voice satellite
(see `hardware/esp32/esphome/`) which connects to HA via Wyoming protocol.

## Plan

When implemented, this will contain:
- HA Add-on packaging (Dockerfile, config.yaml, run.sh)
- Wyoming protocol server wrapping the wake word model
- Example voice pipeline configurations

## Current integration path

```
ESP32-S3 (microWakeWord) → Wyoming TCP:10400 → Home Assistant Voice Pipeline
                                                  ↓
                                            Kiirkirjutaja STT → Intent → Action
```

The add-on will be needed when distributing to users who don't run ESPHome.
For now, the ESPHome YAML in `hardware/esp32/esphome/` is the deployment method.
