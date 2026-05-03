#!/usr/bin/env python3
"""Build a frozen negative regression set for prefix/partial wake-word failures.

The 2026-04-27 v17 incident showed that a model can learn to trigger on
"kuule"/"kule" alone when positive windows are cropped or mislabeled. This
materializes deterministic symlinked clip sets that must remain negative:

- very short/prefix-only Mattias clips (<0.80s by default; raised after STT audit)
- single-word "Kratt" Neurokõne clips
- reversed "Kratt kuule" Neurokõne clips
- "kuule/kule <confusable>" hard negatives

Raw data is never modified.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import wave
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "data"


def wav_duration_s(path: Path) -> float:
    with wave.open(str(path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


def safe_name(path: Path) -> str:
    parts = path.parts[-4:]
    return "__".join(parts)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(BASE))
    except ValueError:
        return str(path)


def link_many(files: list[Path], out_dir: Path) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    for src in files:
        dst = out_dir / safe_name(src)
        if dst.exists() or dst.is_symlink():
            dst.unlink()
        dst.symlink_to(src.resolve())
        records.append({"source": rel(src), "link": rel(dst)})
    return records


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=DATA / "processed" / "prefix_regression_test")
    ap.add_argument("--mattias-short", type=Path, default=DATA / "raw" / "mattias-short" / "positive")
    ap.add_argument("--neurokone-phase1", type=Path, default=DATA / "raw" / "neurokone_phase1")
    ap.add_argument("--hard-neg-v2", type=Path, default=DATA / "raw" / "neurokone_hard_neg_v2")
    ap.add_argument("--prefix-max-duration-s", type=float, default=0.80)
    ap.add_argument("--max-confusables", type=int, default=600)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    output = args.output.resolve()
    if output.exists():
        if not args.force:
            raise SystemExit(f"Output exists: {output} (use --force)")
        shutil.rmtree(output)
    output.mkdir(parents=True)

    sets: dict[str, list[Path]] = {}

    # User-audited: very short Mattias clips around 0.42s are prefix-only/bad.
    prefix_short: list[Path] = []
    for wav in sorted(args.mattias_short.rglob("*.wav")):
        try:
            if wav_duration_s(wav) < args.prefix_max_duration_s:
                prefix_short.append(wav)
        except Exception:
            continue
    sets["prefix_only_mattias_short_lt0p80"] = prefix_short

    # Synthetic Neurokõne phase1 contains many exact single-word "Kratt" clips
    # and reversed "Kratt kuule" clips that are useful negative controls.
    phase1 = sorted(args.neurokone_phase1.rglob("*.wav"))
    sets["single_kratt_neurokone_phase1"] = [
        p for p in phase1 if re.search(r"_[0-9]+_kratt_speed", p.name, re.IGNORECASE)
    ]
    sets["reversed_kratt_kuule_phase1"] = [
        p for p in phase1 if re.search(r"_[0-9]+_kratt_kuule_speed", p.name, re.IGNORECASE)
    ]

    # Hard negatives generated specifically as "kuule/kule <not kratt>".
    confusable_re = re.compile(r"_[0-9]+_(?:kuule|kule|kuuule)_[^/]+_speed", re.IGNORECASE)
    confusables = [p for p in sorted(args.hard_neg_v2.rglob("*.wav")) if confusable_re.search(p.name)]
    if args.max_confusables and len(confusables) > args.max_confusables:
        # Deterministic spread over voices/phrases: sorted list prefix is biased to
        # one speaker, so stride through the full list.
        step = len(confusables) / args.max_confusables
        confusables = [confusables[int(i * step)] for i in range(args.max_confusables)]
    sets["kuule_kule_confusables_neurokone_hard_neg_v2"] = confusables

    manifest = {
        "description": "Negative prefix/partial wake-word regression set; all clips must score below deploy threshold.",
        "policy": "negative: no clip contains exactly the full isolated wake phrase 'kuule/kule kratt' in correct order",
        "output": rel(output),
        "prefix_max_duration_s": args.prefix_max_duration_s,
        "max_confusables": args.max_confusables,
        "sets": {},
    }

    for name, files in sets.items():
        records = link_many(files, output / name)
        manifest["sets"][name] = {
            "count": len(records),
            "examples": records[:10],
        }

    counts = Counter({name: len(files) for name, files in sets.items()})
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"Prefix regression set: {output}")
    for name, n in counts.items():
        print(f"  {name}: {n}")


if __name__ == "__main__":
    main()
