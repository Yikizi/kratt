#!/usr/bin/env python3
"""Segment a long recording into individual wake-word clips using Silero VAD.

Unlike energy-based segmentation, this handles noisy environments (car, street)
by using a neural network trained to distinguish speech from noise.

Usage:
    python segment_vad.py --input data/raw/mattias/*.wav \
                          --output data/processed/positive/mattias \
                          --label kuule_kratt
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

torch.set_num_threads(1)


def load_silero_vad():
    from silero_vad import load_silero_vad as _load, get_speech_timestamps
    model = _load()
    return model, get_speech_timestamps


def segment_with_vad(
    audio: np.ndarray,
    sr: int,
    model,
    get_speech_timestamps,
    *,
    min_clip_s: float = 0.4,
    max_clip_s: float = 3.0,
    pad_s: float = 0.10,
) -> list[tuple[int, int]]:
    """Use Silero VAD to find speech segments, then filter by duration."""
    tensor = torch.from_numpy(audio).float()

    speech_timestamps = get_speech_timestamps(
        tensor,
        model,
        sampling_rate=sr,
        min_speech_duration_ms=200,
        min_silence_duration_ms=250,
        speech_pad_ms=int(pad_s * 1000),
    )

    min_samples = int(min_clip_s * sr)
    max_samples = int(max_clip_s * sr)

    segments = []
    for ts in speech_timestamps:
        start, end = ts["start"], ts["end"]
        duration = end - start
        if min_samples <= duration <= max_samples:
            segments.append((start, end))

    return segments


def main():
    parser = argparse.ArgumentParser(description="Segment recording with Silero VAD")
    parser.add_argument("--input", required=True, nargs="+", help="Input WAV file(s)")
    parser.add_argument("--output", required=True, help="Output directory for clips")
    parser.add_argument("--label", default="kuule_kratt", help="Label prefix")
    parser.add_argument("--target-sr", type=int, default=16000, help="Target sample rate")
    parser.add_argument("--min-clip", type=float, default=0.4, help="Min clip duration (s)")
    parser.add_argument("--max-clip", type=float, default=3.0, help="Max clip duration (s)")
    parser.add_argument("--pad", type=float, default=0.10, help="Padding around each clip (s)")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Loading Silero VAD...")
    model, get_speech_timestamps = load_silero_vad()

    clip_index = 0

    for input_path in args.input:
        input_path = Path(input_path)
        print(f"\nProcessing: {input_path}")

        audio, orig_sr = sf.read(input_path, dtype="float32")
        if audio.ndim > 1:
            audio = audio[:, 0]

        # Silero VAD needs 16kHz
        if orig_sr != args.target_sr:
            import torchaudio
            tensor = torch.from_numpy(audio).float().unsqueeze(0)
            tensor = torchaudio.functional.resample(tensor, orig_sr, args.target_sr)
            audio = tensor.squeeze(0).numpy()
            print(f"  Resampled {orig_sr} -> {args.target_sr} Hz")

        print(f"  Duration: {len(audio)/args.target_sr:.1f}s")

        model.reset_states()
        segments = segment_with_vad(
            audio,
            args.target_sr,
            model,
            get_speech_timestamps,
            min_clip_s=args.min_clip,
            max_clip_s=args.max_clip,
            pad_s=args.pad,
        )

        print(f"  Found {len(segments)} segments")

        for start, end in segments:
            clip = audio[start:end]
            out_file = output_dir / f"{args.label}_{clip_index:04d}.wav"
            sf.write(str(out_file), clip, args.target_sr, subtype="PCM_16")
            clip_index += 1

        print(f"  Wrote clips up to {clip_index - 1:04d}")

    if clip_index == 0:
        print("\nNo clips found!")
        return

    durations = []
    for f in sorted(output_dir.glob("*.wav")):
        d, sr = sf.read(f)
        durations.append(len(d) / sr)

    print(f"\n{'='*50}")
    print(f"Total clips: {clip_index}")
    print(f"Duration: min={min(durations):.2f}s, max={max(durations):.2f}s, mean={np.mean(durations):.2f}s")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
