#!/usr/bin/env bash
# Submit a Kratt-only microWakeWord ablation to SLURM.
#
# This is intentionally separate from submit_hpc_kuule_kratt.sh because the
# target policy is different: any clean utterance of the word "Kratt" should be
# positive, while Kratt-like target-free words should be negatives. Do not feed
# the old two-word positive sources or old hard-negative sets blindly here.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/kratt_paths.sh
source "${SCRIPT_DIR}/lib/kratt_paths.sh"

ROOT_DIR="$(kratt_project_root)"
DATA_ROOT="$(kratt_data_root)"
PROCESSED_DIR="$(kratt_processed_dir)"
DATASETS_DIR="$(kratt_datasets_dir)"
RUNS_DIR="$(kratt_training_runs_dir)"

EXPERIMENT_TAG="v19-kratt-only-smoke"
TRAINING_STEPS="15000,5000"
CLIP_DURATION_MS="1000"
NEGATIVE_LIMIT="5000"
TIME_LIMIT="08:00:00"
PARTITION="common"
CPUS="4"
MEM="48G"
DRY_RUN=0

USE_RECALL_PROFILE=1
USE_SPEC_AUGMENT=1
POINTWISE_FILTERS="96,96,96,96"
TARGET_MINIMIZATION="20"
NEG_CLASS_WEIGHT_FLAG=""
LEARNING_RATES_FLAG=""
VTLP_FLAG=""
AUG_PROFILE_FLAG=""
RESIDUAL_FLAG=""

POSITIVE_MIN_DURATION_S="0.40"
POSITIVE_MAX_DURATION_S="1.20"
KRATT_ONLY_POS_DIR="${PROCESSED_DIR}/positive_kratt_only_v19a/accepted"
KRATT_ONLY_REAL_REVIEWED_POS_DIR="${PROCESSED_DIR}/positive_kratt_only_real_voice_probe_kguard_reviewed/accepted"
INCLUDE_REVIEWED_REAL_POSITIVES=0
CUSTOM_EXTRA_POSITIVE_DIRS=""
CUSTOM_EXTRA_NEGATIVE_DIRS=""
CUSTOM_EXTRA_AMBIENT_DIRS=""

USE_MUSAN_SPEECH=1
USE_MUSAN_MUSIC=1
RIIGIKOGU_FILE_LIMIT=50
INCLUDE_BASE_EXTRA_NEGS=1

CV_ROOT="${DATASETS_DIR}/common-voice-et/cv-corpus-24.0-2025-12-05/et"
CV_WAV_DIR="${DATASETS_DIR}/common-voice-et-wav"
AMBIENT_DIR="${DATASETS_DIR}/musan/musan/noise"
MUSAN_NOISE_DIR="${DATASETS_DIR}/musan/musan/noise"
MIT_IR_DIR="${DATASETS_DIR}/benchmarks/mit-impulse-responses/16khz"
MUSAN_SPEECH_DIR="${DATASETS_DIR}/musan/musan/speech"
MUSAN_MUSIC_DIR="${DATASETS_DIR}/musan/musan/music"
RIIGIKOGU_DIR="${DATASETS_DIR}/riigikogu-stenograms/audio"

KORVO2_NEG_DIR="${PROCESSED_DIR}/negative_korvo2"
KORVO2_NEG_EXTRA_DIR="${PROCESSED_DIR}/negative_korvo2_extra"
KORVO2_NEG_S2_DIR="${PROCESSED_DIR}/negative_korvo2_session2"
KORVO2_AMB_DIR="${PROCESSED_DIR}/ambient_korvo2"
MACBOOK_NEG_DIR="${PROCESSED_DIR}/negative_macbook_segmented"
MINED_FALSE_NEG_V10_DIR="${PROCESSED_DIR}/negative_mined_false_accepts_v10_train"
RAW_MINED_FALSE_ACCEPTS="${DATA_ROOT}/raw/mined_false_accepts"
FAPH_CV_TEST_DIR="${PROCESSED_DIR}/faph_test_cv_et"

