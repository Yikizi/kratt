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
    [--background-noise-dir DIR]... \
    [--impulse-response-dir DIR]... \
    [--training-steps N] \
    [--learning-rates CSV] \
    [--neg-class-weight N] \
    [--recall-profile] \
    [--vtlp-prob P] \
    [--vtlp-alpha-min A] \
    [--vtlp-alpha-max A] \
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
BACKGROUND_NOISE_DIRS=()
IMPULSE_RESPONSE_DIRS=()
TRAINING_STEPS="15000, 5000"
CLIP_DURATION_MS=1500
NEGATIVE_CLASS_WEIGHT="5"
LEARNING_RATES="0.001, 0.0001"
TIME_MASK_SIZE=0
TIME_MASK_COUNT=0
FREQ_MASK_SIZE=0
FREQ_MASK_COUNT=0
# v6-residual ablation proved residual ON = -37% FAPH. Always on by default.
RESIDUAL_CONNECTION="1,1,1,1"
POINTWISE_FILTERS="48, 48, 48, 48"
VTLP_PROB="0.5"
VTLP_ALPHA_MIN="0.85"
VTLP_ALPHA_MAX="1.15"
AUG_PROFILE="aggressive"

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
    --neg-class-weight)
      NEGATIVE_CLASS_WEIGHT="$2"
      shift 2
      ;;
    --learning-rates)
      LEARNING_RATES="$2"
      shift 2
      ;;
    --recall-profile)
      TRAINING_STEPS="15000, 5000"
      NEGATIVE_CLASS_WEIGHT="5"
      LEARNING_RATES="0.001, 0.0001"
      RESIDUAL_CONNECTION="1,1,1,1"
      VTLP_PROB="0.5"
      VTLP_ALPHA_MIN="0.85"
      VTLP_ALPHA_MAX="1.15"
      shift 1
      ;;
    --clip-duration-ms)
      CLIP_DURATION_MS="$2"
      shift 2
      ;;
    --background-noise-dir)
      BACKGROUND_NOISE_DIRS+=("$2")
      shift 2
      ;;
    --impulse-response-dir)
      IMPULSE_RESPONSE_DIRS+=("$2")
      shift 2
      ;;
    --spec-augment)
      TIME_MASK_SIZE=10
      TIME_MASK_COUNT=2
      FREQ_MASK_SIZE=3
      FREQ_MASK_COUNT=2
      shift 1
      ;;
    --residual)
      RESIDUAL_CONNECTION="1,1,1,1"
      shift 1
      ;;
    --no-residual)
      RESIDUAL_CONNECTION="0,0,0,0"
      shift 1
      ;;
    --pointwise-filters)
      POINTWISE_FILTERS="$2"
      shift 2
      ;;
    --vtlp-prob)
      VTLP_PROB="$2"
      shift 2
      ;;
    --vtlp-alpha-min)
      VTLP_ALPHA_MIN="$2"
      shift 2
      ;;
    --vtlp-alpha-max)
      VTLP_ALPHA_MAX="$2"
      shift 2
      ;;
    --no-vtlp)
      VTLP_PROB="0.0"
      shift 1
      ;;
    --aug-profile)
      AUG_PROFILE="$2"
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

trim_csv_len() {
  printf '%s\n' "$1" | tr ',' '\n' | sed 's/^ *//; s/ *$//' | sed '/^$/d' | wc -l | tr -d ' '
}

PHASE_COUNT="$(trim_csv_len "${TRAINING_STEPS}")"
LR_PHASE_COUNT="$(trim_csv_len "${LEARNING_RATES}")"
if [[ "${PHASE_COUNT}" != "${LR_PHASE_COUNT}" ]]; then
  echo "training_steps phases (${PHASE_COUNT}) must match learning_rates phases (${LR_PHASE_COUNT})" >&2
  exit 2
fi

