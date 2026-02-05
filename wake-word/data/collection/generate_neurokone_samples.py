#!/usr/bin/env python3
"""
Generate Phase 1 training dataset using Neurokõne API.

Strategy:
- 12 Estonian speakers
- Multiple variations per speaker:
  - Different speeds (0.8, 0.9, 1.0, 1.1, 1.2)
  - Different contexts (isolated word, with filler, in sentence)
- Target: 1200-3000 samples total

Usage:
    python generate_neurokone_samples.py --output ../raw/neurokone --count 100
"""

import requests
import json
import time
from pathlib import Path
from tqdm import tqdm
import argparse

# API configuration
API_BASE = "https://api.tartunlp.ai/text-to-speech"
API_ENDPOINT = f"{API_BASE}/v2"

# Estonian speakers (exclude Võro speakers)
ESTONIAN_SPEAKERS = [
    "albert", "indrek", "kalev", "kylli", "lee", "liivika",
    "luukas", "mari", "meelis", "peeter", "tambet", "vesta"
]

# Speed variations
SPEEDS = [0.8, 0.9, 1.0, 1.1, 1.2]

# Text variations for "Kratt"
TEXT_VARIATIONS = [
    # Isolated word
    "Kratt",
    "Kratt.",
    "Kratt!",

    # With natural context
    "Kuule Kratt",
    "Tere Kratt",
    "Hei Kratt",
    "Kratt, kuule",
    "Kratt, tere",
    "Kratt, kas sa kuuled",

    # Slightly longer contexts (for variety)
    "Öö Kratt",
    "Oot Kratt",
    "No Kratt",
]


def get_available_speakers():
    """Fetch list of available speakers from API."""
    try:
        response = requests.get(API_ENDPOINT, timeout=10)
        if response.status_code == 200:
            config = response.json()
            return [s["name"] for s in config.get("speakers", [])]
        else:
            print(f"⚠️  Could not fetch speakers: {response.status_code}")
            return ESTONIAN_SPEAKERS
    except Exception as e:
        print(f"⚠️  Error fetching speakers: {e}")
        return ESTONIAN_SPEAKERS


def generate_sample(text, speaker, speed, output_path):
    """
    Generate a single audio sample.

    Args:
        text: Text to synthesize
        speaker: Speaker name
        speed: Speed multiplier (0.5-2.0)
        output_path: Path to save WAV file

    Returns:
        True if successful, False otherwise
    """
    try:
        response = requests.post(
            API_ENDPOINT,
            json={"text": text, "speaker": speaker, "speed": speed},
            timeout=30
        )

        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"  ❌ Error {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False


def generate_dataset(output_dir, samples_per_speaker=100, delay=0.1):
    """
    Generate complete Phase 1 dataset.

    Args:
        output_dir: Output directory for samples
        samples_per_speaker: Target samples per speaker
        delay: Delay between API calls (seconds)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get available speakers
    print("🔍 Fetching available speakers...")
    available_speakers = get_available_speakers()
    estonian_speakers = [s for s in ESTONIAN_SPEAKERS if s in available_speakers]

    print(f"✅ Found {len(estonian_speakers)} Estonian speakers")
    print(f"   Speakers: {', '.join(estonian_speakers)}\n")

    # Calculate total samples
    total_samples = len(estonian_speakers) * samples_per_speaker
    print(f"📊 Target: {samples_per_speaker} samples per speaker")
    print(f"📊 Total: {total_samples} samples\n")

    # Generate samples
    stats = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "by_speaker": {}
    }

    # Create progress bar
    pbar = tqdm(total=total_samples, desc="Generating samples")

    for speaker in estonian_speakers:
        speaker_dir = output_dir / speaker
        speaker_dir.mkdir(exist_ok=True)

        speaker_stats = {"success": 0, "failed": 0}

        # Generate samples for this speaker
        sample_idx = 0
        while speaker_stats["success"] < samples_per_speaker:
            # Cycle through variations
            text_idx = sample_idx % len(TEXT_VARIATIONS)
            speed_idx = (sample_idx // len(TEXT_VARIATIONS)) % len(SPEEDS)

            text = TEXT_VARIATIONS[text_idx]
            speed = SPEEDS[speed_idx]

            # Generate filename
            text_safe = text.replace(" ", "_").replace(",", "").replace(".", "").replace("!", "")
            filename = f"{speaker}_{sample_idx:04d}_{text_safe}_speed{speed}.wav"
            output_path = speaker_dir / filename

            # Generate sample
            success = generate_sample(text, speaker, speed, output_path)

            if success:
                speaker_stats["success"] += 1
                stats["success"] += 1
            else:
                speaker_stats["failed"] += 1
                stats["failed"] += 1

            stats["total"] += 1
            sample_idx += 1
            pbar.update(1)

            # Rate limiting
            time.sleep(delay)

        stats["by_speaker"][speaker] = speaker_stats
        pbar.set_description(f"Generating samples ({speaker} complete)")

    pbar.close()

    # Save statistics
    stats_path = output_dir / "generation_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)

    print("\n" + "="*60)
    print("✅ GENERATION COMPLETE")
    print("="*60)
    print(f"Total samples: {stats['success']}/{stats['total']}")
    print(f"Failed: {stats['failed']}")
    print(f"Output directory: {output_dir}")
    print(f"Statistics saved: {stats_path}")

    # Print per-speaker summary
    print("\n📊 Per-speaker summary:")
    for speaker, speaker_stats in stats["by_speaker"].items():
        print(f"  {speaker:10s}: {speaker_stats['success']:4d} samples")


def main():
    parser = argparse.ArgumentParser(description="Generate Neurokõne training samples")
    parser.add_argument(
        "--output",
        default="../raw/neurokone_phase1",
        help="Output directory (default: ../raw/neurokone_phase1)"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Samples per speaker (default: 100)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.1,
        help="Delay between API calls in seconds (default: 0.1)"
    )

    args = parser.parse_args()

    print("="*60)
    print("NEUROKÕNE DATASET GENERATOR - PHASE 1")
    print("="*60)
    print()

    generate_dataset(
        output_dir=args.output,
        samples_per_speaker=args.count,
        delay=args.delay
    )


if __name__ == "__main__":
    main()
