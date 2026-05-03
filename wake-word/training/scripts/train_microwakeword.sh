#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/kratt_paths.sh
source "${SCRIPT_DIR}/lib/kratt_paths.sh"

ROOT_DIR="$(kratt_project_root)"
PROCESSED_DIR="$(kratt_processed_dir)"
FEATURES_BASE_DIR="$(kratt_training_features_dir)"
RUNS_BASE_DIR="$(kratt_training_runs_dir)"
CONFIGS_DIR="$(kratt_training_configs_dir)"

POS_DIR="${PROCESSED_DIR}/positive_samples"
NEG_DIR="${PROCESSED_DIR}/negative_samples"

FEATURES_DIR="${FEATURES_BASE_DIR}/microwakeword"
TRAIN_DIR_BASE="${RUNS_BASE_DIR}/microwakeword-kratt"
CFG_PATH="${CONFIGS_DIR}/microwakeword-kratt.yaml"

mkdir -p "${CONFIGS_DIR}"
mkdir -p "${FEATURES_BASE_DIR}"
mkdir -p "${RUNS_BASE_DIR}"

TRAIN_DIR="${TRAIN_DIR_BASE}-$(date +%Y%m%d-%H%M%S)"
MMAP_STAMP_PATH="${FEATURES_DIR}/.dataset_stamp.txt"

if [[ ! -d "${POS_DIR}" ]]; then
  echo "Missing positive samples: ${POS_DIR}" >&2
  echo "Run: ${ROOT_DIR}/wake-word/.venv/bin/python ${ROOT_DIR}/wake-word/data/collection/prepare_processed_dataset.py" >&2
  exit 2
fi
if [[ ! -d "${NEG_DIR}" ]]; then
  echo "Missing negative samples: ${NEG_DIR}" >&2
  echo "Run: ${ROOT_DIR}/wake-word/.venv/bin/python ${ROOT_DIR}/wake-word/data/collection/download_negatives.py --output-dir ${PROCESSED_DIR}" >&2
  exit 2
fi

"${SCRIPT_DIR}/setup_microwakeword_env.sh"
# shellcheck disable=SC1091
source "${ROOT_DIR}/wake-word/.venv-microwakeword/bin/activate"

POS_COUNT="$(find "${POS_DIR}" -maxdepth 1 -name '*.wav' | wc -l | tr -d ' ')"
NEG_COUNT="$(find "${NEG_DIR}" -maxdepth 1 -name '*.wav' | wc -l | tr -d ' ')"
CLIP_DURATION_MS=2000
STAMP="pos_wavs=${POS_COUNT} neg_wavs=${NEG_COUNT} clip_ms=${CLIP_DURATION_MS}"

NEED_MMAPS=1
if [[ "${REGEN_MMAPS:-0}" != "1" ]]; then
  if [[ -f "${MMAP_STAMP_PATH}" ]] && [[ "$(cat "${MMAP_STAMP_PATH}")" == "${STAMP}" ]]; then
    if [[ -d "${FEATURES_DIR}/positive/training/wakeword_mmap" && -d "${FEATURES_DIR}/negative/training/negative_mmap" ]]; then
      NEED_MMAPS=0
    fi
  fi
fi

if [[ "${NEED_MMAPS}" == "0" ]]; then
  echo "Found existing mmaps under ${FEATURES_DIR} (stamp match); skipping generation."
else
  echo "Generating mmaps (stamp: ${STAMP})"
  rm -rf "${FEATURES_DIR}/positive" "${FEATURES_DIR}/negative"
  python "${ROOT_DIR}/wake-word/training/scripts/generate_microwakeword_mmaps.py" \
    --positive-dir "${POS_DIR}" \
    --negative-dir "${NEG_DIR}" \
    --out-dir "${FEATURES_DIR}" \
    --clip-duration-ms "${CLIP_DURATION_MS}"
  echo "${STAMP}" > "${MMAP_STAMP_PATH}"
fi

cat > "${CFG_PATH}" <<EOF
window_step_ms: 10
train_dir: "${TRAIN_DIR}"
features:
  - features_dir: "${FEATURES_DIR}/positive"
    sampling_weight: 2.0
    penalty_weight: 1.0
    truth: true
    truncation_strategy: truncate_start
    type: mmap
  - features_dir: "${FEATURES_DIR}/negative"
    sampling_weight: 10.0
    penalty_weight: 1.0
    truth: false
    truncation_strategy: random
    type: mmap
training_steps: [3000]
positive_class_weight: [1]
negative_class_weight: [20]
learning_rates: [0.001]
batch_size: 128
time_mask_max_size: [0]
time_mask_count: [0]
freq_mask_max_size: [0]
freq_mask_count: [0]
eval_step_interval: 250
clip_duration_ms: ${CLIP_DURATION_MS}
minimization_metric: ambient_false_positives_per_hour
maximization_metric: average_viable_recall
target_minimization: 10.0
EOF

python -m microwakeword.model_train_eval \
  --training_config="${CFG_PATH}" \
  --train 1 \
  --test_tflite_streaming_quantized 0 \
  mixednet \
  --residual_connection "0,0,0,0"

# Export/testing step tends to be more reliable when run after training in a separate invocation.
python -m microwakeword.model_train_eval \
  --training_config="${CFG_PATH}" \
  --train 0 \
  --test_tflite_streaming_quantized 1 \
  --use_weights best_weights \
  mixednet \
  --residual_connection "0,0,0,0"

echo
echo "Model artifacts are under: ${TRAIN_DIR}"
