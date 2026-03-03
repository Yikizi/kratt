#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/Users/mattias/kratt"
VENV_DIR="${ROOT_DIR}/wake-word/.venv-microwakeword"

PYTHON_BIN=""
for cand in python3.10 python3.11 python3.12; do
  if command -v "${cand}" >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v "${cand}")"
    break
  fi
done

if [[ -z "${PYTHON_BIN}" ]]; then
  echo "No suitable python found. Need python3.10+." >&2
  exit 2
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip wheel setuptools

# microWakeWord depends on pymicro-features; on macOS this often needs a fork that
# relaxes build constraints. Install the fork first so the dependency is satisfied.
python -m pip install "git+https://github.com/puddly/pymicro-features@puddly/minimum-cpp-version"

# Install microWakeWord from our vendored external repo.
python -m pip install -e "${ROOT_DIR}/external-repos/microWakeWord"

# Plotting/reporting dependencies for experiment analysis.
python -m pip install matplotlib pandas

python -c "import microwakeword; print('microwakeword import OK')"