if ! python3 - "${VTLP_PROB}" "${VTLP_ALPHA_MIN}" "${VTLP_ALPHA_MAX}" <<'PY'
import sys
prob, alpha_min, alpha_max = map(float, sys.argv[1:])
if not (0.0 <= prob <= 1.0):
    raise SystemExit(1)
if alpha_min <= 0 or alpha_max <= 0 or alpha_min > alpha_max:
    raise SystemExit(1)
PY
then
  echo "Invalid VTLP parameters: prob=${VTLP_PROB} alpha_min=${VTLP_ALPHA_MIN} alpha_max=${VTLP_ALPHA_MAX}" >&2
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

STAMP="pos_wavs=${POS_COUNT} neg_wavs=${NEG_COUNT} hard_neg_wavs=${HARD_NEG_COUNT} ambient_wavs=${AMBIENT_COUNT} clip_ms=${CLIP_DURATION_MS} train_steps=${TRAINING_STEPS} lrs=${LEARNING_RATES} neg_w=${NEGATIVE_CLASS_WEIGHT} vtlp=${VTLP_PROB}:${VTLP_ALPHA_MIN}-${VTLP_ALPHA_MAX}"

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
  if [[ ${#BACKGROUND_NOISE_DIRS[@]} -gt 0 ]]; then
    for bg_dir in "${BACKGROUND_NOISE_DIRS[@]}"; do
      MMAP_CMD+=(--background-noise-dir "${bg_dir}")
    done
  fi
  if [[ ${#IMPULSE_RESPONSE_DIRS[@]} -gt 0 ]]; then
    for ir_dir in "${IMPULSE_RESPONSE_DIRS[@]}"; do
      MMAP_CMD+=(--impulse-response-dir "${ir_dir}")
    done
  fi
  MMAP_CMD+=(--vtlp-prob "${VTLP_PROB}")
  MMAP_CMD+=(--vtlp-alpha-min "${VTLP_ALPHA_MIN}" --vtlp-alpha-max "${VTLP_ALPHA_MAX}")
  MMAP_CMD+=(--aug-profile "${AUG_PROFILE}")
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

# Build per-phase weight lists (match number of training phases)
NUM_PHASES=$(echo "${TRAINING_STEPS}" | tr ',' '\n' | wc -l | tr -d ' ')
POS_WEIGHTS=$(printf '1%.0s' $(seq 1 "${NUM_PHASES}") | sed 's/1/, 1/g; s/^, //')
# Avoid `yes | head` which triggers SIGPIPE under pipefail
NEG_WEIGHTS=$(for _ in $(seq 1 "${NUM_PHASES}"); do printf '%s\n' "${NEGATIVE_CLASS_WEIGHT}"; done | paste -sd',' - | sed 's/,/, /g')

echo "Training profile:"
echo "  experiment      ${EXPERIMENT_NAME}"
echo "  training_steps  [${TRAINING_STEPS}]"
echo "  learning_rates  [${LEARNING_RATES}]"
echo "  neg_class_w     [${NEG_WEIGHTS}]"
echo "  residual        ${RESIDUAL_CONNECTION}"
echo "  pointwise       ${POINTWISE_FILTERS}"
echo "  VTLP            prob=${VTLP_PROB} alpha=[${VTLP_ALPHA_MIN}, ${VTLP_ALPHA_MAX}]"

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
positive_class_weight: [${POS_WEIGHTS}]
negative_class_weight: [${NEG_WEIGHTS}]
learning_rates: [${LEARNING_RATES}]
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
  --residual_connection "${RESIDUAL_CONNECTION}" \
  --pointwise_filters "${POINTWISE_FILTERS}"

python -m microwakeword.model_train_eval \
  --training_config="${CFG_PATH}" \
  --train 0 \
  --test_tflite_streaming_quantized 1 \
  --use_weights best_weights \
  mixednet \
  --residual_connection "${RESIDUAL_CONNECTION}" \
  --pointwise_filters "${POINTWISE_FILTERS}"

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
