#!/usr/bin/env bash
set -euo pipefail
# Submit openWakeWord training to HPC GPU queue.
# Uses our pre-recorded WAVs (skips Piper TTS generation).
#
# Usage:
#   bash submit_hpc_openwakeword.sh [--tag v1] [--steps 50000]

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

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag)   TAG="$2"; shift 2 ;;
    --steps) STEPS="$2"; shift 2 ;;
    *)       echo "Unknown: $1" >&2; exit 2 ;;
  esac
done

OWW_OUTPUT="${DATA_ROOT}/training/openwakeword"
OWW_MODEL_DIR="${OWW_OUTPUT}/kuule_kratt"

echo "=== Preparing openWakeWord data ==="

# Create directory structure with our WAVs (symlinks)
ssh_or_local() { eval "$@"; }

mkdir -p "${OWW_MODEL_DIR}/positive_train" \
         "${OWW_MODEL_DIR}/positive_test" \
         "${OWW_MODEL_DIR}/negative_train" \
         "${OWW_MODEL_DIR}/negative_test"

# Positive train: KORVO-2 mic1+mic2 + TTS + SSML + XTTS (same as microWakeWord v6+ positives)
POS_TRAIN="${OWW_MODEL_DIR}/positive_train"
POS_TEST="${OWW_MODEL_DIR}/positive_test"
NEG_TRAIN="${OWW_MODEL_DIR}/negative_train"
NEG_TEST="${OWW_MODEL_DIR}/negative_test"

# Clear and re-link (idempotent)
find "${POS_TRAIN}" -type l -delete 2>/dev/null || true
find "${POS_TEST}" -type l -delete 2>/dev/null || true
find "${NEG_TRAIN}" -type l -delete 2>/dev/null || true
find "${NEG_TEST}" -type l -delete 2>/dev/null || true

# Positive sources
idx=0
for src_dir in \
  "${DATASETS_DIR}/kuule-kratt/positive/mic1" \
  "${DATASETS_DIR}/kuule-kratt/positive/mic2" \
  "${PROCESSED_DIR}/positive_tts" \
  "${PROCESSED_DIR}/positive_tts_ssml" \
  "${DATA_ROOT}/raw/xtts_clones/marta/positive" \
  "${DATA_ROOT}/raw/xtts_clones/annam/positive" \
  "${DATA_ROOT}/raw/xtts_clones/ema/positive"
do
  if [[ -d "${src_dir}" ]]; then
    for f in "${src_dir}"/*.wav; do
      [[ -f "$f" ]] || continue
      ln -sf "$f" "${POS_TRAIN}/pos_$(printf '%05d' $idx).wav"
      idx=$((idx + 1))
    done
    echo "  Positive train: ${src_dir} (running total: ${idx})"
  fi
done

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
echo "  Positive: ${pos_train_count} train, ${pos_test_count} test"

# Negative sources (TTS hard neg only — oWW has its own 31Kh built-in negatives)
neg_idx=0
for src_dir in \
  "${PROCESSED_DIR}/negative_tts_hard" \
  "${PROCESSED_DIR}/negative_tts_hard_v2" \
  "${DATA_ROOT}/augmented/hard_neg_mattias_mac_train" \
  "${DATA_ROOT}/raw/xtts_clones/marta/negative" \
  "${DATA_ROOT}/raw/xtts_clones/annam/negative" \
  "${DATA_ROOT}/raw/xtts_clones/ema/negative"
do
  if [[ -d "${src_dir}" ]]; then
    for f in "${src_dir}"/*.wav; do
      [[ -f "$f" ]] || continue
      ln -sf "$f" "${NEG_TRAIN}/neg_$(printf '%05d' $neg_idx).wav"
      neg_idx=$((neg_idx + 1))
    done
    echo "  Negative train: ${src_dir} (running total: ${neg_idx})"
  fi
done

# Negative test: held-out XTTS isa
for f in "${PROCESSED_DIR}/test_hard_neg_xtts_isa"/*.wav; do
  [[ -f "$f" ]] || continue
  ln -sf "$f" "${NEG_TEST}/$(basename "$f")"
done
neg_train_count=$(find "${NEG_TRAIN}" -name "*.wav" | wc -l)
neg_test_count=$(find "${NEG_TEST}" -name "*.wav" | wc -l)
echo "  Negative: ${neg_train_count} train, ${neg_test_count} test"

echo ""
echo "=== Submitting openWakeWord GPU job (tag: ${TAG}) ==="

RUNS_DIR="${DATA_ROOT}/training/runs"
mkdir -p "${RUNS_DIR}/logs"
JOB_NAME="kratt-oww-${TAG}"
LOG_PATH="${RUNS_DIR}/logs/${JOB_NAME}-%j.out"

JOB_ID="$(
  sbatch \
    --parsable \
    --job-name="${JOB_NAME}" \
    --account=Project_tanel_alumae \
    --partition=gpu \
    --gres=gpu:1 \
    --time=02:00:00 \
    --cpus-per-task=8 \
    --mem=32G \
    --chdir="${ROOT_DIR}" \
    --output="${LOG_PATH}" \
    --error="${LOG_PATH}" <<EOF
#!/usr/bin/env bash
set -euo pipefail

echo "openWakeWord training: ${TAG}"
echo "GPU: \$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
echo "Positive: ${pos_train_count} train, ${pos_test_count} test"
echo "Negative: ${neg_train_count} train, ${neg_test_count} test"

# Patch steps in config
sed "s/^steps: .*/steps: ${STEPS}/" "${CONFIG}" > /tmp/oww_config_${TAG}.yaml

${OWW_VENV}/bin/python -m openwakeword.train \
  --training_config /tmp/oww_config_${TAG}.yaml \
  --augment_clips \
  --train_model

echo "Training complete. Model at: ${OWW_OUTPUT}/kuule_kratt/"
EOF
)"

echo "Submitted ${JOB_NAME} as job ${JOB_ID}"
echo "Log: ${LOG_PATH/\%j/${JOB_ID}}"
