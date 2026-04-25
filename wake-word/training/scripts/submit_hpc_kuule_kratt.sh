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

TRAINING_STEPS="15000, 5000"
NEGATIVE_LIMIT="5000"
TIME_LIMIT="04:00:00"
CPUS="4"
MEM="48G"
EXPERIMENT_TAG="v1"
USE_SPEC_AUGMENT=0
USE_TTS_HARD_NEG_IN_HARD_SET=0
VTLP_FLAG=""
NEG_CLASS_WEIGHT_FLAG=""
LEARNING_RATES_FLAG=""
RECALL_PROFILE_FLAG=""
AUG_PROFILE_FLAG=""

CV_ROOT="${DATASETS_DIR}/common-voice-et/cv-corpus-24.0-2025-12-05/et"
CV_WAV_DIR="${DATASETS_DIR}/common-voice-et-wav"
POSITIVE_MIC1="${DATASETS_DIR}/kuule-kratt/positive/mic1"
POSITIVE_MIC2="${DATASETS_DIR}/kuule-kratt/positive/mic2"
AMBIENT_DIR="${DATASETS_DIR}/musan/musan/noise"
# Augmentation resource dirs (background noise for AddBackgroundNoise, IRs for RIR)
MUSAN_NOISE_DIR="${DATASETS_DIR}/musan/musan/noise"
MIT_IR_DIR="${DATASETS_DIR}/benchmarks/mit-impulse-responses/16khz"
# v10: MUSAN speech (~49h LibriVox+US gov) and music (~41h FMA+Jamendo+classical)
MUSAN_SPEECH_DIR="${DATASETS_DIR}/musan/musan/speech"
MUSAN_MUSIC_DIR="${DATASETS_DIR}/musan/musan/music"
# v10: Riigikogu stenograms (~3084h Estonian parliament speech, 16kHz mono FLAC)
RIIGIKOGU_DIR="${DATASETS_DIR}/riigikogu-stenograms/audio"
KORVO2_NEG_DIR="${PROCESSED_DIR}/negative_korvo2"
KORVO2_NEG_EXTRA_DIR="${PROCESSED_DIR}/negative_korvo2_extra"
KORVO2_NEG_S2_DIR="${PROCESSED_DIR}/negative_korvo2_session2"
KORVO2_AMB_DIR="${PROCESSED_DIR}/ambient_korvo2"
MACBOOK_NEG_DIR="${PROCESSED_DIR}/negative_macbook_segmented"
MINED_FALSE_NEG_V10_DIR="${PROCESSED_DIR}/negative_mined_false_accepts_v10_train"
TTS_POS_DIR="${PROCESSED_DIR}/positive_tts"
TTS_SSML_POS_DIR="${PROCESSED_DIR}/positive_tts_ssml"
TTS_HARD_NEG_DIR="${PROCESSED_DIR}/negative_tts_hard"
TTS_HARD_NEG_V2_DIR="${PROCESSED_DIR}/negative_tts_hard_v2"

# v8: real positives + voice-cloned positives
MAC_POS_DIR="${DATA_ROOT}/raw/mattias/positive"
MAC_POS_AUG_DIR="${DATA_ROOT}/augmented/positive_mattias_mac"
XTTS_POS_MARTA="${DATA_ROOT}/raw/xtts_clones/marta/positive"
XTTS_POS_ANNAM="${DATA_ROOT}/raw/xtts_clones/annam/positive"
XTTS_POS_EMA="${DATA_ROOT}/raw/xtts_clones/ema/positive"
# Mattias short pronunciation "kule kratt" (135 clips, recorded 2026-04-14)
MATTIAS_SHORT_POS="${DATA_ROOT}/raw/mattias-short/positive"
# v17: "Kule Kratt" SSML mirror — same SSML variations as Kuule but with short-u spelling
# 969 clips, 12 speakers, 0 deduped (all acoustically distinct from Kuule originals)
TTS_SSML_KULE_POS_DIR="${DATA_ROOT}/raw/neurokone_ssml_kule"

