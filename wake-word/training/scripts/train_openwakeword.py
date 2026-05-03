#!/usr/bin/env python3
"""
Patched openWakeWord training script for custom (pre-recorded) WAV files.

Fixes applied to upstream openwakeword/train.py:
  1. Piper TTS import moved inside --generate_clips branch (not unconditional)
  2. augmentation_batch_size default lowered to avoid GPU OOM
  3. false_positive_validation_data_path is optional (prints warning if missing)
  4. batch_n_per_class validated as dict

Usage:
  python train_openwakeword.py --training_config config.yaml --augment_clips --train_model

Pre-requisites:
  - WAV files (16kHz, mono) in {output_dir}/{model_name}/positive_train/ etc.
  - melspectrogram.onnx + embedding_model.onnx in openwakeword resources/models/
  - validation_set_features.npy for false positive validation
"""

import torch
try:
    torch.multiprocessing.set_sharing_strategy("file_system")
except RuntimeError as exc:
    # Best-effort guard for HPC DataLoader "too many open files" failures.
    logging.warning("Could not set torch multiprocessing sharing strategy: %s", exc)
import numpy as np
import scipy
import os
import sys
import argparse
import logging
import yaml
from pathlib import Path
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

import openwakeword
from openwakeword.train import Model, convert_onnx_to_tflite
from openwakeword.data import augment_clips, mmap_batch_generator
from openwakeword.utils import compute_features_from_generator, AudioFeatures


def ensure_resource_models():
    """Download melspectrogram.onnx and embedding_model.onnx if missing."""
    import pathlib
    resources_dir = os.path.join(pathlib.Path(openwakeword.__file__).parent.resolve(),
                                 "resources", "models")
    os.makedirs(resources_dir, exist_ok=True)

    required = {
        "melspectrogram.onnx": "https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/melspectrogram.onnx",
        "embedding_model.onnx": "https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/embedding_model.onnx",
        "melspectrogram.tflite": "https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/melspectrogram.tflite",
        "embedding_model.tflite": "https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/embedding_model.tflite",
    }

    for fname, url in required.items():
        fpath = os.path.join(resources_dir, fname)
        if not os.path.exists(fpath):
            logging.info(f"Downloading {fname} from {url}")
            from openwakeword.utils import download_file
            download_file(url, resources_dir)
        else:
            logging.info(f"Found {fname}")


def list_wavs(path: str | os.PathLike[str]) -> list[Path]:
    """Return WAVs from a directory tree, recursively and sorted."""
    return sorted(Path(path).rglob("*.wav"))


def validate_wav_dir(path, name, must_have_files=True):
    """Validate directory exists and contains WAV files."""
    if not os.path.isdir(path):
        raise FileNotFoundError(f"{name} directory does not exist: {path}")
    wav_count = len(list_wavs(path))
    if must_have_files and wav_count == 0:
        raise FileNotFoundError(f"{name} directory has no .wav files: {path}")
    logging.info(f"{name}: {wav_count} WAV files in {path}")
    return wav_count


def check_wav_sample_rate(wav_dir, sample_size=5):
    """Spot-check a few WAVs to verify they are 16kHz."""
    wavs = list_wavs(wav_dir)[:sample_size]
    for wav_path in wavs:
        sr, _ = scipy.io.wavfile.read(str(wav_path))
        if sr != 16000:
            raise ValueError(
                f"WAV file {wav_path} has sample rate {sr}Hz, expected 16000Hz. "
                f"Convert with: ffmpeg -i input.wav -ar 16000 -ac 1 output.wav"
            )


def compute_total_length(positive_test_dir, n_samples=50):
    """Compute total_length from median positive test clip duration, matching upstream logic."""
    positive_clips = list_wavs(positive_test_dir)
    if not positive_clips:
        raise FileNotFoundError(f"No WAV files in positive_test: {positive_test_dir}")

    duration_in_samples = []
    for _ in range(min(n_samples, len(positive_clips))):
        clip = positive_clips[np.random.randint(0, len(positive_clips))]
        sr, dat = scipy.io.wavfile.read(str(clip))
        duration_in_samples.append(len(dat))

    total_length = int(round(np.median(duration_in_samples) / 1000) * 1000) + 12000
    if total_length < 32000:
        total_length = 32000
    elif abs(total_length - 32000) <= 4000:
        total_length = 32000

    logging.info(f"Computed total_length: {total_length} samples "
                 f"({total_length/16000:.2f}s, median clip: "
                 f"{np.median(duration_in_samples)/16000:.2f}s)")
    return total_length


