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
# 2s window is safer for the two-word phrase when source positives contain
# natural leading/trailing silence. Override with --clip-duration-ms for ablations.
CLIP_DURATION_MS="2000"
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
TARGET_MINIMIZATION_FLAG=""
POINTWISE_FILTERS_FLAG=""
RESIDUAL_FLAG=""
POSITIVE_TRUNCATE_RANDOMLY_FLAG=""
DRY_RUN=0
ALLOW_KNOWN_BAD_POSITIVES=0
# STT audit (2026-04-28) found mattias-short clips below 0.80s are prefix/tail/empty, not full wake phrase.
POSITIVE_MIN_DURATION_S="0.80"
POSITIVE_MAX_DURATION_S="4.00"
INCLUDE_REAL_HARD_NEGS=1
INCLUDE_FOLDED_HARD_NEGS=1
INCLUDE_OHEM_CV_MINED=0
# Exclude the rare target token from Common Voice negatives, but keep "kuule"
# as ordinary negative speech. Excluding "kuule" made prefix-only triggering too easy.
CV_EXCLUDE_WORDS=("kratt")
EXCLUDE_NEGATIVE_WAV_DIRS=""
EXCLUDE_CV_SPLIT_ARGS=""

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
RAW_MINED_FALSE_ACCEPTS="${DATA_ROOT}/raw/mined_false_accepts"
FAPH_CV_TEST_DIR="${PROCESSED_DIR}/faph_test_cv_et"
TTS_POS_DIR="${PROCESSED_DIR}/positive_tts"
STRICT_GENERATED_POS_DIR_BASE="${PROCESSED_DIR}/positive_strict_kuule_kule"
TTS_SSML_POS_DIR="${PROCESSED_DIR}/positive_tts_ssml"
TTS_HARD_NEG_DIR="${PROCESSED_DIR}/negative_tts_hard"
TTS_HARD_NEG_V2_DIR="${PROCESSED_DIR}/negative_tts_hard_v2"

# v8: real positives + voice-cloned positives
MAC_POS_DIR="${DATA_ROOT}/raw/mattias/positive"
MAC_POS_AUG_DIR="${DATA_ROOT}/augmented/positive_mattias_mac"
XTTS_POS_MARTA="${DATA_ROOT}/raw/xtts_clones/marta/positive"
XTTS_POS_ANNAM="${DATA_ROOT}/raw/xtts_clones/annam/positive"
XTTS_POS_EMA="${DATA_ROOT}/raw/xtts_clones/ema/positive"
XTTS_POS_MARTA_16K="${DATA_ROOT}/raw/xtts_clones/marta/positive_16k"
XTTS_POS_ANNAM_16K="${DATA_ROOT}/raw/xtts_clones/annam/positive_16k"
XTTS_POS_EMA_16K="${DATA_ROOT}/raw/xtts_clones/ema/positive_16k"
# Strict generated positive builder sources. Policy: exactly two words only:
# "kuule kratt" / "kule kratt" (elongated vowels allowed), no filler prefix.
NEUROKONE_PHASE1_DIR="${DATA_ROOT}/raw/neurokone_phase1"
NEUROKONE_PHASE2_DIR="${DATA_ROOT}/raw/neurokone_phase2"
# Mattias short pronunciation "kule kratt" (135 clips, recorded 2026-04-14)
MATTIAS_SHORT_POS="${DATA_ROOT}/raw/mattias-short/positive"
KULE_VS_KUULE_POS="${DATA_ROOT}/raw/kule_vs_kuule_test"
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
OHEM_EXPERT_A_MINED_DIR="${DATA_ROOT}/mined/ohem_expert_a_all_097"
OHEM_V16C_MINED_DIR="${DATA_ROOT}/mined/ohem_v16c_all_097"
# Isa neg held out for unseen-speaker test (NOT included)

