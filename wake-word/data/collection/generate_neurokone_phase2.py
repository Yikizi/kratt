#!/usr/bin/env python3
"""Generate Phase 2 training dataset: focused on 'Kuule Kratt' pronunciation variants.

Phase 1 had 10 different phrases where 'Kuule Kratt' was only 1/12 of the data.
Phase 2 focuses on the actual wake word with natural pronunciation variations.

Usage:
    python generate_neurokone_phase2.py --output ../raw/neurokone_phase2
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import requests
from tqdm import tqdm

API_ENDPOINT = "https://api.tartunlp.ai/text-to-speech/v2"

ESTONIAN_SPEAKERS = [
    "albert", "indrek", "kalev", "kylli", "lee", "liivika",
    "luukas", "mari", "meelis", "peeter", "tambet", "vesta",
]

SPEEDS = [0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2]

# Pronunciation variants of "Kuule Kratt"
TEXT_VARIATIONS = [
    # Standard
    "Kuule Kratt",
    "Kuule Kratt.",
    "Kuule Kratt!",
    # Shortened / casual
    "Kule Kratt",
    "Kule kratt",
    # Elongated
    "Kuuule Kratt",
    "Kuulee Kratt",
    # Emphasis variations
    "kuule Kratt",
    "Kuule kratt",
    "KUULE KRATT",
    # With filler / context
    "Ee kuule Kratt",
    "No kuule Kratt",
    "Noh kuule Kratt",
]

LABEL_MAP = {
    "Kuule Kratt": "kuule_kratt",
    "Kuule Kratt.": "kuule_kratt",
    "Kuule Kratt!": "kuule_kratt",
    "Kule Kratt": "kule_kratt",
    "Kule kratt": "kule_kratt",
    "Kuuule Kratt": "kuuule_kratt",
    "Kuulee Kratt": "kuulee_kratt",
    "kuule Kratt": "kuule_kratt_low",
    "Kuule kratt": "kuule_kratt_low",
    "KUULE KRATT": "kuule_kratt_caps",
    "Ee kuule Kratt": "ee_kuule_kratt",
    "No kuule Kratt": "no_kuule_kratt",
    "Noh kuule Kratt": "noh_kuule_kratt",
}


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
        print(f"  Error {response.status_code}: {response.text[:100]}")
        return False
    except Exception as e:
        print(f"  Exception: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate Phase 2 Neurokõne samples")
    parser.add_argument("--output", default="../raw/neurokone_phase2")
    parser.add_argument("--delay", type=float, default=0.15, help="Delay between API calls (s)")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    total = len(ESTONIAN_SPEAKERS) * len(TEXT_VARIATIONS) * len(SPEEDS)
    print(f"Phase 2: {len(ESTONIAN_SPEAKERS)} speakers x {len(TEXT_VARIATIONS)} texts x {len(SPEEDS)} speeds = {total} samples")

    stats = {"total": 0, "success": 0, "failed": 0, "by_speaker": {}}
    pbar = tqdm(total=total, desc="Generating")

    for speaker in ESTONIAN_SPEAKERS:
        speaker_dir = output_dir / speaker
        speaker_dir.mkdir(exist_ok=True)
        speaker_stats = {"success": 0, "failed": 0}

        idx = 0
        for text in TEXT_VARIATIONS:
            label = LABEL_MAP[text]
            for speed in SPEEDS:
                filename = f"{speaker}_{idx:04d}_{label}_speed{speed}.wav"
                success = generate_sample(text, speaker, speed, speaker_dir / filename)

                if success:
                    speaker_stats["success"] += 1
                    stats["success"] += 1
                else:
                    speaker_stats["failed"] += 1
                    stats["failed"] += 1

                stats["total"] += 1
                idx += 1
                pbar.update(1)
                time.sleep(args.delay)

        stats["by_speaker"][speaker] = speaker_stats
        pbar.set_description(f"Done: {speaker}")

    pbar.close()

    (output_dir / "generation_stats.json").write_text(
        json.dumps(stats, indent=2) + "\n"
    )

    print(f"\nDone: {stats['success']}/{stats['total']} successful")
    print(f"Output: {output_dir}")
    print(f"\nText variations: {len(TEXT_VARIATIONS)}")
    for text in TEXT_VARIATIONS:
        print(f"  - \"{text}\"")


if __name__ == "__main__":
    main()
