#!/usr/bin/env bash
set -euo pipefail

# Tail ESPHome logs for the Korvo-2 voice satellite.
#
# Usage:
#   ./scripts/deployment/korvo2_logs.sh                # uses kratt-korvo2.local
#   ./scripts/deployment/korvo2_logs.sh 192.168.0.131  # explicit device
#
# You can also set:
#   KORVO2_DEVICE=192.168.0.131 ./scripts/deployment/korvo2_logs.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-esphome"
CFG="${ROOT_DIR}/hardware/esp32/esphome/voice-satellite-esp32-s3-korvo2.yaml"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "Usage: $0 [device]" >&2
  echo "  device: optional, e.g. 192.168.0.131 (default: kratt-korvo2.local)" >&2
  exit 0
fi

if [[ $# -gt 1 ]]; then
  echo "Usage: $0 [device]" >&2
  exit 2
fi

if [[ ! -f "${CFG}" ]]; then
  echo "Config not found: ${CFG}" >&2
  exit 2
fi

if [[ ! -x "${VENV_DIR}/bin/esphome" ]]; then
  echo "ESPHome venv not found at ${VENV_DIR}. Run:" >&2
  echo "  ${ROOT_DIR}/scripts/setup/install_esphome.sh" >&2
  exit 2
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

DEVICE="${1:-${KORVO2_DEVICE:-kratt-korvo2.local}}"
exec esphome logs "${CFG}" --device "${DEVICE}"