# v8: opt-in flags - only use TTS hard negs in legacy "negative" set if explicitly requested
# v10: learned that separate hard_neg feature set HURTS FAPH (v9 = 76 FAPH vs v6 = 21).
#      Prefer --use-legacy-tts-hard-neg (all negatives in one pool) for best results.
# Dataset presets for clean ablation experiments
# v6-data: mic1+mic2 + positive_tts positives, CV ET + KORVO-2 + TTS hard neg in main pool
# v8-data: full v8 dataset (mic + TTS + SSML + Mac + XTTS clones, separate hard neg set)
# current: everything available (default)
# recall-cv: high-recall + low general speech FAPH preset:
#            clean positives (known-bad SSML/XTTS quarantined by default), broad
#            general negatives, Android/Mac mined false accepts, no large
#            hard-negative feature set, no CV OHEM poison.
# Safe default for new deploy-candidate runs. Legacy presets remain available
# via --dataset-preset for historical reproduction/ablations.
DATASET_PRESET="recall-cv"
USE_LEGACY_TTS_HARD_NEG=0
USE_HARD_NEG_FEATURE_SET=1
USE_STRICT_GENERATED_POSITIVES=0
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
_CLI_INCLUDE_REAL_HARD_NEGS=""
_CLI_INCLUDE_FOLDED_HARD_NEGS=""
CUSTOM_EXTRA_NEGATIVE_DIRS=""
CUSTOM_EXTRA_AMBIENT_DIRS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --training-steps) TRAINING_STEPS="$2"; shift 2 ;;
    --clip-duration-ms) CLIP_DURATION_MS="$2"; shift 2 ;;
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
    --pointwise-filters) POINTWISE_FILTERS_FLAG="--pointwise-filters $2"; shift 2 ;;
    --residual) RESIDUAL_FLAG="--residual"; shift 1 ;;
    --no-residual) RESIDUAL_FLAG="--no-residual"; shift 1 ;;
    --positive-truncate-randomly) POSITIVE_TRUNCATE_RANDOMLY_FLAG="--positive-truncate-randomly"; shift 1 ;;
    --include-real-hard-negs) _CLI_INCLUDE_REAL_HARD_NEGS=1; shift 1 ;;
    --no-real-hard-negs) _CLI_INCLUDE_REAL_HARD_NEGS=0; shift 1 ;;
    --include-folded-hard-negs) _CLI_INCLUDE_FOLDED_HARD_NEGS=1; shift 1 ;;
    --no-folded-hard-negs) _CLI_INCLUDE_FOLDED_HARD_NEGS=0; shift 1 ;;
    --extra-negative-dirs) CUSTOM_EXTRA_NEGATIVE_DIRS="$2"; shift 2 ;;
    --extra-ambient-dirs) CUSTOM_EXTRA_AMBIENT_DIRS="$2"; shift 2 ;;
    --no-vtlp) VTLP_FLAG="--no-vtlp"; shift 1 ;;
    --vtlp-prob) VTLP_FLAG="--vtlp-prob $2"; shift 2 ;;
    --vtlp-alpha-min) VTLP_FLAG="${VTLP_FLAG:+${VTLP_FLAG} }--vtlp-alpha-min $2"; shift 2 ;;
    --vtlp-alpha-max) VTLP_FLAG="${VTLP_FLAG:+${VTLP_FLAG} }--vtlp-alpha-max $2"; shift 2 ;;
    --neg-class-weight) NEG_CLASS_WEIGHT_FLAG="--neg-class-weight $2"; shift 2 ;;
    --learning-rates) LEARNING_RATES_FLAG="--learning-rates \"$2\""; shift 2 ;;
    --aug-profile) AUG_PROFILE_FLAG="--aug-profile $2"; shift 2 ;;
    --target-minimization) TARGET_MINIMIZATION_FLAG="--target-minimization $2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift 1 ;;
    --allow-known-bad-positives) ALLOW_KNOWN_BAD_POSITIVES=1; shift 1 ;;
    --positive-min-duration-s) POSITIVE_MIN_DURATION_S="$2"; shift 2 ;;
    --positive-max-duration-s) POSITIVE_MAX_DURATION_S="$2"; shift 2 ;;
    --no-positive-duration-filter) POSITIVE_MIN_DURATION_S="0"; POSITIVE_MAX_DURATION_S="0"; shift 1 ;;
    --include-ohem-cv-mined) INCLUDE_OHEM_CV_MINED=1; shift 1 ;;
    *) echo "Unknown: $1" >&2; exit 2 ;;
  esac
