#!/usr/bin/env python3
"""Generate SSML-enriched positive "Kuule Kratt" samples with prosody variations.

Uses Neurokõne SSML support for pitch, rate, volume, emphasis and pause variations.

Usage:
    python generate_neurokone_ssml_positives.py --output ../raw/neurokone_ssml_positives
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

# SSML variations of "Kuule Kratt" - each tuple is (label, ssml_text)
SSML_VARIATIONS = [
    # Pitch variations
    ("pitch_low20", '<speak><prosody pitch="-20%">Kuule Kratt</prosody></speak>'),
    ("pitch_low10", '<speak><prosody pitch="-10%">Kuule Kratt</prosody></speak>'),
    ("pitch_high10", '<speak><prosody pitch="+10%">Kuule Kratt</prosody></speak>'),
    ("pitch_high20", '<speak><prosody pitch="+20%">Kuule Kratt</prosody></speak>'),
    ("pitch_high30", '<speak><prosody pitch="+30%">Kuule Kratt</prosody></speak>'),

    # Emphasis on first word
    ("emph_kuule", '<speak><emphasis level="strong">Kuule</emphasis> Kratt</speak>'),
    ("emph_kuule_red", '<speak><emphasis level="reduced">Kuule</emphasis> Kratt</speak>'),

    # Emphasis on second word
    ("emph_kratt", '<speak>Kuule <emphasis level="strong">Kratt</emphasis></speak>'),
    ("emph_kratt_red", '<speak>Kuule <emphasis level="reduced">Kratt</emphasis></speak>'),

    # Volume variations
    ("vol_loud", '<speak><prosody volume="loud">Kuule Kratt</prosody></speak>'),
    ("vol_soft", '<speak><prosody volume="soft">Kuule Kratt</prosody></speak>'),
    ("vol_xloud", '<speak><prosody volume="x-loud">Kuule Kratt</prosody></speak>'),
    ("vol_xsoft", '<speak><prosody volume="x-soft">Kuule Kratt</prosody></speak>'),

    # Rate variations (additional to speed param)
    ("rate_slow", '<speak><prosody rate="slow">Kuule Kratt</prosody></speak>'),
    ("rate_fast", '<speak><prosody rate="fast">Kuule Kratt</prosody></speak>'),
    ("rate_xslow", '<speak><prosody rate="x-slow">Kuule Kratt</prosody></speak>'),

    # Pause variations
    ("pause_100", '<speak>Kuule <break time="100ms"/> Kratt</speak>'),
    ("pause_300", '<speak>Kuule <break time="300ms"/> Kratt</speak>'),
    ("pause_500", '<speak>Kuule <break time="500ms"/> Kratt</speak>'),

    # Combined: pitch + emphasis
    ("high_emph_kuule", '<speak><prosody pitch="+15%"><emphasis level="strong">Kuule</emphasis> Kratt</prosody></speak>'),
    ("low_emph_kratt", '<speak><prosody pitch="-15%">Kuule <emphasis level="strong">Kratt</emphasis></prosody></speak>'),

    # Combined: volume + rate
    ("loud_fast", '<speak><prosody volume="loud" rate="fast">Kuule Kratt</prosody></speak>'),
    ("soft_slow", '<speak><prosody volume="soft" rate="slow">Kuule Kratt</prosody></speak>'),

    # Combined: realistic scenarios
    ("whisper_call", '<speak><prosody volume="x-soft" rate="slow">Kuule Kratt</prosody></speak>'),
    ("shout", '<speak><prosody volume="x-loud" pitch="+20%" rate="fast">Kuule Kratt</prosody></speak>'),
    ("tired", '<speak><prosody volume="soft" pitch="-15%" rate="slow">Kuule Kratt</prosody></speak>'),
    ("excited", '<speak><prosody volume="loud" pitch="+25%" rate="fast">Kuule Kratt</prosody></speak>'),
]


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
    parser.add_argument("--output", default="../raw/neurokone_ssml_positives")
    parser.add_argument("--delay", type=float, default=0.12)
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 3 base speeds × SSML variations × speakers
    speeds = [0.9, 1.0, 1.1]
    total = len(ESTONIAN_SPEAKERS) * len(SSML_VARIATIONS) * len(speeds)
    print(f"{len(ESTONIAN_SPEAKERS)} speakers x {len(SSML_VARIATIONS)} SSML variants x {len(speeds)} speeds = {total} samples")

    stats = {"total": 0, "success": 0, "failed": 0}
    pbar = tqdm(total=total, desc="Generating")

    idx = 0
    for speaker in ESTONIAN_SPEAKERS:
        speaker_dir = output_dir / speaker
        speaker_dir.mkdir(exist_ok=True)

        for label, ssml in SSML_VARIATIONS:
            for speed in speeds:
                filename = f"{speaker}_{idx:05d}_{label}_speed{speed}.wav"
                success = generate_sample(ssml, speaker, speed, speaker_dir / filename)

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
    print(f"SSML variations: {len(SSML_VARIATIONS)}")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