# Isa pos held out for unseen-speaker test (NOT included)

# v8: hard negatives (real + voice-cloned)
MAC_HARD_NEG_DIR="${DATA_ROOT}/augmented/hard_neg_mattias_mac_train"
XTTS_HARD_NEG_MARTA="${DATA_ROOT}/raw/xtts_clones/marta/negative"
XTTS_HARD_NEG_ANNAM="${DATA_ROOT}/raw/xtts_clones/annam/negative"
XTTS_HARD_NEG_EMA="${DATA_ROOT}/raw/xtts_clones/ema/negative"
# Real recorded hard negatives (KORVO-2 mic, Mattias "kuule kraam" etc)
KORVO2_HARD_NEG_DIR="${DATA_ROOT}/raw/hard_neg/segmented"
# OHEM-mined CV ET false triggers (expert-a score >= 0.97, 449 clips)
OHEM_MINED_DIR="${DATA_ROOT}/mined/ohem_expert_a_all_097"
# Isa neg held out for unseen-speaker test (NOT included)

# v8: opt-in flags - only use TTS hard negs in legacy "negative" set if explicitly requested
# v10: learned that separate hard_neg feature set HURTS FAPH (v9 = 76 FAPH vs v6 = 21).
#      Prefer --use-legacy-tts-hard-neg (all negatives in one pool) for best results.
# Dataset presets for clean ablation experiments
# v6-data: mic1+mic2 + positive_tts positives, CV ET + KORVO-2 + TTS hard neg in main pool
# v8-data: full v8 dataset (mic + TTS + SSML + Mac + XTTS clones, separate hard neg set)
# current: everything available (default)
DATASET_PRESET="current"
USE_LEGACY_TTS_HARD_NEG=0
USE_HARD_NEG_FEATURE_SET=1
INCLUDE_BASE_EXTRA_NEGS=1
# v10: MUSAN speech/music auto-included if dirs exist (same pattern as KORVO-2 negs).
# Use --no-musan to opt out for ablation experiments.
USE_MUSAN_SPEECH=1
USE_MUSAN_MUSIC=1
# v10: Riigikogu - use N random files (each ~1-5h). 0 = disabled, 50 = ~200h, 100 = ~400h.
RIIGIKOGU_FILE_LIMIT=50

# Track explicit CLI overrides so they take precedence over presets
_CLI_HARD_NEG_FEATURE_SET=""
_CLI_LEGACY_TTS_HARD_NEG=""
_CLI_MUSAN_SPEECH=""
_CLI_MUSAN_MUSIC=""
_CLI_RIIGIKOGU=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --training-steps) TRAINING_STEPS="$2"; shift 2 ;;
    --negative-limit) NEGATIVE_LIMIT="$2"; shift 2 ;;
    --time) TIME_LIMIT="$2"; shift 2 ;;
    --cpus) CPUS="$2"; shift 2 ;;
    --mem) MEM="$2"; shift 2 ;;
    --tag) EXPERIMENT_TAG="$2"; shift 2 ;;
    --use-legacy-tts-hard-neg) _CLI_LEGACY_TTS_HARD_NEG=1; shift 1 ;;
    --no-hard-neg-feature-set) _CLI_HARD_NEG_FEATURE_SET=0; shift 1 ;;
    --spec-augment) USE_SPEC_AUGMENT=1; shift 1 ;;
    --tts-hard-neg-in-hard-set) USE_TTS_HARD_NEG_IN_HARD_SET=1; shift 1 ;;
    --no-musan-speech) _CLI_MUSAN_SPEECH=0; shift 1 ;;
    --no-musan-music) _CLI_MUSAN_MUSIC=0; shift 1 ;;
    --no-musan) _CLI_MUSAN_SPEECH=0; _CLI_MUSAN_MUSIC=0; shift 1 ;;
    --riigikogu-files) _CLI_RIIGIKOGU="$2"; shift 2 ;;
    --no-riigikogu) _CLI_RIIGIKOGU=0; shift 1 ;;
    --dataset-preset) DATASET_PRESET="$2"; shift 2 ;;
    --recall-profile) RECALL_PROFILE_FLAG="--recall-profile"; shift 1 ;;
    --no-vtlp) VTLP_FLAG="--no-vtlp"; shift 1 ;;
    --vtlp-prob) VTLP_FLAG="--vtlp-prob $2"; shift 2 ;;
    --vtlp-alpha-min) VTLP_FLAG="${VTLP_FLAG:+${VTLP_FLAG} }--vtlp-alpha-min $2"; shift 2 ;;
    --vtlp-alpha-max) VTLP_FLAG="${VTLP_FLAG:+${VTLP_FLAG} }--vtlp-alpha-max $2"; shift 2 ;;
    --neg-class-weight) NEG_CLASS_WEIGHT_FLAG="--neg-class-weight $2"; shift 2 ;;
    --learning-rates) LEARNING_RATES_FLAG="--learning-rates \"$2\""; shift 2 ;;
    --aug-profile) AUG_PROFILE_FLAG="--aug-profile $2"; shift 2 ;;
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