done

OUTPUT_DIR="${PROCESSED_DIR}/experiments/kuule_kratt_${EXPERIMENT_TAG}"
STRICT_GENERATED_POS_DIR="${STRICT_GENERATED_POS_DIR_BASE}_${EXPERIMENT_TAG}"

if [[ "${DRY_RUN}" != "1" ]]; then
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
else
  echo "DRY RUN: skipping sbatch and required HPC directory checks"
fi

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
  recall-cv)
    echo "=== PRESET: recall-cv (strict two-word positives + broad general/mined negatives, no hard-neg overdose) ==="
    USE_STRICT_GENERATED_POSITIVES=1
    EXTRA_POS_LIST=(
      "${STRICT_GENERATED_POS_DIR}"
      "${MAC_POS_DIR}" "${MAC_POS_AUG_DIR}"
      "${MATTIAS_SHORT_POS}"
    )
    # Keep broad general negatives but avoid poisoning the canonical FAPH CV test.
    # Crucially: exclude only 'kratt' from CV transcripts, NOT 'kuule'. This lets
    # the model learn that 'kuule' alone is ordinary speech, not a wake event.
    CV_EXCLUDE_WORDS=("kratt")
    EXCLUDE_NEGATIVE_WAV_DIRS="${FAPH_CV_TEST_DIR}"
    EXCLUDE_CV_SPLIT_ARGS="--exclude-cv-split-skip 5000 --exclude-cv-split-limit 2000 --exclude-cv-split-exclude-words kratt kuule"
    USE_HARD_NEG_FEATURE_SET=0
    USE_LEGACY_TTS_HARD_NEG=0
    INCLUDE_REAL_HARD_NEGS=0
    INCLUDE_FOLDED_HARD_NEGS=0
    INCLUDE_OHEM_CV_MINED=0
    USE_MUSAN_SPEECH=1
    USE_MUSAN_MUSIC=1
    RIIGIKOGU_FILE_LIMIT=50
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
[[ -n "$_CLI_INCLUDE_REAL_HARD_NEGS" ]] && INCLUDE_REAL_HARD_NEGS="$_CLI_INCLUDE_REAL_HARD_NEGS"
[[ -n "$_CLI_INCLUDE_FOLDED_HARD_NEGS" ]] && INCLUDE_FOLDED_HARD_NEGS="$_CLI_INCLUDE_FOLDED_HARD_NEGS"