def run_augment_clips(config, positive_train_dir, positive_test_dir,
                      negative_train_dir, negative_test_dir,
                      feature_save_dir, background_paths, rir_paths, overwrite=False):
    """Run augmentation and feature computation."""

    output_check = os.path.join(feature_save_dir, "positive_features_train.npy")
    if os.path.exists(output_check) and not overwrite:
        logging.warning("Feature files already exist, skipping augmentation. Use --overwrite to regenerate.")
        return

    total_length = compute_total_length(positive_test_dir)

    def make_generator(wav_dir, rounds):
        wavs = list_wavs(wav_dir)
        clips = [str(i) for i in wavs] * rounds
        if not clips:
            raise FileNotFoundError(f"No WAV files in {wav_dir}")
        logging.info(f"  {wav_dir}: {len(wavs)} clips x {rounds} rounds = {len(clips)} total")
        return augment_clips(
            clips,
            total_length=total_length,
            batch_size=config["augmentation_batch_size"],
            background_clip_paths=background_paths,
            RIR_paths=rir_paths
        )

    rounds = config["augmentation_rounds"]
    generators = {
        "positive_train": (make_generator(positive_train_dir, rounds),
                           len(list_wavs(positive_train_dir)) * rounds),
        "positive_test": (make_generator(positive_test_dir, rounds),
                          len(list_wavs(positive_test_dir)) * rounds),
        "negative_train": (make_generator(negative_train_dir, rounds),
                           len(list_wavs(negative_train_dir)) * rounds),
        "negative_test": (make_generator(negative_test_dir, rounds),
                          len(list_wavs(negative_test_dir)) * rounds),
    }

    feature_names = {
        "positive_train": "positive_features_train.npy",
        "positive_test": "positive_features_test.npy",
        "negative_train": "negative_features_train.npy",
        "negative_test": "negative_features_test.npy",
    }

    n_cpus = os.cpu_count() or 1
    n_cpus = max(1, n_cpus // 2)
    device = "gpu" if torch.cuda.is_available() else "cpu"

    logging.info(f"Computing features on device={device}, ncpu={n_cpus if device == 'cpu' else 1}")

    for key, (gen, n_files) in generators.items():
        output_file = os.path.join(feature_save_dir, feature_names[key])
        logging.info(f"Computing features for {key} ({n_files} files) -> {output_file}")
        compute_features_from_generator(
            gen,
            n_total=n_files,
            clip_duration=total_length,
            output_file=output_file,
            device=device,
            ncpu=n_cpus if device == "cpu" else 1
        )


def validate_config(config: dict) -> None:
    """Fail fast on the most common openWakeWord config mistakes."""
    required_keys = [
        "model_name",
        "output_dir",
        "augmentation_rounds",
        "augmentation_batch_size",
        "steps",
        "batch_n_per_class",
    ]
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Missing required config key: {key}")

    if not isinstance(config["batch_n_per_class"], dict):
        raise TypeError("batch_n_per_class must be a dict")

    fp_val_path = config.get("false_positive_validation_data_path")
    if fp_val_path:
        fp_val_path = str(fp_val_path)
        if not fp_val_path.endswith(".npy"):
            raise ValueError(
                "false_positive_validation_data_path must point to a .npy file "
                f"(got: {fp_val_path})"
            )

    for key, path in (config.get("feature_data_files") or {}).items():
        if path in (None, "", "null"):
            continue
        if not str(path).endswith(".npy"):
            raise ValueError(f"feature_data_files[{key!r}] must point to a .npy file: {path}")


def preflight_summary(
    config: dict,
    positive_train_dir: str,
    positive_test_dir: str,
    negative_train_dir: str,
    negative_test_dir: str,
) -> None:
    """Log the data layout and catch common empty-input issues before work starts."""
    validate_config(config)
    logging.info("Preflight summary:")
    for label, directory in [
        ("positive_train", positive_train_dir),
        ("positive_test", positive_test_dir),
        ("negative_train", negative_train_dir),
        ("negative_test", negative_test_dir),
    ]:
        logging.info("  %-15s %s", label + ":", directory)

    if config["augmentation_batch_size"] <= 0:
        raise ValueError("augmentation_batch_size must be > 0")
    if config["augmentation_rounds"] <= 0:
        raise ValueError("augmentation_rounds must be > 0")
    if config["steps"] <= 0:
        raise ValueError("steps must be > 0")


def run_train_model(config, feature_save_dir):
    """Run model training."""

    # Load feature shape from test data
    pos_test_path = os.path.join(feature_save_dir, "positive_features_test.npy")
    if not os.path.exists(pos_test_path):
        raise FileNotFoundError(f"Feature file not found: {pos_test_path}. Run --augment_clips first.")

    input_shape = np.load(pos_test_path).shape[1:]
    logging.info(f"Model input shape: {input_shape}")

    # Create model
    oww = Model(
        n_classes=1,
        input_shape=input_shape,
        model_type=config["model_type"],
        layer_dim=config["layer_size"],
        seconds_per_example=1280 * input_shape[0] / 16000
    )
    logging.info(f"Model summary:\n{oww.summary()}")

    # Data transform for different clip lengths
    def f(x, n=input_shape[0]):
        if n > x.shape[1] or n < x.shape[1]:
            x = np.vstack(x)
            new_batch = np.array([x[i:i+n, :] for i in range(0, x.shape[0]-n, n)])
        else:
            return x
        return new_batch

    # Build feature_data_files with actual paths
    feature_data_files = {}
    feature_data_files["positive"] = os.path.join(feature_save_dir, "positive_features_train.npy")
    feature_data_files["adversarial_negative"] = os.path.join(feature_save_dir, "negative_features_train.npy")

    # Add any extra negative datasets from config
    if config.get("feature_data_files"):
        for key, path in config["feature_data_files"].items():
            if key in ("positive", "adversarial_negative"):
                continue  # already set above
            if path and path != "null" and os.path.exists(str(path)):
                feature_data_files[key] = str(path)
                logging.info(f"Added extra negative data: {key} -> {path}")

    # Verify all feature files exist
    for key, path in feature_data_files.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Feature file for '{key}' not found: {path}")
        shape = np.load(path, mmap_mode='r').shape
        logging.info(f"  {key}: {path} shape={shape}")

    # Build transforms
    data_transforms = {key: f for key in feature_data_files.keys()}
    label_transforms = {}
    for key in feature_data_files.keys():
        if key == "positive":
            label_transforms[key] = lambda x: [1 for _ in x]
        else:
            label_transforms[key] = lambda x: [0 for _ in x]

    # Validate and build batch_n_per_class
    batch_n_per_class = config.get("batch_n_per_class", {})
    if not isinstance(batch_n_per_class, dict):
        logging.warning(
            f"batch_n_per_class is {type(batch_n_per_class).__name__}, expected dict. "
            f"Auto-generating with default values."
        )
        batch_n_per_class = {}

    # Ensure all feature keys have batch sizes
    for key in feature_data_files.keys():
        if key not in batch_n_per_class:
            if key == "positive":
                batch_n_per_class[key] = 50
            elif key == "adversarial_negative":
                batch_n_per_class[key] = 50
            else:
                batch_n_per_class[key] = 1024
            logging.info(f"  Auto-set batch_n_per_class['{key}'] = {batch_n_per_class[key]}")

    total_batch = sum(batch_n_per_class.values())
    logging.info(f"Batch sizes per class: {batch_n_per_class} (total: {total_batch})")

    # Create batch generator
    batch_generator = mmap_batch_generator(
        feature_data_files,
        n_per_class=batch_n_per_class,
        data_transform_funcs=data_transforms,
        label_transform_funcs=label_transforms
    )

    class IterDataset(torch.utils.data.IterableDataset):
        def __init__(self, generator):
            self.generator = generator
        def __iter__(self):
            return self.generator

    default_workers = min(4, max(1, os.cpu_count() or 1))
    n_workers = int(config.get("training_num_workers", default_workers))
    n_workers = max(0, n_workers)
    prefetch_factor = int(config.get("training_prefetch_factor", 2))
    prefetch_factor = max(1, prefetch_factor)
    logging.info(
        "Training DataLoader: num_workers=%s, prefetch_factor=%s, sharing_strategy=%s",
        n_workers,
        prefetch_factor,
        torch.multiprocessing.get_sharing_strategy(),
    )
    dataloader_kwargs = {
        "batch_size": None,
        "num_workers": n_workers,
    }
    if n_workers > 0:
        dataloader_kwargs["prefetch_factor"] = prefetch_factor
    X_train = torch.utils.data.DataLoader(
        IterDataset(batch_generator),
        **dataloader_kwargs,
    )

    # Load false positive validation data
    fp_val_path = config.get("false_positive_validation_data_path", "")
    X_val_fp = None
    if fp_val_path and os.path.isfile(fp_val_path):
        logging.info(f"Loading false positive validation data: {fp_val_path}")
        fp_data = np.load(fp_val_path)
        logging.info(f"  Raw shape: {fp_data.shape}")
        fp_data = np.array([fp_data[i:i+input_shape[0]]
                            for i in range(0, fp_data.shape[0]-input_shape[0], 1)])
        fp_labels = np.zeros(fp_data.shape[0]).astype(np.float32)
        fp_batch_size = int(config.get("false_positive_validation_batch_size", 4096))
        fp_batch_size = max(1, min(fp_batch_size, len(fp_labels)))
        X_val_fp = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(
                torch.from_numpy(fp_data),
                torch.from_numpy(fp_labels)
            ),
            batch_size=fp_batch_size
        )
        logging.info(f"  Reshaped to {fp_data.shape[0]} windows, batch_size={fp_batch_size}")
    else:
        logging.warning(
            f"false_positive_validation_data_path not found or empty: '{fp_val_path}'. "
            f"Training will proceed without FP validation (FP/hr metrics will not be computed)."
        )

    # Load balanced validation data
    X_val_pos = np.load(os.path.join(feature_save_dir, "positive_features_test.npy"))
    X_val_neg = np.load(os.path.join(feature_save_dir, "negative_features_test.npy"))
    labels = np.hstack((np.ones(X_val_pos.shape[0]), np.zeros(X_val_neg.shape[0]))).astype(np.float32)

    X_val = torch.utils.data.DataLoader(
        torch.utils.data.TensorDataset(
            torch.from_numpy(np.vstack((X_val_pos, X_val_neg))),
            torch.from_numpy(labels)
        ),
        batch_size=len(labels)
    )

    # Run auto training
    logging.info(f"Starting auto_train: steps={config['steps']}, "
                 f"max_negative_weight={config['max_negative_weight']}, "
                 f"target_fp_per_hour={config['target_false_positives_per_hour']}")

    best_model = oww.auto_train(
        X_train=X_train,
        X_val=X_val,
        false_positive_val_data=X_val_fp,
        steps=config["steps"],
        max_negative_weight=config["max_negative_weight"],
        target_fp_per_hour=config["target_false_positives_per_hour"],
    )

    # Export model
    output_dir = config["output_dir"]
    model_name = config["model_name"]
    oww.export_model(model=best_model, model_name=model_name, output_dir=output_dir)
    logging.info(f"Model saved: {os.path.join(output_dir, model_name + '.onnx')}")

    return best_model


