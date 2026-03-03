#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/Users/mattias/kratt"

usage() {
  cat <<'EOF'
Usage:
  train_microwakeword_experiment.sh \
    --experiment-name NAME \
    --positive-dir DIR \
    --negative-dir DIR \
    [--ambient-dir DIR] \
    [--training-steps N] \
    [--clip-duration-ms N]

This script builds RaggedMmap features, writes a temporary training config,
trains a microWakeWord model, and exports the quantized streaming TFLite model.
EOF
}

EXPERIMENT_NAME=""
POS_DIR=""
NEG_DIR=""
AMBIENT_DIR=""
TRAINING_STEPS=3000
CLIP_DURATION_MS=1500

while [[ $# -gt 0 ]]; do
  case "$1" in
    --experiment-name)
      EXPERIMENT_NAME="$2"
      shift 2
      ;;
    --positive-dir)
      POS_DIR="$2"
      shift 2
      ;;
    --negative-dir)
      NEG_DIR="$2"
      shift 2
      ;;
    --ambient-dir)
      AMBIENT_DIR="$2"
      shift 2
      ;;
    --training-steps)
      TRAINING_STEPS="$2"
      shift 2
      ;;
    --clip-duration-ms)
      CLIP_DURATION_MS="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "${EXPERIMENT_NAME}" || -z "${POS_DIR}" || -z "${NEG_DIR}" ]]; then
  usage >&2
  exit 2
fi

FEATURES_DIR="${ROOT_DIR}/wake-word/training/features/${EXPERIMENT_NAME}"
TRAIN_DIR_BASE="${ROOT_DIR}/wake-word/training/runs/${EXPERIMENT_NAME}"
CFG_PATH="${ROOT_DIR}/wake-word/training/configs/${EXPERIMENT_NAME}.yaml"
TRAIN_DIR="${TRAIN_DIR_BASE}-$(date +%Y%m%d-%H%M%S)"
MMAP_STAMP_PATH="${FEATURES_DIR}/.dataset_stamp.txt"

mkdir -p "${ROOT_DIR}/wake-word/training/configs"
mkdir -p "${ROOT_DIR}/wake-word/training/features"
mkdir -p "${ROOT_DIR}/wake-word/training/runs"

if [[ ! -d "${POS_DIR}" ]]; then
  echo "Missing positive samples: ${POS_DIR}" >&2
  exit 2
fi
if [[ ! -d "${NEG_DIR}" ]]; then
  echo "Missing negative samples: ${NEG_DIR}" >&2
  exit 2
fi
if [[ -n "${AMBIENT_DIR}" && ! -d "${AMBIENT_DIR}" ]]; then
  echo "Missing ambient samples: ${AMBIENT_DIR}" >&2
  exit 2
fi

./wake-word/training/scripts/setup_microwakeword_env.sh
# shellcheck disable=SC1091
source "${ROOT_DIR}/wake-word/.venv-microwakeword/bin/activate"

POS_COUNT="$(find "${POS_DIR}" -maxdepth 1 -name '*.wav' | wc -l | tr -d ' ')"
NEG_COUNT="$(find "${NEG_DIR}" -maxdepth 1 -name '*.wav' | wc -l | tr -d ' ')"
AMBIENT_COUNT="0"
if [[ -n "${AMBIENT_DIR}" ]]; then
  AMBIENT_COUNT="$(find "${AMBIENT_DIR}" -maxdepth 1 -name '*.wav' | wc -l | tr -d ' ')"
fi

STAMP="pos_wavs=${POS_COUNT} neg_wavs=${NEG_COUNT} ambient_wavs=${AMBIENT_COUNT} clip_ms=${CLIP_DURATION_MS}"

NEED_MMAPS=1
if [[ "${REGEN_MMAPS:-0}" != "1" ]]; then
  if [[ -f "${MMAP_STAMP_PATH}" ]] && [[ "$(cat "${MMAP_STAMP_PATH}")" == "${STAMP}" ]]; then
    if [[ -d "${FEATURES_DIR}/positive/training/wakeword_mmap" && -d "${FEATURES_DIR}/negative/training/negative_mmap" ]]; then
      if [[ -z "${AMBIENT_DIR}" || ( -d "${FEATURES_DIR}/negative/validation_ambient/ambient_mmap" && -d "${FEATURES_DIR}/negative/testing_ambient/ambient_mmap" ) ]]; then
        NEED_MMAPS=0
      fi
    fi
  fi
fi

if [[ "${NEED_MMAPS}" == "0" ]]; then
  echo "Found existing mmaps under ${FEATURES_DIR} (stamp match); skipping generation."
else
  echo "Generating mmaps (stamp: ${STAMP})"
  rm -rf "${FEATURES_DIR}/positive" "${FEATURES_DIR}/negative"
  MMAP_CMD=(
    python "${ROOT_DIR}/wake-word/training/scripts/generate_microwakeword_mmaps.py"
    --positive-dir "${POS_DIR}"
    --negative-dir "${NEG_DIR}"
    --out-dir "${FEATURES_DIR}"
    --clip-duration-ms "${CLIP_DURATION_MS}"
  )
  if [[ -n "${AMBIENT_DIR}" ]]; then
    MMAP_CMD+=(--ambient-dir "${AMBIENT_DIR}")
  fi
  "${MMAP_CMD[@]}"
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
training_steps: [${TRAINING_STEPS}]
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

python -m microwakeword.model_train_eval \
  --training_config="${CFG_PATH}" \
  --train 0 \
  --test_tflite_streaming_quantized 1 \
  --use_weights best_weights \
  mixednet \
  --residual_connection "0,0,0,0"

REPORT_CMD=(
  python "${ROOT_DIR}/wake-word/evaluation/microwakeword_report.py"
  --run-dir "${TRAIN_DIR}"
  --positive-dir "${POS_DIR}"
  --negative-dir "${NEG_DIR}"
)
if [[ -n "${AMBIENT_DIR}" ]]; then
  REPORT_CMD+=(--ambient-dir "${AMBIENT_DIR}")
fi
"${REPORT_CMD[@]}"

echo
echo "Model artifacts are under: ${TRAIN_DIR}"