# 2026-04-27 audit: these positive dirs are quarantined by default.
# - SSML dirs contain literal XML tags read aloud by Neurokõne (5-14s clips).
# - XTTS raw/cropped positives are full command prompts, not isolated wake phrase.
# Use --allow-known-bad-positives only for historical reproduction, never for a
# new deploy candidate.
KNOWN_BAD_POSITIVE_DIRS=(
  "${TTS_SSML_POS_DIR}"
  "${DATA_ROOT}/raw/neurokone_ssml_positives"
  "${TTS_SSML_KULE_POS_DIR}"
  "${XTTS_POS_MARTA}"
  "${XTTS_POS_ANNAM}"
  "${XTTS_POS_EMA}"
  "${XTTS_POS_MARTA_16K}"
  "${XTTS_POS_ANNAM_16K}"
  "${XTTS_POS_EMA_16K}"
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

# Build comma-separated exclusion list for prepare_kuule_kratt_experiment.py.
# Only include existing paths so local dry-runs and HPC runs do not fail on dirs
# that are absent in one environment.
EXCLUDE_POSITIVE_WAV_DIRS=""
if [[ "${ALLOW_KNOWN_BAD_POSITIVES}" != "1" ]]; then
  for bad_pos_d in "${KNOWN_BAD_POSITIVE_DIRS[@]}"; do
    if [[ -d "${bad_pos_d}" ]]; then
      EXCLUDE_POSITIVE_WAV_DIRS="${EXCLUDE_POSITIVE_WAV_DIRS:+${EXCLUDE_POSITIVE_WAV_DIRS},}${bad_pos_d}"
    fi
  done
fi

# Build extra positive dirs. The strict generated positive dir may not exist
# until the SLURM job builds it, so include it by path when the preset requests it.
EXTRA_POS=""
for pos_d in "${EXTRA_POS_LIST[@]}"; do
  if [[ "${ALLOW_KNOWN_BAD_POSITIVES}" != "1" ]] && is_known_bad_positive_dir "${pos_d}"; then
    echo "SKIPPING known-bad positive source (2026-04-27 audit): ${pos_d}"
    continue
  fi
  if [[ -d "${pos_d}" ]] || { [[ "${USE_STRICT_GENERATED_POSITIVES}" == "1" ]] && [[ "${pos_d}" == "${STRICT_GENERATED_POS_DIR}" ]]; }; then
    EXTRA_POS="${EXTRA_POS} ${pos_d}"
    if [[ "${pos_d}" == "${STRICT_GENERATED_POS_DIR}" ]] && [[ "${USE_STRICT_GENERATED_POSITIVES}" == "1" ]]; then
      echo "Including generated strict positives (built in job): ${pos_d}"
    else
      echo "Including extra positives: ${pos_d}"
    fi
  fi
done

# Build extra negative dirs (same-device KORVO-2 + MacBook segmented + mined live false accepts; legacy TTS hard neg opt-in)
EXTRA_NEG_LIST=""
if [[ "${INCLUDE_BASE_EXTRA_NEGS}" == "1" ]]; then
  for neg_d in "${KORVO2_NEG_DIR}" "${KORVO2_NEG_EXTRA_DIR}" "${KORVO2_NEG_S2_DIR}" "${MACBOOK_NEG_DIR}" "${MINED_FALSE_NEG_V10_DIR}" "${RAW_MINED_FALSE_ACCEPTS}"; do
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
# Real recorded hard negatives: useful for some experiments, but disabled for
# recall-cv because the objective is general CV/FAPH + recall without hard-neg overdose.
if [[ "${INCLUDE_REAL_HARD_NEGS}" == "1" ]]; then
  for neg_d in "${KORVO2_HARD_NEG_DIR}"; do
    if [[ -d "${neg_d}" ]]; then
      EXTRA_NEG_LIST="${EXTRA_NEG_LIST:+${EXTRA_NEG_LIST},}${neg_d}"
      echo "Including real hard negatives: ${neg_d}"
    fi
  done
fi
# OHEM CV mined clips are powerful, but if they were mined from faph_cv_et they
# poison the primary CV FAPH benchmark. Keep opt-in only.
if [[ "${INCLUDE_OHEM_CV_MINED}" == "1" ]]; then
  for neg_d in "${OHEM_EXPERT_A_MINED_DIR}" "${OHEM_V16C_MINED_DIR}"; do
    if [[ -d "${neg_d}" ]]; then
      EXTRA_NEG_LIST="${EXTRA_NEG_LIST:+${EXTRA_NEG_LIST},}${neg_d}"
      echo "Including OHEM CV mined negatives (OPT-IN, may poison CV FAPH test): ${neg_d}"
    fi
  done
fi
if [[ -n "${CUSTOM_EXTRA_NEGATIVE_DIRS}" ]]; then
  EXTRA_NEG_LIST="${EXTRA_NEG_LIST:+${EXTRA_NEG_LIST},}${CUSTOM_EXTRA_NEGATIVE_DIRS}"
  echo "Including custom extra negative dirs: ${CUSTOM_EXTRA_NEGATIVE_DIRS}"
fi
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
  # When hard neg feature set is OFF, legacy presets may fold hard-neg dirs into
  # the general pool. v17 recall-cv disables this to avoid hard-neg overdose.
  if [[ "${INCLUDE_FOLDED_HARD_NEGS}" == "1" ]]; then
    for hn_d in "${MAC_HARD_NEG_DIR}" "${XTTS_HARD_NEG_MARTA}" "${XTTS_HARD_NEG_ANNAM}" "${XTTS_HARD_NEG_EMA}"; do
      if [[ -d "${hn_d}" ]]; then
        EXTRA_NEG_LIST="${EXTRA_NEG_LIST:+${EXTRA_NEG_LIST},}${hn_d}"
        echo "Folding hard negatives into general pool: ${hn_d}"
      fi
    done
  else
    echo "Not folding hard-negative dirs into general pool for preset: ${DATASET_PRESET}"
  fi
fi

EXTRA_NEG_ARGS=""
if [[ -n "${EXTRA_NEG_LIST}" ]]; then
  EXTRA_NEG_ARGS="--extra-negative-dirs ${EXTRA_NEG_LIST}"
fi

EXTRA_AMB_ARGS=""
EXTRA_AMB_LIST=""
if [[ -d "${KORVO2_AMB_DIR}" ]]; then
  EXTRA_AMB_LIST="${KORVO2_AMB_DIR}"
  echo "Including KORVO-2 ambient: ${KORVO2_AMB_DIR}"
fi
if [[ -n "${CUSTOM_EXTRA_AMBIENT_DIRS}" ]]; then
  EXTRA_AMB_LIST="${EXTRA_AMB_LIST:+${EXTRA_AMB_LIST},}${CUSTOM_EXTRA_AMBIENT_DIRS}"
  echo "Including custom extra ambient dirs: ${CUSTOM_EXTRA_AMBIENT_DIRS}"
fi
if [[ -n "${EXTRA_AMB_LIST}" ]]; then
  EXTRA_AMB_ARGS="--extra-ambient-dirs ${EXTRA_AMB_LIST}"
fi

CV_EXCLUDE_ARGS="--exclude-words ${CV_EXCLUDE_WORDS[*]}"
EXCLUDE_NEGATIVE_ARGS=""
if [[ -n "${EXCLUDE_NEGATIVE_WAV_DIRS}" ]]; then
  EXCLUDE_NEGATIVE_ARGS="--exclude-negative-wav-dirs ${EXCLUDE_NEGATIVE_WAV_DIRS}"
  echo "Excluding held-out negative WAV dirs: ${EXCLUDE_NEGATIVE_WAV_DIRS}"
fi

EXCLUDE_POSITIVE_ARGS=""
if [[ -n "${EXCLUDE_POSITIVE_WAV_DIRS}" ]]; then
  EXCLUDE_POSITIVE_ARGS="--exclude-positive-wav-dirs ${EXCLUDE_POSITIVE_WAV_DIRS}"
  echo "Excluding known-bad positive WAV dirs: ${EXCLUDE_POSITIVE_WAV_DIRS}"
fi

POSITIVE_DURATION_ARGS="--positive-min-duration-s ${POSITIVE_MIN_DURATION_S} --positive-max-duration-s ${POSITIVE_MAX_DURATION_S}"

mkdir -p "${RUNS_DIR}/logs"

JOB_NAME="kratt-kuule-kratt-${EXPERIMENT_TAG}"
LOG_PATH="${RUNS_DIR}/logs/${JOB_NAME}-%j.out"

if [[ "${DRY_RUN}" == "1" ]]; then
  echo
  echo "=== DRY RUN SUMMARY ==="
  echo "job_name: ${JOB_NAME}"
  echo "dataset_preset: ${DATASET_PRESET}"
  echo "output_dir: ${OUTPUT_DIR}"
  echo "positive_base: ${POSITIVE_MIC1} ${POSITIVE_MIC2}"
  echo "extra_positives:${EXTRA_POS:- <none>}"
  echo "strict_generated_positives: ${USE_STRICT_GENERATED_POSITIVES} -> ${STRICT_GENERATED_POS_DIR}"
  echo "strict_sources: ${NEUROKONE_PHASE1_DIR}, ${NEUROKONE_PHASE2_DIR}, ${KULE_VS_KUULE_POS}"
  echo "cv_exclude_words: ${CV_EXCLUDE_WORDS[*]}"
  echo "negative_limit: ${NEGATIVE_LIMIT}"
  echo "extra_neg_dirs: ${EXTRA_NEG_LIST:-<none>}"
  echo "extra_ambient_dirs: ${EXTRA_AMB_LIST:-<none>}"
  echo "exclude_negative_wav_dirs: ${EXCLUDE_NEGATIVE_WAV_DIRS:-<none>}"
  echo "exclude_positive_wav_dirs: ${EXCLUDE_POSITIVE_WAV_DIRS:-<none>}"
  echo "positive_duration_filter: min=${POSITIVE_MIN_DURATION_S}s max=${POSITIVE_MAX_DURATION_S}s"
  echo "allow_known_bad_positives: ${ALLOW_KNOWN_BAD_POSITIVES}"
  echo "exclude_cv_split_args: ${EXCLUDE_CV_SPLIT_ARGS:-<none>}"
  echo "hard_neg_feature_set: ${USE_HARD_NEG_FEATURE_SET} (${HARD_NEG_LIST:-<none>})"
  echo "legacy_tts_hard_neg: ${USE_LEGACY_TTS_HARD_NEG}"
  echo "folded_hard_negs: ${INCLUDE_FOLDED_HARD_NEGS}"
  echo "musan_speech: ${USE_MUSAN_SPEECH}"
  echo "musan_music: ${USE_MUSAN_MUSIC}"
  echo "riigikogu_file_limit: ${RIIGIKOGU_FILE_LIMIT}"
  echo "training_steps: ${TRAINING_STEPS}"
  echo "clip_duration_ms: ${CLIP_DURATION_MS}"
  echo "spec_augment: ${USE_SPEC_AUGMENT}"
  echo "recall_profile_flag: ${RECALL_PROFILE_FLAG:-<none>}"
  echo "pointwise_filters_flag: ${POINTWISE_FILTERS_FLAG:-<default>}"
  echo "residual_flag: ${RESIDUAL_FLAG:-<default>}"
  echo "positive_truncate_randomly_flag: ${POSITIVE_TRUNCATE_RANDOMLY_FLAG:-<default false>}"
  echo "neg_class_weight_flag: ${NEG_CLASS_WEIGHT_FLAG:-<default>}"
  echo "learning_rates_flag: ${LEARNING_RATES_FLAG:-<default>}"
  echo "aug_profile_flag: ${AUG_PROFILE_FLAG:-<default>}"
  echo "target_minimization_flag: ${TARGET_MINIMIZATION_FLAG:-<default 10.0>}"
  exit 0
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

# Step 1b: Build strict generated positives (exactly two words only)
if [[ "${USE_STRICT_GENERATED_POSITIVES}" == "1" ]]; then
  echo "=== Step 1b: Build strict generated positive set ==="
  "${ROOT_DIR}/wake-word/.venv/bin/python" \
    "${ROOT_DIR}/wake-word/data/validation/build_strict_positive_set.py" \
    --output "${STRICT_GENERATED_POS_DIR}" \
    --force \
    --source "${NEUROKONE_PHASE1_DIR}" \
    --source "${NEUROKONE_PHASE2_DIR}" \
    --source "${KULE_VS_KUULE_POS}" \
    --min-duration-s "${POSITIVE_MIN_DURATION_S}" \
    --max-duration-s "${POSITIVE_MAX_DURATION_S}"
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
  ${CV_EXCLUDE_ARGS} \
  ${EXCLUDE_NEGATIVE_ARGS} \
  ${EXCLUDE_POSITIVE_ARGS} \
  ${POSITIVE_DURATION_ARGS} \
  ${EXCLUDE_CV_SPLIT_ARGS} \
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
  ${POINTWISE_FILTERS_FLAG} \
  ${RESIDUAL_FLAG} \
  ${POSITIVE_TRUNCATE_RANDOMLY_FLAG} \
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
