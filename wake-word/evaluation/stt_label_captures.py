#!/usr/bin/env python3
"""Auto-label captured wake word detections using local STT + optional Silero VAD.

This script sweeps Android capture directories, extracts speech-like regions with
Silero VAD when available, transcribes the trimmed audio with the local Kiirkirjutaja
INT8 recognizer, and emits structured JSONL proposals.

Labels:
  - positive: transcript clearly contains "kuule kratt"
  - hard_negative: transcript contains a confusable phrase or any speech-like
    non-positive capture
  - garbage: silence, noise, or clip too speech-poor to be useful

Recommended sweep for the current Android logs:
    python stt_label_captures.py \
        --input output/android-captures-20260414-1115 \
                output/android-captures-20260414-2014 \
        --out wake-word/data/processed/_labeling/android_capture_proposals.jsonl

Optional:
    python stt_label_captures.py --apply wake-word/data/processed/_labeling/android_capture_proposals.jsonl

Silero VAD is optional. If it is not installed, the script falls back to
transcribing the full clip and labels only from the STT output.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import soundfile as sf


REPO_ROOT = Path(__file__).resolve().parents[2]
STT_MODEL_DIR = REPO_ROOT / "stt-integration" / "kiirkirjutaja-source" / "models" / "sherpa-int8"
DEFAULT_OUTPUT = REPO_ROOT / "wake-word" / "data" / "processed" / "_labeling" / "android_capture_proposals.jsonl"
TARGET_SR = 16_000

# Destination test set directories (created if missing)
TEST_POS_DIR = REPO_ROOT / "wake-word" / "data" / "processed" / "test_pos_mined_real"
TEST_HN_DIR = REPO_ROOT / "wake-word" / "data" / "processed" / "test_hard_neg_mined_real"

# VAD / transcription defaults
DEFAULT_MIN_SPEECH_RATIO = 0.12
DEFAULT_MIN_SPEECH_MS = 250
DEFAULT_MIN_SILENCE_MS = 200
DEFAULT_VAD_PAD_MS = 120
DEFAULT_VAD_MERGE_GAP_MS = 160
DEFAULT_EMPTY_TRANSCRIPT_LABEL = "hard_negative"
DEFAULT_STT_PAD_MS = 220

# Phonetic similarity patterns for hard negatives.
# Looking for "kuule" + confusable word, or "k*tt" patterns.
POSITIVE_RX = re.compile(r"\bkuule\s+kra[dt]+t?\b", re.IGNORECASE)
HARD_NEG_PATTERNS = [
    re.compile(r"\bkuule\s+k\w{2,5}\b", re.IGNORECASE),  # "kuule kra*", "kuule ke*"
    re.compile(r"\bkuule\s+r\w+\b", re.IGNORECASE),      # "kuule rott"
    re.compile(r"\bkuule\s+t\w+\b", re.IGNORECASE),      # "kuule tere"
    re.compile(r"\btere\s+kra\w+\b", re.IGNORECASE),
    re.compile(r"\bhei\s+kra\w+\b", re.IGNORECASE),
    re.compile(r"\bkra\w+\b", re.IGNORECASE),            # standalone "kratt", "kraam"
]


@dataclass
class Capture:
    path: Path
    source_root: Path
    transcript: str
    duration_s: float
    speech_ratio: float | None
    speech_duration_s: float | None
    vad_available: bool
    vad_segments: list[dict[str, float]]
    proposed_label: str
    confidence_note: str
    metadata: dict[str, object] = field(default_factory=dict)


def load_recognizer():
    try:
        import sherpa_onnx
    except Exception as exc:  # pragma: no cover - environment dependent
        sys.exit(f"sherpa_onnx is required for labeling but is missing: {exc}")

    md = STT_MODEL_DIR
    if not md.exists():
        sys.exit(f"STT model dir not found: {md}")
    print(f"[STT] Loading from {md}", file=sys.stderr)
    return sherpa_onnx.OnlineRecognizer.from_transducer(
        tokens=str(md / "tokens.txt"),
        encoder=str(md / "encoder.int8.onnx"),
        decoder=str(md / "decoder.int8.onnx"),
        joiner=str(md / "joiner.int8.onnx"),
        num_threads=2,
        sample_rate=TARGET_SR,
        feature_dim=80,
        enable_endpoint_detection=True,
        rule1_min_trailing_silence=5.0,
        rule2_min_trailing_silence=2.0,
        rule3_min_utterance_length=300,
        decoding_method="modified_beam_search",
    )


def load_vad_backend():
    """Load Silero VAD if available.

    Returns:
        model, get_speech_timestamps, enabled, note
    """
    try:
        import torch
        from silero_vad import get_speech_timestamps
        from silero_vad import load_silero_vad as _load_silero_vad
    except Exception as exc:
        return None, None, False, f"silero_vad unavailable: {exc}"

    torch.set_num_threads(1)
    model = _load_silero_vad()
    return model, get_speech_timestamps, True, "silero_vad"


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    audio, sr = sf.read(str(path), always_2d=False)
    if audio.ndim > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32, copy=False)
    if sr != TARGET_SR:
        import librosa

        audio = librosa.resample(audio, orig_sr=sr, target_sr=TARGET_SR).astype(np.float32)
        sr = TARGET_SR
    return audio, sr


def normalize_audio(audio: np.ndarray) -> np.ndarray:
    return np.clip(audio, -1.0, 1.0).astype(np.float32, copy=False)


def merge_segments(segments: list[tuple[int, int]], max_gap_s: float, sr: int) -> list[tuple[int, int]]:
    if not segments:
        return []
    gap = int(max_gap_s * sr)
    merged: list[list[int]] = [[segments[0][0], segments[0][1]]]
    for start, end in segments[1:]:
        last = merged[-1]
        if start <= last[1] + gap:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]


def analyze_vad(
    audio: np.ndarray,
    sr: int,
    model,
    get_speech_timestamps,
    *,
    pad_ms: int,
    min_speech_ms: int,
    min_silence_ms: int,
    merge_gap_ms: int,
) -> tuple[list[tuple[int, int]], float, float]:
    """Return merged speech segments plus total speech ratio/duration."""
    try:
        import torch
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(f"torch unavailable for Silero VAD: {exc}") from exc

    tensor = torch.from_numpy(audio).float()
    raw_segments = get_speech_timestamps(
        tensor,
        model,
        sampling_rate=sr,
        min_speech_duration_ms=min_speech_ms,
        min_silence_duration_ms=min_silence_ms,
        speech_pad_ms=pad_ms,
    )

    segments = [(int(ts["start"]), int(ts["end"])) for ts in raw_segments]
    segments = merge_segments(segments, merge_gap_ms / 1000.0, sr)
    segments = [(start, end) for start, end in segments if end > start]
    if not segments:
        return [], 0.0, 0.0

    speech_samples = sum(end - start for start, end in segments)
    speech_duration_s = speech_samples / sr
    speech_ratio = speech_samples / len(audio) if len(audio) else 0.0
    return segments, speech_ratio, speech_duration_s


def trim_audio_for_stt(
    audio: np.ndarray,
    segments: list[tuple[int, int]],
    *,
    pad_ms: int,
    sr: int,
) -> tuple[np.ndarray, tuple[int, int] | None]:
    if not segments:
        return audio, None

    pad = int(pad_ms * sr / 1000.0)
    start = max(0, segments[0][0] - pad)
    end = min(len(audio), segments[-1][1] + pad)
    return audio[start:end], (start, end)


def transcribe_audio(recognizer, audio: np.ndarray, sr: int, *, tail_pad_ms: int = DEFAULT_STT_PAD_MS) -> str:
    if len(audio) == 0:
        return ""

    stream = recognizer.create_stream()
    stream.accept_waveform(sr, normalize_audio(audio))

    # Deterministic tail padding helps endpoint detection without injecting
    # random noise into the transcription path.
    tail = np.zeros(int(sr * tail_pad_ms / 1000.0), dtype=np.float32)
    if len(tail):
        stream.accept_waveform(sr, tail)
    stream.input_finished()

    while recognizer.is_ready(stream):
        recognizer.decode_stream(stream)
    text = recognizer.get_result(stream).strip()
    recognizer.reset(stream)
    return text


def classify_transcript(transcript: str) -> tuple[str, str]:
    """Return (label, note) given the STT transcript."""
    t = transcript.strip().lower()
    if not t:
        return DEFAULT_EMPTY_TRANSCRIPT_LABEL, "empty transcript"

    if POSITIVE_RX.search(t):
        return "positive", f"matched wake phrase: {POSITIVE_RX.pattern}"

    for rx in HARD_NEG_PATTERNS:
        m = rx.search(t)
        if m:
            return "hard_negative", f"matched pattern {rx.pattern!r}: {m.group(0)!r}"

    return "hard_negative", "speech-like audio but no wake-phrase match"


def load_index_metadata(root: Path) -> dict[str, dict]:
    """Load capture metadata from a sidecar index.jsonl if present."""
    index_path = root / "index.jsonl"
    if not index_path.exists():
        return {}

    lookup: dict[str, dict] = {}
    with index_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            local_wav = rec.get("local_wav")
            wav_basename = rec.get("wav_basename")
            if local_wav:
                lookup[str(Path(local_wav).resolve())] = rec
            if wav_basename:
                lookup[str(wav_basename)] = rec
    return lookup


def collect_files(input_dirs: Iterable[Path], limit: int | None = None) -> list[tuple[Path, Path]]:
    items: list[tuple[Path, Path]] = []
    for root in input_dirs:
        if not root.exists():
            print(f"[WARN] input dir missing: {root}", file=sys.stderr)
            continue
        for wav in sorted(root.rglob("*.wav")):
            items.append((root, wav))
            if limit is not None and len(items) >= limit:
                return items
    return items


def serialize_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def label_capture(
    path: Path,
    source_root: Path,
    recognizer,
    *,
    metadata_lookup: dict[str, dict],
    vad_model,
    get_speech_timestamps,
    vad_enabled: bool,
    min_speech_ratio: float,
    min_speech_ms: int,
    min_silence_ms: int,
    vad_pad_ms: int,
    merge_gap_ms: int,
) -> Capture:
    audio, sr = load_audio(path)
    duration_s = len(audio) / sr if sr else 0.0

    segments: list[tuple[int, int]] = []
    speech_ratio: float | None = None
    speech_duration_s: float | None = None
    stt_audio = audio
    vad_note = "vad_disabled"

    if vad_enabled and vad_model is not None and get_speech_timestamps is not None:
        try:
            vad_model.reset_states()
            segments, speech_ratio, speech_duration_s = analyze_vad(
                audio,
                sr,
                vad_model,
                get_speech_timestamps,
                pad_ms=vad_pad_ms,
                min_speech_ms=min_speech_ms,
                min_silence_ms=min_silence_ms,
                merge_gap_ms=merge_gap_ms,
            )
            vad_note = "silero_vad"
            stt_audio, _ = trim_audio_for_stt(audio, segments, pad_ms=vad_pad_ms, sr=sr)
        except Exception as exc:
            vad_note = f"vad_failed: {exc}"
            segments = []
            speech_ratio = None
            speech_duration_s = None
            stt_audio = audio

    transcript = transcribe_audio(recognizer, stt_audio, sr)

    if speech_ratio is not None and (
        speech_ratio < min_speech_ratio or (speech_duration_s is not None and speech_duration_s * 1000 < min_speech_ms)
    ):
        label = "garbage"
        note = f"{vad_note}; speech_ratio={speech_ratio:.3f} below threshold"
    else:
        label, note = classify_transcript(transcript)
        if not transcript.strip():
            note = f"{vad_note}; empty transcript"
        else:
            note = f"{vad_note}; {note}"

    metadata = metadata_lookup.get(str(path.resolve())) or metadata_lookup.get(path.name) or {}
    vad_segments = [
        {
            "start_s": round(start / sr, 3),
            "end_s": round(end / sr, 3),
            "duration_s": round((end - start) / sr, 3),
        }
        for start, end in segments
    ]
    return Capture(
        path=path,
        source_root=source_root,
        transcript=transcript,
        duration_s=duration_s,
        speech_ratio=speech_ratio,
        speech_duration_s=speech_duration_s,
        vad_available=vad_enabled and vad_model is not None and get_speech_timestamps is not None,
        vad_segments=vad_segments,
        proposed_label=label,
        confidence_note=note,
        metadata=metadata,
    )


def transcribe_dirs(
    input_dirs: list[Path],
    out_path: Path,
    *,
    limit: int | None,
    use_vad: bool,
    min_speech_ratio: float,
    min_speech_ms: int,
    min_silence_ms: int,
    vad_pad_ms: int,
    merge_gap_ms: int,
) -> None:
    recognizer = load_recognizer()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    vad_model = None
    get_speech_timestamps = None
    if use_vad:
        vad_model, get_speech_timestamps, vad_available, vad_note = load_vad_backend()
        if vad_available:
            print(f"[VAD] {vad_note}", file=sys.stderr)
        else:
            print(f"[VAD] fallback: {vad_note}", file=sys.stderr)
    else:
        print("[VAD] disabled by flag", file=sys.stderr)

    metadata_by_root = {root.resolve(): load_index_metadata(root) for root in input_dirs}

    captures: list[Capture] = []
    for source_root, wav in collect_files(input_dirs, limit=limit):
        try:
            cap = label_capture(
                wav,
                source_root,
                recognizer,
                metadata_lookup=metadata_by_root.get(source_root.resolve(), {}),
                vad_model=vad_model,
                get_speech_timestamps=get_speech_timestamps,
                vad_enabled=use_vad,
                min_speech_ratio=min_speech_ratio,
                min_speech_ms=min_speech_ms,
                min_silence_ms=min_silence_ms,
                vad_pad_ms=vad_pad_ms,
                merge_gap_ms=merge_gap_ms,
            )
        except Exception as exc:
            print(f"[ERR] {wav.name}: {exc}", file=sys.stderr)
            continue

        captures.append(cap)
        src_tag = cap.source_root.name
        ratio = f"{cap.speech_ratio:.3f}" if cap.speech_ratio is not None else "n/a"
        print(
            f"  [{cap.proposed_label:14s}] {src_tag}/{wav.name}  |  "
            f"speech={ratio}  |  '{cap.transcript}'",
            file=sys.stderr,
        )

    with out_path.open("w") as f:
        for cap in captures:
            f.write(
                json.dumps(
                    {
                        "path": serialize_path(cap.path),
                        "abs_path": str(cap.path.resolve()),
                        "source_root": str(cap.source_root.resolve()),
                        "transcript": cap.transcript,
                        "duration_s": round(cap.duration_s, 3),
                        "vad_available": cap.vad_available,
                        "speech_ratio": None if cap.speech_ratio is None else round(cap.speech_ratio, 4),
                        "speech_duration_s": None if cap.speech_duration_s is None else round(cap.speech_duration_s, 3),
                        "vad_segments": cap.vad_segments,
                        "stt_source": "vad_envelope" if cap.vad_segments else "full_clip",
                        "proposed_label": cap.proposed_label,
                        "note": cap.confidence_note,
                        "metadata": cap.metadata,
                    }
                )
                + "\n"
            )

    summary = {"positive": 0, "hard_negative": 0, "garbage": 0}
    for cap in captures:
        summary[cap.proposed_label] = summary.get(cap.proposed_label, 0) + 1
    print(f"\n[DONE] {len(captures)} files transcribed → {out_path}", file=sys.stderr)
    print(f"       {summary}", file=sys.stderr)


def apply_labels(jsonl_path: Path) -> None:
    """Copy files into destination test sets based on JSONL labels."""
    TEST_POS_DIR.mkdir(parents=True, exist_ok=True)
    TEST_HN_DIR.mkdir(parents=True, exist_ok=True)

    counts = {"positive": 0, "hard_negative": 0, "garbage": 0, "skipped": 0}
    with jsonl_path.open() as f:
        for line in f:
            rec = json.loads(line)
            src = Path(rec["abs_path"])
            label = rec.get("label") or rec.get("proposed_label")
            if not src.exists():
                counts["skipped"] += 1
                continue
            if label == "positive":
                dst = TEST_POS_DIR / src.name
            elif label == "hard_negative":
                dst = TEST_HN_DIR / src.name
            else:
                counts["garbage"] += 1
                continue
            shutil.copy2(src, dst)
            counts[label] += 1

    print(f"[APPLY] {counts}", file=sys.stderr)
    print(f"  positives → {TEST_POS_DIR}", file=sys.stderr)
    print(f"  hard_negs → {TEST_HN_DIR}", file=sys.stderr)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", nargs="+", type=Path, help="Input directories to scan for .wav files")
    p.add_argument("--out", type=Path, default=DEFAULT_OUTPUT, help="JSONL output path")
    p.add_argument("--limit", type=int, default=None, help="Limit the total number of WAVs processed")
    p.add_argument("--no-vad", action="store_true", help="Disable Silero VAD and transcribe full clips")
    p.add_argument(
        "--min-speech-ratio",
        type=float,
        default=DEFAULT_MIN_SPEECH_RATIO,
        help="Minimum VAD speech ratio before a clip is considered speech-like",
    )
    p.add_argument("--min-speech-ms", type=int, default=DEFAULT_MIN_SPEECH_MS, help="Minimum speech duration from VAD")
    p.add_argument("--min-silence-ms", type=int, default=DEFAULT_MIN_SILENCE_MS, help="Silero VAD minimum silence duration")
    p.add_argument("--vad-pad-ms", type=int, default=DEFAULT_VAD_PAD_MS, help="Padding around VAD segments before STT")
    p.add_argument("--merge-gap-ms", type=int, default=DEFAULT_VAD_MERGE_GAP_MS, help="Merge VAD segments separated by at most this gap")
    p.add_argument("--apply", type=Path, metavar="JSONL", help="Apply labels from JSONL: copy files to test set dirs")
    args = p.parse_args()

    if args.apply:
        apply_labels(args.apply)
        return

    if not args.input:
        sys.exit("Either --input or --apply must be given")

    transcribe_dirs(
        args.input,
        args.out,
        limit=args.limit,
        use_vad=not args.no_vad,
        min_speech_ratio=args.min_speech_ratio,
        min_speech_ms=args.min_speech_ms,
        min_silence_ms=args.min_silence_ms,
        vad_pad_ms=args.vad_pad_ms,
        merge_gap_ms=args.merge_gap_ms,
    )


if __name__ == "__main__":
    main()
