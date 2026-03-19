#!/usr/bin/env python3
"""Segment a long recording into individual wake-word clips using energy-based VAD.

Usage:
    python segment_recordings.py --input data/raw/mattias/rec_0001_mic1.wav \
                                 --output data/processed/positive/mattias \
                                 --label kuule_kratt

The script:
  1. Resamples to 16 kHz (microWakeWord standard)
  2. Detects speech segments via RMS energy + silence gaps
  3. Writes individual clips with padding
"""

from __future__ import annotations

import argparse
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf


def detect_segments(
    audio: np.ndarray,
    sr: int,
    *,
    frame_length: int = 1024,
    hop_length: int = 256,
    energy_threshold_db: float = -40.0,
    min_silence_s: float = 0.3,
    min_clip_s: float = 0.4,
    max_clip_s: float = 3.0,
    pad_s: float = 0.15,
) -> list[tuple[int, int]]:
    """Return (start_sample, end_sample) pairs for detected utterances."""
    rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
    rms_db = librosa.amplitude_to_db(rms, ref=np.max(rms))

    is_speech = rms_db > energy_threshold_db
    # Convert frame indices -> sample indices
    frame_to_sample = lambda f: int(f * hop_length)

    segments: list[tuple[int, int]] = []
    in_segment = False
    seg_start = 0
    silence_frames = 0
    min_silence_frames = int(min_silence_s * sr / hop_length)

    for i, active in enumerate(is_speech):
        if active:
            if not in_segment:
                seg_start = i
                in_segment = True
            silence_frames = 0
        else:
            if in_segment:
                silence_frames += 1
                if silence_frames >= min_silence_frames:
                    seg_end = i - silence_frames
                    segments.append((frame_to_sample(seg_start), frame_to_sample(seg_end)))
                    in_segment = False
                    silence_frames = 0

    # Close last segment
    if in_segment:
        segments.append((frame_to_sample(seg_start), frame_to_sample(len(is_speech) - 1)))

    # Apply padding and duration filters
    pad_samples = int(pad_s * sr)
    min_samples = int(min_clip_s * sr)
    max_samples = int(max_clip_s * sr)

    filtered = []
    for start, end in segments:
        start = max(0, start - pad_samples)
        end = min(len(audio), end + pad_samples)
        duration = end - start
        if min_samples <= duration <= max_samples:
            filtered.append((start, end))

    return filtered


def main():
    parser = argparse.ArgumentParser(description="Segment long recording into wake-word clips")
    parser.add_argument("--input", required=True, nargs="+", help="Input WAV file(s)")
    parser.add_argument("--output", required=True, help="Output directory for clips")
    parser.add_argument("--label", default="kuule_kratt", help="Label prefix for clip filenames")
    parser.add_argument("--target-sr", type=int, default=16000, help="Target sample rate")
    parser.add_argument("--energy-threshold-db", type=float, default=-40.0,
                        help="RMS energy threshold in dB (relative to peak)")
    parser.add_argument("--min-silence", type=float, default=0.3, help="Min silence gap between segments (s)")
    parser.add_argument("--min-clip", type=float, default=0.4, help="Min clip duration (s)")
    parser.add_argument("--max-clip", type=float, default=3.0, help="Max clip duration (s)")
    parser.add_argument("--pad", type=float, default=0.15, help="Padding around each clip (s)")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    clip_index = 0

    for input_path in args.input:
        input_path = Path(input_path)
        print(f"\nProcessing: {input_path}")

        audio, orig_sr = sf.read(input_path, dtype="float32")
        if audio.ndim > 1:
            audio = audio[:, 0]  # take first channel

        # Resample to target SR
        if orig_sr != args.target_sr:
            audio = librosa.resample(audio, orig_sr=orig_sr, target_sr=args.target_sr)
            print(f"  Resampled {orig_sr} -> {args.target_sr} Hz")

        print(f"  Duration: {len(audio)/args.target_sr:.1f}s")

        segments = detect_segments(
            audio,
            args.target_sr,
            energy_threshold_db=args.energy_threshold_db,
            min_silence_s=args.min_silence,
            min_clip_s=args.min_clip,
            max_clip_s=args.max_clip,
            pad_s=args.pad,
        )

        print(f"  Found {len(segments)} segments")

        for start, end in segments:
            clip = audio[start:end]
            duration = len(clip) / args.target_sr
            out_file = output_dir / f"{args.label}_{clip_index:04d}.wav"
            sf.write(str(out_file), clip, args.target_sr, subtype="PCM_16")
            clip_index += 1

        print(f"  Wrote clips {clip_index - len(segments):04d}..{clip_index - 1:04d}")

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