usage() {
  cat <<'EOF'
Usage:
  submit_hpc_kratt_only.sh --tag TAG [options]

Core options:
  --tag TAG                         Experiment tag (default: v19-kratt-only-smoke)
  --positive-dir DIR                Clean Kratt-only positive dir (default: positive_kratt_only_v19a/accepted)
  --include-reviewed-real-positives Include reviewed real-source accepted cuts (off by default)
  --extra-positive-dirs CSV         Additional positive dirs (comma-separated)
  --training-steps CSV              Training phases (default: 15000,5000)
  --clip-duration-ms N              Model clip duration (default: 1000 for one-word Kratt)
  --negative-limit N                Common Voice conversion/negative limit (default: 5000)
  --time HH:MM:SS                   Slurm time (default: 08:00:00)
  --partition NAME                  Slurm partition (default: common; short max is 4h)
  --mem MEM                         Slurm memory (default: 48G)
  --dry-run                         Print submit plan only

Training knobs:
  --recall-profile / --no-recall-profile
  --spec-augment / --no-spec-augment
  --pointwise-filters CSV           Default: 96,96,96,96
  --target-minimization FAPH        Default: 20
  --neg-class-weight N
  --learning-rates CSV
  --no-vtlp
  --vtlp-prob P
  --aug-profile NAME
  --residual / --no-residual

Negative/augmentation knobs:
  --no-base-extra-negs
  --extra-negative-dirs CSV
  --extra-ambient-dirs CSV
  --no-musan / --no-musan-speech / --no-musan-music
  --riigikogu-files N / --no-riigikogu
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag) EXPERIMENT_TAG="$2"; shift 2 ;;
    --positive-dir) KRATT_ONLY_POS_DIR="$2"; shift 2 ;;
    --include-reviewed-real-positives) INCLUDE_REVIEWED_REAL_POSITIVES=1; shift 1 ;;
    --extra-positive-dirs) CUSTOM_EXTRA_POSITIVE_DIRS="$2"; shift 2 ;;
    --training-steps) TRAINING_STEPS="$2"; shift 2 ;;
    --clip-duration-ms) CLIP_DURATION_MS="$2"; shift 2 ;;
    --negative-limit) NEGATIVE_LIMIT="$2"; shift 2 ;;
    --time) TIME_LIMIT="$2"; shift 2 ;;
    --partition) PARTITION="$2"; shift 2 ;;
    --cpus) CPUS="$2"; shift 2 ;;
    --mem) MEM="$2"; shift 2 ;;
    --positive-min-duration-s) POSITIVE_MIN_DURATION_S="$2"; shift 2 ;;
    --positive-max-duration-s) POSITIVE_MAX_DURATION_S="$2"; shift 2 ;;
    --no-positive-duration-filter) POSITIVE_MIN_DURATION_S="0"; POSITIVE_MAX_DURATION_S="0"; shift 1 ;;
    --recall-profile) USE_RECALL_PROFILE=1; shift 1 ;;
    --no-recall-profile) USE_RECALL_PROFILE=0; shift 1 ;;
    --spec-augment) USE_SPEC_AUGMENT=1; shift 1 ;;
    --no-spec-augment) USE_SPEC_AUGMENT=0; shift 1 ;;
    --pointwise-filters) POINTWISE_FILTERS="$2"; shift 2 ;;
    --target-minimization) TARGET_MINIMIZATION="$2"; shift 2 ;;
    --neg-class-weight) NEG_CLASS_WEIGHT_FLAG="--neg-class-weight $2"; shift 2 ;;
    --learning-rates) LEARNING_RATES_FLAG="--learning-rates \"$2\""; shift 2 ;;
    --no-vtlp) VTLP_FLAG="--no-vtlp"; shift 1 ;;
    --vtlp-prob) VTLP_FLAG="--vtlp-prob $2"; shift 2 ;;
    --aug-profile) AUG_PROFILE_FLAG="--aug-profile $2"; shift 2 ;;
    --residual) RESIDUAL_FLAG="--residual"; shift 1 ;;
    --no-residual) RESIDUAL_FLAG="--no-residual"; shift 1 ;;
    --no-base-extra-negs) INCLUDE_BASE_EXTRA_NEGS=0; shift 1 ;;
    --extra-negative-dirs) CUSTOM_EXTRA_NEGATIVE_DIRS="$2"; shift 2 ;;
    --extra-ambient-dirs) CUSTOM_EXTRA_AMBIENT_DIRS="$2"; shift 2 ;;
    --no-musan) USE_MUSAN_SPEECH=0; USE_MUSAN_MUSIC=0; shift 1 ;;
    --no-musan-speech) USE_MUSAN_SPEECH=0; shift 1 ;;
    --no-musan-music) USE_MUSAN_MUSIC=0; shift 1 ;;
    --riigikogu-files) RIIGIKOGU_FILE_LIMIT="$2"; shift 2 ;;
    --no-riigikogu) RIIGIKOGU_FILE_LIMIT=0; shift 1 ;;
    --dry-run) DRY_RUN=1; shift 1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown: $1" >&2; usage >&2; exit 2 ;;
  esac