# Apply dataset preset overrides
case "${DATASET_PRESET}" in
  v6-data)
    echo "=== PRESET: v6-data (mic1+mic2 + TTS pos, legacy TTS hard neg in main pool) ==="
    USE_LEGACY_TTS_HARD_NEG=1
    USE_HARD_NEG_FEATURE_SET=0
    USE_MUSAN_SPEECH=0
    USE_MUSAN_MUSIC=0
    RIIGIKOGU_FILE_LIMIT=0
    EXTRA_POS_LIST=("${TTS_POS_DIR}")
    ;;
  v6-plus)
    echo "=== PRESET: v6-plus (v6 + Mac pos + mattias-short + XTTS clones + Kule SSML) ==="
    USE_LEGACY_TTS_HARD_NEG=1
    USE_HARD_NEG_FEATURE_SET=0
    USE_MUSAN_SPEECH=0
    USE_MUSAN_MUSIC=0
    RIIGIKOGU_FILE_LIMIT=0
    EXTRA_POS_LIST=(
      "${TTS_POS_DIR}"
      "${TTS_SSML_KULE_POS_DIR}"
      "${MAC_POS_DIR}" "${MAC_POS_AUG_DIR}"
      "${XTTS_POS_MARTA}" "${XTTS_POS_ANNAM}" "${XTTS_POS_EMA}"
      "${MATTIAS_SHORT_POS}"
    )
    ;;
  v8-data)
    echo "=== PRESET: v8-data (full v8: mic + TTS + SSML + Mac + XTTS, separate hard neg) ==="
    USE_LEGACY_TTS_HARD_NEG=0
    USE_HARD_NEG_FEATURE_SET=1
    USE_MUSAN_SPEECH=0
    USE_MUSAN_MUSIC=0
    RIIGIKOGU_FILE_LIMIT=0
    EXTRA_POS_LIST=(
      "${TTS_POS_DIR}" "${TTS_SSML_POS_DIR}"
      "${MAC_POS_DIR}" "${MAC_POS_AUG_DIR}"
      "${XTTS_POS_MARTA}" "${XTTS_POS_ANNAM}" "${XTTS_POS_EMA}"
    )
    ;;
  confusable-filter)
    echo "=== PRESET: confusable-filter (pos=kuule kratt real+TTS, neg=hard neg ONLY) ==="
    # Same positives as expert-a (real + TTS, both domains represented)
    EXTRA_POS_LIST=(
      "${TTS_POS_DIR}" "${TTS_SSML_POS_DIR}"
      "${TTS_SSML_KULE_POS_DIR}"
      "${MAC_POS_DIR}" "${MAC_POS_AUG_DIR}"
      "${XTTS_POS_MARTA}" "${XTTS_POS_ANNAM}" "${XTTS_POS_EMA}"
      "${MATTIAS_SHORT_POS}"
    )
    # No CV ET random negatives — only hard negatives as the negative class
    NEGATIVE_LIMIT="-1"
    # Exclude generic/random negative pools entirely for this preset
    INCLUDE_BASE_EXTRA_NEGS=0
    # Hard neg sources go into the MAIN negative pool (not separate feature set)
    USE_HARD_NEG_FEATURE_SET=0
    # Include ALL hard neg sources (TTS + real) as regular negatives
    USE_LEGACY_TTS_HARD_NEG=1
    # No MUSAN/Riigikogu — keep negatives focused on phonetic confusables only
    USE_MUSAN_SPEECH=0
    USE_MUSAN_MUSIC=0
    RIIGIKOGU_FILE_LIMIT=0
    ;;
  current|*)
    echo "=== PRESET: current (all available data) ==="
    EXTRA_POS_LIST=(
      "${TTS_POS_DIR}" "${TTS_SSML_POS_DIR}"
      "${TTS_SSML_KULE_POS_DIR}"
      "${MAC_POS_DIR}" "${MAC_POS_AUG_DIR}"
      "${XTTS_POS_MARTA}" "${XTTS_POS_ANNAM}" "${XTTS_POS_EMA}"
      "${MATTIAS_SHORT_POS}"
    )
    ;;
