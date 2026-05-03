#!/usr/bin/env python3
"""
Prepare DiPCo benchmark splits from extracted files or a DiPCo archive.

Usage:
  python3 prepare_dipco_splits.py
  python3 prepare_dipco_splits.py --source /path/to/dipco
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import tarfile
import tempfile
from pathlib import Path
from zipfile import ZipFile


DEV_SESSIONS = {"S02", "S04", "S05", "S09", "S10"}
EVAL_SESSIONS = {"S01", "S03", "S06", "S07", "S08"}
KNOWN_SESSIONS = DEV_SESSIONS | EVAL_SESSIONS


def normalize_path(p: Path) -> Path:
    return Path(os.path.abspath(p))


def detect_session(path: Path) -> str | None:
    """
    Find a session id (S01..S10) without assuming exact directory layout.
    """
    text = str(path.name)
    for part in re.split(r"[\\/._-]", text):
        m = re.fullmatch(r"S(\d{1,2})", part.upper())
        if m:
            idx = int(m.group(1))
            if 1 <= idx <= 10:
                return f"S{idx:02d}"
    match = re.search(r"S(\d{1,2})", text.upper())
    if match:
        idx = int(match.group(1))
        if 1 <= idx <= 10:
            return f"S{idx:02d}"
    return None


def extract_archive(source: Path) -> tuple[Path, list[Path]]:
    tmp_root = Path(tempfile.mkdtemp(prefix="dipco-archive-"))
    wavs: list[Path] = []
    suffix = source.suffix.lower()

    if suffix == ".zip":
        with ZipFile(source, "r") as zf:
            for member in zf.namelist():
                if not member.lower().endswith(".wav"):
                    continue
                out_path = tmp_root / member
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src, open(out_path, "wb") as dst:
                    dst.write(src.read())
                wavs.append(out_path)
        return tmp_root, wavs

    with tarfile.open(source, "r:*") as tf:
        for member in tf.getmembers():
            if not member.isfile() or not member.name.lower().endswith(".wav"):
                continue
            out_path = tmp_root / member.name
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with tf.extractfile(member) as src, open(out_path, "wb") as dst:
                if src is None:
                    continue
                dst.write(src.read())
            wavs.append(out_path)

    return tmp_root, wavs


def resolve_source(benchmarks_root: Path) -> Path | None:
    candidates = [
        benchmarks_root / "dipco",
        benchmarks_root / "DipCo.tgz",
        benchmarks_root / "DiPCo.tgz",
        benchmarks_root / "DipCo.tar.gz",
        benchmarks_root / "DiPCo.tar.gz",
        benchmarks_root / "dipco.tar",
        benchmarks_root / "dipco.tar.gz",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    for env_name in ("KRATT_DATA", "KRATTDATA"):
        env_root = os.environ.get(env_name)
        if env_root:
            env_dir = Path(env_root) / "datasets" / "benchmarks"
            for candidate_name in ("dipco", "DipCo.tgz", "DiPCo.tgz", "dipco.tgz"):
                candidate = env_dir / candidate_name
                if candidate.exists():
                    return candidate
    return None


def collect_waves(source: Path) -> tuple[Path, list[Path]]:
    if source.is_dir():
        wavs = [
            f for f in source.rglob("*")
            if f.is_file() and f.suffix.lower() == ".wav"
        ]
        return source, sorted(wavs)

    suffix = source.suffix.lower()
    if suffix not in {".tgz", ".gz", ".tar", ".zip", ".xz", ".bz2"}:
        raise SystemExit(f"Unsupported source type: {source}")

    return extract_archive(source)


def write_file(src: Path, dst: Path, *, copy_mode: bool, overwrite: bool) -> str:
    if dst.exists():
        if not overwrite:
            return "exists"
        if dst.is_dir():
            return "skip_dir"
        dst.unlink()

    dst.parent.mkdir(parents=True, exist_ok=True)
    if copy_mode:
        shutil.copy2(src, dst)
        return "copy"
    os.symlink(src, dst)
    return "link"


def main() -> None:
    p = argparse.ArgumentParser(description="Split DiPCo WAVs into dev/eval by session.")
    p.add_argument("--source", help="DiPCo source directory or archive.")
    p.add_argument("--benchmarks-root", default=None, help="Default output base.")
    p.add_argument(
        "--copy",
        action="store_true",
        help="Copy instead of symlink (default when source is an archive).",
    )
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing outputs.")
    args = p.parse_args()

    repo_root = normalize_path(Path(__file__).resolve().parents[2])
    benchmarks_root = (
        normalize_path(Path(args.benchmarks_root))
        if args.benchmarks_root else
        (repo_root / "wake-word" / "data" / "processed" / "benchmarks")
    )

    source = Path(args.source) if args.source else resolve_source(benchmarks_root)
    if source is None:
        raise SystemExit(
            "Could not auto-detect DiPCo source. Provide --source explicitly."
        )
    source = normalize_path(source)
    source_base, wav_files = collect_waves(source)
    if not source_base.exists() or not wav_files:
        raise SystemExit(f"No WAV files found in {source}")
    is_temp_source = source_base != source

    dev_root = benchmarks_root / "dipco-dev"
    eval_root = benchmarks_root / "dipco-eval"
    copy_mode = args.copy or (source_base != source)

    copied = linked = skipped = unknown = 0
    try:
        for wav in wav_files:
            session = detect_session(wav)
            if session is None or session not in KNOWN_SESSIONS:
                unknown += 1
                continue

            target_root = dev_root if session in DEV_SESSIONS else eval_root
            rel = wav.relative_to(source_base)
            target = target_root / rel
            status = write_file(
                wav, target, copy_mode=copy_mode, overwrite=args.overwrite
            )
            if status == "copy":
                copied += 1
            elif status == "link":
                linked += 1
            elif status == "skip_dir":
                unknown += 1
            else:
                skipped += 1

        print(f"Source: {source}")
        print(f"Mode: {'copy' if copy_mode else 'symlink'}")
        print(
            f"Dev: {', '.join(sorted(DEV_SESSIONS))} -> {dev_root}\n"
            f"Eval: {', '.join(sorted(EVAL_SESSIONS))} -> {eval_root}"
        )
        print(
            f"Copied: {copied}, Linked: {linked}, "
            f"Skipped: {skipped}, Unknown: {unknown}"
        )
    finally:
        if is_temp_source:
            shutil.rmtree(source_base, ignore_errors=True)


if __name__ == "__main__":
    main()
