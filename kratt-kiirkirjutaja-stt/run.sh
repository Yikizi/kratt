#!/usr/bin/env bash
set -euo pipefail

OPTIONS_FILE="/data/options.json"
MODEL_DIR="/data/models/sherpa-int8"
DEFAULT_MODEL_BASE_URL="${MODEL_BASE_URL:-https://huggingface.co/TalTechNLP/streaming-zipformer.et-en/resolve/main}"

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

MODEL_BASE_URL="$(read_option model_base_url "$DEFAULT_MODEL_BASE_URL")"
DEBUG_LOGGING="$(read_option debug_logging false)"

mkdir -p "$MODEL_DIR"

for file in encoder.int8.onnx decoder.int8.onnx joiner.int8.onnx tokens.txt; do
  if [[ ! -s "$MODEL_DIR/$file" ]]; then
    echo "Downloading Kiirkirjutaja model file: $file"
    tmp_file="$MODEL_DIR/$file.tmp"
    rm -f "$tmp_file"
    curl -fL --retry 5 --retry-delay 2 \
      "$MODEL_BASE_URL/$file" \
      -o "$tmp_file"
    mv "$tmp_file" "$MODEL_DIR/$file"
  fi
done

if [[ "$DEBUG_LOGGING" == "true" ]]; then
  export PYTHONASYNCIODEBUG=1
fi

exec python /opt/kiirkirjutaja/main.py \
  --wyoming-uri tcp://0.0.0.0:10300 \
  --model-dir "$MODEL_DIR"
