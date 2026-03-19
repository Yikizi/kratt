#!/usr/bin/env bash
# Convert Common Voice MP3 clips to 16kHz mono WAV.
# One-time operation, results are cached in OUTPUT_DIR.
#
# Usage:
#   convert_cv_mp3_to_wav.sh <cv_clips_dir> <output_dir> [limit]
#
# Example:
#   convert_cv_mp3_to_wav.sh .../cv-corpus-24.0-2025-12-05/et/clips .../common-voice-et-wav 5000

set -euo pipefail

CV_CLIPS="${1:?Usage: $0 <cv_clips_dir> <output_dir> [limit]}"
OUTPUT_DIR="${2:?Usage: $0 <cv_clips_dir> <output_dir> [limit]}"
LIMIT="${3:-0}"

if [[ ! -d "${CV_CLIPS}" ]]; then
  echo "Source not found: ${CV_CLIPS}" >&2
  exit 2
fi

if ! command -v sox >/dev/null 2>&1; then
  echo "sox not found" >&2
  exit 2
fi

mkdir -p "${OUTPUT_DIR}"

# Count already converted
EXISTING=$(find "${OUTPUT_DIR}" -maxdepth 1 -name '*.wav' | wc -l | tr -d ' ')
echo "Existing WAVs in output: ${EXISTING}"

# List MP3s, skip already converted
CONVERTED=0
SKIPPED=0
ERRORS=0

find "${CV_CLIPS}" -maxdepth 1 -name '*.mp3' -print0 | while IFS= read -r -d '' mp3; do

  base="$(basename "${mp3}" .mp3)"
  wav="${OUTPUT_DIR}/${base}.wav"

  if [[ -f "${wav}" ]]; then
    SKIPPED=$((SKIPPED + 1))
    CONVERTED=$((CONVERTED + 1))
    if [[ "${LIMIT}" -gt 0 && "${CONVERTED}" -ge "${LIMIT}" ]]; then
      break
    fi
    continue
  fi

  if sox "${mp3}" -r 16000 -c 1 -b 16 "${wav}" 2>/dev/null; then
    CONVERTED=$((CONVERTED + 1))
  else
    ERRORS=$((ERRORS + 1))
  fi

  if [[ "${LIMIT}" -gt 0 && "${CONVERTED}" -ge "${LIMIT}" ]]; then
    break
  fi

  if (( CONVERTED % 1000 == 0 )); then
    echo "  Converted: ${CONVERTED} (skipped: ${SKIPPED}, errors: ${ERRORS})"
  fi
done

TOTAL=$(find "${OUTPUT_DIR}" -maxdepth 1 -name '*.wav' | wc -l | tr -d ' ')
echo "Done. Total WAVs: ${TOTAL} (new: $((CONVERTED - SKIPPED)), skipped: ${SKIPPED}, errors: ${ERRORS})"