done

OUTPUT_DIR="${PROCESSED_DIR}/experiments/kratt_only_${EXPERIMENT_TAG}"
JOB_NAME="kratt-only-${EXPERIMENT_TAG}"
LOG_PATH="${RUNS_DIR}/logs/${JOB_NAME}-%j.out"

POSITIVE_DIRS=("${KRATT_ONLY_POS_DIR}")
if [[ "${INCLUDE_REVIEWED_REAL_POSITIVES}" == "1" ]]; then
  POSITIVE_DIRS+=("${KRATT_ONLY_REAL_REVIEWED_POS_DIR}")
fi
if [[ -n "${CUSTOM_EXTRA_POSITIVE_DIRS}" ]]; then
  IFS=',' read -r -a _custom_pos <<< "${CUSTOM_EXTRA_POSITIVE_DIRS}"
  POSITIVE_DIRS+=("${_custom_pos[@]}")
fi

EXTRA_NEG_LIST=""
append_csv_dir_if_exists() {
  local d="$1"
  if [[ -d "${d}" ]]; then
    EXTRA_NEG_LIST="${EXTRA_NEG_LIST:+${EXTRA_NEG_LIST},}${d}"
    echo "Including extra negatives: ${d}"
  fi
}

if [[ "${INCLUDE_BASE_EXTRA_NEGS}" == "1" ]]; then
  for neg_d in \
    "${KORVO2_NEG_DIR}" "${KORVO2_NEG_EXTRA_DIR}" "${KORVO2_NEG_S2_DIR}" \
    "${MACBOOK_NEG_DIR}" "${MINED_FALSE_NEG_V10_DIR}" "${RAW_MINED_FALSE_ACCEPTS}"; do
    append_csv_dir_if_exists "${neg_d}"
  done
fi
if [[ "${USE_MUSAN_SPEECH}" == "1" ]]; then append_csv_dir_if_exists "${MUSAN_SPEECH_DIR}"; fi
if [[ "${USE_MUSAN_MUSIC}" == "1" ]]; then append_csv_dir_if_exists "${MUSAN_MUSIC_DIR}"; fi
if [[ "${RIIGIKOGU_FILE_LIMIT}" -gt 0 ]] && [[ -d "${RIIGIKOGU_DIR}" ]]; then
  RIIGIKOGU_SUBSET="${PROCESSED_DIR}/riigikogu_subset_${RIIGIKOGU_FILE_LIMIT}"
  if [[ ! -d "${RIIGIKOGU_SUBSET}" && "${DRY_RUN}" != "1" ]]; then
    echo "Creating Riigikogu subset (${RIIGIKOGU_FILE_LIMIT} files)..."
    mkdir -p "${RIIGIKOGU_SUBSET}"
    find "${RIIGIKOGU_DIR}" -name "*.flac" | awk 'BEGIN{srand(42)}{print rand()"\t"$0}' | sort -n | cut -f2 | head -n "${RIIGIKOGU_FILE_LIMIT}" | while read -r f; do
      ln -sf "$f" "${RIIGIKOGU_SUBSET}/$(basename "$f")"
    done
  fi
  if [[ -d "${RIIGIKOGU_SUBSET}" || "${DRY_RUN}" == "1" ]]; then
    EXTRA_NEG_LIST="${EXTRA_NEG_LIST:+${EXTRA_NEG_LIST},}${RIIGIKOGU_SUBSET}"
    echo "Including Riigikogu subset: ${RIIGIKOGU_SUBSET}"
  fi
fi
if [[ -n "${CUSTOM_EXTRA_NEGATIVE_DIRS}" ]]; then
  EXTRA_NEG_LIST="${EXTRA_NEG_LIST:+${EXTRA_NEG_LIST},}${CUSTOM_EXTRA_NEGATIVE_DIRS}"
  echo "Including custom extra negative dirs: ${CUSTOM_EXTRA_NEGATIVE_DIRS}"
fi

