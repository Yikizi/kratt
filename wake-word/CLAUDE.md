# wake-word/

Core contribution: "Kuule Kratt" wake word model training and evaluation.

## Structure

```
wake-word/
├── data/collection/            # Recording scripts, TTS generation, augmentation
├── training/
│   ├── scripts/                # Train, generate mmaps, HPC submit scripts
│   └── configs/                # Training YAML configs (openwakeword, microwakeword)
├── models/                     # Versioned trained models
│   ├── kuule-kratt-v1..v16c/    # Each: .tflite + analysis/dataset_summary.json
│   └── hpc-smoke-marvin*/      # Smoke test models (marvin keyword)
├── evaluation/                 # Benchmarks, live testing, fuzzer
│   ├── live_test_tflite.py     # Real-time mic evaluation with sliding-window
│   ├── compare_models.py       # Side-by-side model comparison
│   ├── deterministic_trigger_fuzzer.py  # Reproducible threshold fuzzing
│   ├── test_sets.py            # Held-out test set definitions
│   └── fpr_logs/               # Historical false-positive rate logs
├── docs/                       # Bibliography tracker, sanity check notes
├── DATA_STRATEGY.md            # Data sourcing decisions
└── README.md                   # Setup and usage instructions
```

## Key facts

- Wake word: "Kuule Kratt" (two words, not just "Kratt")
- Framework: microWakeWord (TFLite INT8 for ESP32)
- Current best: **v16c** (148KB, 100% recall, 100% hard neg rejection, FAPH 75) + MoE consensus (Expert A + Expert B2) achieves sub-1 FAPH (0.79) at 0.996/0.996
- Training: TalTech HPC cluster (SLURM), scripts in training/scripts/
- Evaluation metric: FAPH (False Accepts Per Hour) at fixed threshold
- Positive data: real recordings + Neurokone TTS + XTTS voice clones
- Negative data: Riigikogu speech, Google Speech Commands, ambient recordings

## Critical rules

- Same mic must appear in BOTH positive and negative classes (mic symmetry)
- Only "Kuule Kratt" is a valid positive label (not just "Kratt")
- Neurokone is deterministic — always dedup generated samples
- Never rm -rf data dirs; generate alongside, let user decide

## Dev workflow

```bash
# Environment
(cd wake-word && uv sync)

# Live model test (v16c as example)
(cd wake-word && uv run python evaluation/live_test_tflite.py models/kuule-kratt-v16c/kuule_kratt_v16c.tflite)

# MoE consensus test
(cd wake-word && uv run python evaluation/multi_model_live_test.py --models expert-a expert-b2 --thresholds 0.996 0.996)

# Generate training features
(cd wake-word && uv run python training/scripts/generate_microwakeword_mmaps.py)

# Submit HPC job
(cd wake-word/training/scripts && bash submit_hpc_kuule_kratt.sh)
```
