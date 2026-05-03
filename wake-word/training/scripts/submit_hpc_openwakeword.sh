#!/usr/bin/env bash
set -euo pipefail
# Submit openWakeWord training to HPC GPU queue.
# Uses our pre-recorded WAVs (skips Piper TTS generation).
#
# Usage:
#   bash submit_hpc_openwakeword.sh [--tag v1] [--steps 50000] [--time 04:00:00]

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/kratt_paths.sh"

ROOT_DIR="$(kratt_project_root)"
DATA_ROOT="$(kratt_data_root)"
PROCESSED_DIR="$(kratt_processed_dir)"
DATASETS_DIR="$(kratt_datasets_dir)"
OWW_VENV="${ROOT_DIR}/wake-word/.venv-openwakeword"
CONFIG="${ROOT_DIR}/wake-word/training/configs/openwakeword-kuule-kratt.yaml"

TAG="v1"
STEPS="50000"
PARTITION="gpu"
TIME_LIMIT="04:00:00"
MEMORY="48G"
GRES="gpu:1"
OVERWRITE_FEATURES=1
DATASET_PRESET="legacy-hard-neg"
EXPERIMENT_DIR="${PROCESSED_DIR}/experiments/kuule_kratt_v17dry"
DRY_RUN=0
ALLOW_KNOWN_BAD_POSITIVES=0
MAX_NEGATIVE_WEIGHT=""
TARGET_FP_PER_HOUR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag)            TAG="$2"; shift 2 ;;
    --steps)          STEPS="$2"; shift 2 ;;
    --partition)      PARTITION="$2"; shift 2 ;;
    --time)           TIME_LIMIT="$2"; shift 2 ;;
    --mem)            MEMORY="$2"; shift 2 ;;
    --gres)           GRES="$2"; shift 2 ;;
    --reuse-features) OVERWRITE_FEATURES=0; shift ;;
    --dataset-preset) DATASET_PRESET="$2"; shift 2 ;;
    --experiment-dir) EXPERIMENT_DIR="$2"; shift 2 ;;
    --allow-known-bad-positives) ALLOW_KNOWN_BAD_POSITIVES=1; shift ;;
    --max-negative-weight) MAX_NEGATIVE_WEIGHT="$2"; shift 2 ;;
    --target-fp-per-hour) TARGET_FP_PER_HOUR="$2"; shift 2 ;;
    --dry-run)        DRY_RUN=1; shift ;;
    *)                echo "Unknown: $1" >&2; exit 2 ;;
  esac
done

OWW_OUTPUT="${DATA_ROOT}/training/openwakeword"
MODEL_NAME="kuule_kratt_$(printf '%s' "${TAG}" | tr -c 'A-Za-z0-9_' '_')"
OWW_MODEL_DIR="${OWW_OUTPUT}/${MODEL_NAME}"
VAL_FEATURES="${OWW_OUTPUT}/validation_set_features.npy"
RUNS_DIR="${DATA_ROOT}/training/runs"

require_cmd() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "ERROR: required command not found: ${cmd}" >&2
    exit 2
  fi
}

count_audio() {
  local dir="$1"
  find -L "${dir}" -type f \( -name "*.wav" -o -name "*.flac" \) | wc -l | tr -d ' '
}

stage_audio_dir() {
  local src_dir="$1" dst_dir="$2" prefix="$3" start_idx="$4"
  local idx="${start_idx}"
  [[ -d "${src_dir}" ]] || { echo "${idx}"; return 0; }
  while IFS= read -r -d '' f; do
    resample_to_16k "$f" "${dst_dir}/${prefix}_$(printf '%05d' "${idx}").wav"
    idx=$((idx + 1))
  done < <(find -L "${src_dir}" -type f \( -name "*.wav" -o -name "*.flac" \) -print0 | sort -z)
  echo "${idx}"
}

echo "=== Preparing openWakeWord data ==="

if (( DRY_RUN != 1 )); then
  require_cmd sbatch
