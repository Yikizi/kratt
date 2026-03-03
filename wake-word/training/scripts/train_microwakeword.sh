#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/Users/mattias/kratt"

POS_DIR="${ROOT_DIR}/wake-word/data/processed/positive_samples"
NEG_DIR="${ROOT_DIR}/wake-word/data/processed/negative_samples"

FEATURES_DIR="${ROOT_DIR}/wake-word/training/features/microwakeword"
TRAIN_DIR_BASE="${ROOT_DIR}/wake-word/training/runs/microwakeword-kratt"
CFG_PATH="${ROOT_DIR}/wake-word/training/configs/microwakeword-kratt.yaml"

mkdir -p "${ROOT_DIR}/wake-word/training/configs"
mkdir -p "${ROOT_DIR}/wake-word/training/features"
mkdir -p "${ROOT_DIR}/wake-word/training/runs"

TRAIN_DIR="${TRAIN_DIR_BASE}-$(date +%Y%m%d-%H%M%S)"
MMAP_STAMP_PATH="${FEATURES_DIR}/.dataset_stamp.txt"

if [[ ! -d "${POS_DIR}" ]]; then
  echo "Missing positive samples: ${POS_DIR}" >&2
  echo "Run: /Users/mattias/kratt/wake-word/.venv/bin/python /Users/mattias/kratt/wake-word/data/collection/prepare_processed_dataset.py" >&2
  exit 2
fi
if [[ ! -d "${NEG_DIR}" ]]; then
  echo "Missing negative samples: ${NEG_DIR}" >&2
  echo "Run: /Users/mattias/kratt/wake-word/.venv/bin/python /Users/mattias/kratt/wake-word/data/collection/download_negatives.py --output-dir /Users/mattias/kratt/wake-word/data/processed" >&2
  exit 2
fi

./wake-word/training/scripts/setup_microwakeword_env.sh
# shellcheck disable=SC1091
source "${ROOT_DIR}/wake-word/.venv-microwakeword/bin/activate"

POS_COUNT="$(find "${POS_DIR}" -maxdepth 1 -name '*.wav' | wc -l | tr -d ' ')"
NEG_COUNT="$(find "${NEG_DIR}" -maxdepth 1 -name '*.wav' | wc -l | tr -d ' ')"
STAMP="pos_wavs=${POS_COUNT} neg_wavs=${NEG_COUNT} clip_ms=1500"

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
    --clip-duration-ms 1500
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
clip_duration_ms: 1500
target_minimization: 0.0
minimization_metric: null
maximization_metric: accuracy
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