EXTRA_AMB_LIST=""
if [[ -d "${KORVO2_AMB_DIR}" ]]; then
  EXTRA_AMB_LIST="${KORVO2_AMB_DIR}"
fi
if [[ -n "${CUSTOM_EXTRA_AMBIENT_DIRS}" ]]; then
  EXTRA_AMB_LIST="${EXTRA_AMB_LIST:+${EXTRA_AMB_LIST},}${CUSTOM_EXTRA_AMBIENT_DIRS}"
fi

printf -v POSITIVE_DIR_ARGS ' %q' "${POSITIVE_DIRS[@]}"
EXTRA_NEG_ARGS=""
[[ -n "${EXTRA_NEG_LIST}" ]] && EXTRA_NEG_ARGS="--extra-negative-dirs ${EXTRA_NEG_LIST}"
EXTRA_AMB_ARGS=""
[[ -n "${EXTRA_AMB_LIST}" ]] && EXTRA_AMB_ARGS="--extra-ambient-dirs ${EXTRA_AMB_LIST}"
EXCLUDE_NEGATIVE_ARGS=""
[[ -d "${FAPH_CV_TEST_DIR}" || "${DRY_RUN}" == "1" ]] && EXCLUDE_NEGATIVE_ARGS="--exclude-negative-wav-dirs ${FAPH_CV_TEST_DIR}"
EXCLUDE_CV_SPLIT_ARGS="--exclude-cv-split-skip 5000 --exclude-cv-split-limit 2000 --exclude-cv-split-exclude-words kratt kuule"
POSITIVE_DURATION_ARGS="--positive-min-duration-s ${POSITIVE_MIN_DURATION_S} --positive-max-duration-s ${POSITIVE_MAX_DURATION_S}"
RECALL_PROFILE_FLAG=""
[[ "${USE_RECALL_PROFILE}" == "1" ]] && RECALL_PROFILE_FLAG="--recall-profile"
SPEC_AUGMENT_FLAG=""
[[ "${USE_SPEC_AUGMENT}" == "1" ]] && SPEC_AUGMENT_FLAG="--spec-augment"
POINTWISE_FILTERS_FLAG="--pointwise-filters ${POINTWISE_FILTERS}"
TARGET_MINIMIZATION_FLAG="--target-minimization ${TARGET_MINIMIZATION}"

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "DRY RUN: skipping sbatch and required HPC directory checks"
  echo
  echo "=== KRATT-ONLY DRY RUN SUMMARY ==="
  echo "job_name: ${JOB_NAME}"
  echo "target_policy: single word 'Kratt' should trigger; two-word exact phrase policy is not used"
  echo "partition: ${PARTITION}"
  echo "time_limit: ${TIME_LIMIT}"
  echo "output_dir: ${OUTPUT_DIR}"
  echo "positive_dirs:${POSITIVE_DIR_ARGS}"
  echo "positive_duration_filter: min=${POSITIVE_MIN_DURATION_S}s max=${POSITIVE_MAX_DURATION_S}s"
  echo "cv_exclude_words: kratt"
  echo "negative_limit: ${NEGATIVE_LIMIT}"
  echo "extra_neg_dirs: ${EXTRA_NEG_LIST:-<none>}"
  echo "extra_ambient_dirs: ${EXTRA_AMB_LIST:-<none>}"
  echo "exclude_negative_wav_dirs: ${FAPH_CV_TEST_DIR}"
  echo "exclude_cv_split_args: ${EXCLUDE_CV_SPLIT_ARGS}"
  echo "hard_neg_feature_set: disabled by default for first Kratt-only ablation"
  echo "training_steps: ${TRAINING_STEPS}"
  echo "clip_duration_ms: ${CLIP_DURATION_MS}"
  echo "recall_profile: ${USE_RECALL_PROFILE}"
  echo "spec_augment: ${USE_SPEC_AUGMENT}"
  echo "pointwise_filters: ${POINTWISE_FILTERS}"
  echo "target_minimization: ${TARGET_MINIMIZATION}"
  echo "vtlp_flag: ${VTLP_FLAG:-<default>}"
  echo "neg_class_weight_flag: ${NEG_CLASS_WEIGHT_FLAG:-<default>}"
  echo "learning_rates_flag: ${LEARNING_RATES_FLAG:-<default>}"
  echo "aug_profile_flag: ${AUG_PROFILE_FLAG:-<default>}"
  echo "residual_flag: ${RESIDUAL_FLAG:-<default>}"
  echo
  echo "NOTE: local dry-run uses the current machine's KRATT_DATA. Real submit runs on HPC with KRATT_DATA=/gpfs/mariana/smbhome/malinh/kratt-data."
  echo "      Before real submit, sync repo + ${PROCESSED_DIR}/positive_kratt_only_v19a to HPC."
  exit 0
