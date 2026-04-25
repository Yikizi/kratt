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


# ── VTLP (Vocal Tract Length Perturbation) ──────────────────────────────────
# Warps mel frequency axis to simulate different vocal tract lengths.
# Ref: Jaitly & Hinton 2013, Deka et al. 2025.
# alpha > 1.0 = shorter tract (child/female), alpha < 1.0 = longer (adult male).

def vtlp_warp_spectrogram(
    spectrogram: np.ndarray,
    alpha: float,
) -> np.ndarray:
    """Warp the frequency axis of a (time, n_mels) spectrogram."""
    n_mels = spectrogram.shape[1]
    warped = np.zeros_like(spectrogram)

    for i in range(n_mels):
        orig_idx = i / alpha
        if orig_idx >= n_mels - 1:
            warped[:, i] = spectrogram[:, -1]
        elif orig_idx <= 0:
            warped[:, i] = spectrogram[:, 0]
        else:
            low = int(orig_idx)
            frac = orig_idx - low
            warped[:, i] = (1.0 - frac) * spectrogram[:, low] + frac * spectrogram[:, low + 1]

    return warped


def vtlp_generator(
    gen,
    *,
    probability: float = 0.5,
    alpha_min: float = 0.85,
    alpha_max: float = 1.15,
    rng: random.Random | None = None,
):
    """Wrap a spectrogram generator, applying random VTLP warp."""
    rng = rng or random.Random()
    for spec in gen:
        if rng.random() < probability:
            alpha = rng.uniform(alpha_min, alpha_max)
            spec = vtlp_warp_spectrogram(spec, alpha)
        yield spec


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
        self.paths = sorted(
            [p for p in self.input_directory.glob("*.wav")]
            + [p for p in self.input_directory.glob("*.flac")]
        )
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


