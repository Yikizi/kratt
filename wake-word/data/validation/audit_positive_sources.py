#!/usr/bin/env python3
"""Audit candidate positive wake-word source directories before training.

Checks that positive clips are plausible wake-word clips and that known-bad
sources from the 2026-04-27 audit are not accidentally included.

Example:
    uv run python data/validation/audit_positive_sources.py \
        data/processed/positive_tts data/raw/mattias/positive \
        data/raw/mattias-short/positive
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from pathlib import Path

import soundfile as sf

KNOWN_BAD_DIR_NAMES = {
    "positive_tts_ssml": "Neurokõne read SSML/XML tags aloud (5-14s clips)",
    "neurokone_ssml_positives": "Neurokõne read SSML/XML tags aloud (5-14s clips)",
    "neurokone_ssml_kule": "Kule SSML mirror of corrupt SSML data",
}


def duration_s(path: Path) -> float:
    info = sf.info(str(path))
    return float(info.frames) / float(info.samplerate)


def sha1_file(path: Path) -> tuple[int, str]:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return path.stat().st_size, h.hexdigest()


def summarize_dir(path: Path, min_s: float, max_s: float) -> dict:
    files = sorted(path.rglob("*.wav"))
    durations: list[float] = []
    unreadable: list[str] = []
    too_short: list[tuple[str, float]] = []
    too_long: list[tuple[str, float]] = []

    for f in files:
        try:
            d = duration_s(f)
        except Exception as e:  # pragma: no cover - diagnostic script
            unreadable.append(f"{f}: {e}")
            continue
        durations.append(d)
        if min_s > 0 and d < min_s:
            too_short.append((str(f), d))
        if max_s > 0 and d > max_s:
            too_long.append((str(f), d))

    known_bad_reason = ""
    for part in path.parts:
        if part in KNOWN_BAD_DIR_NAMES:
            known_bad_reason = KNOWN_BAD_DIR_NAMES[part]
            break
    if not known_bad_reason and "xtts_clones" in path.parts and path.name in {"positive", "positive_16k"}:
        known_bad_reason = "XTTS positive source is a full-command prompt/crop; requires manual segmentation before training"

    summary: dict = {
        "path": str(path),
        "files": len(files),
        "readable": len(durations),
        "unreadable": unreadable[:20],
        "known_bad_reason": known_bad_reason,
        "too_short_count": len(too_short),
        "too_long_count": len(too_long),
        "too_short_examples": too_short[:20],
        "too_long_examples": too_long[:20],
    }
    if durations:
        qs = statistics.quantiles(durations, n=4) if len(durations) >= 4 else [min(durations), statistics.median(durations), max(durations)]
        summary.update(
            {
                "min_s": round(min(durations), 3),
                "p25_s": round(qs[0], 3),
                "median_s": round(statistics.median(durations), 3),
                "p75_s": round(qs[2], 3),
                "max_s": round(max(durations), 3),
            }
        )
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dirs", nargs="+", help="Positive source dirs to audit")
    ap.add_argument("--min-duration-s", type=float, default=0.80)
    ap.add_argument("--max-duration-s", type=float, default=4.00)
    ap.add_argument("--json", action="store_true", help="Print JSON instead of a table")
    ap.add_argument("--fail-on-suspicious", action="store_true", help="Exit non-zero if known-bad/too-short/too-long clips are found")
    args = ap.parse_args()

    summaries = []
    suspicious = False
    for d in args.dirs:
        path = Path(d).expanduser().resolve()
        if not path.exists():
            summaries.append({"path": str(path), "missing": True})
            suspicious = True
            continue
        s = summarize_dir(path, args.min_duration_s, args.max_duration_s)
        summaries.append(s)
        if s.get("known_bad_reason") or s.get("too_short_count", 0) or s.get("too_long_count", 0) or s.get("unreadable"):
            suspicious = True

    if args.json:
        print(json.dumps(summaries, indent=2, ensure_ascii=False))
    else:
        print("path\tn\tmedian\tmin\tmax\tshort\tlong\tknown_bad")
        for s in summaries:
            if s.get("missing"):
                print(f"{s['path']}\tMISSING")
                continue
            print(
                f"{s['path']}\t{s['readable']}\t{s.get('median_s', '-')}\t"
                f"{s.get('min_s', '-')}\t{s.get('max_s', '-')}\t"
                f"{s['too_short_count']}\t{s['too_long_count']}\t"
                f"{s['known_bad_reason'] or '-'}"
            )

    return 2 if suspicious and args.fail_on_suspicious else 0


if __name__ == "__main__":
    raise SystemExit(main())