esac

# CLI flags override preset values (explicit flag always wins)
[[ -n "$_CLI_HARD_NEG_FEATURE_SET" ]] && USE_HARD_NEG_FEATURE_SET="$_CLI_HARD_NEG_FEATURE_SET"
[[ -n "$_CLI_LEGACY_TTS_HARD_NEG" ]] && USE_LEGACY_TTS_HARD_NEG="$_CLI_LEGACY_TTS_HARD_NEG"
[[ -n "$_CLI_MUSAN_SPEECH" ]] && USE_MUSAN_SPEECH="$_CLI_MUSAN_SPEECH"
[[ -n "$_CLI_MUSAN_MUSIC" ]] && USE_MUSAN_MUSIC="$_CLI_MUSAN_MUSIC"
[[ -n "$_CLI_RIIGIKOGU" ]] && RIIGIKOGU_FILE_LIMIT="$_CLI_RIIGIKOGU"

# Build extra positive dirs
EXTRA_POS=""
for pos_d in "${EXTRA_POS_LIST[@]}"; do
  if [[ -d "${pos_d}" ]]; then
    EXTRA_POS="${EXTRA_POS} ${pos_d}"
    echo "Including extra positives: ${pos_d}"
  fi
done

# Build extra negative dirs (same-device KORVO-2 + MacBook segmented + mined live false accepts; legacy TTS hard neg opt-in)
EXTRA_NEG_LIST=""
if [[ "${INCLUDE_BASE_EXTRA_NEGS}" == "1" ]]; then
  for neg_d in "${KORVO2_NEG_DIR}" "${KORVO2_NEG_EXTRA_DIR}" "${KORVO2_NEG_S2_DIR}" "${MACBOOK_NEG_DIR}" "${MINED_FALSE_NEG_V10_DIR}"; do
    if [[ -d "${neg_d}" ]]; then
      EXTRA_NEG_LIST="${EXTRA_NEG_LIST:+${EXTRA_NEG_LIST},}${neg_d}"
      echo "Including extra negatives: ${neg_d}"
    fi
  done
else
  echo "Skipping base extra negatives for preset: ${DATASET_PRESET}"
fi
# v10: opt-in MUSAN speech (~49h LibriVox) and music (~41h)
if [[ "${USE_MUSAN_SPEECH}" == "1" ]] && [[ -d "${MUSAN_SPEECH_DIR}" ]]; then
  EXTRA_NEG_LIST="${EXTRA_NEG_LIST:+${EXTRA_NEG_LIST},}${MUSAN_SPEECH_DIR}"
  echo "Including MUSAN speech (~49h): ${MUSAN_SPEECH_DIR}"