AUG_PROFILES = {
    # v6-residual era defaults (Apr 12) — gentle, gave FAPH ~4
    "gentle": {
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
    # Moderate — halfway between gentle and aggressive, controlled experiment
    "moderate": {
        "SevenBandParametricEQ": 0.10,
        "TanhDistortion": 0.05,
        "PitchShift": 0.15,
        "BandStopFilter": 0.10,
        "AddColorNoise": 0.15,
        "AddBackgroundNoise": 0.20,
        "Gain": 1.0,
        "GainTransition": 0.25,
        "RIR": 0.10,
    },
    # Aggressive — current defaults, gave FAPH ~115
    "aggressive": {
        "SevenBandParametricEQ": 0.30,
        "TanhDistortion": 0.05,
        "PitchShift": 0.40,
        "BandStopFilter": 0.15,
        "AddColorNoise": 0.20,
        "AddBackgroundNoise": 0.50,
        "Gain": 1.0,
        "GainTransition": 0.30,
        "RIR": 0.30,
    },
}


def build_augmenter(
    clip_duration_ms: int,
    background_paths: list[str] | None = None,
    impulse_paths: list[str] | None = None,
    aug_profile: str = "aggressive",
) -> Augmentation:
    """Build an Augmentation instance.

    Args:
        clip_duration_ms: Target clip duration in milliseconds.
        background_paths: Directories containing background noise WAVs.
        impulse_paths: Directories containing room impulse response WAVs.
        aug_profile: One of 'gentle', 'moderate', 'aggressive'.
    """
    bg = background_paths or []
    ir = impulse_paths or []
    probs = AUG_PROFILES[aug_profile].copy()

    return Augmentation(
        augmentation_duration_s=clip_duration_ms / 1000.0,
        augmentation_probabilities=probs,
        impulse_paths=ir,
        background_paths=bg,
        background_min_snr_db=-5,
        background_max_snr_db=10,
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
    background_paths: list[str] | None = None,
    impulse_paths: list[str] | None = None,
    vtlp_prob: float = 0.0,
    vtlp_alpha_min: float = 0.85,
    vtlp_alpha_max: float = 1.15,
    aug_profile: str = "aggressive",
) -> None:
    ensure_dirs(out_dir)

    clips = SimpleWavClips(
        input_directory=str(input_dir),
        file_pattern="*.wav",
        random_split_seed=seed,
        split_count=split_count,
    )
    augmenter = build_augmenter(
        clip_duration_ms=clip_duration_ms,
        background_paths=background_paths,
        impulse_paths=impulse_paths,
        aug_profile=aug_profile,
    )

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

        spec_gen = spectrograms.spectrogram_generator(
            split=split_name,
            repeat=repetition,
        )

        # Apply VTLP on training split only (not val/test)
        if vtlp_prob > 0 and split == "training":
            spec_gen = vtlp_generator(
                spec_gen,
                probability=vtlp_prob,
                alpha_min=vtlp_alpha_min,
                alpha_max=vtlp_alpha_max,
                rng=random.Random(seed + 7),
            )

        RaggedMmap.from_generator(
            out_dir=str(out_dir / split / mmap_name),
            sample_generator=spec_gen,
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
    parser.add_argument(
        "--background-noise-dir", action="append", default=[],
        help="Directory of background noise WAVs for AddBackgroundNoise augmentation "
             "(e.g. MUSAN noise). Can be specified multiple times.",
    )
    parser.add_argument(
        "--impulse-response-dir", action="append", default=[],
        help="Directory of room impulse response WAVs for RIR augmentation "
             "(e.g. MIT IRs at 16kHz). Can be specified multiple times.",
    )
    parser.add_argument("--seed", type=int, default=10)
    parser.add_argument("--split-count", type=float, default=0.1)
    parser.add_argument("--ambient-split-count", type=float, default=0.5)
    parser.add_argument("--clip-duration-ms", type=int, default=1500)
    parser.add_argument(
        "--vtlp-prob", type=float, default=0.5,
        help="Probability of applying VTLP warp per spectrogram (0=off). Default: 0.5",
    )
    parser.add_argument(
        "--vtlp-alpha-min", type=float, default=0.85,
        help="Minimum VTLP warp factor (default: 0.85 = longer vocal tract)",
    )
    parser.add_argument(
        "--vtlp-alpha-max", type=float, default=1.15,
        help="Maximum VTLP warp factor (default: 1.15 = shorter vocal tract)",
    )
    parser.add_argument(
        "--aug-profile", default="aggressive",
        choices=list(AUG_PROFILES.keys()),
        help="Augmentation intensity profile (default: aggressive)",
    )

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

    # Resolve and validate augmentation resource directories
    background_paths: list[str] = []
    for d in args.background_noise_dir:
        p = Path(d).expanduser().resolve()
        if not p.exists():
            print(f"WARNING: background noise dir not found, skipping: {p}")
        else:
            background_paths.append(str(p))

    impulse_paths: list[str] = []
    for d in args.impulse_response_dir:
        p = Path(d).expanduser().resolve()
        if not p.exists():
            print(f"WARNING: impulse response dir not found, skipping: {p}")
        else:
            impulse_paths.append(str(p))

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
    if background_paths:
        print(f"Background noise dirs: {background_paths}")
    else:
        print("WARNING: No background noise dirs provided; AddBackgroundNoise will be a no-op")
    if impulse_paths:
        print(f"Impulse response dirs: {impulse_paths}")
    else:
        print("WARNING: No impulse response dirs provided; RIR augmentation will be a no-op")
    if args.vtlp_prob > 0:
        print(f"VTLP: prob={args.vtlp_prob}, alpha=[{args.vtlp_alpha_min}, {args.vtlp_alpha_max}]")
    else:
        print("VTLP: disabled")
    print(f"Aug profile: {args.aug_profile}")
    print(f"Output: {out_dir}")

    common_kwargs = dict(
        vtlp_prob=args.vtlp_prob,
        vtlp_alpha_min=args.vtlp_alpha_min,
        vtlp_alpha_max=args.vtlp_alpha_max,
        aug_profile=args.aug_profile,
    )

    generate_one(
        input_dir=positive_dir,
        out_dir=out_dir / "positive",
        mmap_name="wakeword_mmap",
        seed=args.seed,
        split_count=args.split_count,
        clip_duration_ms=args.clip_duration_ms,
        background_paths=background_paths,
        impulse_paths=impulse_paths,
        **common_kwargs,
    )
    generate_one(
        input_dir=negative_dir,
        out_dir=out_dir / "negative",
        mmap_name="negative_mmap",
        seed=args.seed,
        split_count=args.split_count,
        clip_duration_ms=args.clip_duration_ms,
        background_paths=background_paths,
        impulse_paths=impulse_paths,
        **common_kwargs,
    )
    if hard_negative_dir is not None:
        generate_one(
            input_dir=hard_negative_dir,
            out_dir=out_dir / "hard_negative",
            mmap_name="hard_negative_mmap",
            seed=args.seed,
            split_count=args.split_count,
            clip_duration_ms=args.clip_duration_ms,
            background_paths=background_paths,
            impulse_paths=impulse_paths,
            **common_kwargs,
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
