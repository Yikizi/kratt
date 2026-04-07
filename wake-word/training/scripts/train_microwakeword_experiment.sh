#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/kratt_paths.sh
source "${SCRIPT_DIR}/lib/kratt_paths.sh"

ROOT_DIR="$(kratt_project_root)"
FEATURES_BASE_DIR="$(kratt_training_features_dir)"
RUNS_BASE_DIR="$(kratt_training_runs_dir)"
CONFIGS_DIR="$(kratt_training_configs_dir)"

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
HARD_NEG_DIR=""
AMBIENT_DIR=""
TRAINING_STEPS=3000
CLIP_DURATION_MS=1500
TIME_MASK_SIZE=0
TIME_MASK_COUNT=0
FREQ_MASK_SIZE=0
FREQ_MASK_COUNT=0

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
    --hard-negative-dir)
      HARD_NEG_DIR="$2"
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
    --spec-augment)
      TIME_MASK_SIZE=10
      TIME_MASK_COUNT=2
      FREQ_MASK_SIZE=3
      FREQ_MASK_COUNT=2
      shift 1
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

FEATURES_DIR="${FEATURES_BASE_DIR}/${EXPERIMENT_NAME}"
TRAIN_DIR_BASE="${RUNS_BASE_DIR}/${EXPERIMENT_NAME}"
CFG_PATH="${CONFIGS_DIR}/${EXPERIMENT_NAME}.yaml"
TRAIN_DIR="${TRAIN_DIR_BASE}-$(date +%Y%m%d-%H%M%S)"
MMAP_STAMP_PATH="${FEATURES_DIR}/.dataset_stamp.txt"

mkdir -p "${CONFIGS_DIR}"
mkdir -p "${FEATURES_BASE_DIR}"
mkdir -p "${RUNS_BASE_DIR}"

if [[ ! -d "${POS_DIR}" ]]; then
  echo "Missing positive samples: ${POS_DIR}" >&2
  exit 2
fi
if [[ ! -d "${NEG_DIR}" ]]; then
  echo "Missing negative samples: ${NEG_DIR}" >&2
  exit 2
fi
if [[ -n "${HARD_NEG_DIR}" && ! -d "${HARD_NEG_DIR}" ]]; then
  echo "Missing hard negative samples: ${HARD_NEG_DIR}" >&2
  exit 2
fi
if [[ -n "${AMBIENT_DIR}" && ! -d "${AMBIENT_DIR}" ]]; then
  echo "Missing ambient samples: ${AMBIENT_DIR}" >&2
  exit 2
fi

"${SCRIPT_DIR}/setup_microwakeword_env.sh"
# shellcheck disable=SC1091
source "${ROOT_DIR}/wake-word/.venv-microwakeword/bin/activate"

POS_COUNT="$(find "${POS_DIR}" -maxdepth 1 -name '*.wav' | wc -l | tr -d ' ')"
NEG_COUNT="$(find "${NEG_DIR}" -maxdepth 1 -name '*.wav' | wc -l | tr -d ' ')"
HARD_NEG_COUNT="0"
if [[ -n "${HARD_NEG_DIR}" ]]; then
  HARD_NEG_COUNT="$(find "${HARD_NEG_DIR}" -maxdepth 1 -name '*.wav' | wc -l | tr -d ' ')"
fi
AMBIENT_COUNT="0"
if [[ -n "${AMBIENT_DIR}" ]]; then
  AMBIENT_COUNT="$(find "${AMBIENT_DIR}" -maxdepth 1 -name '*.wav' | wc -l | tr -d ' ')"
fi

STAMP="pos_wavs=${POS_COUNT} neg_wavs=${NEG_COUNT} hard_neg_wavs=${HARD_NEG_COUNT} ambient_wavs=${AMBIENT_COUNT} clip_ms=${CLIP_DURATION_MS}"

NEED_MMAPS=1
if [[ "${REGEN_MMAPS:-0}" != "1" ]]; then
  if [[ -f "${MMAP_STAMP_PATH}" ]] && [[ "$(cat "${MMAP_STAMP_PATH}")" == "${STAMP}" ]]; then
    if [[ -d "${FEATURES_DIR}/positive/training/wakeword_mmap" && -d "${FEATURES_DIR}/negative/training/negative_mmap" ]]; then
      HARD_NEG_OK=1
      if [[ -n "${HARD_NEG_DIR}" && ! -d "${FEATURES_DIR}/hard_negative/training/hard_negative_mmap" ]]; then
        HARD_NEG_OK=0
      fi
      if [[ "${HARD_NEG_OK}" == "1" ]]; then
        if [[ -z "${AMBIENT_DIR}" || ( -d "${FEATURES_DIR}/negative/validation_ambient/ambient_mmap" && -d "${FEATURES_DIR}/negative/testing_ambient/ambient_mmap" ) ]]; then
          NEED_MMAPS=0
        fi
      fi
    fi
  fi
fi

if [[ "${NEED_MMAPS}" == "0" ]]; then
  echo "Found existing mmaps under ${FEATURES_DIR} (stamp match); skipping generation."
else
  echo "Generating mmaps (stamp: ${STAMP})"
  rm -rf "${FEATURES_DIR}/positive" "${FEATURES_DIR}/negative" "${FEATURES_DIR}/hard_negative"
  MMAP_CMD=(
    python "${ROOT_DIR}/wake-word/training/scripts/generate_microwakeword_mmaps.py"
    --positive-dir "${POS_DIR}"
    --negative-dir "${NEG_DIR}"
    --out-dir "${FEATURES_DIR}"
    --clip-duration-ms "${CLIP_DURATION_MS}"
  )
  if [[ -n "${HARD_NEG_DIR}" ]]; then
    MMAP_CMD+=(--hard-negative-dir "${HARD_NEG_DIR}")
  fi
  if [[ -n "${AMBIENT_DIR}" ]]; then
    MMAP_CMD+=(--ambient-dir "${AMBIENT_DIR}")
  fi
  "${MMAP_CMD[@]}"
  echo "${STAMP}" > "${MMAP_STAMP_PATH}"
fi

HARD_NEG_BLOCK=""
if [[ -n "${HARD_NEG_DIR}" ]]; then
  HARD_NEG_BLOCK=$(cat <<EOB
  - features_dir: "${FEATURES_DIR}/hard_negative"
    sampling_weight: 4.0
    penalty_weight: 3.0
    truth: false
    truncation_strategy: truncate_start
    type: mmap
EOB
)
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
${HARD_NEG_BLOCK}
training_steps: [${TRAINING_STEPS}]
positive_class_weight: [1]
negative_class_weight: [20]
learning_rates: [0.001]
batch_size: 128
time_mask_max_size: [${TIME_MASK_SIZE}]
time_mask_count: [${TIME_MASK_COUNT}]
freq_mask_max_size: [${FREQ_MASK_SIZE}]
freq_mask_count: [${FREQ_MASK_COUNT}]
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
if [[ -n "${HARD_NEG_DIR}" ]]; then
  REPORT_CMD+=(--hard-negative-dir "${HARD_NEG_DIR}")
fi
if [[ -n "${AMBIENT_DIR}" ]]; then
  REPORT_CMD+=(--ambient-dir "${AMBIENT_DIR}")
fi
"${REPORT_CMD[@]}"

echo
echo "Model artifacts are under: ${TRAIN_DIR}"
