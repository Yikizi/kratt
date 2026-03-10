#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 /absolute/path/to/config.yaml [/dev/cu.usbmodemXXXX]" >&2
  exit 2
fi

CFG="$1"
if [[ ! -f "${CFG}" ]]; then
  echo "Config not found: ${CFG}" >&2
  exit 2
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-esphome"

if [[ ! -x "${VENV_DIR}/bin/esphome" ]]; then
  echo "ESPHome venv not found at ${VENV_DIR}. Run:" >&2
  echo "  ${ROOT_DIR}/scripts/setup/install_esphome.sh" >&2
  exit 2
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

if [[ $# -eq 2 ]]; then
  DEVICE="$2"
  esphome run "${CFG}" --device "${DEVICE}"
else
  esphome run "${CFG}"
fi