fi
require_cmd find
require_cmd mv
require_cmd sed
require_cmd wget
if (( DRY_RUN != 1 )); then
  [[ -x "${OWW_VENV}/bin/python" ]] || {
    echo "ERROR: openWakeWord venv python not found: ${OWW_VENV}/bin/python" >&2
    exit 2
  }
  [[ -f "${CONFIG}" ]] || {
    echo "ERROR: config not found: ${CONFIG}" >&2
    exit 2
  }
fi

# Resample a WAV to 16kHz mono s16le if not already 16kHz.
# Uses COPIES (not symlinks) so the training script always sees 16kHz files,
# regardless of what sample rate the source WAVs are in.
#
# Uses sox (confirmed available on HPC) with ffmpeg as fallback.
if ! command -v sox >/dev/null 2>&1 && ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ERROR: neither sox nor ffmpeg found. One is required for resampling." >&2
  exit 2
fi

resample_to_16k() {
  local src="$1" dst="$2"
  if [[ -f "${dst}" ]]; then
    return 0  # already exists, skip
  fi
  # Always resample via sox/ffmpeg -- the tool handles the no-op case
  # efficiently when input is already 16kHz.
  if command -v sox >/dev/null 2>&1; then
    sox "${src}" -r 16000 -c 1 -b 16 "${dst}" 2>/dev/null
  else
    ffmpeg -y -hide_banner -loglevel error \
      -i "${src}" -ar 16000 -ac 1 -sample_fmt s16 "${dst}"
  fi
}

mkdir -p "${OWW_MODEL_DIR}/positive_train" \
         "${OWW_MODEL_DIR}/positive_test" \
         "${OWW_MODEL_DIR}/negative_train" \
         "${OWW_MODEL_DIR}/negative_test"

POS_TRAIN="${OWW_MODEL_DIR}/positive_train"
POS_TEST="${OWW_MODEL_DIR}/positive_test"
NEG_TRAIN="${OWW_MODEL_DIR}/negative_train"
NEG_TEST="${OWW_MODEL_DIR}/negative_test"

POSITIVE_TRAIN_SOURCES=()
POSITIVE_TEST_SOURCES=()
NEGATIVE_TRAIN_SOURCES=()
NEGATIVE_TEST_SOURCES=()
SPLIT_POSITIVES=1

case "${DATASET_PRESET}" in
  legacy-hard-neg)
    # Original openWakeWord attempt: many synthetic hard negatives. Kept for reproducibility.
    POSITIVE_TRAIN_SOURCES=(
      "${DATASETS_DIR}/kuule-kratt/positive/mic1"
      "${DATASETS_DIR}/kuule-kratt/positive/mic2"
      "${PROCESSED_DIR}/positive_tts"
      "${PROCESSED_DIR}/positive_tts_ssml"
      "${DATA_ROOT}/raw/xtts_clones/marta/positive"
      "${DATA_ROOT}/raw/xtts_clones/annam/positive"
      "${DATA_ROOT}/raw/xtts_clones/ema/positive"
    )
    NEGATIVE_TRAIN_SOURCES=(
      "${PROCESSED_DIR}/negative_tts_hard"
      "${PROCESSED_DIR}/negative_tts_hard_v2"
      "${DATA_ROOT}/augmented/hard_neg_mattias_mac_train"
      "${DATA_ROOT}/raw/xtts_clones/marta/negative"
      "${DATA_ROOT}/raw/xtts_clones/annam/negative"
      "${DATA_ROOT}/raw/xtts_clones/ema/negative"
    )
    NEGATIVE_TEST_SOURCES=(
      "${PROCESSED_DIR}/test_hard_neg_xtts_isa"
      "${DATA_ROOT}/raw/xtts_clones/isa/negative"
    )
    ;;
  recall-cv)
    # Reuse the already validated v17 recall-cv experiment manifest/split.
    # This avoids maintaining two divergent dataset recipes.
    SPLIT_POSITIVES=0
    POSITIVE_TRAIN_SOURCES=("${EXPERIMENT_DIR}/positive_samples")
    POSITIVE_TEST_SOURCES=("${EXPERIMENT_DIR}/test_positive_samples")
    NEGATIVE_TRAIN_SOURCES=("${EXPERIMENT_DIR}/negative_samples")
    NEGATIVE_TEST_SOURCES=("${DATA_ROOT}/raw/xtts_clones/isa/negative")
    ;;
  *)
    echo "ERROR: unknown dataset preset: ${DATASET_PRESET}" >&2
    exit 2
    ;;
