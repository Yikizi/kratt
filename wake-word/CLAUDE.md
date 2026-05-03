# wake-word/

Core contribution: "Kuule Kratt" wake-word model training and evaluation.

## Structure

```
wake-word/
├── data/collection/            # Recording scripts, TTS generation, augmentation
├── data/validation/            # Positive/source audits, strict-positive and regression builders
├── training/
│   ├── scripts/                # Train, generate mmaps, HPC submit scripts
│   └── configs/                # Training YAML configs (openWakeWord, microwakeword)
├── models/                     # Versioned trained models
│   ├── kuule-kratt-v1..v18*/    # Historical + diagnostic microWakeWord models
│   ├── kuule-kratt-checkpoint-* # checkpoint-FAPH diagnostic exports
│   └── openwakeword/            # openWakeWord experiments
├── evaluation/                 # Benchmarks, live testing, fuzzer, reports
│   ├── benchmark_all_models.py  # Main multi-model benchmark runner
│   ├── test_sets.py            # Held-out / diagnostic test set registry
│   ├── multi_model_live_test.py # Parallel multi-model live/shadow testing
│   └── fpr_logs/               # Historical false-positive rate logs
├── docs/                       # Model lineage, data timeline, audit reports
├── DATA_STRATEGY.md            # Current data sourcing / quality policy
└── README.md                   # Setup and usage instructions
```

## Key facts (updated 2026-04-29)

- Wake word: **"Kuule Kratt"** / practical variant **"Kule Kratt"** — exact two-word phrase, not just `kuule`, `kule`, or `kratt`.
- Framework: microWakeWord (TFLite INT8 for ESP32); openWakeWord remains experimental/comparative.
- Current stable single-model baseline / active demo candidate: **`v16c`**.
- v17/v18/checkpoint runs are **diagnostic**, not final deploy candidates:
  - v17 exposed positive-label corruption.
  - v18 showed clean positives are necessary but not sufficient.
  - checkpoint-FAPH showed ambient-FAPH checkpointing can collapse recall.
- Final evaluation must report **FAPH + real/unseen-speaker recall + hard/prefix/confusable FPR** together at frozen thresholds.
- User-test audio collection is now the critical path; use `kratt user-test` and `docs/user-testing/ten-minute-shadow-demo-protocol.md`.

## Critical rules

- Same mic should appear in BOTH positive and negative classes (mic symmetry).
- Only exact `kuule/kule kratt` phrase variants are valid positive labels.
- Neurokõne is deterministic — always dedup generated samples.
- Known-bad SSML/XML and full-command XTTS positive sources are quarantined by default.
- Prefix-only, single-word, reversed-order, and confusable phrases are negatives / regression controls.
- Never rm -rf data dirs; generate alongside, let the user decide.
- Do not train on user-test audio before final evaluation unless the thesis explicitly separates train/test usage.

## Dev workflow

```bash
# Environment
(cd wake-word && uv sync)

# Live model test (v16c as stable baseline example)
./cli/kratt live v16c 0.997

# Multi-model / consensus live test
(cd wake-word && uv run python evaluation/multi_model_live_test.py --models expert-a expert-b2 --thresholds 0.996 0.996)

# Full benchmark subset
(cd wake-word && uv run python evaluation/benchmark_all_models.py --models v16c expert-a expert-b2)

# Generate training features / submit HPC job (only if thesis schedule allows)
(cd wake-word && uv run python training/scripts/generate_microwakeword_mmaps.py)
./cli/kratt train v19a --dataset-preset recall-cv --dry-run

# User-test labelled recorder
./cli/kratt user-test P01 --active-model v16c --new-session-subdir
```
