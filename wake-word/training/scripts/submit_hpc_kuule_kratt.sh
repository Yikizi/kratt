#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/kratt_paths.sh
source "${SCRIPT_DIR}/lib/kratt_paths.sh"

ROOT_DIR="$(kratt_project_root)"
DATA_ROOT="$(kratt_data_root)"
PROCESSED_DIR="$(kratt_processed_dir)"
DATASETS_DIR="$(kratt_datasets_dir)"
RUNS_DIR="$(kratt_training_runs_dir)"

TRAINING_STEPS="10000"
NEGATIVE_LIMIT="5000"
TIME_LIMIT="02:30:00"
CPUS="4"
MEM="16G"
EXPERIMENT_TAG="v1"

CV_ROOT="${DATASETS_DIR}/common-voice-et/cv-corpus-24.0-2025-12-05/et"
CV_WAV_DIR="${DATASETS_DIR}/common-voice-et-wav"
POSITIVE_MIC1="${DATASETS_DIR}/kuule-kratt/positive/mic1"
POSITIVE_MIC2="${DATASETS_DIR}/kuule-kratt/positive/mic2"
AMBIENT_DIR="${DATASETS_DIR}/musan/musan/noise"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --training-steps) TRAINING_STEPS="$2"; shift 2 ;;
    --negative-limit) NEGATIVE_LIMIT="$2"; shift 2 ;;
    --time) TIME_LIMIT="$2"; shift 2 ;;
    --cpus) CPUS="$2"; shift 2 ;;
    --mem) MEM="$2"; shift 2 ;;
    --tag) EXPERIMENT_TAG="$2"; shift 2 ;;
    *) echo "Unknown: $1" >&2; exit 2 ;;
  esac
done

OUTPUT_DIR="${PROCESSED_DIR}/experiments/kuule_kratt_${EXPERIMENT_TAG}"

if ! command -v sbatch >/dev/null 2>&1; then
  echo "sbatch not found. Run on Slurm login node." >&2
  exit 2
fi

for d in "${CV_ROOT}" "${POSITIVE_MIC1}" "${POSITIVE_MIC2}" "${AMBIENT_DIR}"; do
  if [[ ! -d "${d}" ]]; then
    echo "Missing: ${d}" >&2
    exit 2
  fi
done

mkdir -p "${RUNS_DIR}/logs"

JOB_NAME="kratt-kuule-kratt-${EXPERIMENT_TAG}"
LOG_PATH="${RUNS_DIR}/logs/${JOB_NAME}-%j.out"

JOB_ID="$(
  sbatch \
    --parsable \
    --job-name="${JOB_NAME}" \
    --account=Project_tanel_alumae \
    --time="${TIME_LIMIT}" \
    --cpus-per-task="${CPUS}" \
    --mem="${MEM}" \
    --chdir="${ROOT_DIR}" \
    --output="${LOG_PATH}" \
    --error="${LOG_PATH}" \
    --export=ALL,KRATT_ROOT="${ROOT_DIR}",KRATT_DATA="${DATA_ROOT}" <<EOF
#!/usr/bin/env bash
set -euo pipefail

echo "Slurm job: \${SLURM_JOB_ID}"
echo "Repo root: ${ROOT_DIR}"
echo "Data root: ${DATA_ROOT}"

# Step 1: Convert CV MP3 → WAV (one-time, cached)
echo "=== Step 1: Convert Common Voice MP3 → WAV ==="
bash "${ROOT_DIR}/wake-word/training/scripts/convert_cv_mp3_to_wav.sh" \
  "${CV_ROOT}/clips" \
  "${CV_WAV_DIR}" \
  "${NEGATIVE_LIMIT}"

# Step 2: Prepare experiment directory (symlinks only)
echo "=== Step 2: Prepare experiment directory ==="
"${ROOT_DIR}/wake-word/.venv/bin/python" \
  "${ROOT_DIR}/wake-word/training/scripts/prepare_kuule_kratt_experiment.py" \
  --positive-dirs "${POSITIVE_MIC1}" "${POSITIVE_MIC2}" \
  --cv-root "${CV_ROOT}" \
  --cv-wav-dir "${CV_WAV_DIR}" \
  --ambient-dir "${AMBIENT_DIR}" \
  --output-dir "${OUTPUT_DIR}" \
  --negative-limit ${NEGATIVE_LIMIT} \
  --force

# Step 3: Train (same script as marvin)
echo "=== Step 3: Train ==="
"${ROOT_DIR}/wake-word/training/scripts/train_microwakeword_experiment.sh" \
  --experiment-name "microwakeword-kuule-kratt-${EXPERIMENT_TAG}" \
  --positive-dir "${OUTPUT_DIR}/positive_samples" \
  --negative-dir "${OUTPUT_DIR}/negative_samples" \
  --ambient-dir "${OUTPUT_DIR}/ambient_samples" \
  --training-steps "${TRAINING_STEPS}"
EOF
)"

echo "Submitted ${JOB_NAME} as job ${JOB_ID}"
echo "Log: ${LOG_PATH/\%j/${JOB_ID}}"
