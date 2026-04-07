#!/usr/bin/env python3
"""Extract short audio clips around each detection for manual verification.

Runs a wake word model on a directory of WAVs and extracts 6s clips centered
on each activation. Used to verify whether detections are real wake words or
false positives.

Usage:
    python extract_detection_clips.py \
        --model models/kuule-kratt-v6/kuule_kratt_v6.tflite \
        --input-dir data/raw/macbook_negatives \
        --output-dir data/processed/_verify_macbook_bg \
        --threshold 0.995
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf

from microwakeword.inference import Model


STEP_MS = 10
CLIP_DURATION_S = 6.0
SR = 16000


def load_16k_int16(path: Path) -> np.ndarray:
    audio, sr = sf.read(str(path), always_2d=False)
    if audio.ndim > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32, copy=False)
    if sr != SR:
        import librosa
        audio = librosa.resample(audio, orig_sr=sr, target_sr=SR)
    audio = np.clip(audio, -1.0, 1.0)
    return (audio * 32767.0).astype(np.int16)


def moving_average(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1 or values.size == 0:
        return values
    kernel = np.ones(window, dtype=np.float32) / float(window)
    return np.convolve(values, kernel, mode="valid")


def find_all_detections(smoothed_scores: np.ndarray, threshold: float,
                         refractory_frames: int) -> list[int]:
    """Return list of frame indices where activations occurred."""
    detections = []
    cooldown = 0
    for i, s in enumerate(smoothed_scores):
        if cooldown > 0:
            cooldown -= 1
            continue
        if s >= threshold:
            detections.append(i)
            cooldown = refractory_frames
    return detections


def extract_clip(pcm: np.ndarray, center_frame: int, step_ms: int) -> np.ndarray:
    """Extract CLIP_DURATION_S of audio centered on a detection frame."""
    center_sample = int(center_frame * step_ms * SR / 1000)
    half = int(CLIP_DURATION_S * SR / 2)
    start = max(0, center_sample - half)
    end = min(len(pcm), center_sample + half)
    return pcm[start:end]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--input-dir", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--threshold", type=float, default=0.995)
    p.add_argument("--ma-window", type=int, default=5)
    p.add_argument("--refractory-ms", type=int, default=2000)
    args = p.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    refractory_frames = max(1, args.refractory_ms // STEP_MS)

    print(f"Loading model: {args.model}")
    model = Model(args.model)

    files = sorted(Path(args.input_dir).glob("*.wav"))
    if not files:
        raise SystemExit(f"No WAVs in {args.input_dir}")

    manifest = []
    clip_idx = 0

    for f in files:
        pcm = load_16k_int16(f)

        raw = np.array(model.predict_clip(pcm, step_ms=STEP_MS), dtype=np.float32)
        smoothed = moving_average(raw, args.ma_window)

        detections = find_all_detections(smoothed, args.threshold, refractory_frames)

        for det_frame in detections:
            det_ms = det_frame * STEP_MS
            det_s = det_ms / 1000
            score = float(smoothed[det_frame])

            clip = extract_clip(pcm, det_frame, STEP_MS)

            out_name = f"det_{clip_idx:03d}_{f.stem}_at_{int(det_s)}s_score_{score:.3f}.wav"
            out_path = output_dir / out_name
            sf.write(str(out_path), clip, SR, subtype="PCM_16")

            manifest.append({
                "clip_idx": clip_idx,
                "source_file": f.name,
                "detection_time_s": round(det_s, 2),
                "score": round(score, 4),
                "clip_file": out_name,
            })

            print(f"  [{clip_idx:3d}] {f.name} @ {det_s:6.1f}s  score={score:.3f}  -> {out_name}")
            clip_idx += 1

        try:
            model.reset_states()
        except Exception:
            pass

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    print()
    print(f"Total detections extracted: {len(manifest)}")
    print(f"Output: {output_dir}")
    print()
    print("Listen to each clip and mark which are REAL wake words vs false positives.")
    print(f"Then edit {manifest_path} and add \"is_wake_word\": true/false to each entry.")


if __name__ == "__main__":
    main()
