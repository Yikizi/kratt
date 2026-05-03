#!/usr/bin/env python3
"""Build a strict positive set containing only "Kuule Kratt" / "Kule Kratt".

This creates a flat symlink directory from raw/generated sources while excluding
known problematic variants such as:
- SSML/XML read-aloud clips,
- filler-prefix prompts ("Ee/No/Noh kuule Kratt"),
- reversed phrases ("Kratt kuule"),
- prefix-only or very short clips.

Elongated spellings such as "Kuuule Kratt" / "Kuulee Kratt" are allowed because
they are still exactly the two-word wake phrase.

The output is intended as the TTS/generated positive source for future clean
training runs. Real manually recorded positives can still be passed separately.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

import soundfile as sf

DEFAULT_INCLUDE_PATTERNS = [
    # Neurokõne phase1: albert_0003_Kuule_Kratt_speed0.8.wav
    r"(^|_)kuule_kratt_speed[0-9.]",
    # Neurokõne phase2 exact + capitalization-only variants.
    r"(^|_)kuule_kratt_(low_|caps_)?speed[0-9.]",
    # Casual accepted spelling/pronunciation.
    r"(^|_)kule_kratt_speed[0-9.]",
    # Elongated but still exactly two words.
    r"(^|_)kuuule_kratt_speed[0-9.]",
    r"(^|_)kuulee_kratt_speed[0-9.]",
    # Direct A/B test clips: mari_kuule_kratt.wav / mari_kule_kratt.wav
    r"(^|_)(kuule|kule)_kratt\.wav$",
]

DEFAULT_EXCLUDE_PATTERNS = [
    r"ee_kuule_kratt",
    r"no_kuule_kratt",
    r"noh_kuule_kratt",
    r"kratt_kuule",
    r"ssml",
    r"emph",
    r"prosody",
    r"pause",
]


def duration_s(path: Path) -> float:
    info = sf.info(str(path))
    return float(info.frames) / float(info.samplerate)


def audio_fingerprint(path: Path) -> tuple[int, str]:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return path.stat().st_size, h.hexdigest()


def compile_any(patterns: list[str]) -> list[re.Pattern[str]]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def matches_any(patterns: list[re.Pattern[str]], text: str) -> bool:
    return any(p.search(text) for p in patterns)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, help="Flat output dir of symlinks")
    ap.add_argument("--source", action="append", default=[], help="Source dir; may be repeated")
    ap.add_argument("--force", action="store_true", help="Replace existing output dir")
    ap.add_argument("--min-duration-s", type=float, default=0.80)
    ap.add_argument("--max-duration-s", type=float, default=4.00)
    args = ap.parse_args()

    output = Path(args.output).expanduser().resolve()
    if output.exists():
        if not args.force:
            raise SystemExit(f"Output exists: {output} (use --force)")
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    sources = [Path(s).expanduser().resolve() for s in args.source]
    if not sources:
        root = Path(__file__).resolve().parents[1]
        sources = [
            root / "raw" / "neurokone_phase1",
            root / "raw" / "neurokone_phase2",
            root / "raw" / "kule_vs_kuule_test",
        ]

    include = compile_any(DEFAULT_INCLUDE_PATTERNS)
    exclude = compile_any(DEFAULT_EXCLUDE_PATTERNS)

    manifest: dict = {
        "policy": "strict Kuule Kratt / Kule Kratt positives only",
        "sources": [str(s) for s in sources],
        "min_duration_s": args.min_duration_s,
        "max_duration_s": args.max_duration_s,
        "include_patterns": DEFAULT_INCLUDE_PATTERNS,
        "exclude_patterns": DEFAULT_EXCLUDE_PATTERNS,
        "accepted": [],
        "rejected_counts": {},
        "rejected_examples": {},
    }

    def reject(reason: str, path: Path, dur: float | None = None) -> None:
        manifest["rejected_counts"][reason] = manifest["rejected_counts"].get(reason, 0) + 1
        examples = manifest["rejected_examples"].setdefault(reason, [])
        if len(examples) < 20:
            item: dict = {"file": str(path)}
            if dur is not None:
                item["duration_s"] = round(dur, 3)
            examples.append(item)

    accepted_idx = 0
    seen_realpaths: set[Path] = set()
    seen_audio_fingerprints: set[tuple[int, str]] = set()
    for src in sources:
        if not src.exists():
            reject("missing_source", src)
            continue
        for wav in sorted(src.rglob("*.wav")):
            real = wav.resolve()
            if real in seen_realpaths:
                reject("duplicate_realpath", wav)
                continue
            name = wav.name.lower()
            rel_text = str(wav.relative_to(src)).lower()
            if matches_any(exclude, rel_text):
                reject("exclude_pattern", wav)
                continue
            if not matches_any(include, name):
                reject("not_exact_phrase_filename", wav)
                continue
            try:
                dur = duration_s(wav)
            except Exception as e:
                reject(f"unreadable:{e.__class__.__name__}", wav)
                continue
            if args.min_duration_s > 0 and dur < args.min_duration_s:
                reject("too_short", wav, dur)
                continue
            if args.max_duration_s > 0 and dur > args.max_duration_s:
                reject("too_long", wav, dur)
                continue
            fp = audio_fingerprint(wav)
            if fp in seen_audio_fingerprints:
                reject("duplicate_audio_fingerprint", wav, dur)
                continue

            dst = output / f"strict_pos_{accepted_idx:05d}_{wav.stem}.wav"
            dst.symlink_to(real)
            seen_realpaths.add(real)
            seen_audio_fingerprints.add(fp)
            manifest["accepted"].append(
                {"output": dst.name, "source": str(wav), "duration_s": round(dur, 3)}
            )
            accepted_idx += 1

    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"Strict positive set: {output}")
    print(f"  accepted: {accepted_idx}")
    for reason, count in sorted(manifest["rejected_counts"].items()):
        print(f"  rejected {reason}: {count}")

    if accepted_idx == 0:
        raise SystemExit("No strict positives accepted; refusing to continue")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