fi
if [[ "${USE_MUSAN_MUSIC}" == "1" ]] && [[ -d "${MUSAN_MUSIC_DIR}" ]]; then
  EXTRA_NEG_LIST="${EXTRA_NEG_LIST:+${EXTRA_NEG_LIST},}${MUSAN_MUSIC_DIR}"
  echo "Including MUSAN music (~41h): ${MUSAN_MUSIC_DIR}"
fi
# v10: Riigikogu Estonian parliament speech (subset of 1001 FLAC files)
if [[ "${RIIGIKOGU_FILE_LIMIT}" -gt 0 ]] && [[ -d "${RIIGIKOGU_DIR}" ]]; then
  # Create a symlink dir with N random files to control dataset size
  RIIGIKOGU_SUBSET="${PROCESSED_DIR}/riigikogu_subset_${RIIGIKOGU_FILE_LIMIT}"
  if [[ ! -d "${RIIGIKOGU_SUBSET}" ]]; then
    echo "Creating Riigikogu subset (${RIIGIKOGU_FILE_LIMIT} files)..."
    mkdir -p "${RIIGIKOGU_SUBSET}"
    # Use awk for deterministic shuffle (shuf --random-source needs more entropy than 3 bytes)
    find "${RIIGIKOGU_DIR}" -name "*.flac" | awk 'BEGIN{srand(42)}{print rand()"\t"$0}' | sort -n | cut -f2 | head -n "${RIIGIKOGU_FILE_LIMIT}" | while read -r f; do
      ln -sf "$f" "${RIIGIKOGU_SUBSET}/$(basename "$f")"
    done
  fi
  RK_COUNT=$(find "${RIIGIKOGU_SUBSET}" -name "*.flac" | wc -l)
  EXTRA_NEG_LIST="${EXTRA_NEG_LIST:+${EXTRA_NEG_LIST},}${RIIGIKOGU_SUBSET}"
  echo "Including Riigikogu subset (${RK_COUNT} files): ${RIIGIKOGU_SUBSET}"
fi
if [[ "${USE_LEGACY_TTS_HARD_NEG}" == "1" ]]; then
  for neg_d in "${TTS_HARD_NEG_DIR}" "${TTS_HARD_NEG_V2_DIR}"; do
    if [[ -d "${neg_d}" ]]; then
      EXTRA_NEG_LIST="${EXTRA_NEG_LIST:+${EXTRA_NEG_LIST},}${neg_d}"
      echo "Including legacy TTS hard negatives in general neg pool: ${neg_d}"
    fi
  done
fi
# Real recorded hard negatives (KORVO-2 + OHEM mined)
for neg_d in "${KORVO2_HARD_NEG_DIR}" "${OHEM_MINED_DIR}"; do
  if [[ -d "${neg_d}" ]]; then
    EXTRA_NEG_LIST="${EXTRA_NEG_LIST:+${EXTRA_NEG_LIST},}${neg_d}"
    echo "Including real hard negatives: ${neg_d}"
  fi
done
# Build hard negative dirs (separate feature set with higher penalty weight)
HARD_NEG_LIST=""
HARD_NEG_ARGS=""
if [[ "${USE_HARD_NEG_FEATURE_SET}" == "1" ]]; then
  for hn_d in "${MAC_HARD_NEG_DIR}" "${XTTS_HARD_NEG_MARTA}" "${XTTS_HARD_NEG_ANNAM}" "${XTTS_HARD_NEG_EMA}"; do
    if [[ -d "${hn_d}" ]]; then
      HARD_NEG_LIST="${HARD_NEG_LIST:+${HARD_NEG_LIST},}${hn_d}"
      echo "Including hard negatives: ${hn_d}"
    fi
  done
  if [[ "${USE_TTS_HARD_NEG_IN_HARD_SET}" == "1" ]]; then
    for hn_d in "${TTS_HARD_NEG_DIR}" "${TTS_HARD_NEG_V2_DIR}"; do
      if [[ -d "${hn_d}" ]]; then
        HARD_NEG_LIST="${HARD_NEG_LIST:+${HARD_NEG_LIST},}${hn_d}"
        echo "Including TTS hard negatives in HARD SET: ${hn_d}"
      fi
    done
  fi
  if [[ -n "${HARD_NEG_LIST}" ]]; then
    HARD_NEG_ARGS="--hard-negative-dirs ${HARD_NEG_LIST}"
  fi