esac

KNOWN_BAD_POSITIVE_DIRS=(
  "${PROCESSED_DIR}/positive_tts_ssml"
  "${DATA_ROOT}/raw/neurokone_ssml_positives"
  "${DATA_ROOT}/raw/neurokone_ssml_kule"
  "${DATA_ROOT}/raw/xtts_clones/marta/positive"
  "${DATA_ROOT}/raw/xtts_clones/annam/positive"
  "${DATA_ROOT}/raw/xtts_clones/ema/positive"
  "${DATA_ROOT}/raw/xtts_clones/marta/positive_16k"
  "${DATA_ROOT}/raw/xtts_clones/annam/positive_16k"
  "${DATA_ROOT}/raw/xtts_clones/ema/positive_16k"
)

is_known_bad_positive_dir() {
  local candidate="$1"
  local bad
  for bad in "${KNOWN_BAD_POSITIVE_DIRS[@]}"; do
    if [[ "${candidate}" == "${bad}" ]]; then
      return 0
    fi
  done
  return 1
}

if [[ "${ALLOW_KNOWN_BAD_POSITIVES}" != "1" ]]; then
  FILTERED_POSITIVE_TRAIN_SOURCES=()
  for src in "${POSITIVE_TRAIN_SOURCES[@]}"; do
    if is_known_bad_positive_dir "${src}"; then
      echo "SKIPPING known-bad openWakeWord positive source (2026-04-27 audit): ${src}"
      continue
    fi
    FILTERED_POSITIVE_TRAIN_SOURCES+=("${src}")
  done
  POSITIVE_TRAIN_SOURCES=("${FILTERED_POSITIVE_TRAIN_SOURCES[@]}")
fi

echo "=== Preflight ==="
echo "  tag: ${TAG}"
echo "  model_name: ${MODEL_NAME}"
echo "  dataset_preset: ${DATASET_PRESET}"
echo "  experiment_dir: ${EXPERIMENT_DIR}"
echo "  allow_known_bad_positives: ${ALLOW_KNOWN_BAD_POSITIVES}"
echo "  max_negative_weight: ${MAX_NEGATIVE_WEIGHT:-config default}"
echo "  target_fp_per_hour: ${TARGET_FP_PER_HOUR:-config default}"
for src in "${POSITIVE_TRAIN_SOURCES[@]}"; do
  if [[ -d "${src}" ]]; then
    echo "  positive train source: ${src} ($(count_audio "${src}") audio files)"
  else
    echo "  WARN missing positive train source: ${src}"
  fi
