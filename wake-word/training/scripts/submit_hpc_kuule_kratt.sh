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
KORVO2_NEG_DIR="${PROCESSED_DIR}/negative_korvo2"
KORVO2_NEG_EXTRA_DIR="${PROCESSED_DIR}/negative_korvo2_extra"
KORVO2_NEG_S2_DIR="${PROCESSED_DIR}/negative_korvo2_session2"
KORVO2_AMB_DIR="${PROCESSED_DIR}/ambient_korvo2"
TTS_POS_DIR="${PROCESSED_DIR}/positive_tts"
TTS_SSML_POS_DIR="${PROCESSED_DIR}/positive_tts_ssml"
TTS_HARD_NEG_DIR="${PROCESSED_DIR}/negative_tts_hard"
TTS_HARD_NEG_V2_DIR="${PROCESSED_DIR}/negative_tts_hard_v2"

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

# Build extra positive dirs (TTS + SSML)
EXTRA_POS=""
for pos_d in "${TTS_POS_DIR}" "${TTS_SSML_POS_DIR}"; do
  if [[ -d "${pos_d}" ]]; then
    EXTRA_POS="${EXTRA_POS} ${pos_d}"
    echo "Including extra positives: ${pos_d}"
  fi
done

# Build extra negative dirs (same-device + TTS hard negatives)
EXTRA_NEG_LIST=""
for neg_d in "${KORVO2_NEG_DIR}" "${KORVO2_NEG_EXTRA_DIR}" "${KORVO2_NEG_S2_DIR}" "${TTS_HARD_NEG_DIR}" "${TTS_HARD_NEG_V2_DIR}"; do
  if [[ -d "${neg_d}" ]]; then
    EXTRA_NEG_LIST="${EXTRA_NEG_LIST:+${EXTRA_NEG_LIST},}${neg_d}"
    echo "Including extra negatives: ${neg_d}"
  fi
done
EXTRA_NEG_ARGS=""
if [[ -n "${EXTRA_NEG_LIST}" ]]; then
  EXTRA_NEG_ARGS="--extra-negative-dirs ${EXTRA_NEG_LIST}"
fi

EXTRA_AMB_ARGS=""
if [[ -d "${KORVO2_AMB_DIR}" ]]; then
  EXTRA_AMB_ARGS="--extra-ambient-dirs ${KORVO2_AMB_DIR}"
  echo "Including KORVO-2 ambient: ${KORVO2_AMB_DIR}"
fi

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
  --positive-dirs "${POSITIVE_MIC1}" "${POSITIVE_MIC2}" ${EXTRA_POS} \
  --cv-root "${CV_ROOT}" \
  --cv-wav-dir "${CV_WAV_DIR}" \
  --ambient-dir "${AMBIENT_DIR}" \
  --output-dir "${OUTPUT_DIR}" \
  --negative-limit ${NEGATIVE_LIMIT} \
  --force \
  ${EXTRA_NEG_ARGS} \
  ${EXTRA_AMB_ARGS}

# Step 3: Train (same script as marvin)
echo "=== Step 3: Train ==="
"${ROOT_DIR}/wake-word/training/scripts/train_microwakeword_experiment.sh" \
  --experiment-name "microwakeword-kuule-kratt-${EXPERIMENT_TAG}" \
  --positive-dir "${OUTPUT_DIR}/positive_samples" \
  --negative-dir "${OUTPUT_DIR}/negative_samples" \
  --ambient-dir "${OUTPUT_DIR}/ambient_samples" \
  --training-steps "${TRAINING_STEPS}" \
  --spec-augment
EOF
)"

echo "Submitted ${JOB_NAME} as job ${JOB_ID}"
echo "Log: ${LOG_PATH/\%j/${JOB_ID}}"

# Submit notification job that fires when training finishes
PUSHCUT_API_KEY="${PUSHCUT_API_KEY:-}"
if [[ -z "${PUSHCUT_API_KEY}" ]]; then
  echo "PUSHCUT_API_KEY not set, skipping notification"
fi
PUSHCUT_API="https://api.pushcut.io/${PUSHCUT_API_KEY}/notifications/Hpc%20job%20complete"
if [[ -n "${PUSHCUT_API_KEY}" ]]; then
NOTIFY_ID="$(
  sbatch \
    --parsable \
    --dependency=afterany:${JOB_ID} \
    --account=Project_tanel_alumae \
    --partition=short \
    --time=00:05:00 \
    --cpus-per-task=1 \
    --mem=256M \
    --job-name="notify-${EXPERIMENT_TAG}" \
    --wrap="EXIT_CODE=\$(sacct -j ${JOB_ID} --format=ExitCode -n | head -1 | tr -d ' '); curl -s -X POST '${PUSHCUT_API}' -H 'Content-Type: application/json' -d '{\"title\": \"Kuule Kratt ${EXPERIMENT_TAG} done\", \"text\": \"Job ${JOB_ID} finished. Exit: '\${EXIT_CODE}'\"}'"
)"
echo "Notification job: ${NOTIFY_ID} (fires after ${JOB_ID})"
fi
