#!/bin/zsh
set -euo pipefail

ROOT_DIR="/Users/mattias/kratt"
WAKE_WORD_DIR="${ROOT_DIR}/wake-word"
PYTHON_BIN="${WAKE_WORD_DIR}/.venv-microwakeword/bin/python"
LOG_DIR="${ROOT_DIR}/output/demo-logs"

mkdir -p "${LOG_DIR}"

timestamp="$(date +%Y%m%d_%H%M%S)"
log_file="${LOG_DIR}/live_test_${timestamp}.log"
latest_link="${LOG_DIR}/live_test_latest.log"

model="models/kuule-kratt-v6/kuule_kratt_v6.tflite"
threshold="0.97"

if [[ $# -gt 0 ]]; then
  extra_args=("$@")
else
  extra_args=(--model "${model}" --threshold "${threshold}")
fi

echo "Logging live test output to ${log_file}"
echo "Tail with: tail -f ${log_file}"
echo

ln -sfn "${log_file}" "${latest_link}"

cd "${WAKE_WORD_DIR}"
PYTHONUNBUFFERED=1 "${PYTHON_BIN}" evaluation/live_test_tflite.py "${extra_args[@]}" 2>&1 | tee -a "${log_file}"
