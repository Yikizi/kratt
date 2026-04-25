#!/usr/bin/env python3
"""Resume XTTS cloning - generate only missing samples for a speaker.

Checks existing files and generates only what's missing.

Usage:
    python resume_xtts_clones.py --name ema
    python resume_xtts_clones.py --name isa
    python resume_xtts_clones.py --name ode --positive-target 200 --skip-negatives
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import shutil

from generate_xtts_clones import (
    POSITIVE_TEXTS,
    NEGATIVE_TEXTS,
    CLIP_DURATION_S,
    build_positive_plan,
    find_best_reference,
    ensure_generated_variant,
    slugify_prompt,
)


def load_manifest(output_dir: Path) -> dict | None:
    manifest_path = output_dir / "generation_manifest.json"
    if not manifest_path.exists():
        return None
    try:
        return json.loads(manifest_path.read_text())
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Resume XTTS clone generation")
    parser.add_argument("--name", required=True)
    parser.add_argument("--output-root", default="../raw/xtts_clones")
    parser.add_argument("--ref-root", default="../raw/voice_references")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument(
        "--positive-target",
        type=int,
        default=None,
        help="Generate this many positive variants using the deterministic target plan "
             "(overrides --repeats for positives).",
    )
    parser.add_argument("--seed", type=int, default=42, help="Shuffle seed used by --positive-target mode.")
    parser.add_argument("--skip-negatives", action="store_true", help="Only resume positives.")
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()

    output_dir = Path(args.output_root) / args.name
    ref_dir = Path(args.ref_root) / args.name

    pos_dir = output_dir / "positive"
    pos_16k_dir = output_dir / "positive_16k"
    neg_dir = output_dir / "negative"
    neg_16k_dir = output_dir / "negative_16k"

    for d in [pos_dir, pos_16k_dir, neg_dir, neg_16k_dir]:
        d.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest(output_dir)
    if manifest and manifest.get("seed") is not None:
        args.seed = int(manifest["seed"])
    if manifest and manifest.get("positive_target") is not None and args.positive_target is None:
        args.positive_target = int(manifest["positive_target"])
    elif manifest and args.positive_target is not None:
        manifest_target = manifest.get("positive_target")
        if manifest_target is not None and int(manifest_target) != args.positive_target:
            raise SystemExit(
                f"Manifest target mismatch: manifest has {manifest_target}, "
                f"requested {args.positive_target}."
            )

    if args.positive_target is not None:
        positive_plan = build_positive_plan(POSITIVE_TEXTS, args.positive_target, args.seed)
        expected_pos = [
            (
                int(item["slot"]),
                str(item["text"]),
                str(item["slug"]),
                pos_dir / f"{args.name}_xtts_pos_{int(item['slot']):04d}_{str(item['slug'])}.wav",
                pos_16k_dir / f"{args.name}_xtts_pos_{int(item['slot']):04d}_{str(item['slug'])}.wav",
            )
            for item in positive_plan
        ]
    else:
        expected_pos = []
        idx = 0
        for text in POSITIVE_TEXTS:
            safe = slugify_prompt(text)
            for r in range(args.repeats):
                out_24k = pos_dir / f"{args.name}_xtts_pos_{idx:04d}_{safe}_r{r}.wav"
                out_16k = pos_16k_dir / f"{args.name}_xtts_pos_{idx:04d}_{safe}_r{r}.wav"
                expected_pos.append((idx, text, safe, out_24k, out_16k))
                idx += 1

    expected_neg = []
    if not args.skip_negatives:
        idx = 0
        for text in NEGATIVE_TEXTS:
            safe = slugify_prompt(text)
            for r in range(args.repeats):
                out_24k = neg_dir / f"{args.name}_xtts_neg_{idx:04d}_{safe}_r{r}.wav"
                out_16k = neg_16k_dir / f"{args.name}_xtts_neg_{idx:04d}_{safe}_r{r}.wav"
                expected_neg.append((idx, text, safe, out_24k, out_16k))
                idx += 1

    missing_pos = [item for item in expected_pos if not item[-1].exists()]
    missing_neg = [item for item in expected_neg if not item[-1].exists()]

    print(f"  {args.name}:")
    print(f"    Positiivseid: {len(expected_pos) - len(missing_pos)}/{len(expected_pos)} olemas")
    print(f"    Negatiivseid: {len(expected_neg) - len(missing_neg)}/{len(expected_neg)} olemas")
    print(f"    Puudu: {len(missing_pos) + len(missing_neg)}")

    if not missing_pos and not missing_neg:
        print("  Kõik olemas!")
        return

    # Connect to XTTS
    ref_path = find_best_reference(ref_dir)
    print(f"\n  Referents: {ref_path.name}")
    print("  Ühendan TartuNLP XTTS v2...")
    from gradio_client import Client, handle_file
    client = Client("tartuNLP/XTTSv2-est", verbose=False)
    ref_handle = handle_file(str(ref_path))
    print("  Ühendatud\n")

    success = 0
    failed = 0

    # Generate missing positives
    for item in missing_pos:
        if args.positive_target is not None:
            idx, text, safe, out_24k, out_16k = item
        else:
            idx, text, safe, out_24k, out_16k = item
        if ensure_generated_variant(client, text, ref_handle, out_24k, out_16k, clip_s=CLIP_DURATION_S):
            success += 1
            print(f"  pos {idx:04d}: {text}")
        else:
            failed += 1
        time.sleep(args.delay)

    # Generate missing negatives
    for idx, text, safe, out_24k, out_16k in missing_neg:
        if ensure_generated_variant(client, text, ref_handle, out_24k, out_16k, clip_s=None):
            success += 1
            print(f"  neg {idx:04d}: {text}")
        else:
            failed += 1
        time.sleep(args.delay)

    print(f"\n  Valmis: {success} edukat, {failed} ebaõnnestunud")


if __name__ == "__main__":
    main()
