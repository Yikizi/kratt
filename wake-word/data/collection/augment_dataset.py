#!/usr/bin/env python3
"""
Augment Phase 1 dataset with audio transformations.

Takes 1800 clean Neurokõne samples and creates 5 variations per sample:
1. Time stretch (slower)
2. Time stretch (faster)
3. Pitch shift
4. Background noise
5. Combined (realistic)

Output: ~9000 augmented samples organized by speaker and augmentation type.
"""

import numpy as np
import soundfile as sf
from audiomentations import (
    Compose,
    TimeStretch,
    PitchShift,
    AddGaussianNoise,
    Gain,
)
from pathlib import Path
from tqdm import tqdm
import argparse
import json

# Augmentation configurations
AUGMENTATIONS = {
    "time_slow": {
        "transform": lambda: TimeStretch(min_rate=0.85, max_rate=0.90, p=1.0),
        "suffix": "_ts_slow"
    },
    "time_fast": {
        "transform": lambda: TimeStretch(min_rate=1.10, max_rate=1.15, p=1.0),
        "suffix": "_ts_fast"
    },
    "pitch_shift": {
        "transform": lambda: PitchShift(min_semitones=-2, max_semitones=2, p=1.0),
        "suffix": "_pitch"
    },
    "noise": {
        "transform": lambda: Compose([
            AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.01, p=1.0),
            Gain(min_gain_db=-3, max_gain_db=3, p=0.5),
        ]),
        "suffix": "_noise"
    },
    "combined": {
        "transform": lambda: Compose([
            TimeStretch(min_rate=0.9, max_rate=1.1, p=0.8),
            PitchShift(min_semitones=-1, max_semitones=1, p=0.7),
            AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.005, p=0.5),
            Gain(min_gain_db=-3, max_gain_db=3, p=0.8),
        ]),
        "suffix": "_combined"
    }
}


def augment_file(input_path, output_dir, augmentation_name, transform):
    """
    Apply augmentation to a single file.

    Args:
        input_path: Path to input WAV file
        output_dir: Directory to save augmented file
        augmentation_name: Name of augmentation (for subdirectory)
        transform: Audiomentations transform object

    Returns:
        True if successful, False otherwise
    """
    try:
        # Load audio
        audio, sample_rate = sf.read(input_path)

        # Convert to float32 if needed
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        # Apply augmentation
        augmented = transform(samples=audio, sample_rate=sample_rate)

        # Create output path
        input_path = Path(input_path)
        speaker_dir = output_dir / augmentation_name / input_path.parent.name
        speaker_dir.mkdir(parents=True, exist_ok=True)

        # Generate output filename
        suffix = AUGMENTATIONS[augmentation_name]["suffix"]
        output_filename = input_path.stem + suffix + input_path.suffix
        output_path = speaker_dir / output_filename

        # Save augmented audio
        sf.write(output_path, augmented, sample_rate)

        return True

    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False


def augment_dataset(input_dir, output_dir, augmentations=None):
    """
    Augment entire dataset.

    Args:
        input_dir: Directory containing original samples (organized by speaker)
        output_dir: Directory to save augmented samples
        augmentations: List of augmentation names to apply (default: all)
    """

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Use all augmentations if not specified
    if augmentations is None:
        augmentations = list(AUGMENTATIONS.keys())

    print(f"📂 Input: {input_dir}")
    print(f"📂 Output: {output_dir}")
    print(f"🎵 Augmentations: {', '.join(augmentations)}\n")

    # Find all WAV files
    wav_files = list(input_dir.glob("*/*.wav"))
    total_files = len(wav_files)

    if total_files == 0:
        print("❌ No WAV files found!")
        return

    print(f"📊 Found {total_files} original samples")
    print(f"📊 Will generate {total_files * len(augmentations)} augmented samples\n")

    # Statistics
    stats = {
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "total_input_files": total_files,
        "augmentations": augmentations,
        "results": {},
        "success": 0,
        "failed": 0
    }

    # Process each augmentation type
    for aug_name in augmentations:
        print(f"\n{'='*60}")
        print(f"🎵 Applying: {aug_name}")
        print(f"{'='*60}\n")

        transform = AUGMENTATIONS[aug_name]["transform"]()
        aug_stats = {"success": 0, "failed": 0}

        # Process files with progress bar
        for wav_file in tqdm(wav_files, desc=f"{aug_name}"):
            success = augment_file(wav_file, output_dir, aug_name, transform)

            if success:
                aug_stats["success"] += 1
                stats["success"] += 1
            else:
                aug_stats["failed"] += 1
                stats["failed"] += 1

        stats["results"][aug_name] = aug_stats
        print(f"✅ {aug_name}: {aug_stats['success']}/{total_files} successful")

    # Save statistics
    stats_path = output_dir / "augmentation_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)

    # Final summary
    print("\n" + "="*60)
    print("✅ AUGMENTATION COMPLETE")
    print("="*60)
    print(f"\nOriginal samples: {total_files}")
    print(f"Augmented samples: {stats['success']}")
    print(f"Failed: {stats['failed']}")
    print(f"Total dataset: {total_files + stats['success']} samples")
    print(f"\n📁 Output: {output_dir}")
    print(f"📊 Statistics: {stats_path}")

    # Per-augmentation summary
    print("\n📊 Per-augmentation results:")
    for aug_name, aug_stats in stats["results"].items():
        print(f"  {aug_name:15s}: {aug_stats['success']:5d} samples")


def main():
    parser = argparse.ArgumentParser(
        description="Augment wake word dataset with audio transformations"
    )
    parser.add_argument(
        "--input",
        default="../raw/neurokone_phase1",
        help="Input directory with original samples"
    )
    parser.add_argument(
        "--output",
        default="../augmented/phase1",
        help="Output directory for augmented samples"
    )
    parser.add_argument(
        "--augmentations",
        nargs="+",
        choices=list(AUGMENTATIONS.keys()),
        help="Specific augmentations to apply (default: all)"
    )

    args = parser.parse_args()

    print("="*60)
    print("PHASE 1 DATASET AUGMENTATION")
    print("="*60)
    print()

    augment_dataset(
        input_dir=args.input,
        output_dir=args.output,
        augmentations=args.augmentations
    )


if __name__ == "__main__":
    main()
