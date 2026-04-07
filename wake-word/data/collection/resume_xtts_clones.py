#!/usr/bin/env python3
"""Resume XTTS cloning - generate only missing samples for a speaker.

Checks existing files and generates only what's missing.

Usage:
    python resume_xtts_clones.py --name ema
    python resume_xtts_clones.py --name isa
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import soundfile as sf
import librosa
import shutil

from generate_xtts_clones import (
    POSITIVE_TEXTS,
    NEGATIVE_TEXTS,
    CLIP_DURATION_S,
    find_best_reference,
    generate_with_xtts,
    clip_and_resample_to_16k,
)


def main():
    parser = argparse.ArgumentParser(description="Resume XTTS clone generation")
    parser.add_argument("--name", required=True)
    parser.add_argument("--output-root", default="../raw/xtts_clones")
    parser.add_argument("--ref-root", default="../raw/voice_references")
    parser.add_argument("--repeats", type=int, default=3)
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

    # Build expected file lists
    expected_pos = []  # (idx, text, safe, repeat, out_24k, out_16k)
    idx = 0
    for i, text in enumerate(POSITIVE_TEXTS):
        safe = text.replace(" ", "_").replace(",", "").replace(".", "").replace("!", "").replace("?", "")
        for r in range(args.repeats):
            out_24k = pos_dir / f"{args.name}_xtts_pos_{idx:04d}_{safe}_r{r}.wav"
            out_16k = pos_16k_dir / f"{args.name}_xtts_pos_{idx:04d}_{safe}_r{r}.wav"
            expected_pos.append((idx, text, safe, r, out_24k, out_16k))
            idx += 1

    expected_neg = []
    idx = 0
    for i, text in enumerate(NEGATIVE_TEXTS):
        safe = text.replace(" ", "_").replace(",", "").replace(".", "").replace("!", "").replace("?", "")
        for r in range(args.repeats):
            out_24k = neg_dir / f"{args.name}_xtts_neg_{idx:04d}_{safe}_r{r}.wav"
            out_16k = neg_16k_dir / f"{args.name}_xtts_neg_{idx:04d}_{safe}_r{r}.wav"
            expected_neg.append((idx, text, safe, r, out_24k, out_16k))
            idx += 1

    # Find missing
    missing_pos = [item for item in expected_pos if not item[5].exists()]
    missing_neg = [item for item in expected_neg if not item[5].exists()]

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
    for idx, text, safe, r, out_24k, out_16k in missing_pos:
        if generate_with_xtts(client, text, ref_handle, out_24k):
            clip_and_resample_to_16k(out_24k, out_16k, clip_s=CLIP_DURATION_S)
            success += 1
            print(f"  pos {idx:04d}/r{r}: {text}")
        else:
            failed += 1
        time.sleep(args.delay)

    # Generate missing negatives
    for idx, text, safe, r, out_24k, out_16k in missing_neg:
        if generate_with_xtts(client, text, ref_handle, out_24k):
            clip_and_resample_to_16k(out_24k, out_16k, clip_s=None)
            success += 1
            print(f"  neg {idx:04d}/r{r}: {text}")
        else:
            failed += 1
        time.sleep(args.delay)

    print(f"\n  Valmis: {success} edukat, {failed} ebaõnnestunud")


if __name__ == "__main__":
    main()
