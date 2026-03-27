#!/usr/bin/env python3
"""Generate hard negative TTS samples using phonetically similar phrases.

Uses the phrase list from hard_negative_phrases.py to generate TTS clips
that should NOT trigger "Kuule Kratt" detection.

Usage:
    python generate_neurokone_hard_neg_v2.py --output ../raw/neurokone_hard_neg_v2
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import requests
from tqdm import tqdm

from hard_negative_phrases import ALL_PHRASES

API_ENDPOINT = "https://api.tartunlp.ai/text-to-speech/v2"

ESTONIAN_SPEAKERS = [
    "albert", "indrek", "kalev", "kylli", "lee", "liivika",
    "luukas", "mari", "meelis", "peeter", "tambet", "vesta",
]

SPEEDS = [0.85, 0.95, 1.0, 1.05, 1.15]


def generate_sample(text: str, speaker: str, speed: float, output_path: Path) -> bool:
    try:
        response = requests.post(
            API_ENDPOINT,
            json={"text": text, "speaker": speaker, "speed": speed},
            timeout=30,
        )
        if response.status_code == 200:
            output_path.write_bytes(response.content)
            return True
        return False
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="../raw/neurokone_hard_neg_v2")
    parser.add_argument("--delay", type=float, default=0.12)
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    total = len(ESTONIAN_SPEAKERS) * len(ALL_PHRASES) * len(SPEEDS)
    print(f"{len(ESTONIAN_SPEAKERS)} speakers x {len(ALL_PHRASES)} phrases x {len(SPEEDS)} speeds = {total} samples")

    stats = {"total": 0, "success": 0, "failed": 0}
    pbar = tqdm(total=total, desc="Generating")

    idx = 0
    for speaker in ESTONIAN_SPEAKERS:
        speaker_dir = output_dir / speaker
        speaker_dir.mkdir(exist_ok=True)

        for text in ALL_PHRASES:
            label = text.lower().replace(" ", "_").replace(",", "").replace(".", "")
            for speed in SPEEDS:
                filename = f"{speaker}_{idx:05d}_{label}_speed{speed}.wav"
                success = generate_sample(text, speaker, speed, speaker_dir / filename)

                if success:
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
                stats["total"] += 1
                idx += 1
                pbar.update(1)
                time.sleep(args.delay)

    pbar.close()

    (output_dir / "generation_stats.json").write_text(
        json.dumps(stats, indent=2) + "\n"
    )

    print(f"\nDone: {stats['success']}/{stats['total']} successful")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
