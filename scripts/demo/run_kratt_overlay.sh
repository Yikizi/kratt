#!/bin/zsh
set -euo pipefail

ROOT_DIR="/Users/mattias/kratt"
SCRIPT_PATH="${ROOT_DIR}/scripts/demo/kratt_detection_overlay.swift"

exec xcrun swift "${SCRIPT_PATH}" "$@"
