#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-esphome"

# ESPHome currently requires Python < 3.14.
# Prefer a Homebrew / system install that satisfies this, falling back sensibly.
PYTHON_BIN=""
for cand in python3.13 python3.12 python3.11 python3.10; do
  if command -v "${cand}" >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v "${cand}")"
    break
  fi
done

if [[ -z "${PYTHON_BIN}" ]]; then
  echo "No suitable Python found (need python3.11+). Install Python 3.12 or 3.13 and retry." >&2
  exit 2
fi

rm -rf "${VENV_DIR}"
"${PYTHON_BIN}" -m venv "${VENV_DIR}"
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip
python -m pip install "esphome>=2026.1.0"

cat <<'EOF'
ESPHome installed in .venv-esphome.

Usage:
  source /Users/mattias/kratt/.venv-esphome/bin/activate
  esphome version
EOF
