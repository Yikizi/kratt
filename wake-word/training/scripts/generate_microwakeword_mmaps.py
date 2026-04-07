#!/usr/bin/env python3
"""
Generate RaggedMmap spectrogram feature sets for microWakeWord training.

Creates the folder structure expected by microWakeWord:
  <out>/<split>/<name>_mmap/
Where split is one of:
  training / validation / testing
Optional ambient negatives are written to:
  validation_ambient / testing_ambient
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np
import soundfile as sf

from mmap_ninja.ragged import RaggedMmap

from microwakeword.audio.augmentation import Augmentation
from microwakeword.audio.spectrograms import SpectrogramGeneration


def load_16k_mono(path: Path) -> np.ndarray:
    audio, sr = sf.read(str(path), always_2d=False)
    if isinstance(audio, np.ndarray) and audio.ndim > 1:
        audio = audio[:, 0]
    audio = audio.astype(np.float32, copy=False)
    if sr != 16000:
        # librosa is installed in the microwakeword venv via audiomentations deps.
        import librosa

        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000).astype(
            np.float32, copy=False
        )
    return audio


class SimpleWavClips:
    """
    Minimal replacement for microwakeword.audio.clips.Clips.

    Why:
    - Newer `datasets` versions require `torchcodec` for Audio decoding.
    - For this project we only need to load local WAVs and resample to 16kHz.
    """

    def __init__(self, input_directory: str, file_pattern: str, random_split_seed: int, split_count: float):
        self.input_directory = Path(input_directory)
        self.paths = sorted([p for p in self.input_directory.glob(file_pattern)])
        if not self.paths:
            raise ValueError(f"No clips found in {input_directory} matching {file_pattern}")

        rnd = random.Random(random_split_seed)
        shuffled = self.paths[:]
        rnd.shuffle(shuffled)

        split_n = int(len(shuffled) * split_count)
        testvalid = shuffled[: 2 * split_n]
        train = shuffled[2 * split_n :]
        test = testvalid[:split_n]
        valid = testvalid[split_n:]

        self.split_clips = {"train": train, "test": test, "validation": valid}
        self.clips = shuffled

    def audio_generator(self, split: str | None = None, repeat: int = 1):
        if split is None:
            clip_list = self.clips
        else:
            clip_list = self.split_clips[split]
        for _ in range(repeat):
            for p in clip_list:
                yield load_16k_mono(p)

    def get_random_clip(self):
        p = random.choice(self.clips)
        return load_16k_mono(p)

    def random_audio_generator(self, max_clips: int = 10**18):
        while max_clips > 0:
            max_clips -= 1
            yield self.get_random_clip()


def ensure_dirs(base: Path, include_ambient: bool = False) -> None:
    for split in ("training", "validation", "testing"):
        (base / split).mkdir(parents=True, exist_ok=True)
    if include_ambient:
        for split in ("validation_ambient", "testing_ambient"):
            (base / split).mkdir(parents=True, exist_ok=True)


def build_augmenter(clip_duration_ms: int) -> Augmentation:
    # Keep it light initially: add some color noise + gain, no external backgrounds/impulses.
    return Augmentation(
        augmentation_duration_s=clip_duration_ms / 1000.0,
        augmentation_probabilities={
            "SevenBandParametricEQ": 0.05,
            "TanhDistortion": 0.05,
            "PitchShift": 0.05,
            "BandStopFilter": 0.05,
            "AddColorNoise": 0.15,
            "AddBackgroundNoise": 0.0,
            "Gain": 1.0,
            "GainTransition": 0.25,
            "RIR": 0.0,
        },
        impulse_paths=[],
        background_paths=[],
        min_jitter_s=0.0,
        max_jitter_s=0.0,
        truncate_randomly=True,
    )


def build_identity_augmenter() -> Augmentation:
    return Augmentation(
        augmentation_duration_s=None,
        augmentation_probabilities={
            "SevenBandParametricEQ": 0.0,
            "TanhDistortion": 0.0,
            "PitchShift": 0.0,
            "BandStopFilter": 0.0,
            "AddColorNoise": 0.0,
            "AddBackgroundNoise": 0.0,
            "Gain": 0.0,
            "GainTransition": 0.0,
            "RIR": 0.0,
        },
        impulse_paths=[],
        background_paths=[],
        min_jitter_s=0.0,
        max_jitter_s=0.0,
        truncate_randomly=False,
    )


def generate_one(
    input_dir: Path,
    out_dir: Path,
    mmap_name: str,
    seed: int,
    split_count: float,
    clip_duration_ms: int,
) -> None:
    ensure_dirs(out_dir)

    clips = SimpleWavClips(
        input_directory=str(input_dir),
        file_pattern="*.wav",
        random_split_seed=seed,
        split_count=split_count,
    )
    augmenter = build_augmenter(clip_duration_ms=clip_duration_ms)

    for split in ("training", "validation", "testing"):
        split_name = "train"
        repetition = 2
        slide_frames = 10

        if split == "validation":
            split_name = "validation"
            repetition = 1
            slide_frames = 10
        elif split == "testing":
            split_name = "test"
            repetition = 1
            # Testing uses streaming model, no artificial repetition.
            slide_frames = 1

        spectrograms = SpectrogramGeneration(
            clips=clips,
            augmenter=augmenter,
            slide_frames=slide_frames,
            step_ms=10,
        )

        RaggedMmap.from_generator(
            out_dir=str(out_dir / split / mmap_name),
            sample_generator=spectrograms.spectrogram_generator(
                split=split_name,
                repeat=repetition,
            ),
            batch_size=100,
            verbose=True,
        )


def generate_ambient(
    input_dir: Path,
    out_dir: Path,
    mmap_name: str,
    seed: int,
    clip_duration_ms: int,
    ambient_split_count: float,
) -> None:
    ensure_dirs(out_dir, include_ambient=True)

    clips = SimpleWavClips(
        input_directory=str(input_dir),
        file_pattern="*.wav",
        random_split_seed=seed,
        split_count=ambient_split_count,
    )
    augmenter = build_identity_augmenter()
    spectrograms = SpectrogramGeneration(
        clips=clips,
        augmenter=augmenter,
        slide_frames=1,
        step_ms=10,
    )

    split_map = {
        "validation_ambient": "validation",
        "testing_ambient": "test",
    }
    for split, split_name in split_map.items():
        RaggedMmap.from_generator(
            out_dir=str(out_dir / split / mmap_name),
            sample_generator=spectrograms.spectrogram_generator(
                split=split_name,
                repeat=1,
            ),
            batch_size=100,
            verbose=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--positive-dir", required=True)
    parser.add_argument("--negative-dir", required=True)
    parser.add_argument("--hard-negative-dir",
                        help="Optional dir of hard (phonetically similar) negatives. "
                             "Generates a separate hard_negative/ feature set.")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--ambient-dir")
    parser.add_argument("--seed", type=int, default=10)
    parser.add_argument("--split-count", type=float, default=0.1)
    parser.add_argument("--ambient-split-count", type=float, default=0.5)
    parser.add_argument("--clip-duration-ms", type=int, default=1500)

    args = parser.parse_args()

    positive_dir = Path(args.positive_dir).expanduser().resolve()
    negative_dir = Path(args.negative_dir).expanduser().resolve()
    hard_negative_dir = (
        Path(args.hard_negative_dir).expanduser().resolve()
        if args.hard_negative_dir
        else None
    )
    out_dir = Path(args.out_dir).expanduser().resolve()
    ambient_dir = (
        Path(args.ambient_dir).expanduser().resolve() if args.ambient_dir else None
    )

    if not positive_dir.exists():
        raise SystemExit(f"Positive dir not found: {positive_dir}")
    if not negative_dir.exists():
        raise SystemExit(f"Negative dir not found: {negative_dir}")
    if hard_negative_dir is not None and not hard_negative_dir.exists():
        raise SystemExit(f"Hard negative dir not found: {hard_negative_dir}")
    if ambient_dir is not None and not ambient_dir.exists():
        raise SystemExit(f"Ambient dir not found: {ambient_dir}")

    (out_dir / "positive").mkdir(parents=True, exist_ok=True)
    (out_dir / "negative").mkdir(parents=True, exist_ok=True)
    if hard_negative_dir is not None:
        (out_dir / "hard_negative").mkdir(parents=True, exist_ok=True)

    print(f"Positive clips: {positive_dir}")
    print(f"Negative clips: {negative_dir}")
    if hard_negative_dir is not None:
        print(f"Hard negative clips: {hard_negative_dir}")
    if ambient_dir is not None:
        print(f"Ambient clips: {ambient_dir}")
    print(f"Output: {out_dir}")

    generate_one(
        input_dir=positive_dir,
        out_dir=out_dir / "positive",
        mmap_name="wakeword_mmap",
        seed=args.seed,
        split_count=args.split_count,
        clip_duration_ms=args.clip_duration_ms,
    )
    generate_one(
        input_dir=negative_dir,
        out_dir=out_dir / "negative",
        mmap_name="negative_mmap",
        seed=args.seed,
        split_count=args.split_count,
        clip_duration_ms=args.clip_duration_ms,
    )
    if hard_negative_dir is not None:
        generate_one(
            input_dir=hard_negative_dir,
            out_dir=out_dir / "hard_negative",
            mmap_name="hard_negative_mmap",
            seed=args.seed,
            split_count=args.split_count,
            clip_duration_ms=args.clip_duration_ms,
        )
    if ambient_dir is not None:
        generate_ambient(
            input_dir=ambient_dir,
            out_dir=out_dir / "negative",
            mmap_name="ambient_mmap",
            seed=args.seed,
            clip_duration_ms=args.clip_duration_ms,
            ambient_split_count=args.ambient_split_count,
        )


if __name__ == "__main__":
    main()
