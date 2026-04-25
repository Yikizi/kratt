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

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag)            TAG="$2"; shift 2 ;;
    --steps)          STEPS="$2"; shift 2 ;;
    --partition)      PARTITION="$2"; shift 2 ;;
    --time)           TIME_LIMIT="$2"; shift 2 ;;
    --mem)            MEMORY="$2"; shift 2 ;;
    --gres)           GRES="$2"; shift 2 ;;
    --reuse-features) OVERWRITE_FEATURES=0; shift ;;
    *)                echo "Unknown: $1" >&2; exit 2 ;;
  esac
done

OWW_OUTPUT="${DATA_ROOT}/training/openwakeword"
OWW_MODEL_DIR="${OWW_OUTPUT}/kuule_kratt"
VAL_FEATURES="${OWW_OUTPUT}/validation_set_features.npy"
RUNS_DIR="${DATA_ROOT}/training/runs"

require_cmd() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "ERROR: required command not found: ${cmd}" >&2
    exit 2
  fi
}

count_wavs() {
  local dir="$1"
  find "${dir}" -type f -name "*.wav" | wc -l | tr -d ' '
}

echo "=== Preparing openWakeWord data ==="

require_cmd sbatch
require_cmd find
require_cmd mv
require_cmd sed
require_cmd wget
[[ -x "${OWW_VENV}/bin/python" ]] || {
  echo "ERROR: openWakeWord venv python not found: ${OWW_VENV}/bin/python" >&2
  exit 2
}
[[ -f "${CONFIG}" ]] || {
  echo "ERROR: config not found: ${CONFIG}" >&2
  exit 2
}

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

# Positive train: KORVO-2 mic1+mic2 + TTS + SSML + XTTS (same as microWakeWord v6+ positives)
POS_TRAIN="${OWW_MODEL_DIR}/positive_train"
POS_TEST="${OWW_MODEL_DIR}/positive_test"
NEG_TRAIN="${OWW_MODEL_DIR}/negative_train"
NEG_TEST="${OWW_MODEL_DIR}/negative_test"

POSITIVE_SOURCES=(
  "${DATASETS_DIR}/kuule-kratt/positive/mic1"
  "${DATASETS_DIR}/kuule-kratt/positive/mic2"
  "${PROCESSED_DIR}/positive_tts"
  "${PROCESSED_DIR}/positive_tts_ssml"
  "${DATA_ROOT}/raw/xtts_clones/marta/positive"
  "${DATA_ROOT}/raw/xtts_clones/annam/positive"
  "${DATA_ROOT}/raw/xtts_clones/ema/positive"
)

NEGATIVE_SOURCES=(
  "${PROCESSED_DIR}/negative_tts_hard"
  "${PROCESSED_DIR}/negative_tts_hard_v2"
  "${DATA_ROOT}/augmented/hard_neg_mattias_mac_train"
  "${DATA_ROOT}/raw/xtts_clones/marta/negative"
  "${DATA_ROOT}/raw/xtts_clones/annam/negative"
  "${DATA_ROOT}/raw/xtts_clones/ema/negative"
)

NEGATIVE_TEST_SOURCE="${PROCESSED_DIR}/test_hard_neg_xtts_isa"

echo "=== Preflight ==="
for src in "${POSITIVE_SOURCES[@]}"; do
  if [[ -d "${src}" ]]; then
    echo "  positive source: ${src} ($(count_wavs "${src}") wavs)"
  else
    echo "  WARN missing positive source: ${src}"
  fi
done
for src in "${NEGATIVE_SOURCES[@]}"; do
  if [[ -d "${src}" ]]; then
    echo "  negative source: ${src} ($(count_wavs "${src}") wavs)"
  else
    echo "  WARN missing negative source: ${src}"
  fi
done
if [[ ! -d "${NEGATIVE_TEST_SOURCE}" ]]; then
  echo "ERROR: negative test source missing: ${NEGATIVE_TEST_SOURCE}" >&2
  exit 2
fi

