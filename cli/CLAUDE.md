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
| `kratt hpc` | Submit/monitor HPC training jobs |
| `kratt label` | Label or inspect captured clips |
| `kratt live` | Run live mic test with one or more models |
| `kratt models` | List trained models with metadata |
| `kratt prepare-negative-splits` | Materialize scaled negative train/dev/eval splits (optional/future-work) |
| `kratt rec` | Record wake word samples |
| `kratt thesis-dashboard` | Thesis automation/dashboard helper |
| `kratt train` | Training wrapper / HPC submit front-end |
| `kratt tts` | Generate TTS samples |
| `kratt user-test` | Record labelled 10-minute user-test trials (`trials.jsonl` + WAVs) |

## Adding commands

Add a new executable script in `cli/commands/kratt-<name>`.
The gateway auto-discovers commands by filename.

Every new workflow script should have a CLI wrapper unless it is intentionally internal.
