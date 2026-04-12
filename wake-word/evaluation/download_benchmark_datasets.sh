#!/usr/bin/env bash
# Download standard wake word evaluation benchmark datasets to HPC.
# Run inside tmux on HPC login node.
#
# Usage:
#   tmux attach -t kratt-0
#   bash /path/to/download_benchmark_datasets.sh
#
# Datasets downloaded:
#   1. DiPCo (Dinner Party Corpus) - ~5.5h far-field conversational speech
#      Used by: openWakeWord (primary FAPH benchmark)
#   2. LibriSpeech test-clean - ~5.4h read English speech
#      Used by: Picovoice (primary FAPH benchmark)
#   3. MUSDB18-HQ test subset - ~3.5h music (stems mixed to mono)
#      Used by: openWakeWord (music robustness)
#   4. MIT Impulse Responses - room impulse responses for RIR augmentation
#      Used by: openWakeWord (reverberation augmentation)

set -euo pipefail

DATASETS_DIR="${KRATT_DATA:-/gpfs/mariana/smbhome/$(whoami)/kratt-data}/datasets"
BENCHMARKS_DIR="${DATASETS_DIR}/benchmarks"
mkdir -p "${BENCHMARKS_DIR}"

echo "========================================="
echo "Downloading standard FAPH benchmark datasets"
echo "Target: ${BENCHMARKS_DIR}"
echo "========================================="

# ─── 1. DiPCo (Dinner Party Corpus) ─────────────────────────────────────────
# ~5.5 hours of far-field dinner party recordings. 10 sessions, each ~30 min.
# Canonical FAPH benchmark for openWakeWord.
# Source: https://arxiv.org/abs/1909.13447
DIPCO_DIR="${BENCHMARKS_DIR}/dipco"
if [[ -d "${DIPCO_DIR}" ]] && [[ $(find "${DIPCO_DIR}" -name "*.wav" 2>/dev/null | wc -l) -gt 0 ]]; then
  echo "[SKIP] DiPCo already exists ($(find "${DIPCO_DIR}" -name "*.wav" | wc -l) wavs)"
else
  echo "[DOWNLOAD] DiPCo Dinner Party Corpus..."
  mkdir -p "${DIPCO_DIR}"
  # DiPCo is distributed via LDC but also available on Zenodo/GitHub
  # Primary: https://github.com/chimechallenge/CHiME7_DASR_falign
  # Audio files: hosted on Zenodo
  cd "${DIPCO_DIR}"

  # Try the direct Zenodo download (DiPCo audio)
  if ! wget -q --show-progress -O dipco_audio.tar.gz \
    "https://zenodo.org/records/4417781/files/DiPCo.tar.gz" 2>/dev/null; then
    echo "[WARN] DiPCo direct download failed. Try manual download from:"
    echo "  https://zenodo.org/records/4417781"
    echo "  Place DiPCo.tar.gz in ${DIPCO_DIR}/"
  else
    tar xzf dipco_audio.tar.gz && rm dipco_audio.tar.gz
    echo "[OK] DiPCo: $(find . -name "*.wav" | wc -l) wav files"
  fi
fi

# ─── 2. LibriSpeech test-clean ───────────────────────────────────────────────
# ~5.4 hours of read English speech, 40 speakers.
# Canonical FAPH benchmark for Picovoice.
LIBRI_DIR="${BENCHMARKS_DIR}/librispeech-test-clean"
if [[ -d "${LIBRI_DIR}" ]] && [[ $(find "${LIBRI_DIR}" -name "*.flac" 2>/dev/null | wc -l) -gt 0 ]]; then
  echo "[SKIP] LibriSpeech test-clean already exists ($(find "${LIBRI_DIR}" -name "*.flac" | wc -l) flacs)"
else
  echo "[DOWNLOAD] LibriSpeech test-clean (~350MB)..."
  mkdir -p "${LIBRI_DIR}"
  cd "${LIBRI_DIR}"
  wget -q --show-progress -O test-clean.tar.gz \
    "https://www.openslr.org/resources/12/test-clean.tar.gz"
  tar xzf test-clean.tar.gz && rm test-clean.tar.gz
  echo "[OK] LibriSpeech test-clean: $(find . -name "*.flac" | wc -l) flac files"
