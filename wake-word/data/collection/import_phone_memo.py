#!/usr/bin/env python3
"""
Import a "long take" phone recording (e.g. iPhone Voice Memo .m4a) and cut it into
fixed-length wake word clips suitable for microWakeWord training.

Design goals:
- Minimal dependencies: use ffmpeg for decoding, stdlib for WAV IO + numpy for DSP.
- Output WAVs: mono, 16 kHz, 16-bit PCM.
- Segment by simple RMS + silence detection (works well when you speak the wake word
  with pauses in between).

Typical usage:
  ./wake-word/data/collection/import_phone_memo.py \
    --in-file ~/Downloads/kratt.m4a \
    --out-dir wake-word/data/processed/positive_samples \
    --prefix korvo2_iphone_kratt \
    --target-ms 1500
"""

from __future__ import annotations

import argparse
import math
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import wave


def _run(cmd: list[str]) -> None:
    subprocess.check_call(cmd)


def decode_to_wav_16k_mono(in_file: Path, out_wav: Path) -> None:
    # Force a deterministic format for segmentation + training.
    _run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(in_file),
            "-ac",
            "1",
            "-ar",
            "16000",
            "-f",
            "wav",
            str(out_wav),
        ]
    )


def read_wav_mono_16k(wav_path: Path) -> np.ndarray:
    with wave.open(str(wav_path), "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        fr = wf.getframerate()
        n_frames = wf.getnframes()
        if n_channels != 1:
            raise ValueError(f"Expected mono wav, got channels={n_channels}")
        if fr != 16000:
            raise ValueError(f"Expected 16kHz wav, got framerate={fr}")
        if sampwidth != 2:
            raise ValueError(f"Expected 16-bit PCM wav, got sampwidth={sampwidth}")

        raw = wf.readframes(n_frames)
    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    # Normalize to [-1, 1] for RMS computation.
    audio /= 32768.0
    return audio


def write_wav_mono_16k_int16(path: Path, audio_f32: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Clip and convert to int16 PCM.
    audio_f32 = np.asarray(audio_f32, dtype=np.float32)
    audio_i16 = np.clip(audio_f32, -1.0, 1.0)
    audio_i16 = (audio_i16 * 32767.0).astype(np.int16)

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio_i16.tobytes())


def frames_rms_db(audio: np.ndarray, frame_len: int, hop_len: int) -> np.ndarray:
    if len(audio) < frame_len:
        return np.array([], dtype=np.float32)
    n = 1 + (len(audio) - frame_len) // hop_len
    out = np.empty(n, dtype=np.float32)
    eps = 1e-12
    for i in range(n):
        start = i * hop_len
        frame = audio[start : start + frame_len]
        rms = float(np.sqrt(np.mean(frame * frame)))
        out[i] = 20.0 * math.log10(max(rms, eps))
    return out


def segments_from_vad_like(
    rms_db: np.ndarray,
    hop_len: int,
    sr: int,
    threshold_db: float,
    min_speech_ms: int,
    min_silence_ms: int,
) -> list[tuple[int, int]]:
    """
    Return list of (start_sample, end_sample) segments where speech is present.
    """
    if rms_db.size == 0:
        return []

    speech = rms_db > threshold_db

    min_speech_frames = max(1, int(round((min_speech_ms / 1000.0) * sr / hop_len)))
    min_silence_frames = max(1, int(round((min_silence_ms / 1000.0) * sr / hop_len)))

    segments: list[tuple[int, int]] = []
    in_seg = False
    seg_start_f = 0
    silence_run = 0

    for i, is_speech in enumerate(speech.tolist()):
        if is_speech:
            silence_run = 0
            if not in_seg:
                in_seg = True
                seg_start_f = i
        else:
            if in_seg:
                silence_run += 1
                if silence_run >= min_silence_frames:
                    seg_end_f = i - silence_run + 1
                    if (seg_end_f - seg_start_f) >= min_speech_frames:
                        start_s = seg_start_f * hop_len
                        end_s = seg_end_f * hop_len
                        segments.append((start_s, end_s))
                    in_seg = False
                    silence_run = 0

    if in_seg:
        seg_end_f = len(speech)
        if (seg_end_f - seg_start_f) >= min_speech_frames:
            segments.append((seg_start_f * hop_len, seg_end_f * hop_len))

    return segments


def force_target_window(
    start_s: int,
    end_s: int,
    total_s: int,
    target_s: int,
) -> tuple[int, int]:
    """
    Center a fixed-length window around the segment mid-point.
    """
    seg_mid = (start_s + end_s) // 2
    half = target_s // 2
    out_start = seg_mid - half
    out_end = out_start + target_s

    if out_start < 0:
        out_start = 0
        out_end = target_s
    if out_end > total_s:
        out_end = total_s
        out_start = max(0, out_end - target_s)
    return out_start, out_end


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-file", required=True, help="Input audio file (m4a/wav/...)")
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parents[3] / "wake-word" / "data" / "processed" / "positive_samples"),
        help="Output directory for clipped WAVs (default: wake-word/data/processed/positive_samples)",
    )
    parser.add_argument("--prefix", default="korvo2_iphone_kratt", help="Output filename prefix")
    parser.add_argument("--target-ms", type=int, default=1500, help="Clip length in ms (default: 1500)")
    parser.add_argument("--frame-ms", type=int, default=30, help="RMS frame size in ms (default: 30)")
    parser.add_argument("--hop-ms", type=int, default=10, help="RMS hop size in ms (default: 10)")
    parser.add_argument("--threshold-offset-db", type=float, default=18.0, help="Speech threshold above noise floor (default: +18dB)")
    parser.add_argument("--min-speech-ms", type=int, default=200, help="Minimum speech segment length (default: 200)")
    parser.add_argument("--min-silence-ms", type=int, default=220, help="Minimum silence to close a segment (default: 220)")
    parser.add_argument("--max-clips", type=int, default=300, help="Safety cap on number of clips (default: 300)")

    args = parser.parse_args()

    in_file = Path(args.in_file).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    prefix = args.prefix

    if not in_file.exists():
        raise SystemExit(f"Input file not found: {in_file}")

    sr = 16000
    target_s = int(sr * (args.target_ms / 1000.0))
    frame_len = int(sr * (args.frame_ms / 1000.0))
    hop_len = int(sr * (args.hop_ms / 1000.0))

    with tempfile.TemporaryDirectory(prefix="kratt_phone_import_") as td:
        tmp_wav = Path(td) / "decoded.wav"
        decode_to_wav_16k_mono(in_file=in_file, out_wav=tmp_wav)

        audio = read_wav_mono_16k(tmp_wav)
        if audio.size == 0:
            raise SystemExit("Decoded audio is empty")

        rms_db = frames_rms_db(audio, frame_len=frame_len, hop_len=hop_len)
        if rms_db.size == 0:
            raise SystemExit("Audio too short for chosen frame/hop")

        # Estimate noise floor and choose a threshold relative to it.
        noise_floor = float(np.percentile(rms_db, 20.0))
        threshold_db = noise_floor + float(args.threshold_offset_db)

        segs = segments_from_vad_like(
            rms_db=rms_db,
            hop_len=hop_len,
            sr=sr,
            threshold_db=threshold_db,
            min_speech_ms=args.min_speech_ms,
            min_silence_ms=args.min_silence_ms,
        )

        if not segs:
            raise SystemExit(
                f"No speech segments found. Try lowering --threshold-offset-db (noise_floor={noise_floor:.1f}dB, threshold={threshold_db:.1f}dB)."
            )

        total_samp = int(audio.shape[0])
        clips_written = 0
        for idx, (s0, s1) in enumerate(segs, start=1):
            if clips_written >= args.max_clips:
                break

            c0, c1 = force_target_window(s0, s1, total_s=total_samp, target_s=target_s)
            clip = audio[c0:c1]
            if clip.shape[0] != target_s:
                # Pad if we hit file boundaries.
                pad = target_s - clip.shape[0]
                clip = np.pad(clip, (0, max(0, pad)), mode="constant")
                clip = clip[:target_s]

            out_path = out_dir / f"{prefix}_{idx:04d}.wav"
            write_wav_mono_16k_int16(out_path, clip)
            clips_written += 1

        print(f"Input: {in_file}")
        print(f"Output dir: {out_dir}")
        print(f"Noise floor ~ {noise_floor:.1f} dBFS, threshold ~ {threshold_db:.1f} dBFS")
        print(f"Speech segments: {len(segs)}")
        print(f"Clips written: {clips_written}")


if __name__ == "__main__":
    main()

