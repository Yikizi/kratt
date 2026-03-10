#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 /absolute/path/to/model.tflite /absolute/path/to/output.json" >&2
  exit 2
fi

TFLITE="$1"
OUT_JSON="$2"

if [[ ! -f "${TFLITE}" ]]; then
  echo "TFLite not found: ${TFLITE}" >&2
  exit 2
fi

OUT_DIR="$(cd "$(dirname "${OUT_JSON}")" && pwd)"
OUT_JSON_BASENAME="$(basename "${OUT_JSON}")"

mkdir -p "${OUT_DIR}"

cat > "${OUT_DIR}/${OUT_JSON_BASENAME}" <<EOF
{
  "type": "micro",
  "wake_word": "kratt",
  "author": "Mattias",
  "trained_languages": ["et"],
  "model": "${TFLITE}",
  "version": 2,
  "micro": {
    "probability_cutoff": 0.97,
    "sliding_window_size": 5,
    "feature_step_size": 10,
    "tensor_arena_size": 22860,
    "minimum_esphome_version": "2024.7"
  }
}
EOF

echo "Wrote model manifest: ${OUT_DIR}/${OUT_JSON_BASENAME}"

