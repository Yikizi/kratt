#!/usr/bin/env python3
"""
Run a streaming FAPH (False Activations Per Hour) test on a wake-word model.

Loads a directory of WAV files (treated as the long-form ambient stream),
runs streaming inference, applies a sliding-window moving average, and
counts how many distinct activations cross the configured threshold.

The clips are concatenated with a small inter-clip silence so streaming
state cannot smear detections across clip boundaries.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import soundfile as sf

from microwakeword.inference import Model


def load_16k_int16(path: Path) -> np.ndarray:
    audio, sr = sf.read(str(path), always_2d=False)
    if isinstance(audio, np.ndarray) and audio.ndim > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32, copy=False)
    if sr != 16000:
        import librosa
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000).astype(
            np.float32, copy=False
        )
    audio = np.clip(audio, -1.0, 1.0)
    return (audio * 32767.0).astype(np.int16)


def moving_average(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1 or values.size == 0:
        return values
    kernel = np.ones(window, dtype=np.float32) / float(window)
    return np.convolve(values, kernel, mode="valid")


def count_activations(
    smoothed_scores: np.ndarray,
    threshold: float,
    refractory_frames: int,
) -> int:
    """Count distinct activations: each cross of `threshold` followed by a
    refractory period before the next can fire."""
    activations = 0
    cooldown = 0
    for s in smoothed_scores:
        if cooldown > 0:
            cooldown -= 1
            continue
        if s >= threshold:
            activations += 1
            cooldown = refractory_frames
    return activations


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="Path to streaming TFLite model")
    p.add_argument("--input-dir", required=True, help="Directory of WAVs to test on")
    p.add_argument("--threshold", type=float, default=0.97)
    p.add_argument("--ma-window", type=int, default=5,
                   help="Moving-average window over raw scores (frames)")
    p.add_argument("--refractory-ms", type=int, default=2000,
                   help="Cooldown after each activation (ms)")
    p.add_argument("--step-ms", type=int, default=10)
    p.add_argument("--silence-ms", type=int, default=300,
                   help="Inter-clip silence to inject between clips")
    p.add_argument("--limit", type=int, default=0,
                   help="Optional cap on number of files to process")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    refractory_frames = max(1, args.refractory_ms // args.step_ms)
    silence_samples = (args.silence_ms * 16000) // 1000
    silence = np.zeros(silence_samples, dtype=np.int16)

    files = sorted(Path(args.input_dir).glob("*.wav"))
    if args.limit > 0:
        files = files[: args.limit]
    if not files:
        raise SystemExit(f"No WAV files in {args.input_dir}")

    print(f"Loading model: {args.model}")
    model = Model(args.model)

    total_audio_samples = 0
    total_activations = 0
    activation_log: list[tuple[float, int, str]] = []

    for idx, f in enumerate(files):
        pcm = load_16k_int16(f)
        # Inject leading silence so model state from previous clip drains
        pcm = np.concatenate([silence, pcm])
        total_audio_samples += pcm.size

        raw_scores = np.array(
            model.predict_clip(pcm, step_ms=args.step_ms),
            dtype=np.float32,
        )
        smoothed = moving_average(raw_scores, args.ma_window)
        clip_activations = count_activations(smoothed, args.threshold, refractory_frames)

        if clip_activations > 0:
            # Find first frame index >= threshold for logging
            try:
                first_frame = int(np.argmax(smoothed >= args.threshold))
                first_ms = first_frame * args.step_ms
                activation_log.append((idx, clip_activations, f.name))
                print(
                    f"  ACT  {f.name}  count={clip_activations}  "
                    f"first@{first_ms}ms  max_smoothed={smoothed.max():.3f}"
                )
            except Exception:
                pass

        total_activations += clip_activations

        # reset model state at clip boundary so we don't smear across files
        try:
            model.reset_states()
        except Exception:
            pass

        if (idx + 1) % 250 == 0:
            print(f"  ...{idx + 1}/{len(files)} clips processed, total activations={total_activations}")

    total_seconds = total_audio_samples / 16000.0
    total_hours = total_seconds / 3600.0
    faph = total_activations / total_hours if total_hours > 0 else 0

    print()
    print("=" * 60)
    print(f"Model:           {args.model}")
    print(f"Threshold:       {args.threshold}")
    print(f"Refractory:      {args.refractory_ms} ms")
    print(f"MA window:       {args.ma_window} frames")
    print(f"Inter-clip silence: {args.silence_ms} ms")
    print(f"Files processed: {len(files)}")
    print(f"Total duration:  {total_seconds:.0f}s = {total_seconds/60:.1f}min = {total_hours:.2f}h")
    print(f"Activations:     {total_activations}")
    print(f"FAPH:            {faph:.2f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
