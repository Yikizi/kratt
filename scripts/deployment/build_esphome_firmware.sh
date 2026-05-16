#!/usr/bin/env bash
# Build a pre-flashable ESPHome firmware artifact for the Kratt wake-word satellite.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONFIG="${ROOT}/hardware/esp32/esphome/voice-satellite-esp32-s3-korvo2.yaml"
MODEL="v16c"
CUTOFF="0.996"
OUT_ROOT="${ROOT}/output/firmware/esphome"

usage() {
  cat <<'EOF'
Usage: build_esphome_firmware.sh [--config PATH] [--model v16c] [--cutoff 0.996] [--out-dir DIR]

Builds ESPHome firmware and copies firmware binaries plus provenance into output/firmware/esphome/.
Default target is ESP32-S3-Korvo-2 with Kuule Kratt v16c.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) CONFIG="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --cutoff) CUTOFF="$2"; shift 2 ;;
    --out-dir) OUT_ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ ! -f "$CONFIG" ]]; then
  echo "ESPHome config not found: $CONFIG" >&2
  exit 1
fi
if [[ ! -x "${ROOT}/.venv-esphome/bin/esphome" ]]; then
  echo "ESPHome CLI not found. Run: ./scripts/setup/install_esphome.sh" >&2
  exit 1
fi

"${ROOT}/cli/kratt" prepare-esphome-model "$MODEL" --cutoff "$CUTOFF"
"${ROOT}/.venv-esphome/bin/esphome" compile "$CONFIG"

DEVICE_NAME="$(python3 - "$CONFIG" <<'PY'
import re
import sys
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding="utf-8")
match = re.search(r"^\s*name:\s*[\"']?([^\"'\n]+)", text, re.M)
print(match.group(1).strip() if match else "kratt-device")
PY
)"
BUILD_DIR="$(dirname "$CONFIG")/.esphome/build/${DEVICE_NAME}/.pioenvs/${DEVICE_NAME}"
if [[ ! -d "$BUILD_DIR" ]]; then
  # Fallback for configs that use a sanitized PlatformIO env name.
  BUILD_DIR="$(find "$(dirname "$CONFIG")/.esphome/build" -path '*/.pioenvs/*' -type d | head -1 || true)"
fi
if [[ -z "$BUILD_DIR" || ! -d "$BUILD_DIR" ]]; then
  echo "Could not locate ESPHome build output" >&2
  exit 1
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="${OUT_ROOT}/${DEVICE_NAME}-${MODEL}-${STAMP}"
mkdir -p "$OUT_DIR"

copied=0
for f in firmware.bin firmware.factory.bin firmware.ota.bin; do
  if [[ -f "$BUILD_DIR/$f" ]]; then
    cp "$BUILD_DIR/$f" "$OUT_DIR/"
    copied=$((copied + 1))
  fi
done
if [[ "$copied" -eq 0 ]]; then
  echo "No firmware*.bin files found in $BUILD_DIR" >&2
  exit 1
fi

cp "$CONFIG" "$OUT_DIR/source-config.yaml"
cp "${ROOT}/hardware/esp32/esphome/models/kratt.json" "$OUT_DIR/kratt-model-manifest.json"
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum "$OUT_DIR"/* > "$OUT_DIR/SHA256SUMS.txt"
else
  shasum -a 256 "$OUT_DIR"/* > "$OUT_DIR/SHA256SUMS.txt"
fi
GIT_COMMIT="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo unknown)"

cat > "$OUT_DIR/README.md" <<EOF
# Kratt ESPHome firmware artifact

- Built: ${STAMP}
- Git commit: ${GIT_COMMIT}
- Device/config name: ${DEVICE_NAME}
- Source config: ${CONFIG}
- Wake-word model: ${MODEL}
- Probability cutoff: ${CUTOFF}

Files:

- \`firmware.factory.bin\` if present: full serial/web flash image for initial install.
- \`firmware.bin\` / \`firmware.ota.bin\` if present: ESPHome update artifacts.
- \`source-config.yaml\`: config used for this build.
- \`kratt-model-manifest.json\`: local microWakeWord manifest used for this build.
- \`SHA256SUMS.txt\`: checksums.

Flash path for normal users should point to the factory image where available, not manual wake-word YAML editing.
EOF

printf 'Firmware artifact written to: %s\n' "$OUT_DIR"
ls -lh "$OUT_DIR"
