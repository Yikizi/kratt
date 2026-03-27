#!/usr/bin/env python3
"""Process KORVO-2 recording session: extract negatives and ambient.

The session contains a long recording where:
- First ~14 minutes: intentional speech (negative data, no wake word)
- Rest: unintentional ambient recording (device left on)

Both parts are useful:
- Speech portion → segmented into negative clips via Silero VAD
- Ambient portion → resampled to 16kHz as continuous ambient file

Usage:
    python process_korvo2_session.py \
        --input ../raw/korvo2_session1/amb_0006_mic1.wav \
        --speech-end 840 \
        --output-negatives ../../data/processed/negative_korvo2 \
        --output-ambient ../../data/processed/ambient_korvo2
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

torch.set_num_threads(1)

TARGET_SR = 16000


def load_silero_vad():
    from silero_vad import load_silero_vad as _load, get_speech_timestamps
    model = _load()
    return model, get_speech_timestamps


def segment_speech(
    audio: np.ndarray,
    sr: int,
    model,
    get_speech_timestamps,
    *,
    min_clip_s: float = 1.0,
    max_clip_s: float = 10.0,
    pad_s: float = 0.10,
) -> list[tuple[int, int]]:
    """Use Silero VAD to find speech segments."""
    tensor = torch.from_numpy(audio).float()
    speech_timestamps = get_speech_timestamps(
        tensor, model, sampling_rate=sr,
        min_speech_duration_ms=500,
        min_silence_duration_ms=400,
        speech_pad_ms=int(pad_s * 1000),
    )
    min_samples = int(min_clip_s * sr)
    max_samples = int(max_clip_s * sr)
    segments = []
    for ts in speech_timestamps:
        start, end = ts["start"], ts["end"]
        if min_samples <= (end - start) <= max_samples:
            segments.append((start, end))
    return segments


def resample(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    if orig_sr == target_sr:
        return audio
    tensor = torch.from_numpy(audio).float().unsqueeze(0)
    tensor = torchaudio.functional.resample(tensor, orig_sr, target_sr)
    return tensor.squeeze(0).numpy()


def main():
    parser = argparse.ArgumentParser(description="Process KORVO-2 session recording")
    parser.add_argument("--input", required=True, help="Input WAV file")
    parser.add_argument("--speech-end", type=float, default=840,
                        help="End of speech portion in seconds (default: 840 = 14 min)")
    parser.add_argument("--output-negatives", default="negative_korvo2",
                        help="Output dir for negative speech clips")
    parser.add_argument("--output-ambient", default="ambient_korvo2",
                        help="Output dir for ambient files")
    parser.add_argument("--ambient-chunk-s", type=float, default=300,
                        help="Split ambient into chunks of this length (default: 300s = 5min)")
    args = parser.parse_args()

    input_path = Path(args.input)
    neg_dir = Path(args.output_negatives)
    amb_dir = Path(args.output_ambient)
    neg_dir.mkdir(parents=True, exist_ok=True)
    amb_dir.mkdir(parents=True, exist_ok=True)

    # Read file info
    info = sf.info(str(input_path))
    orig_sr = info.samplerate
    total_s = info.duration
    speech_end_sample = int(args.speech_end * orig_sr)

    print(f"Input: {input_path}")
    print(f"Duration: {total_s:.0f}s ({total_s/3600:.1f}h), SR={orig_sr}Hz")
    print(f"Speech portion: 0 - {args.speech_end:.0f}s")
    print(f"Ambient portion: {args.speech_end:.0f}s - {total_s:.0f}s")

    # === Part 1: Speech portion → negative clips ===
    print(f"\n{'='*50}")
    print("Part 1: Extracting negative speech clips")
    print(f"{'='*50}")

    audio_speech, _ = sf.read(str(input_path), start=0, stop=speech_end_sample, dtype="float32")
    audio_speech = resample(audio_speech, orig_sr, TARGET_SR)
    print(f"Speech audio: {len(audio_speech)/TARGET_SR:.1f}s at {TARGET_SR}Hz")

    print("Loading Silero VAD...")
    model, get_speech_timestamps = load_silero_vad()
    model.reset_states()

    segments = segment_speech(audio_speech, TARGET_SR, model, get_speech_timestamps)
    print(f"Found {len(segments)} speech segments")

    durations = []
    for i, (start, end) in enumerate(segments):
        clip = audio_speech[start:end]
        dur = len(clip) / TARGET_SR
        durations.append(dur)
        out_file = neg_dir / f"korvo2_neg_{i:04d}.wav"
        sf.write(str(out_file), clip, TARGET_SR, subtype="PCM_16")

    if durations:
        print(f"Clips: {len(durations)}, duration: {min(durations):.1f}-{max(durations):.1f}s, "
              f"mean={np.mean(durations):.1f}s, total={sum(durations):.0f}s")

    # === Part 2: Ambient portion → chunked files ===
    print(f"\n{'='*50}")
    print("Part 2: Extracting ambient audio")
    print(f"{'='*50}")

    ambient_start_sample = speech_end_sample
    chunk_samples_orig = int(args.ambient_chunk_s * orig_sr)
    chunk_idx = 0
    pos = ambient_start_sample
    total_ambient_s = 0

    while pos < int(total_s * orig_sr):
        end = min(pos + chunk_samples_orig, int(total_s * orig_sr))
        audio_chunk, _ = sf.read(str(input_path), start=pos, stop=end, dtype="float32")
        audio_chunk = resample(audio_chunk, orig_sr, TARGET_SR)

        chunk_dur = len(audio_chunk) / TARGET_SR
        if chunk_dur < 10:  # skip very short tail chunks
            break

        out_file = amb_dir / f"korvo2_ambient_{chunk_idx:04d}.wav"
        sf.write(str(out_file), audio_chunk, TARGET_SR, subtype="PCM_16")
        total_ambient_s += chunk_dur
        chunk_idx += 1
        pos = end

    print(f"Ambient chunks: {chunk_idx}, total: {total_ambient_s:.0f}s ({total_ambient_s/3600:.1f}h)")

    # === Summary ===
    manifest = {
        "source": str(input_path.name),
        "original_sr": orig_sr,
        "target_sr": TARGET_SR,
        "speech_end_s": args.speech_end,
        "negative_clips": len(segments),
        "negative_total_s": round(sum(durations), 1) if durations else 0,
        "ambient_chunks": chunk_idx,
        "ambient_total_s": round(total_ambient_s, 1),
    }

    manifest_path = neg_dir.parent / "korvo2_session1_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"\n{'='*50}")
    print("Done!")
    print(f"  Negatives: {neg_dir} ({len(segments)} clips)")
    print(f"  Ambient:   {amb_dir} ({chunk_idx} chunks, {total_ambient_s/3600:.1f}h)")
    print(f"  Manifest:  {manifest_path}")


if __name__ == "__main__":
    main()
