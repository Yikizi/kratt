#!/usr/bin/env python3
"""
Demo script to showcase audio augmentation techniques.
Shows how augmentation transforms a single audio sample.
"""

import numpy as np
import soundfile as sf
from audiomentations import (
    Compose,
    TimeStretch,
    PitchShift,
    AddGaussianNoise,
    Gain,
    RoomSimulator
)
from pathlib import Path

def augment_demo(input_path, output_dir):
    """
    Apply different augmentations to a single audio file and save results.

    This demonstrates what each augmentation does:
    - Time stretching: Makes audio faster/slower without changing pitch
    - Pitch shifting: Makes voice higher/lower
    - Noise: Adds background noise
    - Room simulation: Adds reverb/echo like different rooms
    - Gain: Makes louder/quieter
    """

    # Load audio
    audio, sample_rate = sf.read(input_path)

    print(f"📂 Input: {input_path}")
    print(f"   Sample rate: {sample_rate} Hz")
    print(f"   Duration: {len(audio)/sample_rate:.2f}s")
    print(f"   Shape: {audio.shape}\n")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save original for comparison
    original_path = output_dir / "0_original.wav"
    sf.write(original_path, audio, sample_rate)
    print(f"✅ Original saved: {original_path}")

    # 1. Time Stretch (slower)
    print("\n🎵 Augmentation 1: Time Stretch (0.85x - slower)")
    print("   Why: People speak at different speeds")
    transform = TimeStretch(min_rate=0.85, max_rate=0.85, p=1.0)
    augmented = transform(samples=audio, sample_rate=sample_rate)
    output_path = output_dir / "1_time_stretch_slow.wav"
    sf.write(output_path, augmented, sample_rate)
    print(f"   ✅ Saved: {output_path}")

    # 2. Time Stretch (faster)
    print("\n🎵 Augmentation 2: Time Stretch (1.15x - faster)")
    transform = TimeStretch(min_rate=1.15, max_rate=1.15, p=1.0)
    augmented = transform(samples=audio, sample_rate=sample_rate)
    output_path = output_dir / "2_time_stretch_fast.wav"
    sf.write(output_path, augmented, sample_rate)
    print(f"   ✅ Saved: {output_path}")

    # 3. Pitch Shift (lower)
    print("\n🎵 Augmentation 3: Pitch Shift (-2 semitones - deeper voice)")
    print("   Why: Voice pitch varies by person, mood, time of day")
    transform = PitchShift(min_semitones=-2, max_semitones=-2, p=1.0)
    augmented = transform(samples=audio, sample_rate=sample_rate)
    output_path = output_dir / "3_pitch_shift_lower.wav"
    sf.write(output_path, augmented, sample_rate)
    print(f"   ✅ Saved: {output_path}")

    # 4. Pitch Shift (higher)
    print("\n🎵 Augmentation 4: Pitch Shift (+2 semitones - higher voice)")
    transform = PitchShift(min_semitones=2, max_semitones=2, p=1.0)
    augmented = transform(samples=audio, sample_rate=sample_rate)
    output_path = output_dir / "4_pitch_shift_higher.wav"
    sf.write(output_path, augmented, sample_rate)
    print(f"   ✅ Saved: {output_path}")

    # 5. Background Noise
    print("\n🎵 Augmentation 5: Gaussian Noise (light background noise)")
    print("   Why: Real environments have AC, fans, distant sounds")
    transform = AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.01, p=1.0)
    augmented = transform(samples=audio, sample_rate=sample_rate)
    output_path = output_dir / "5_with_noise.wav"
    sf.write(output_path, augmented, sample_rate)
    print(f"   ✅ Saved: {output_path}")

    # 6. Quieter (Gain reduction)
    print("\n🎵 Augmentation 6: Quieter (-6dB)")
    print("   Why: People don't always speak at same volume")
    transform = Gain(min_gain_db=-6, max_gain_db=-6, p=1.0)
    augmented = transform(samples=audio, sample_rate=sample_rate)
    output_path = output_dir / "6_quieter.wav"
    sf.write(output_path, augmented, sample_rate)
    print(f"   ✅ Saved: {output_path}")

    # 7. Louder (Gain increase)
    print("\n🎵 Augmentation 7: Louder (+3dB)")
    transform = Gain(min_gain_db=3, max_gain_db=3, p=1.0)
    augmented = transform(samples=audio, sample_rate=sample_rate)
    output_path = output_dir / "7_louder.wav"
    sf.write(output_path, augmented, sample_rate)
    print(f"   ✅ Saved: {output_path}")

    # 8. Room Simulation (small room)
    print("\n🎵 Augmentation 8: Room Simulation (adds reverb/echo)")
    print("   Why: Different rooms have different acoustics")
    try:
        transform = RoomSimulator(p=1.0)
        augmented = transform(samples=audio, sample_rate=sample_rate)
        output_path = output_dir / "8_room_reverb.wav"
        sf.write(output_path, augmented, sample_rate)
        print(f"   ✅ Saved: {output_path}")
    except Exception as e:
        print(f"   ⚠️  Room simulation skipped: {e}")

    # 9. Combined (realistic real-world scenario)
    print("\n🎵 Augmentation 9: Combined (time + pitch + noise)")
    print("   Why: Real world has multiple factors at once")
    transform = Compose([
        TimeStretch(min_rate=0.9, max_rate=1.1, p=1.0),
        PitchShift(min_semitones=-1, max_semitones=1, p=1.0),
        AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.005, p=0.5),
        Gain(min_gain_db=-3, max_gain_db=3, p=1.0),
    ])
    augmented = transform(samples=audio, sample_rate=sample_rate)
    output_path = output_dir / "9_combined_realistic.wav"
    sf.write(output_path, augmented, sample_rate)
    print(f"   ✅ Saved: {output_path}")

    print("\n" + "="*60)
    print("✅ DEMO COMPLETE!")
    print("="*60)
    print(f"\n📁 All augmented samples saved to: {output_dir}")
    print("\nNext: Listen to the files to hear the differences!")
    print("      Original vs each augmentation shows what model will learn.")


if __name__ == "__main__":
    # Use one of our generated samples
    input_file = "../raw/neurokone_phase1/mari/mari_0000_Kratt_speed0.8.wav"
    output_dir = "../raw/augmentation_demo"

    print("="*60)
    print("AUDIO AUGMENTATION DEMO")
    print("="*60)
    print("\nThis demo shows how we create variations of audio samples")
    print("to make the model more robust to real-world conditions.\n")

    augment_demo(input_file, output_dir)