def main():
    parser = argparse.ArgumentParser(
        description="Train openWakeWord model from pre-recorded WAV files"
    )
    parser.add_argument("--training_config", required=True, type=str,
                        help="Path to YAML training config")
    parser.add_argument("--generate_clips", action="store_true", default=False,
                        help="Generate synthetic clips via Piper TTS (requires piper-sample-generator)")
    parser.add_argument("--augment_clips", action="store_true", default=False,
                        help="Augment WAV files and compute features")
    parser.add_argument("--train_model", action="store_true", default=False,
                        help="Train the model on pre-computed features")
    parser.add_argument("--overwrite", action="store_true", default=False,
                        help="Overwrite existing feature files")
    parser.add_argument("--convert_to_tflite", action="store_true", default=False,
                        help="Convert ONNX model to TFLite format")
    parser.add_argument("--preflight-only", action="store_true", default=False,
                        help="Validate config/data/resources and exit before augmentation/training")
    args = parser.parse_args()

    config = yaml.load(open(args.training_config, 'r').read(), yaml.Loader)

    # --- Validate early ---
    logging.info("=" * 60)
    logging.info("openWakeWord training (patched for custom WAV files)")
    logging.info("=" * 60)

    # Ensure feature extraction models are available
    ensure_resource_models()

    # Define output locations
    config["output_dir"] = os.path.abspath(config["output_dir"])
    os.makedirs(os.path.join(config["output_dir"], config["model_name"]), exist_ok=True)

    positive_train_dir = os.path.join(config["output_dir"], config["model_name"], "positive_train")
    positive_test_dir = os.path.join(config["output_dir"], config["model_name"], "positive_test")
    negative_train_dir = os.path.join(config["output_dir"], config["model_name"], "negative_train")
    negative_test_dir = os.path.join(config["output_dir"], config["model_name"], "negative_test")
    feature_save_dir = os.path.join(config["output_dir"], config["model_name"])
    preflight_summary(
        config,
        positive_train_dir,
        positive_test_dir,
        negative_train_dir,
        negative_test_dir,
    )

    # --- Step 0: Validate WAV directories ---
    # Full WAV validation is required for augmentation/preflight, but not when
    # resuming from existing .npy feature caches with --train_model only.
    if args.augment_clips or args.preflight_only:
        logging.info("Validating WAV directories...")
        for d, name in [
            (positive_train_dir, "positive_train"),
            (positive_test_dir, "positive_test"),
            (negative_train_dir, "negative_train"),
            (negative_test_dir, "negative_test"),
        ]:
            validate_wav_dir(d, name, must_have_files=True)
            check_wav_sample_rate(d)

    # Get RIR and background paths
    rir_paths = []
    for rir_dir in config.get("rir_paths", []):
        if os.path.isdir(rir_dir):
            rir_paths.extend([i.path for i in os.scandir(rir_dir)])
    logging.info(f"RIR files: {len(rir_paths)}")

    background_paths = []
    bg_paths = config.get("background_paths", [])
    bg_rates = config.get("background_paths_duplication_rate", [1] * len(bg_paths))
    if len(bg_rates) != len(bg_paths):
        bg_rates = [1] * len(bg_paths)
    for bg_path, rate in zip(bg_paths, bg_rates):
        if os.path.isdir(bg_path):
            background_paths.extend([i.path for i in os.scandir(bg_path)] * rate)
    logging.info(f"Background audio files: {len(background_paths)}")

    if args.preflight_only:
        logging.info("Preflight checks passed.")
        return

    # --- Step 1: Generate clips (only if requested) ---
    if args.generate_clips:
        logging.info("=" * 60)
        logging.info("Step 1: Generating synthetic clips via Piper TTS")
        logging.info("=" * 60)
        # Only import Piper when actually needed
        piper_path = config.get("piper_sample_generator_path", "")
        if not piper_path or not os.path.isdir(piper_path):
            raise FileNotFoundError(
                f"piper_sample_generator_path is invalid: '{piper_path}'. "
                f"Clone https://github.com/dscripka/piper-sample-generator"
            )
        sys.path.insert(0, os.path.abspath(piper_path))
        from generate_samples import generate_samples
        # (upstream generate_clips logic would go here -- omitted since we use our own WAVs)
        raise NotImplementedError(
            "--generate_clips is not implemented in the patched script. "
            "Use the upstream openwakeword/train.py for TTS generation, "
            "or pre-populate the WAV directories manually."
        )

    # --- Step 2: Augment clips and compute features ---
    if args.augment_clips:
        logging.info("=" * 60)
        logging.info("Step 2: Augmenting clips and computing features")
        logging.info("=" * 60)
        run_augment_clips(
            config, positive_train_dir, positive_test_dir,
            negative_train_dir, negative_test_dir,
            feature_save_dir, background_paths, rir_paths,
            overwrite=args.overwrite
        )

    # --- Step 3: Train model ---
    if args.train_model:
        logging.info("=" * 60)
        logging.info("Step 3: Training model")
        logging.info("=" * 60)
        best_model = run_train_model(config, feature_save_dir)

        # --- Step 4 (optional): Convert to TFLite ---
        if args.convert_to_tflite:
            onnx_path = os.path.join(config["output_dir"], config["model_name"] + ".onnx")
            tflite_path = os.path.join(config["output_dir"], config["model_name"] + ".tflite")
            logging.info(f"Converting {onnx_path} -> {tflite_path}")
            convert_onnx_to_tflite(onnx_path, tflite_path)

    logging.info("Done!")


if __name__ == "__main__":
    main()