done
if (( ${#POSITIVE_TEST_SOURCES[@]} > 0 )); then
  for src in "${POSITIVE_TEST_SOURCES[@]}"; do
    if [[ -d "${src}" ]]; then
      echo "  positive test source: ${src} ($(count_audio "${src}") audio files)"
    else
      echo "  WARN missing positive test source: ${src}"
    fi
  done
fi
for src in "${NEGATIVE_TRAIN_SOURCES[@]}"; do
  if [[ -d "${src}" ]]; then
    echo "  negative train source: ${src} ($(count_audio "${src}") audio files)"
  else
    echo "  WARN missing negative train source: ${src}"
  fi
done
neg_test_available=0
for src in "${NEGATIVE_TEST_SOURCES[@]}"; do
  if [[ -d "${src}" ]]; then
    c=$(count_audio "${src}")
    echo "  negative test source: ${src} (${c} audio files)"
    (( c > 0 )) && neg_test_available=1
  else
    echo "  WARN missing negative test source: ${src}"
  fi
done
if (( neg_test_available == 0 )); then
  echo "ERROR: no usable negative test source found." >&2
  exit 2
fi

if (( DRY_RUN == 1 )); then
  echo "DRY RUN: not staging data or submitting sbatch."
  exit 0
fi

# Clear old copies (full idempotent rebuild)
find "${POS_TRAIN}" -maxdepth 1 -name "*.wav" -delete 2>/dev/null || true
find "${POS_TEST}" -maxdepth 1 -name "*.wav" -delete 2>/dev/null || true
find "${NEG_TRAIN}" -maxdepth 1 -name "*.wav" -delete 2>/dev/null || true
find "${NEG_TEST}" -maxdepth 1 -name "*.wav" -delete 2>/dev/null || true

# Positive sources -- resample to 16kHz copies
echo "  Resampling positive train audio to 16kHz..."
idx=0
for src_dir in "${POSITIVE_TRAIN_SOURCES[@]}"; do
  before=${idx}
  idx=$(stage_audio_dir "${src_dir}" "${POS_TRAIN}" "pos" "${idx}")
  echo "  Positive train: ${src_dir} (+$((idx - before)), running total: ${idx})"
done
if (( idx == 0 )); then
  echo "ERROR: no positive training audio was staged." >&2
  exit 2
fi

if (( SPLIT_POSITIVES == 1 )); then
  # Hold out ~15% for test (deterministic: every 7th file)
  test_idx=0
  for f in "${POS_TRAIN}"/pos_*.wav; do
    [[ -f "$f" ]] || continue
    i=$(basename "$f" | sed 's/pos_0*//;s/\.wav//')
    if (( i % 7 == 0 )); then
      mv "$f" "${POS_TEST}/pos_test_$(printf '%05d' $test_idx).wav"
      test_idx=$((test_idx + 1))
    fi
  done
else
  echo "  Resampling positive test audio to 16kHz..."
  test_idx=0
  for src_dir in "${POSITIVE_TEST_SOURCES[@]}"; do
    before=${test_idx}
    test_idx=$(stage_audio_dir "${src_dir}" "${POS_TEST}" "pos_test" "${test_idx}")
    echo "  Positive test: ${src_dir} (+$((test_idx - before)), running total: ${test_idx})"
  done
fi
pos_train_count=$(find "${POS_TRAIN}" -name "*.wav" | wc -l)
pos_test_count=$(find "${POS_TEST}" -name "*.wav" | wc -l)
if (( pos_train_count == 0 || pos_test_count == 0 )); then
  echo "ERROR: positive split produced empty train/test set (${pos_train_count}/${pos_test_count})." >&2
  exit 2
fi
echo "  Positive: ${pos_train_count} train, ${pos_test_count} test"

# Negative sources -- resample to 16kHz copies
echo "  Resampling negative train audio to 16kHz..."
neg_idx=0
for src_dir in "${NEGATIVE_TRAIN_SOURCES[@]}"; do
  before=${neg_idx}
  neg_idx=$(stage_audio_dir "${src_dir}" "${NEG_TRAIN}" "neg" "${neg_idx}")
  echo "  Negative train: ${src_dir} (+$((neg_idx - before)), running total: ${neg_idx})"
done
if (( neg_idx == 0 )); then
  echo "ERROR: no negative training audio was staged." >&2
  exit 2
fi

neg_test_idx=0
for src_dir in "${NEGATIVE_TEST_SOURCES[@]}"; do
  before=${neg_test_idx}
  neg_test_idx=$(stage_audio_dir "${src_dir}" "${NEG_TEST}" "neg_test" "${neg_test_idx}")
  echo "  Negative test: ${src_dir} (+$((neg_test_idx - before)), running total: ${neg_test_idx})"
done
neg_train_count=$(find "${NEG_TRAIN}" -name "*.wav" | wc -l)
neg_test_count=$(find "${NEG_TEST}" -name "*.wav" | wc -l)
if (( neg_train_count == 0 || neg_test_count == 0 )); then
  echo "ERROR: negative split produced empty train/test set (${neg_train_count}/${neg_test_count})." >&2
  exit 2
fi
echo "  Negative: ${neg_train_count} train, ${neg_test_count} test"

echo ""
echo "=== Submitting openWakeWord GPU job (tag: ${TAG}) ==="

mkdir -p "${RUNS_DIR}/logs"
JOB_NAME="kratt-oww-${TAG}"
LOG_PATH="${RUNS_DIR}/logs/${JOB_NAME}-%j.out"

JOB_ID="$(
  sbatch \
    --parsable \
    --job-name="${JOB_NAME}" \
    --account=Project_tanel_alumae \
    --partition="${PARTITION}" \
    --gres="${GRES}" \
    --time="${TIME_LIMIT}" \
    --cpus-per-task=8 \
    --mem="${MEMORY}" \
    --chdir="${ROOT_DIR}" \
    --output="${LOG_PATH}" \
    --error="${LOG_PATH}" <<EOF
#!/usr/bin/env bash
set -euo pipefail

echo "openWakeWord training: ${TAG}"
ulimit -n 65535 || true
echo "ulimit -n: $(ulimit -n)"
echo "GPU: \$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
echo "Positive: ${pos_train_count} train, ${pos_test_count} test"
echo "Negative: ${neg_train_count} train, ${neg_test_count} test"

# Ensure feature extraction models are available in the venv package
OWW_RESOURCES=\$(${OWW_VENV}/bin/python -c "import openwakeword, pathlib, os; print(os.path.join(pathlib.Path(openwakeword.__file__).parent.resolve(), 'resources', 'models'))")
mkdir -p "\${OWW_RESOURCES}"
for model_file in melspectrogram.onnx embedding_model.onnx melspectrogram.tflite embedding_model.tflite; do
  if [[ ! -f "\${OWW_RESOURCES}/\${model_file}" ]]; then
    echo "Downloading \${model_file}..."
    wget --tries=3 --timeout=30 --waitretry=5 -q -O "\${OWW_RESOURCES}/\${model_file}" \
      "https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/\${model_file}"
  fi
done

# Download validation features if not present
if [[ ! -f "${VAL_FEATURES}" ]]; then
  echo "Downloading validation_set_features.npy from HuggingFace (~280MB)..."
  wget --tries=3 --timeout=30 --waitretry=5 -q -O "${VAL_FEATURES}" \
    "https://huggingface.co/datasets/davidscripka/openwakeword_features/resolve/main/validation_set_features.npy"
fi

# Patch tag-specific model name and steps in config
TMP_CONFIG=\$(mktemp /tmp/oww_config_${TAG}.XXXXXX.yaml)
trap 'rm -f "\${TMP_CONFIG}"' EXIT
${OWW_VENV}/bin/python - "${CONFIG}" "\${TMP_CONFIG}" <<'PYCONFIG'
import sys
from pathlib import Path
import yaml
src = Path(sys.argv[1])
dst = Path(sys.argv[2])
config = yaml.safe_load(src.read_text())
config["model_name"] = "${MODEL_NAME}"
config["steps"] = int("${STEPS}")
max_negative_weight = "${MAX_NEGATIVE_WEIGHT}"
target_fp_per_hour = "${TARGET_FP_PER_HOUR}"
if max_negative_weight:
    config["max_negative_weight"] = int(max_negative_weight)
if target_fp_per_hour:
    config["target_false_positives_per_hour"] = float(target_fp_per_hour)
dst.write_text(yaml.safe_dump(config, sort_keys=False))
PYCONFIG

if [[ ${OVERWRITE_FEATURES} -eq 1 ]]; then
  echo "Removing stale feature caches before rerun..."
  rm -f "${OWW_MODEL_DIR}/positive_features_"*.npy "${OWW_MODEL_DIR}/negative_features_"*.npy
fi

# Use patched training script (fixes Piper import, batch_n_per_class, etc.)
${OWW_VENV}/bin/python \
  "${ROOT_DIR}/wake-word/training/scripts/train_openwakeword.py" \
  --training_config "\${TMP_CONFIG}" \
  --preflight-only

${OWW_VENV}/bin/python \
  "${ROOT_DIR}/wake-word/training/scripts/train_openwakeword.py" \
  --training_config "\${TMP_CONFIG}" \
  --augment_clips \
  $([[ ${OVERWRITE_FEATURES} -eq 1 ]] && echo --overwrite) \
  --train_model

echo "Training complete. Model at: ${OWW_OUTPUT}/${MODEL_NAME}.onnx"
EOF
)"

echo "Submitted ${JOB_NAME} as job ${JOB_ID}"
echo "Log: ${LOG_PATH/\%j/${JOB_ID}}"
echo "Resources: partition=${PARTITION} time=${TIME_LIMIT} mem=${MEMORY} gres=${GRES}"