fi

if ! command -v sbatch >/dev/null 2>&1; then
  echo "sbatch not found. Run on Slurm login node." >&2
  exit 2
fi
for d in "${CV_ROOT}" "${CV_WAV_DIR}" "${AMBIENT_DIR}" "${POSITIVE_DIRS[@]}"; do
  if [[ ! -d "${d}" ]]; then
    echo "Missing required dir: ${d}" >&2
    exit 2
  fi
done

mkdir -p "${RUNS_DIR}/logs"

JOB_ID="$(
  sbatch \
    --parsable \
    --job-name="${JOB_NAME}" \
    --account=Project_tanel_alumae \
    --partition="${PARTITION}" \
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
echo "Target policy: Kratt-only single word"

if [[ "${NEGATIVE_LIMIT}" == "-1" ]]; then
  echo "=== Step 1: SKIPPED CV conversion (NEGATIVE_LIMIT=${NEGATIVE_LIMIT}) ==="
else
  echo "=== Step 1: Convert Common Voice MP3 -> WAV ==="
  bash "${ROOT_DIR}/wake-word/training/scripts/convert_cv_mp3_to_wav.sh" \
    "${CV_ROOT}/clips" \
    "${CV_WAV_DIR}" \
    "${NEGATIVE_LIMIT}"
fi

echo "=== Step 2: Prepare Kratt-only experiment directory ==="
"${ROOT_DIR}/wake-word/.venv/bin/python" \
  "${ROOT_DIR}/wake-word/training/scripts/prepare_kuule_kratt_experiment.py" \
  --positive-dirs ${POSITIVE_DIR_ARGS} \
  --cv-root "${CV_ROOT}" \
  --cv-wav-dir "${CV_WAV_DIR}" \
  --ambient-dir "${AMBIENT_DIR}" \
  --output-dir "${OUTPUT_DIR}" \
  --negative-limit ${NEGATIVE_LIMIT} \
  --force \
  --exclude-words kratt \
  ${EXCLUDE_NEGATIVE_ARGS} \
  ${POSITIVE_DURATION_ARGS} \
  ${EXCLUDE_CV_SPLIT_ARGS} \
  ${EXTRA_NEG_ARGS} \
  ${EXTRA_AMB_ARGS}

echo "=== Step 3: Train Kratt-only microWakeWord ==="
TRAIN_BG_NOISE_ARG=""
if [[ -d "${MUSAN_NOISE_DIR}" ]]; then
  TRAIN_BG_NOISE_ARG="--background-noise-dir ${MUSAN_NOISE_DIR}"
fi
TRAIN_IR_ARG=""
if [[ -d "${MIT_IR_DIR}" ]]; then
  TRAIN_IR_ARG="--impulse-response-dir ${MIT_IR_DIR}"
fi

"${ROOT_DIR}/wake-word/training/scripts/train_microwakeword_experiment.sh" \
  --experiment-name "microwakeword-kratt-only-${EXPERIMENT_TAG}" \
  --positive-dir "${OUTPUT_DIR}/positive_samples" \
  --negative-dir "${OUTPUT_DIR}/negative_samples" \
  --ambient-dir "${OUTPUT_DIR}/ambient_samples" \
  \${TRAIN_BG_NOISE_ARG} \
  \${TRAIN_IR_ARG} \
  ${RECALL_PROFILE_FLAG} \
  ${SPEC_AUGMENT_FLAG} \
  ${POINTWISE_FILTERS_FLAG} \
  ${RESIDUAL_FLAG} \
  --training-steps "${TRAINING_STEPS}" \
  --clip-duration-ms "${CLIP_DURATION_MS}" \
  ${VTLP_FLAG} \
  ${NEG_CLASS_WEIGHT_FLAG} \
  ${LEARNING_RATES_FLAG} \
  ${AUG_PROFILE_FLAG} \
  ${TARGET_MINIMIZATION_FLAG}
EOF
)"

echo "Submitted ${JOB_NAME} as job ${JOB_ID}"
echo "Log: ${LOG_PATH/\%j/${JOB_ID}}"
