#!/usr/bin/env bash
# Submit Fish Audio S2 Pro voice cloning job to TalTech HPC.
#
# Prerequisites (one-time on HPC):
#   git clone https://github.com/fishaudio/fish-speech.git ~/fish-speech
#   cd ~/fish-speech && conda create -n fish-speech python=3.12
#   conda activate fish-speech && pip install -e .[cu126]
#   huggingface-cli download fishaudio/s2-pro --local-dir checkpoints/s2-pro
#
# Usage:
#   ./submit_hpc_fish_tts.sh --name marta --ref-wav /path/to/marta_ref.wav
#   ./submit_hpc_fish_tts.sh --name annam --ref-wav /path/to/annam_ref.wav --repeats 5
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/kratt_paths.sh"

ROOT_DIR="$(kratt_project_root)"
DATA_ROOT="$(kratt_data_root)"

# Defaults
NAME=""
REF_WAV=""
REPEATS=3
TIME_LIMIT="02:00:00"
# TODO: Update these for your HPC GPU partition
GPU_PARTITION="gpu"
GPU_GRES="gpu:1"
FISH_DIR="${HOME}/fish-speech"
CONDA_ENV="fish-speech"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) NAME="$2"; shift 2 ;;
    --ref-wav) REF_WAV="$2"; shift 2 ;;
    --repeats) REPEATS="$2"; shift 2 ;;
    --time) TIME_LIMIT="$2"; shift 2 ;;
    --partition) GPU_PARTITION="$2"; shift 2 ;;
    --gres) GPU_GRES="$2"; shift 2 ;;
    --fish-dir) FISH_DIR="$2"; shift 2 ;;
    *) echo "Unknown: $1" >&2; exit 2 ;;
  esac
done

[[ -z "$NAME" ]] && { echo "Usage: $0 --name <speaker> --ref-wav <path> [--repeats N]"; exit 1; }
[[ -z "$REF_WAV" ]] && { echo "--ref-wav required"; exit 1; }

if ! command -v sbatch >/dev/null 2>&1; then
  echo "sbatch not found. Run on Slurm login node." >&2
  exit 1
fi

OUTPUT_DIR="${DATA_ROOT}/fish_clones/${NAME}"
REF_TEXT="Ükskord vaidlesid põhjatuul ja päike selle üle, kumb neist on tugevam."
LOG_DIR="${DATA_ROOT}/training/logs"
mkdir -p "${LOG_DIR}"

JOB_NAME="kratt-fish-tts-${NAME}"
LOG_PATH="${LOG_DIR}/${JOB_NAME}-%j.out"

# Positive and negative texts (same as XTTS pipeline)
read -r -d '' GENERATE_SCRIPT << 'PYSCRIPT' || true
import sys, json, os, shutil, time, subprocess
from pathlib import Path

name = os.environ["FISH_NAME"]
ref_wav = os.environ["FISH_REF_WAV"]
ref_text = os.environ["FISH_REF_TEXT"]
repeats = int(os.environ["FISH_REPEATS"])
output_dir = Path(os.environ["FISH_OUTPUT_DIR"])
fish_dir = Path(os.environ["FISH_DIR"])
checkpoint = fish_dir / "checkpoints" / "s2-pro"

POSITIVE_TEXTS = [
    "Kuule Kratt pane tuli põlema",
    "Kuule Kratt mis kell on",
    "Kuule Kratt mis ilm täna on",
    "Kuule Kratt mängi muusikat",
    "Kuule Kratt lülita lamp välja",
    "Kuule Kratt pane taimer käima",
    "Kuule Kratt helista emale",
    "Kuule Kratt kas sa kuuled mind",
    "Kuule Kratt palun pane raadio mängima",
    "Kuule Kratt ütle mis temperatuur on",
    "Kuule Kratt tule siia",
    "Kuule Kratt oota natuke",
    "Kuule Kratt aitäh sulle",
    "Kuule Kratt mis uudised on",
    "Kuule Kratt pane muusika kinni",
    "Kuule Kratt ava uks lahti",
]

NEGATIVE_TEXTS = [
    "Kuule kraad", "Kuule kraam", "Kuule ratt", "Kuule matt",
    "Kuule krats", "Kuule kraft", "Kuule pratt", "Kuule kriit",
    "Kuule kruvi", "Kuule kroon", "Kuule kass", "Kuule koer",
    "Kuule siin", "Kuule nüüd", "Kuule palun",
    "Tere Kratt", "Hei Kratt", "Kratt kuule", "See kratt", "Mis kratt",
]

# Emotion tags unique to Fish Audio (XTTS can't do this)
EMOTION_POSITIVE_TEXTS = [
    "[excited] Kuule Kratt pane tuli põlema",
    "[whisper] Kuule Kratt mis kell on",
    "[tired voice] Kuule Kratt lülita lamp välja",
    "[professional tone] Kuule Kratt mis ilm täna on",
    "[low voice] Kuule Kratt tule siia",
    "[high voice] Kuule Kratt oota natuke",
]

CLIP_S = 1.3

