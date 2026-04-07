#!/usr/bin/env python3
"""Generate training samples using XTTS v2 voice cloning.

Clones a speaker's voice from reference audio and generates both
positive ("Kuule Kratt") and negative (hard negative) samples.
Symmetry principle: same cloned voice in both classes.

Usage:
    python generate_xtts_clones.py --name marta \
        --ref-dir ../raw/voice_references/marta \
        --output ../raw/xtts_clones/marta
"""

from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

import numpy as np
import soundfile as sf
from tqdm import tqdm

# Positive texts — "Kuule Kratt" in natural sentence context.
# XTTS handles short phrases poorly (wrong stress/prosody).
# Generate in context, then cut first CLIP_DURATION_S to extract "Kuule Kratt".
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

# Duration to cut from start of generated audio (captures "Kuule Kratt" + trailing silence)
CLIP_DURATION_S = 1.3

# Hard negatives (same voice, wrong phrase — symmetry principle)
NEGATIVE_TEXTS = [
    "Kuule kraad",
    "Kuule kraam",
    "Kuule ratt",
    "Kuule matt",
    "Kuule krats",
    "Kuule kraft",
    "Kuule pratt",
    "Kuule kriit",
    "Kuule kruvi",
    "Kuule kroon",
    "Kuule kass",
    "Kuule koer",
    "Kuule siin",
    "Kuule nüüd",
    "Kuule palun",
    "Tere Kratt",
    "Hei Kratt",
    "Kratt kuule",
    "See kratt",
    "Mis kratt",
]


def find_best_reference(ref_dir: Path) -> Path:
    """Pick the best reference WAV (largest file = longest recording)."""
    wavs = sorted(ref_dir.glob("*.wav"), key=lambda f: f.stat().st_size, reverse=True)
    if not wavs:
        raise FileNotFoundError(f"No WAV files in {ref_dir}")
    return wavs[0]


def clip_and_resample_to_16k(audio_path: Path, output_path: Path, clip_s: float | None = None):
    """Optionally clip to first N seconds, then resample to 16kHz mono for training."""
    import librosa

    audio, sr = librosa.load(str(audio_path), sr=16000, mono=True)
    if clip_s is not None:
        max_samples = int(clip_s * 16000)
        audio = audio[:max_samples]
    sf.write(str(output_path), audio, 16000, subtype="PCM_16")


def generate_with_xtts(
    client,
    text: str,
    ref_handle,
    output_path: Path,
    retries: int = 2,
) -> bool:
    """Generate one sample via XTTS v2 Gradio API."""
    for attempt in range(retries + 1):
        try:
            result = client.predict(
                prompt=text,
                language="et",
                speaker_wav=ref_handle,
                voice_cleanup=False,
                agree=True,
                api_name="/predict",
            )
            # result is (audio_path, metrics_text, ref_used)
            audio_path = result[0]
            shutil.copy2(audio_path, str(output_path))
            return True
        except Exception as e:
            if attempt < retries:
                time.sleep(2)
                continue
            print(f"    ❌ {text}: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Generate XTTS v2 cloned voice samples")
    parser.add_argument("--name", required=True, help="Speaker name")
    parser.add_argument("--ref-dir", required=True, help="Directory with reference WAV(s)")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--skip-negatives", action="store_true", help="Only generate positives")
    parser.add_argument("--repeats", type=int, default=3, help="Generate each phrase N times (default: 3)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between API calls (s)")
    args = parser.parse_args()

    ref_dir = Path(args.ref_dir)
    output_dir = Path(args.output)

    # Find best reference
    ref_path = find_best_reference(ref_dir)
    ref_audio, ref_sr = sf.read(ref_path)
    ref_dur = len(ref_audio) / ref_sr
    print(f"  Referents: {ref_path.name} ({ref_dur:.1f}s, {ref_sr}Hz)")

    # Connect to XTTS
    print("  Ühendan TartuNLP XTTS v2...")
    from gradio_client import Client, handle_file
    client = Client("tartuNLP/XTTSv2-est", verbose=False)
    ref_handle = handle_file(str(ref_path))
    print("  ✅ Ühendatud\n")

    # Generate positives
    pos_dir = output_dir / "positive"
    pos_dir.mkdir(parents=True, exist_ok=True)
    pos_16k_dir = output_dir / "positive_16k"
    pos_16k_dir.mkdir(parents=True, exist_ok=True)

    stats = {"name": args.name, "ref": ref_path.name, "positive": 0, "negative": 0, "failed": 0}

    total_pos = len(POSITIVE_TEXTS) * args.repeats
    print(f"  Genereerin positiivseid ({len(POSITIVE_TEXTS)} fraasi × {args.repeats} korda = {total_pos}, lõikan {CLIP_DURATION_S}s)...")
    idx = 0
    for i, text in enumerate(POSITIVE_TEXTS):
        safe = text.replace(" ", "_").replace(",", "").replace(".", "").replace("!", "").replace("?", "")
        for r in range(args.repeats):
            out_24k = pos_dir / f"{args.name}_xtts_pos_{idx:04d}_{safe}_r{r}.wav"
            out_16k = pos_16k_dir / f"{args.name}_xtts_pos_{idx:04d}_{safe}_r{r}.wav"

            if generate_with_xtts(client, text, ref_handle, out_24k):
                clip_and_resample_to_16k(out_24k, out_16k, clip_s=CLIP_DURATION_S)
                stats["positive"] += 1
            else:
                stats["failed"] += 1
            idx += 1
            print(f"\r  pos: {idx}/{total_pos}", end="", flush=True)
            time.sleep(args.delay)
    print()

    # Generate negatives (symmetry principle)
    if not args.skip_negatives:
        neg_dir = output_dir / "negative"
        neg_dir.mkdir(parents=True, exist_ok=True)
        neg_16k_dir = output_dir / "negative_16k"
        neg_16k_dir.mkdir(parents=True, exist_ok=True)

        total_neg = len(NEGATIVE_TEXTS) * args.repeats
        print(f"\n  Genereerin negatiivseid ({len(NEGATIVE_TEXTS)} fraasi × {args.repeats} korda = {total_neg})...")
        idx = 0
        for i, text in enumerate(NEGATIVE_TEXTS):
            safe = text.replace(" ", "_").replace(",", "").replace(".", "").replace("!", "").replace("?", "")
            for r in range(args.repeats):
                out_24k = neg_dir / f"{args.name}_xtts_neg_{idx:04d}_{safe}_r{r}.wav"
                out_16k = neg_16k_dir / f"{args.name}_xtts_neg_{idx:04d}_{safe}_r{r}.wav"

                if generate_with_xtts(client, text, ref_handle, out_24k):
                    clip_and_resample_to_16k(out_24k, out_16k, clip_s=None)
                    stats["negative"] += 1
                else:
                    stats["failed"] += 1
                idx += 1
                print(f"\r  neg: {idx}/{total_neg}", end="", flush=True)
                time.sleep(args.delay)
        print()

    # Save stats
    stats_path = output_dir / "generation_stats.json"
    stats_path.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n")

    print(f"\n  {'=' * 50}")
    print(f"  ✅ {args.name} kloonid valmis")
    print(f"     Positiivseid: {stats['positive']}")
    print(f"     Negatiivseid: {stats['negative']}")
    print(f"     Ebaõnnestunud: {stats['failed']}")
    print(f"     24kHz: {output_dir}/positive/ ja negative/")
    print(f"     16kHz: {output_dir}/positive_16k/ ja negative_16k/")
    print(f"     Stats: {stats_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  ⚠️ Katkestatud.")
    except Exception as e:
        print(f"\n  ❌ {e}")
        raise
