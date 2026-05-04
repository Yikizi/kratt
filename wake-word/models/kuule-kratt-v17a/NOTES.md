# kuule-kratt-v17a notes

**Created:** 2026-04-26  
**Status:** Failed deploy candidate; retained as a data-quality incident marker.
**Metadata:** `analysis/dataset_summary.json`, `analysis/training_config_snapshot.json`, and `training_config.yaml` restored from HPC on 2026-05-03.

## Hypothesis

A high-recall `recall-cv` preset with broader general negatives and CV sentences
containing `kuule` should reduce prefix-only false triggers while maintaining
unseen-speaker recall.

## Delta from v16 family

- Expanded positives with SSML/Kule/Mattias/XTTS sources.
- Broad general/mined negatives, no large hard-negative feature set.
- CV exclusion changed to exclude `kratt` but not `kuule`, intending to teach
  that `kuule` alone is ordinary speech.

## Data / config

- Positives: 5307
- Negatives: 11675
- Ambient: 1002
- Training steps: 15000 + 5000
- SpecAug: OFF in restored config (`freq_mask_count: [0]`, `time_mask_count: [0]`)
- Checkpoint objective: accuracy (`target_minimization: 0.0`, `maximization_metric: accuracy`)

## Observed result

Benchmark `wake-word/evaluation/benchmark_v17_full_20260426.csv` @0.995:

- Rec Isa: 100%
- Rec Ode: 82%
- Rec Mattias short: 99%
- Rec Friend1: 96%
- Hard neg Mac FPR: 100%
- Hard neg Isa FPR: 95%
- FAPH CV: 190
- FAPH LibriSpeech: 334
- FAPH MacBook bg: 206
- FAPH DiPCo: 112

The model strongly over-triggered and was reported live to trigger on `kuule` /
`kule` alone.

## Root cause found after training

2026-04-27 manual listening confirmed positive-data corruption:

- SSML positive dirs contained Neurokõne reading XML tags aloud.
- Kule SSML mirror had the same failure.
- XTTS positive sources were full command prompts, not isolated wake phrase.
- Some very short Mattias clips were prefix-only/corrupt.

This means v17a was trained with positive labels that did not consistently mean
"full two-word wake phrase".

## Interpretation

v17a is useful evidence that positive label purity and temporal alignment are
first-order constraints. It is not a model to deploy.

## Next step

Train v18 only after applying the positive-data guard rails documented in
`wake-word/docs/POSITIVE_DATA_QUALITY_AUDIT_20260427.md`.
