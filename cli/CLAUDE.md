# cli/

Project CLI tool — `kratt <command>` gateway for common development tasks.

## Usage

```bash
./cli/kratt <command> [args...]
```

## Commands (current high-signal set)

| Command | Purpose |
|---------|---------|
| `kratt android` | Build/install/pull/analyze Android false-trigger logger |
| `kratt benchmark` | Benchmark helpers |
| `kratt bg` | Background / field-run helpers |
| `kratt compare` | Side-by-side held-out model comparison |
| `kratt demo` | Run demo pipeline |
| `kratt det` | DET / threshold curve helpers |
| `kratt faph-log` | FAPH log tooling |
| `kratt flash` | Flash ESP32 firmware / model config |
| `kratt prepare-esphome-model` | Copy selected model into ESPHome manifest without flashing |
| `kratt hpc` | Submit/monitor HPC training jobs |
| `kratt label` | Label or inspect captured clips |
| `kratt live` | Run live mic test with one or more models |
| `kratt models` | List trained models with metadata |
| `kratt prepare-negative-splits` | Materialize scaled negative train/dev/eval splits (optional/future-work) |
| `kratt rec` | Record wake word samples |
| `kratt thesis-dashboard` | Thesis automation/dashboard helper |
| `kratt thesis-lint` | Run terminology, claim, style, scope, and formal thesis lint checks |
| `kratt thesis-watch` | Watch LaTeX thesis sources and auto-rebuild/open PDF |
| `kratt terms` | Check thesis terminology against Ekilex/Sõnaveeb data |
| `kratt train` | Training wrapper / HPC submit front-end |
| `kratt tts` | Generate TTS samples |
| `kratt user-test` | Record labelled 10-minute user-test trials (`trials.jsonl` + WAVs) |
| `kratt user-test-fixtures` | Generate synthetic WAV fixtures for user-test smoke/replay |
| `kratt validate-user-test` | Validate user-test session JSONL/WAV integrity before analysis |
| `kratt replay-user-test` | Replay labelled user-test WAVs through frozen wake-word models |
| `kratt summarize-user-test` | Aggregate replay outputs into thesis-ready recall/FPR tables |

## Adding commands

Add a new executable script in `cli/commands/kratt-<name>`.
The gateway auto-discovers commands by filename.

Every new workflow script should have a CLI wrapper unless it is intentionally internal.
