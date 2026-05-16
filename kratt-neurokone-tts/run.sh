#!/usr/bin/env bash
set -euo pipefail

OPTIONS_FILE="/data/options.json"
MODEL_ROOT="/data/models"
MODEL_DIR="$MODEL_ROOT/multispeaker"
DEFAULT_MODEL_ZIP_URL="https://github.com/TartuNLP/text-to-speech-worker/releases/download/v3.1.0/multispeaker.zip"
DEFAULT_VOICE="meelis"
DEFAULT_SPEED="1.0"
DEFAULT_MAX_INPUT_LENGTH="500"

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

MODEL_ZIP_URL="$(read_option model_zip_url "${TARTUNLP_MODEL_ZIP_URL:-$DEFAULT_MODEL_ZIP_URL}")"
VOICE="$(read_option voice "${TARTUNLP_TTS_VOICE:-$DEFAULT_VOICE}")"
SPEED="$(read_option speed "${TARTUNLP_TTS_SPEED:-$DEFAULT_SPEED}")"
MAX_INPUT_LENGTH="$(read_option max_input_length "${TARTUNLP_TTS_MAX_INPUT_LENGTH:-$DEFAULT_MAX_INPUT_LENGTH}")"
DEBUG_LOGGING="$(read_option debug_logging "${DEBUG_LOGGING:-false}")"

mkdir -p "$MODEL_ROOT" /data/nltk /data/cache /data/huggingface
export NLTK_DATA="/data/nltk"
export XDG_CACHE_HOME="/data/cache"
export HF_HOME="/data/huggingface"
export TRANSFORMERS_CACHE="/data/huggingface"

if [[ ! -s "$MODEL_DIR/model_weights.hdf5" || ! -s "$MODEL_DIR/config.yaml" ]]; then
  echo "Downloading local TartuNLP TTS model: $MODEL_ZIP_URL"
  python3 - "$MODEL_ZIP_URL" "$MODEL_ROOT" <<'PY'
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

url = sys.argv[1]
model_root = Path(sys.argv[2])
model_root.mkdir(parents=True, exist_ok=True)
with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
    tmp_path = Path(tmp.name)
try:
    with urllib.request.urlopen(url, timeout=120) as response, tmp_path.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
    with zipfile.ZipFile(tmp_path) as zf:
        zf.extractall(model_root)
finally:
    tmp_path.unlink(missing_ok=True)
PY
fi

python3 - <<'PY'
import nltk
for pkg in ("punkt", "punkt_tab"):
    try:
        nltk.download(pkg, download_dir="/data/nltk", quiet=True)
    except Exception:
        # Older NLTK versions may not have punkt_tab; punkt is enough there.
        pass
PY

args=(
  python3 /opt/kratt/wyoming_tartunlp_local.py
  --uri tcp://0.0.0.0:10301
  --model-config /app/config/config.yaml
  --model-name multispeaker
  --model-dir "$MODEL_DIR"
  --voice "$VOICE"
  --speed "$SPEED"
  --max-input-length "$MAX_INPUT_LENGTH"
)

if [[ "$DEBUG_LOGGING" == "true" ]]; then
  args+=(--debug)
fi

exec "${args[@]}"
