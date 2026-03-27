#!/usr/bin/env bash
# Quick live test for wake word models
# Usage: ./live_test.sh v7        (threshold 0.9)
#        ./live_test.sh v6 0.85   (custom threshold)
#        ./live_test.sh            (latest model)

set -euo pipefail
cd "$(dirname "$0")/.."

VERSION="${1:-}"
THRESHOLD="${2:-0.9}"

if [[ -z "$VERSION" ]]; then
  # Find latest model
  VERSION=$(ls -d models/kuule-kratt-v* 2>/dev/null | sort -V | tail -1 | grep -o 'v[0-9]*')
  echo "Using latest: $VERSION"
fi

MODEL="models/kuule-kratt-${VERSION}/kuule_kratt_${VERSION}.tflite"

if [[ ! -f "$MODEL" ]]; then
  echo "Model not found: $MODEL"
  echo "Available:"
  ls -d models/kuule-kratt-v*/kuule_kratt_v*.tflite 2>/dev/null | sed 's/.*kuule-kratt-/  /' | sed 's/\/.*//'
  exit 1
fi

echo "Model: $MODEL ($(du -h "$MODEL" | cut -f1))"
echo "Threshold: $THRESHOLD"
echo ""

exec .venv-microwakeword/bin/python evaluation/live_test_tflite.py \
  --model "$MODEL" \
  --threshold "$THRESHOLD" \
  --name "kuule kratt $VERSION"
