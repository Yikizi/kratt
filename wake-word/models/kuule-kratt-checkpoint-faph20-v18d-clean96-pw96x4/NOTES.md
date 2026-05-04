# kuule-kratt-checkpoint-faph20-v18d-clean96-pw96x4

Created on HPC 2026-04-29 as SLURM job `922280`; completed in 4:50:17 on partition `common` and downloaded locally the same day.

## Hypothesis

Use the v18d clean-positive 96-filter architecture, but relax the FAPH-oriented checkpoint target from `10.0` to `20.0` to test whether external recall improves before ambient false accepts become unacceptable.

## Delta

- Based on v18d clean-positive / 96-filter / residual configuration.
- `clip_duration_ms: 2000`.
- SpecAugment ON.
- `pointwise_filters: 96,96,96,96`.
- `target_minimization: 20.0`.
- `minimization_metric: ambient_false_positives_per_hour`.
- `maximization_metric: average_viable_recall`.

## Data summary

Training config is archived in `training_config.yaml`; microWakeWord analysis config is in `analysis/training_config_snapshot.json`.

Downloaded analysis summary:

- Positives: 1185
- Negatives: 11675
- Ambient clips: 1002 (~12.18h)
- TFLite size: 158KB

## Observed result

Benchmark sources:

- `wake-word/evaluation/benchmark_checkpoint_faph20_20260429.md`
- `wake-word/evaluation/benchmark_checkpoint_faph20_20260429_analysis.md`
- `wake-word/evaluation/positive_recall_probe_checkpoint_faph20_20260429.md`

At threshold `0.995`:

- Rec Isa XTTS: 72.9%
- Rec Friend1: 42.1%
- Rec Ode: 90.9%
- Rec Mattias short: 81.5%
- HN Mac FPR: 46.7%
- HN Isa FPR: 61.7%
- Prefix-only FPR: 73.2%
- Single-Kratt FPR: 95.2%
- `kuule/kule` confusable FPR: 78.3%
- FAPH CV ET: 23.29
- FAPH LibriSpeech: 8.00
- FAPH Mac background: 52.24
- FAPH DiPCo: 3.01

Consensus with `v16c` at `0.995` reduced ambient FAPH strongly (CV 0.52; LS/Mac/DiPCo 0), but still had weak Friend1 recall (40.0%) and high confusable FPR (78.2%).

## Interpretation

Relaxing checkpoint target from 10 to 20 restored some real-speaker recall (`Friend1` 22.1% → 42.1%) but not enough to make the model deployable. The cost was substantial ambient FAPH regression (`CV` 4.19 → 23.29; `Mac bg` 9.42 → 52.24 at threshold 0.995). Phrase selectivity remains unsolved: the model still fires on most prefix-only and `kuule/kule <not kratt>` confusable examples.

This is a useful Pareto-boundary diagnostic, not a production candidate.

## Next step

Do not promote as a deployment model. Use the checkpoint-FAPH series in the thesis as evidence that checkpoint/model selection must optimize a composite objective: ambient FAPH + real/unseen-speaker recall + held-out prefix/confusable rejection.
