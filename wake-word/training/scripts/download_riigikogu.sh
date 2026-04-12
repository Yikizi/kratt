#!/usr/bin/env bash
# Download Riigikogu audio-stenograms dataset from HuggingFace to smbhome.
#
# IMPORTANT: Forces HF cache to smbhome (2TB) instead of default home (500GB).
#
# Usage (inside tmux on HPC login node):
#   export HF_TOKEN="hf_xxx"  # if not already set
#   bash wake-word/training/scripts/download_riigikogu.sh
#
# Downloads to: $KRATT_DATA/datasets/riigikogu-stenograms/
# HF cache at:  $KRATT_DATA/.hf-cache/

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/kratt_paths.sh"

DATA_ROOT="$(kratt_data_root)"
DATASETS_DIR="$(kratt_datasets_dir)"

# Force HF cache to smbhome to avoid filling home quota
export HF_HOME="${DATA_ROOT}/.hf-cache"
export HF_HUB_CACHE="${DATA_ROOT}/.hf-cache/hub"
export HUGGINGFACE_HUB_CACHE="${DATA_ROOT}/.hf-cache/hub"
mkdir -p "${HF_HOME}"

VENV="${SCRIPT_DIR}/../../.venv-microwakeword"
if [[ ! -f "${VENV}/bin/python" ]]; then
  echo "microWakeWord venv not found at ${VENV}" >&2
  exit 1
fi

PYTHON="${VENV}/bin/python"
OUT_DIR="${DATASETS_DIR}/riigikogu-stenograms"
mkdir -p "${OUT_DIR}"

echo "============================================"
echo "Downloading TalTechNLP/riigikogu-audio-stenograms-2018-2025"
echo "HF cache:  ${HF_HOME}"
echo "Output:    ${OUT_DIR}"
echo "============================================"

# Check token
if [[ -z "${HF_TOKEN:-}" ]]; then
  echo ""
  echo "WARNING: HF_TOKEN not set. Dataset may require authentication."
  echo "Set it with: export HF_TOKEN='hf_xxx'"
  echo ""
fi

# Use huggingface_hub snapshot_download for efficient parallel download
export OUT_DIR
${PYTHON} << PYEOF
import os
import sys
from pathlib import Path

from huggingface_hub import snapshot_download

dataset_id = "TalTechNLP/riigikogu-audio-stenograms-2018-2025"
out_dir = "${OUT_DIR}"
token = os.environ.get("HF_TOKEN", "${HF_TOKEN}")

print(f"Starting download of {dataset_id}...")
print(f"This is ~184 GB. Will take 30-120 min depending on bandwidth.")
print()

try:
    path = snapshot_download(
        repo_id=dataset_id,
        repo_type="dataset",
        local_dir=out_dir,
        token=token,
        resume_download=True,
    )
    print(f"\nDownload complete: {path}")
except KeyboardInterrupt:
    print("\nDownload interrupted. Re-run to resume (supports resume).")
    sys.exit(1)
except Exception as e:
    print(f"\nError: {e}")
    print("If authentication error, ensure HF_TOKEN is set.")
    sys.exit(1)
PYEOF

echo ""
echo "============================================"
echo "Download complete. Checking contents..."
echo "============================================"
find "${OUT_DIR}" -name "*.wav" -o -name "*.flac" -o -name "*.mp3" -o -name "*.opus" | wc -l
echo "audio files found"
du -sh "${OUT_DIR}"