# Clear old symlinks AND old copies (full idempotent rebuild)
# Use find to avoid "argument list too long" with thousands of WAVs
find "${POS_TRAIN}" -maxdepth 1 -name "*.wav" -delete 2>/dev/null || true
find "${POS_TEST}" -maxdepth 1 -name "*.wav" -delete 2>/dev/null || true
find "${NEG_TRAIN}" -maxdepth 1 -name "*.wav" -delete 2>/dev/null || true
find "${NEG_TEST}" -maxdepth 1 -name "*.wav" -delete 2>/dev/null || true

# Positive sources -- resample to 16kHz copies
echo "  Resampling positive WAVs to 16kHz (this may take a few minutes)..."
idx=0
for src_dir in "${POSITIVE_SOURCES[@]}"; do
  if [[ -d "${src_dir}" ]]; then
    for f in "${src_dir}"/*.wav; do
      [[ -f "$f" ]] || continue
      resample_to_16k "$f" "${POS_TRAIN}/pos_$(printf '%05d' $idx).wav"
      idx=$((idx + 1))
    done
    echo "  Positive train: ${src_dir} (running total: ${idx})"
  fi
done
if (( idx == 0 )); then
  echo "ERROR: no positive training WAVs were staged." >&2
  exit 2
fi

# Hold out ~15% for test (deterministic: every 7th file)
test_idx=0
for f in "${POS_TRAIN}"/pos_*.wav; do
  i=$(basename "$f" | sed 's/pos_0*//;s/\.wav//')
  if (( i % 7 == 0 )); then
    mv "$f" "${POS_TEST}/pos_test_$(printf '%05d' $test_idx).wav"
    test_idx=$((test_idx + 1))
  fi
done
pos_train_count=$(find "${POS_TRAIN}" -name "*.wav" | wc -l)
pos_test_count=$(find "${POS_TEST}" -name "*.wav" | wc -l)
if (( pos_train_count == 0 || pos_test_count == 0 )); then
  echo "ERROR: positive split produced empty train/test set (${pos_train_count}/${pos_test_count})." >&2
  exit 2
fi
echo "  Positive: ${pos_train_count} train, ${pos_test_count} test"

# Negative sources -- resample to 16kHz copies
echo "  Resampling negative WAVs to 16kHz..."
neg_idx=0
for src_dir in "${NEGATIVE_SOURCES[@]}"; do
  if [[ -d "${src_dir}" ]]; then
    for f in "${src_dir}"/*.wav; do
      [[ -f "$f" ]] || continue
      resample_to_16k "$f" "${NEG_TRAIN}/neg_$(printf '%05d' $neg_idx).wav"
      neg_idx=$((neg_idx + 1))
    done
    echo "  Negative train: ${src_dir} (running total: ${neg_idx})"
  fi
done
if (( neg_idx == 0 )); then
  echo "ERROR: no negative training WAVs were staged." >&2
  exit 2
fi

# Negative test: held-out XTTS isa -- resample to 16kHz copies
for f in "${NEGATIVE_TEST_SOURCE}"/*.wav; do
  [[ -f "$f" ]] || continue
  resample_to_16k "$f" "${NEG_TEST}/$(basename "$f")"
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
if [[ ! -f "\${VAL_FEATURES}" ]]; then
  echo "Downloading validation_set_features.npy from HuggingFace (~280MB)..."
  wget --tries=3 --timeout=30 --waitretry=5 -q -O "\${VAL_FEATURES}" \
    "https://huggingface.co/datasets/davidscripka/openwakeword_features/resolve/main/validation_set_features.npy"
fi

# Patch steps in config
TMP_CONFIG=\$(mktemp /tmp/oww_config_${TAG}.XXXXXX.yaml)
trap 'rm -f "\${TMP_CONFIG}"' EXIT
sed "s/^steps: .*/steps: ${STEPS}/" "${CONFIG}" > "\${TMP_CONFIG}"

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

echo "Training complete. Model at: ${OWW_OUTPUT}/kuule_kratt/"
EOF
)"

echo "Submitted ${JOB_NAME} as job ${JOB_ID}"
echo "Log: ${LOG_PATH/\%j/${JOB_ID}}"
echo "Resources: partition=${PARTITION} time=${TIME_LIMIT} mem=${MEMORY} gres=${GRES}"
