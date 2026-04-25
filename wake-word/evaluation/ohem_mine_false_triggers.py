#!/usr/bin/env python3
"""Online Hard Example Mining: score all clips in a directory with a model,
rank by max confidence, output the top false triggers.

Usage:
    python ohem_mine_false_triggers.py \
        --model models/kuule-kratt-expert-a/kuule_kratt_expert-a.tflite \
        --clips data/processed/faph_test_cv_et \
        --top 200 \
        --out-csv evaluation/ohem_expert_a_cv_et.csv \
        --copy-to data/mined/ohem_expert_a_top200
"""
from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path

import numpy as np
import soundfile as sf

from microwakeword.inference import Model

STEP_MS = 10
SR = 16_000


def score_clip(model: Model, wav_path: Path) -> float:
    """Run inference on a clip via predict_clip and return the max score."""
    audio, file_sr = sf.read(str(wav_path), dtype="int16")
    if file_sr != SR:
        import librosa
        audio_f = audio.astype(np.float32) / 32768.0
        audio_f = librosa.resample(audio_f, orig_sr=file_sr, target_sr=SR)
        audio = (audio_f * 32768).astype(np.int16)

    if audio.ndim > 1:
        audio = audio[:, 0]

    predictions = model.predict_clip(audio, step_ms=STEP_MS)
    if not predictions:
        return 0.0
    return float(max(predictions))


def main():
    parser = argparse.ArgumentParser(description="OHEM false trigger mining")
    parser.add_argument("--model", required=True, help="Path to .tflite model")
    parser.add_argument("--clips", required=True, help="Directory of WAV clips to score")
    parser.add_argument("--top", type=int, default=200, help="Number of top false triggers to output")
    parser.add_argument("--out-csv", required=True, help="Output CSV with scores")
    parser.add_argument("--copy-to", default=None, help="Copy top clips to this directory")
    parser.add_argument("--threshold", type=float, default=0.0, help="Only report clips above this score")
    args = parser.parse_args()

    model_path = Path(args.model)
    clips_dir = Path(args.clips)
    out_csv = Path(args.out_csv)

    wavs = sorted(clips_dir.glob("*.wav"))
    if not wavs:
        print(f"No .wav files found in {clips_dir}")
        return

    print(f"Model: {model_path.name}")
    print(f"Clips: {len(wavs)} in {clips_dir}")
    print(f"Scoring...")

    model = Model(str(model_path))

    results = []
    for i, wav in enumerate(wavs):
        score = score_clip(model, wav)
        results.append((wav.name, score))
        if (i + 1) % 200 == 0:
            print(f"  {i + 1}/{len(wavs)} scored...")

    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)

    # Filter by threshold
    if args.threshold > 0:
        results = [(n, s) for n, s in results if s >= args.threshold]

    # Write CSV
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "max_score"])
        for name, score in results:
            writer.writerow([name, f"{score:.6f}"])

    print(f"\nResults saved to {out_csv}")
    print(f"Total clips scored: {len(wavs)}")

    # Report top N
    top_n = min(args.top, len(results))
    above_50 = sum(1 for _, s in results if s >= 0.5)
    above_90 = sum(1 for _, s in results if s >= 0.9)
    above_97 = sum(1 for _, s in results if s >= 0.97)
    above_99 = sum(1 for _, s in results if s >= 0.99)

    print(f"\nDistribution:")
    print(f"  score >= 0.50: {above_50} clips")
    print(f"  score >= 0.90: {above_90} clips")
    print(f"  score >= 0.97: {above_97} clips")
    print(f"  score >= 0.99: {above_99} clips")
    print(f"\nTop {top_n} false triggers:")
    for name, score in results[:top_n]:
        print(f"  {score:.4f}  {name}")

    # Optionally copy top clips
    if args.copy_to:
        copy_dir = Path(args.copy_to)
        copy_dir.mkdir(parents=True, exist_ok=True)
        for name, score in results[:top_n]:
            src = clips_dir / name
            dst = copy_dir / name
            shutil.copy2(src, dst)
        print(f"\nCopied top {top_n} clips to {copy_dir}")


if __name__ == "__main__":
    main()