else
  # When hard neg feature set is OFF, fold hard neg dirs into general negative pool
  for hn_d in "${MAC_HARD_NEG_DIR}" "${XTTS_HARD_NEG_MARTA}" "${XTTS_HARD_NEG_ANNAM}" "${XTTS_HARD_NEG_EMA}"; do
    if [[ -d "${hn_d}" ]]; then
      EXTRA_NEG_LIST="${EXTRA_NEG_LIST:+${EXTRA_NEG_LIST},}${hn_d}"
      echo "Folding hard negatives into general pool: ${hn_d}"
    fi
  done
fi

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
if [[ "${NEGATIVE_LIMIT}" == "-1" ]]; then
  echo "=== Step 1: SKIPPED (NEGATIVE_LIMIT=${NEGATIVE_LIMIT}, no CV negatives needed) ==="
else
  echo "=== Step 1: Convert Common Voice MP3 → WAV ==="
  bash "${ROOT_DIR}/wake-word/training/scripts/convert_cv_mp3_to_wav.sh" \
    "${CV_ROOT}/clips" \
    "${CV_WAV_DIR}" \
    "${NEGATIVE_LIMIT}"
fi

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
  ${EXTRA_AMB_ARGS} \
  ${HARD_NEG_ARGS}

# Step 3: Train (same script as marvin)
echo "=== Step 3: Train ==="
TRAIN_HARD_NEG_ARG=""
if [[ -d "${OUTPUT_DIR}/hard_negative_samples" ]]; then
  TRAIN_HARD_NEG_ARG="--hard-negative-dir ${OUTPUT_DIR}/hard_negative_samples"
fi

TRAIN_SPEC_AUGMENT_ARG=""
if [[ "${USE_SPEC_AUGMENT}" == "1" ]]; then
  TRAIN_SPEC_AUGMENT_ARG="--spec-augment"
fi

# Build augmentation resource args (background noise + room impulse responses)
TRAIN_BG_NOISE_ARG=""
if [[ -d "${MUSAN_NOISE_DIR}" ]]; then
  TRAIN_BG_NOISE_ARG="--background-noise-dir ${MUSAN_NOISE_DIR}"
  echo "Augmentation: background noise from ${MUSAN_NOISE_DIR}"
fi
TRAIN_IR_ARG=""
if [[ -d "${MIT_IR_DIR}" ]]; then
  TRAIN_IR_ARG="--impulse-response-dir ${MIT_IR_DIR}"
  echo "Augmentation: impulse responses from ${MIT_IR_DIR}"
fi

"${ROOT_DIR}/wake-word/training/scripts/train_microwakeword_experiment.sh" \
  --experiment-name "microwakeword-kuule-kratt-${EXPERIMENT_TAG}" \
  --positive-dir "${OUTPUT_DIR}/positive_samples" \
  --negative-dir "${OUTPUT_DIR}/negative_samples" \
  --ambient-dir "${OUTPUT_DIR}/ambient_samples" \
  \${TRAIN_HARD_NEG_ARG} \
  \${TRAIN_SPEC_AUGMENT_ARG} \
  \${TRAIN_BG_NOISE_ARG} \
  \${TRAIN_IR_ARG} \
  ${RECALL_PROFILE_FLAG} \
  --training-steps "${TRAINING_STEPS}" \
  ${VTLP_FLAG} \
  ${NEG_CLASS_WEIGHT_FLAG} \
  ${LEARNING_RATES_FLAG} \
  ${AUG_PROFILE_FLAG}
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