fi

# ─── 3. MUSDB18-HQ test subset ──────────────────────────────────────────────
# ~3.5 hours of professionally mixed music with stems.
# Used by openWakeWord for music false-positive testing.
# Note: MUSDB18-HQ is ~30GB full. We download only the test subset.
MUSDB_DIR="${BENCHMARKS_DIR}/musdb18-test"
if [[ -d "${MUSDB_DIR}" ]] && [[ $(find "${MUSDB_DIR}" -name "*.wav" -o -name "*.mp4" 2>/dev/null | wc -l) -gt 0 ]]; then
  echo "[SKIP] MUSDB18 test already exists"
else
  echo "[INFO] MUSDB18-HQ requires manual download or stemmusic pip package."
  echo "  Option A: pip install musdb && python -c 'import musdb; musdb.DB(download=True)'"
  echo "  Option B: https://zenodo.org/records/3338373"
  echo "  Place test tracks in ${MUSDB_DIR}/"
  mkdir -p "${MUSDB_DIR}"
fi

# ─── 4. MIT Impulse Responses ────────────────────────────────────────────────
# Room impulse responses for RIR augmentation.
# Used by openWakeWord to simulate reverberant environments.
MIT_IR_DIR="${BENCHMARKS_DIR}/mit-impulse-responses"
if [[ -d "${MIT_IR_DIR}" ]] && [[ $(find "${MIT_IR_DIR}" -name "*.wav" 2>/dev/null | wc -l) -gt 0 ]]; then
  echo "[SKIP] MIT IRs already exist ($(find "${MIT_IR_DIR}" -name "*.wav" | wc -l) wavs)"
else
  echo "[DOWNLOAD] MIT Impulse Responses..."
  mkdir -p "${MIT_IR_DIR}"
  cd "${MIT_IR_DIR}"
  # HuggingFace dataset from openWakeWord author
  if command -v git-lfs >/dev/null 2>&1 || command -v git >/dev/null 2>&1; then
    git clone --depth 1 https://huggingface.co/datasets/davidscripka/MIT_environmental_impulse_responses . 2>/dev/null || \
      echo "[WARN] git clone failed. Download manually from https://huggingface.co/datasets/davidscripka/MIT_environmental_impulse_responses"
  else
    echo "[WARN] git not available. Download manually."
  fi
fi

# ─── 5. Convert everything to 16kHz mono WAV ────────────────────────────────
echo ""
echo "========================================="
echo "Converting to 16kHz mono WAV..."
echo "========================================="

# LibriSpeech FLAC → WAV
LIBRI_WAV="${BENCHMARKS_DIR}/librispeech-test-clean-wav"
if [[ -d "${LIBRI_DIR}" ]] && [[ ! -d "${LIBRI_WAV}" ]]; then
  echo "Converting LibriSpeech FLAC → 16kHz WAV..."
  mkdir -p "${LIBRI_WAV}"
  find "${LIBRI_DIR}" -name "*.flac" | while read -r f; do
    base=$(basename "$f" .flac)
    sox "$f" -r 16000 -c 1 -b 16 "${LIBRI_WAV}/${base}.wav" 2>/dev/null || true
  done
  echo "[OK] LibriSpeech WAV: $(find "${LIBRI_WAV}" -name "*.wav" | wc -l) files"
fi

# DiPCo WAV resample if needed (DiPCo is typically 16kHz already)
if [[ -d "${DIPCO_DIR}" ]]; then
  sample_rate=$(soxi -r "$(find "${DIPCO_DIR}" -name "*.wav" | head -1)" 2>/dev/null || echo "unknown")
  echo "DiPCo sample rate: ${sample_rate}"
fi

echo ""
echo "========================================="
echo "Summary:"
find "${BENCHMARKS_DIR}" -mindepth 1 -maxdepth 1 -type d | while read -r d; do
  name=$(basename "$d")
  wav_count=$(find "$d" -name "*.wav" 2>/dev/null | wc -l)
  flac_count=$(find "$d" -name "*.flac" 2>/dev/null | wc -l)
  echo "  ${name}: ${wav_count} wav, ${flac_count} flac"
done
echo "========================================="
