#!/usr/bin/env python3
"""Extract speech segments from the ambient portion of a KORVO-2 recording.

The first 840s were intentional speech (already processed). This script
runs Silero VAD on the remainder (840s to end) to find intermittent speech
activity, extracts clips of 1-10s, resamples to 16kHz, and saves them.

Processes in 5-minute chunks to avoid loading the full 2GB file.

Usage:
    python extract_korvo2_ambient_speech.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

torch.set_num_threads(1)

# === Configuration ===
INPUT_PATH = Path(__file__).resolve().parent.parent / "raw" / "korvo2_session1" / "amb_0006_mic1.wav"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "processed" / "negative_korvo2_extra"
TARGET_SR = 16000
AMBIENT_START_S = 840.0       # Skip the intentional speech portion
CHUNK_DURATION_S = 300.0      # Process 5 minutes at a time
MIN_CLIP_S = 1.0
MAX_CLIP_S = 10.0
SPEECH_PAD_MS = 100
MIN_SPEECH_MS = 500
MIN_SILENCE_MS = 400


def load_silero_vad():
    from silero_vad import load_silero_vad as _load, get_speech_timestamps
    model = _load()
    return model, get_speech_timestamps


def resample(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    if orig_sr == target_sr:
        return audio
    tensor = torch.from_numpy(audio).float().unsqueeze(0)
    tensor = torchaudio.functional.resample(tensor, orig_sr, target_sr)
    return tensor.squeeze(0).numpy()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    info = sf.info(str(INPUT_PATH))
    orig_sr = info.samplerate
    total_duration_s = info.duration
    total_frames = info.frames

    print(f"Input: {INPUT_PATH}")
    print(f"Duration: {total_duration_s:.0f}s ({total_duration_s/3600:.1f}h), SR={orig_sr}Hz")
    print(f"Scanning ambient portion: {AMBIENT_START_S:.0f}s - {total_duration_s:.0f}s")
    print(f"  = {total_duration_s - AMBIENT_START_S:.0f}s ({(total_duration_s - AMBIENT_START_S)/3600:.1f}h)")
    print()

    print("Loading Silero VAD...")
    model, get_speech_timestamps = load_silero_vad()
    print("VAD loaded.\n")

    # Process in chunks
    chunk_samples_orig = int(CHUNK_DURATION_S * orig_sr)
    start_sample = int(AMBIENT_START_S * orig_sr)

    all_clips = []  # (global_start_s, global_end_s, clip_index)
    clip_index = 0
    chunk_count = 0

    pos = start_sample
    while pos < total_frames:
        end = min(pos + chunk_samples_orig, total_frames)
        chunk_start_s = pos / orig_sr
        chunk_end_s = end / orig_sr

        # Read chunk at original SR
        audio_chunk, _ = sf.read(str(INPUT_PATH), start=pos, stop=end, dtype="float32")

        # Resample to 16kHz for VAD
        audio_16k = resample(audio_chunk, orig_sr, TARGET_SR)

        # Reset VAD state for each chunk
        model.reset_states()

        # Run VAD
        tensor = torch.from_numpy(audio_16k).float()
        speech_timestamps = get_speech_timestamps(
            tensor, model, sampling_rate=TARGET_SR,
            min_speech_duration_ms=MIN_SPEECH_MS,
            min_silence_duration_ms=MIN_SILENCE_MS,
            speech_pad_ms=SPEECH_PAD_MS,
        )

        min_samples = int(MIN_CLIP_S * TARGET_SR)
        max_samples = int(MAX_CLIP_S * TARGET_SR)

        chunk_clips = 0
        for ts in speech_timestamps:
            seg_start, seg_end = ts["start"], ts["end"]
            seg_len = seg_end - seg_start
            if min_samples <= seg_len <= max_samples:
                clip = audio_16k[seg_start:seg_end]
                out_file = OUTPUT_DIR / f"korvo2_neg_extra_{clip_index:04d}.wav"
                sf.write(str(out_file), clip, TARGET_SR, subtype="PCM_16")

                global_start = chunk_start_s + seg_start / TARGET_SR
                global_end = chunk_start_s + seg_end / TARGET_SR
                all_clips.append({
                    "index": clip_index,
                    "file": out_file.name,
                    "global_start_s": round(global_start, 2),
                    "global_end_s": round(global_end, 2),
                    "duration_s": round(seg_len / TARGET_SR, 2),
                })
                clip_index += 1
                chunk_clips += 1

        if chunk_clips > 0:
            print(f"  Chunk {chunk_count:3d} [{chunk_start_s:7.0f}s - {chunk_end_s:7.0f}s]: "
                  f"{chunk_clips} clips extracted")

        chunk_count += 1
        pos = end

    # === Summary ===
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total clips extracted: {len(all_clips)}")

    if not all_clips:
        print("No speech clips found in the ambient portion.")
        return

    durations = [c["duration_s"] for c in all_clips]
    total_dur = sum(durations)
    print(f"Total speech duration: {total_dur:.1f}s ({total_dur/60:.1f} min)")
    print(f"Clip duration range: {min(durations):.1f}s - {max(durations):.1f}s")
    print(f"Mean clip duration: {np.mean(durations):.2f}s")
    print(f"Median clip duration: {np.median(durations):.2f}s")

    # Distribution across the recording (in 30-min bins)
    print(f"\n{'='*60}")
    print("DISTRIBUTION ACROSS RECORDING (30-min bins)")
    print(f"{'='*60}")

    bin_size_s = 1800  # 30 minutes
    max_time = max(c["global_end_s"] for c in all_clips)
    bin_start = AMBIENT_START_S

    while bin_start < max_time:
        bin_end = bin_start + bin_size_s
        bin_clips = [c for c in all_clips if c["global_start_s"] >= bin_start and c["global_start_s"] < bin_end]
        if bin_clips:
            bin_dur = sum(c["duration_s"] for c in bin_clips)
            h_start = int(bin_start // 3600)
            m_start = int((bin_start % 3600) // 60)
            h_end = int(bin_end // 3600)
            m_end = int((bin_end % 3600) // 60)
            print(f"  {h_start}:{m_start:02d} - {h_end}:{m_end:02d}  : "
                  f"{len(bin_clips):3d} clips, {bin_dur:6.1f}s total")
        bin_start = bin_end

    # Save manifest
    manifest = {
        "source": INPUT_PATH.name,
        "original_sr": orig_sr,
        "target_sr": TARGET_SR,
        "ambient_start_s": AMBIENT_START_S,
        "total_clips": len(all_clips),
        "total_speech_duration_s": round(total_dur, 1),
        "min_clip_s": round(min(durations), 2),
        "max_clip_s": round(max(durations), 2),
        "mean_clip_s": round(float(np.mean(durations)), 2),
        "clips": all_clips,
    }
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"\nManifest saved: {manifest_path}")
    print(f"Clips saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