def run_fish_tts(text, output_wav, ref_wav, ref_text):
    """Generate one sample using Fish Speech CLI."""
    # Step 1: Extract voice tokens
    codec_cmd = [
        sys.executable, str(fish_dir / "fish_speech/models/dac/inference.py"),
        "-i", ref_wav,
        "--checkpoint-path", str(checkpoint / "codec.pth"),
    ]

    # Step 2: Generate semantic tokens
    gen_cmd = [
        sys.executable, str(fish_dir / "fish_speech/models/text2semantic/inference.py"),
        "--text", text,
        "--prompt-text", ref_text,
        "--prompt-tokens", "fake.npy",
        "--compile",
    ]

    # Step 3: Decode to audio
    decode_cmd = [
        sys.executable, str(fish_dir / "fish_speech/models/dac/inference.py"),
        "-i", "codes_0.npy",
    ]

    try:
        subprocess.run(codec_cmd, check=True, capture_output=True)
        subprocess.run(gen_cmd, check=True, capture_output=True)
        subprocess.run(decode_cmd, check=True, capture_output=True)
        shutil.copy2("fake.wav", str(output_wav))
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERROR: {text}: {e.stderr[:200] if e.stderr else e}")
        return False

def clip_to_16k(wav_in, wav_out, clip_s=None):
    """Clip and resample to 16kHz."""
    import librosa, soundfile as sf
    audio, sr = librosa.load(str(wav_in), sr=16000, mono=True)
    if clip_s:
        audio = audio[:int(clip_s * 16000)]
    sf.write(str(wav_out), audio, 16000, subtype="PCM_16")

# Setup output dirs
for sub in ["positive", "positive_16k", "negative", "negative_16k",
            "emotion_positive", "emotion_positive_16k"]:
    (output_dir / sub).mkdir(parents=True, exist_ok=True)

stats = {"name": name, "positive": 0, "negative": 0, "emotion": 0, "failed": 0}

# Generate positives
all_pos = POSITIVE_TEXTS + EMOTION_POSITIVE_TEXTS
for i, text in enumerate(all_pos):
    is_emotion = i >= len(POSITIVE_TEXTS)
    sub = "emotion_positive" if is_emotion else "positive"
    safe = text.replace(" ", "_").replace("[", "").replace("]", "").replace(",", "")
    for r in range(repeats):
        out_24k = output_dir / sub / f"{name}_fish_pos_{i:04d}_{safe}_r{r}.wav"
        out_16k = output_dir / f"{sub}_16k" / f"{name}_fish_pos_{i:04d}_{safe}_r{r}.wav"
        if run_fish_tts(text, out_24k, ref_wav, ref_text):
            clip_to_16k(out_24k, out_16k, clip_s=CLIP_S)
            if is_emotion:
                stats["emotion"] += 1
            else:
                stats["positive"] += 1
        else:
            stats["failed"] += 1
        print(f"  pos: {i*repeats+r+1}/{len(all_pos)*repeats}")

# Generate negatives
for i, text in enumerate(NEGATIVE_TEXTS):
    safe = text.replace(" ", "_").replace(",", "")
    for r in range(repeats):
        out_24k = output_dir / "negative" / f"{name}_fish_neg_{i:04d}_{safe}_r{r}.wav"
        out_16k = output_dir / "negative_16k" / f"{name}_fish_neg_{i:04d}_{safe}_r{r}.wav"
        if run_fish_tts(text, out_24k, ref_wav, ref_text):
            clip_to_16k(out_24k, out_16k, clip_s=None)
            stats["negative"] += 1
        else:
            stats["failed"] += 1
        print(f"  neg: {i*repeats+r+1}/{len(NEGATIVE_TEXTS)*repeats}")

(output_dir / "generation_stats.json").write_text(json.dumps(stats, indent=2) + "\n")
print(f"\nDone: {stats}")
PYSCRIPT

JOB_ID="$(
  sbatch \
    --parsable \
    --job-name="${JOB_NAME}" \
    --account=Project_tanel_alumae \
    --partition="${GPU_PARTITION}" \
    --gres="${GPU_GRES}" \
    --time="${TIME_LIMIT}" \
    --cpus-per-task=4 \
    --mem=32G \
    --chdir="${FISH_DIR}" \
    --output="${LOG_PATH}" \
    --error="${LOG_PATH}" \
    --export=ALL,FISH_NAME="${NAME}",FISH_REF_WAV="${REF_WAV}",FISH_REF_TEXT="${REF_TEXT}",FISH_REPEATS="${REPEATS}",FISH_OUTPUT_DIR="${OUTPUT_DIR}",FISH_DIR="${FISH_DIR}" <<EOF
#!/usr/bin/env bash
set -euo pipefail

echo "Job: \${SLURM_JOB_ID} on \$(hostname)"
echo "GPU: \$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo 'no GPU info')"

# Activate conda env
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null
conda activate ${CONDA_ENV}

python -c "${GENERATE_SCRIPT}"
EOF
)"

echo "Submitted ${JOB_NAME} as job ${JOB_ID}"
echo "  Speaker: ${NAME}"
echo "  Ref: ${REF_WAV}"
echo "  Repeats: ${REPEATS}"
echo "  Output: ${OUTPUT_DIR}"
echo "  Log: ${LOG_PATH/\%j/${JOB_ID}}"
echo ""
echo "Expected output:"
echo "  Positives: $((16 * REPEATS)) + $((6 * REPEATS)) emotion = $(( (16 + 6) * REPEATS ))"
echo "  Negatives: $((20 * REPEATS))"
