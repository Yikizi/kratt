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

usage() {
  cat <<EOF
Usage:
  submit_hpc_smoke_run.sh [options]

Options:
  --target-word WORD       Public Speech Commands target word (default: marvin)
  --ambient-dir DIR        Ambient wav directory for false-accept evaluation
  --training-steps N       microWakeWord training steps (default: 250)
  --negative-limit N       Max negative wavs for dataset prep (default: 4000)
  --source-root DIR        Speech Commands root (default: ${DATASETS_DIR}/speech-commands)
  --output-dir DIR         Experiment output dir (default: ${PROCESSED_DIR}/experiments/speech_commands_<word>_hpc_smoke)
  --time HH:MM:SS          Slurm time limit (default: 01:00:00)
  --cpus N                 Slurm cpus-per-task (default: 4)
  --mem SIZE               Slurm memory request (default: 16G)
  -h, --help               Show this help
EOF
}

default_speech_commands_root() {
  local candidate
  for candidate in \
    "${DATASETS_DIR}/speech-commands" \
    "${DATASETS_DIR}/speech_commands" \
    "${ROOT_DIR}/wake-word/data/processed/speech_commands"
  do
    if [[ -d "${candidate}" ]]; then
      printf '%s\n' "${candidate}"
      return
    fi
  done
  printf '%s\n' "${DATASETS_DIR}/speech-commands"
}

TARGET_WORD="marvin"
AMBIENT_DIR=""
TRAINING_STEPS="250"
NEGATIVE_LIMIT="4000"
TIME_LIMIT="01:00:00"
CPUS="4"
MEM="16G"
SOURCE_ROOT="$(default_speech_commands_root)"
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-word)
      TARGET_WORD="$2"
      shift 2
      ;;
    --training-steps)
      TRAINING_STEPS="$2"
      shift 2
      ;;
    --ambient-dir)
      AMBIENT_DIR="$2"
      shift 2
      ;;
    --negative-limit)
      NEGATIVE_LIMIT="$2"
      shift 2
      ;;
    --source-root)
      SOURCE_ROOT="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --time)
      TIME_LIMIT="$2"
      shift 2
      ;;
    --cpus)
      CPUS="$2"
      shift 2
      ;;
    --mem)
      MEM="$2"
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

if [[ -z "${OUTPUT_DIR}" ]]; then
  OUTPUT_DIR="${PROCESSED_DIR}/experiments/speech_commands_${TARGET_WORD}_hpc_smoke"
fi

if ! command -v sbatch >/dev/null 2>&1; then
  echo "sbatch not found. Run this script on the Slurm login node." >&2
  exit 2
fi

if [[ ! -x "${ROOT_DIR}/wake-word/.venv/bin/python" ]]; then
  echo "Missing ${ROOT_DIR}/wake-word/.venv/bin/python" >&2
  echo "Create it first with: cd ${ROOT_DIR}/wake-word && uv sync --extra datasets" >&2
  exit 2
fi

if [[ ! -d "${SOURCE_ROOT}" ]]; then
  echo "Speech Commands root not found: ${SOURCE_ROOT}" >&2
  exit 2
fi
if [[ -z "${AMBIENT_DIR}" ]]; then
  echo "Ambient dir is required. Pass --ambient-dir <dir>." >&2
  exit 2
fi
if [[ ! -d "${AMBIENT_DIR}" ]]; then
  echo "Ambient dir not found: ${AMBIENT_DIR}" >&2
  exit 2
fi

mkdir -p "${RUNS_DIR}/logs"

JOB_NAME="kratt-mww-smoke-${TARGET_WORD}"
LOG_PATH="${RUNS_DIR}/logs/${JOB_NAME}-%j.out"
DF_TARGET="${DATA_ROOT}"
if [[ ! -e "${DF_TARGET}" ]]; then
  DF_TARGET="$(dirname "${DATA_ROOT}")"
fi

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
echo "Disk usage:"
df -h "${DF_TARGET}"

"${ROOT_DIR}/wake-word/.venv/bin/python" "${ROOT_DIR}/wake-word/training/scripts/prepare_speech_commands_experiment.py" \
  --source-root "${SOURCE_ROOT}" \
  --target-word "${TARGET_WORD}" \
  --output-dir "${OUTPUT_DIR}" \
  --ambient-dir "${AMBIENT_DIR}" \
  --negative-limit "${NEGATIVE_LIMIT}" \
  --force

"${ROOT_DIR}/wake-word/training/scripts/train_microwakeword_experiment.sh" \
  --experiment-name "microwakeword-hpc-smoke-${TARGET_WORD}" \
  --positive-dir "${OUTPUT_DIR}/positive_samples" \
  --negative-dir "${OUTPUT_DIR}/negative_samples" \
  --ambient-dir "${OUTPUT_DIR}/ambient_samples" \
  --training-steps "${TRAINING_STEPS}"
EOF
)"

echo "Submitted ${JOB_NAME} as job ${JOB_ID}"
echo "Log: ${LOG_PATH/\%j/${JOB_ID}}"
