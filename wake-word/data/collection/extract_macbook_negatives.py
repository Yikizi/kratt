#!/usr/bin/env python3
"""Extract speech segments from MacBook background recordings.

Runs Silero VAD on the 14 × 5min background files captured during the
2026-03-24 FPR test session. Extracts short speech clips (1-10s) and saves
them as 16kHz mono WAV files for use as in-domain MacBook negatives.

Usage:
    python extract_macbook_negatives.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

torch.set_num_threads(1)

# === Configuration ===
INPUT_DIR = Path(__file__).resolve().parent.parent / "raw" / "macbook_negatives"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "processed" / "negative_macbook_segmented"
TARGET_SR = 16000
MIN_CLIP_S = 1.0
MAX_CLIP_S = 10.0
SPEECH_PAD_MS = 100
MIN_SPEECH_MS = 500
MIN_SILENCE_MS = 400


def load_silero_vad():
    from silero_vad import load_silero_vad as _load, get_speech_timestamps
    model = _load()
    return model, get_speech_timestamps


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(INPUT_DIR.glob("*.wav"))
    if not files:
        raise SystemExit(f"No WAV files in {INPUT_DIR}")

    print(f"Input dir: {INPUT_DIR}")
    print(f"Output dir: {OUTPUT_DIR}")
    print(f"Files: {len(files)}")
    print()

    print("Loading Silero VAD...")
    model, get_speech_timestamps = load_silero_vad()
    print("VAD loaded.\n")

    min_samples = int(MIN_CLIP_S * TARGET_SR)
    max_samples = int(MAX_CLIP_S * TARGET_SR)

    all_clips = []
    clip_index = 0
    total_input_s = 0.0
    total_speech_s = 0.0

    for file_idx, wav_path in enumerate(files):
        audio, sr = sf.read(str(wav_path), dtype="float32", always_2d=False)
        if audio.ndim > 1:
            audio = audio[:, 0]

        if sr != TARGET_SR:
            import torchaudio
            tensor = torch.from_numpy(audio).float().unsqueeze(0)
            tensor = torchaudio.functional.resample(tensor, sr, TARGET_SR)
            audio = tensor.squeeze(0).numpy()

        duration_s = len(audio) / TARGET_SR
        total_input_s += duration_s

        # Reset VAD state for each file
        model.reset_states()

        tensor = torch.from_numpy(audio).float()
        speech_timestamps = get_speech_timestamps(
            tensor, model, sampling_rate=TARGET_SR,
            min_speech_duration_ms=MIN_SPEECH_MS,
            min_silence_duration_ms=MIN_SILENCE_MS,
            speech_pad_ms=SPEECH_PAD_MS,
        )

        file_clips = 0
        file_speech_s = 0.0
        for ts in speech_timestamps:
            seg_start, seg_end = ts["start"], ts["end"]
            seg_len = seg_end - seg_start
            if min_samples <= seg_len <= max_samples:
                clip = audio[seg_start:seg_end]
                out_file = OUTPUT_DIR / f"macbook_neg_{clip_index:04d}.wav"
                sf.write(str(out_file), clip, TARGET_SR, subtype="PCM_16")

                clip_duration_s = seg_len / TARGET_SR
                all_clips.append({
                    "index": clip_index,
                    "file": out_file.name,
                    "source": wav_path.name,
                    "source_start_s": round(seg_start / TARGET_SR, 2),
                    "source_end_s": round(seg_end / TARGET_SR, 2),
                    "duration_s": round(clip_duration_s, 2),
                })
                clip_index += 1
                file_clips += 1
                file_speech_s += clip_duration_s

        total_speech_s += file_speech_s
        print(f"  [{file_idx+1:2d}/{len(files)}] {wav_path.name}: "
              f"{file_clips:3d} clips ({file_speech_s:5.1f}s speech / {duration_s:5.0f}s total)")

    # === Summary ===
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Input audio:     {total_input_s:.0f}s ({total_input_s/60:.1f}min)")
    print(f"Total clips:     {len(all_clips)}")
    print(f"Total speech:    {total_speech_s:.0f}s ({total_speech_s/60:.1f}min)")
    print(f"Speech ratio:    {total_speech_s/total_input_s*100:.0f}%")

    if all_clips:
        durations = [c["duration_s"] for c in all_clips]
        print(f"Clip range:      {min(durations):.1f}s - {max(durations):.1f}s")
        print(f"Mean clip:       {np.mean(durations):.2f}s")
        print(f"Median clip:     {np.median(durations):.2f}s")

    # Save manifest
    manifest = {
        "source_dir": str(INPUT_DIR),
        "source_files": [f.name for f in files],
        "target_sr": TARGET_SR,
        "total_input_s": round(total_input_s, 1),
        "total_clips": len(all_clips),
        "total_speech_s": round(total_speech_s, 1),
        "min_clip_s": MIN_CLIP_S,
        "max_clip_s": MAX_CLIP_S,
        "clips": all_clips,
    }
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"\nManifest: {manifest_path}")
    print(f"Clips saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
