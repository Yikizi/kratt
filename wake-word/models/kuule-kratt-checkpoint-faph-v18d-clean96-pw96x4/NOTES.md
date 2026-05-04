# kuule-kratt-checkpoint-faph-v18d-clean96-pw96x4

Created on HPC 2026-04-28; downloaded and benchmarked locally on 2026-04-29.

## Hypothesis

Use the v18d clean-positive 96-filter architecture, but select the exported checkpoint using an ambient-FAPH-oriented checkpoint objective rather than accuracy-first model selection.

## Delta

- Based on v18d clean-positive / 96-filter / residual configuration.
- `clip_duration_ms: 1500` in the downloaded training config.
- SpecAugment ON.
- `pointwise_filters: 96,96,96,96`.
- `target_minimization: 2.0`.
- `minimization_metric: ambient_false_positives_per_hour`.
- `maximization_metric: average_viable_recall`.

## Data summary

From `analysis/dataset_summary.json`:

- Positives: 1648
- Negatives: 11675
- Ambient clips: 1002 (~12.18h)

## Observed result

Benchmark source: `wake-word/evaluation/benchmark_checkpoint_models_20260429.md` and `wake-word/evaluation/benchmark_checkpoint_models_20260429_analysis.md`.

At threshold `0.995`:

- Rec Isa XTTS: 4.2%
- Rec friend1: 0.7%
- HN Mac FPR: 20.0%
- HN Isa FPR: 0.0%
- Prefix-only FPR: 67.3%
- Single-Kratt FPR: 30.6%
- `kuule/kule` confusable FPR: 24.5%
- FAPH CV ET: 1.31
- FAPH LibriSpeech: 0.89
- FAPH Mac background: 0.86
- FAPH DiPCo: 0.60

## Interpretation

This is an extreme low-FAPH checkpoint, but not a wake-word candidate. It appears to achieve low ambient false accepts mostly by becoming over-conservative; external positive recall collapses almost completely. It is therefore useful as evidence that FAPH-optimized checkpoint selection can overfit the checkpoint objective if unseen-speaker recall is not part of the selection criterion.

## Next step

Do not promote. Use as a negative/control result in checkpoint-selection discussion.
