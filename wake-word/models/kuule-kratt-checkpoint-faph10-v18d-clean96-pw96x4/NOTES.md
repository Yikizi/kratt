# kuule-kratt-checkpoint-faph10-v18d-clean96-pw96x4

Created on HPC 2026-04-28. SLURM job `922050` timed out before TFLite export, but `best_weights.weights.h5` existed. Exported manually with HPC job `922275` on 2026-04-29.

## Hypothesis

Use the v18d clean-positive 96-filter architecture, but select checkpoints with a corrected FAPH-oriented checkpoint objective (`target_minimization: 10.0`) instead of the previous accuracy-biased selection.

## Delta

- Based on v18d clean-positive / 96-filter / residual configuration.
- `clip_duration_ms: 2000`.
- SpecAugment ON.
- `pointwise_filters: 96,96,96,96`.
- `target_minimization: 10.0`.
- `minimization_metric: ambient_false_positives_per_hour`.
- `maximization_metric: average_viable_recall`.

## Data summary

Training config snapshot is in `training_config.yaml`. The run uses the strict clean-positive flow and broad negatives from the v18d family.

## Observed result

Benchmark source: `wake-word/evaluation/benchmark_checkpoint_models_20260429.md` and `wake-word/evaluation/benchmark_checkpoint_models_20260429_analysis.md`.

At threshold `0.995`:

- Rec Isa XTTS: 72.9%
- Rec friend1: 22.1%
- HN Mac FPR: 80.0%
- HN Isa FPR: 35.0%
- Prefix-only FPR: 58.6%
- Single-Kratt FPR: 86.0%
- `kuule/kule` confusable FPR: 85.8%
- FAPH CV ET: 4.19
- FAPH LibriSpeech: 3.02
- FAPH Mac background: 9.42
- FAPH DiPCo: 0.60

Consensus with `v16c` at `0.995` reduces ambient FAPH strongly (CV 0.26, LS/Mac/DiPCo 0), but still has weak friend1 recall (20.7%) and high prefix/confusable FPR.

## Interpretation

The corrected checkpoint objective successfully selects a much lower-FAPH model than the original v18d, but the model is not deployable: real-speaker recall is poor and phrase selectivity is still weak. This is useful as a diagnostic result showing that FAPH-only checkpoint selection is not enough; unseen-speaker recall and prefix/confusable rejection must be part of model selection.

## Next step

Do not promote as production candidate. If this line is continued, checkpoint selection needs a composite validation objective: ambient FAPH + real/unseen-speaker recall + held-out prefix/confusable negatives.
