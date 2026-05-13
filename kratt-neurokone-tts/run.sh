#!/usr/bin/env bash
set -euo pipefail

OPTIONS_FILE="/data/options.json"

read_option() {
  local key="$1"
  local default_value="$2"
  python3 - "$OPTIONS_FILE" "$key" "$default_value" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
key = sys.argv[2]
default = sys.argv[3]
value = default
if path.exists():
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        value = data.get(key, default)
    except Exception:
        value = default
if isinstance(value, bool):
    print("true" if value else "false")
else:
    print(value)
PY
}

VOICE="$(read_option voice "${NEUROKONE_VOICE:-mari}")"
SPEED="$(read_option speed "${NEUROKONE_SPEED:-1.0}")"
DEBUG_LOGGING="$(read_option debug_logging "${DEBUG_LOGGING:-false}")"

args=(
  python /opt/neurokone/wyoming_neurokone.py
  --uri tcp://0.0.0.0:10301
  --voice "$VOICE"
  --speed "$SPEED"
)

if [[ "$DEBUG_LOGGING" == "true" ]]; then
  args+=(--debug)
fi

exec "${args[@]}"
