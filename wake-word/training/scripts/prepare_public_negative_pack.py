#!/usr/bin/env python3
"""Prepare an opt-in public broad-negative pack for new wake-word training.

The default starter pack intentionally downloads only clean public data with a
stable direct URL (LibriSpeech test-clean). It writes a bounded 2s WAV pool and
a manifest with provenance/leakage notes. Larger and Estonian-specific packs can
be added later when the source/license/download path is stable enough for public
onboarding.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tarfile
import time
import urllib.request
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import soundfile as sf

LIBRISPEECH_TEST_CLEAN_URL = "https://www.openslr.org/resources/12/test-clean.tar.gz"
AUDIO_EXTS = {".wav", ".flac"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profile", default="starter-public-v1", choices=["starter-public-v1"], help="Public negative-pack profile")
    p.add_argument("--output-dir", required=True, help="Segmented WAV output directory")
    p.add_argument("--cache-dir", default="~/.cache/kratt/negative-packs", help="Download/extract cache directory")
    p.add_argument("--max-clips", type=int, default=10000, help="Max 2s clips to create (default: 10000)")
    p.add_argument("--clip-seconds", type=float, default=2.0, help="Clip length in seconds (default: 2.0)")
    p.add_argument("--sample-rate", type=int, default=16000, help="Output sample rate (default: 16000)")
    p.add_argument("--windows-per-file", type=int, default=4, help="Max windows to take from each source file")
    p.add_argument("--force", action="store_true", help="Reuse/extend existing output directory")
    p.add_argument("--dry-run", action="store_true", help="Print plan without downloading/extracting/segmenting")
    args = p.parse_args()
    if args.max_clips < 1:
        raise SystemExit("--max-clips must be >= 1")
    if args.clip_seconds <= 0:
        raise SystemExit("--clip-seconds must be > 0")
    if args.windows_per_file < 1:
        raise SystemExit("--windows-per-file must be >= 1")
    return args


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"Using cached download: {dest}")
        return
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    print(f"Downloading {url}")
    print(f"  -> {dest}")
    with urllib.request.urlopen(url) as response, tmp.open("wb") as out:
        total = int(response.headers.get("Content-Length") or 0)
        done = 0
        last = time.monotonic()
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
            done += len(chunk)
            now = time.monotonic()
            if now - last > 1.0:
                if total:
                    print(f"  {done / 1024**2:.1f}/{total / 1024**2:.1f} MiB ({100 * done / total:.1f}%)")
                else:
                    print(f"  {done / 1024**2:.1f} MiB")
                last = now
    tmp.replace(dest)


def safe_extract_tar(tar_path: Path, dest: Path) -> None:
    marker = dest / ".extract-complete"
    if marker.exists():
        print(f"Using cached extract: {dest}")
        return
    dest.mkdir(parents=True, exist_ok=True)
    print(f"Extracting {tar_path} -> {dest}")
    base = dest.resolve()
    with tarfile.open(tar_path, "r:gz") as tar:
        members = tar.getmembers()
        for member in members:
            target = (dest / member.name).resolve()
            if not str(target).startswith(str(base)):
                raise RuntimeError(f"Unsafe tar member path: {member.name}")
        tar.extractall(dest)
    marker.write_text(now_iso() + "\n", encoding="utf-8")


def audio_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_EXTS)


def load_audio(path: Path, sample_rate: int) -> np.ndarray:
    audio, sr = sf.read(str(path), always_2d=False)
    if getattr(audio, "ndim", 1) > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32, copy=False)
    if sr != sample_rate:
        # Keep the public bootstrap dependency-light. LibriSpeech is already 16 kHz;
        # non-matching sources are skipped rather than pulling in a resampler.
        raise ValueError(f"sample_rate_mismatch:{sr}")
    return np.clip(audio, -1.0, 1.0)


def write_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())


def segment_files(
    files: list[Path],
    out_dir: Path,
    *,
    max_clips: int,
    clip_seconds: float,
    sample_rate: int,
    windows_per_file: int,
) -> dict:
    clip_samples = int(round(clip_seconds * sample_rate))
    out_dir.mkdir(parents=True, exist_ok=True)
    created = 0
    skipped_existing = 0
    errors: list[dict] = []
    source_hours = 0.0

    for src_index, path in enumerate(files, start=1):
        if created >= max_clips:
            break
        try:
            audio = load_audio(path, sample_rate)
        except Exception as exc:
            errors.append({"path": str(path), "error": str(exc)})
            continue
        source_hours += len(audio) / sample_rate / 3600.0
        if len(audio) < max(clip_samples // 2, 1):
            continue

        max_start = max(0, len(audio) - clip_samples)
        if max_start == 0:
            starts = [0]
        else:
            n = min(windows_per_file, max(1, math.floor(len(audio) / clip_samples)))
            if n == 1:
                starts = [max_start // 2]
            else:
                starts = [int(round(i * max_start / (n - 1))) for i in range(n)]

        stem = path.stem.replace(" ", "_")[:80]
        for window_index, start in enumerate(starts, start=1):
            if created >= max_clips:
                break
            clip = audio[start : start + clip_samples]
            if clip.size < clip_samples:
                clip = np.pad(clip, (0, clip_samples - clip.size))
            out_path = out_dir / f"librispeech_{src_index:05d}_{window_index:02d}_{stem}.wav"
            if out_path.exists():
                skipped_existing += 1
            else:
                write_wav(out_path, clip, sample_rate)
            created += 1
            if created % 500 == 0:
                print(f"  segmented {created}/{max_clips} clips")

    return {
        "created_or_existing": created,
        "skipped_existing": skipped_existing,
        "source_files_seen": src_index if files else 0,
        "source_hours_seen": round(source_hours, 3),
        "errors": errors[:50],
        "error_count": len(errors),
    }


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    cache_dir = Path(args.cache_dir).expanduser().resolve() / args.profile
    archive = cache_dir / "downloads" / "librispeech-test-clean.tar.gz"
    extract_dir = cache_dir / "extract"

    print("=== Prepare public negative pack ===")
    print(f"Profile:    {args.profile}")
    print(f"Output:     {output_dir}")
    print(f"Cache:      {cache_dir}")
    print(f"Max clips:  {args.max_clips}")
    print(f"Clip secs:  {args.clip_seconds}")
    print("Sources:")
    print(f"  - LibriSpeech test-clean: {LIBRISPEECH_TEST_CLEAN_URL}")
    print("Note: this pack is public broad speech coverage. It is not a held-out benchmark if used for training.")

    if args.dry_run:
        return 0

    if output_dir.exists() and any(output_dir.iterdir()) and not args.force:
        manifest = output_dir / "MANIFEST.json"
        if manifest.exists():
            print(f"Output already prepared: {output_dir}")
            return 0
        raise SystemExit(f"Output directory exists and is not empty: {output_dir}. Use --force to extend/reuse.")

    download(LIBRISPEECH_TEST_CLEAN_URL, archive)
    safe_extract_tar(archive, extract_dir)
    files = audio_files(extract_dir)
    if not files:
        raise SystemExit(f"No audio files found after extracting {archive}")
    print(f"Found {len(files)} source audio files")

    stats = segment_files(
        files,
        output_dir,
        max_clips=args.max_clips,
        clip_seconds=args.clip_seconds,
        sample_rate=args.sample_rate,
        windows_per_file=args.windows_per_file,
    )
    total_files = len(audio_files(output_dir))
    manifest = {
        "created_by": "prepare_public_negative_pack.py",
        "created_at": now_iso(),
        "profile": args.profile,
        "output": str(output_dir),
        "cache_dir": str(cache_dir),
        "clip_seconds": args.clip_seconds,
        "sample_rate": args.sample_rate,
        "max_clips": args.max_clips,
        "total_audio_files": total_files,
        "total_clip_hours": round(total_files * args.clip_seconds / 3600.0, 3),
        "sources": [
            {
                "label": "librispeech_test_clean",
                "url": LIBRISPEECH_TEST_CLEAN_URL,
                "archive": str(archive),
                "archive_sha256": sha256_file(archive),
                "license": "LibriSpeech/OpenSLR terms; see http://www.openslr.org/12",
                **stats,
            }
        ],
        "warning": "This is a public broad-negative training pack. Do not report this same source as held-out FAPH for a model trained on it.",
        "recommended_next_step": "Run live false-accept mining in the target environment and retrain with mined false positives as hard negatives.",
    }
    (output_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\nDone")
    print(f"  clips: {total_files}")
    print(f"  hours: {manifest['total_clip_hours']}")
    print(f"  manifest: {output_dir / 'MANIFEST.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
