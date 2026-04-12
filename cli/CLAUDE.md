# cli/

Project CLI tool — `kratt <command>` gateway for common development tasks.

## Usage

```bash
./cli/kratt <command> [args...]
```

## Commands

| Command | Purpose |
|---------|---------|
| `kratt live` | Run live mic test with a model |
| `kratt compare` | Side-by-side model comparison |
| `kratt flash` | Flash ESP32 firmware |
| `kratt hpc` | Submit/monitor HPC training jobs |
| `kratt models` | List trained models with metadata |
| `kratt rec` | Record wake word samples |
| `kratt train` | Local training wrapper |
| `kratt tts` | Generate TTS samples |

## Adding commands

Add a new executable script in `cli/commands/kratt-<name>`.
The gateway auto-discovers commands by filename.
