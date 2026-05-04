# kuule-kratt-v17b notes

**Created:** 2026-04-26  
**Status:** Failed deploy candidate; retained as a data-quality incident marker.
**Metadata:** `analysis/dataset_summary.json`, `analysis/training_config_snapshot.json`, and `training_config.yaml` restored from HPC on 2026-05-03.

## Hypothesis

Variant of v17a intended to improve the recall/FAPH balance while keeping the
same broad `recall-cv` direction: expanded positives, broad negatives, and no
hard-negative overdose.

## Data / config

- Positives: 5307
- Negatives: 11675
- Ambient: 1002
- Training steps: 15000 + 5000
- SpecAug: ON in restored config (`freq_mask_count: [2]`, `time_mask_count: [2]`)
- Checkpoint objective: accuracy (`target_minimization: 0.0`, `maximization_metric: accuracy`)

## Observed result

Benchmark `wake-word/evaluation/benchmark_v17_full_20260426.csv` @0.995:

- Rec Isa: 100%
- Rec Ode: 91%
- Rec Mattias short: 100%
- Rec Friend1: 99%
- Hard neg Mac FPR: 100%
- Hard neg Isa FPR: 82%
- FAPH CV: 144
- FAPH LibriSpeech: 256
- FAPH MacBook bg: 140
- FAPH DiPCo: 50

v17b improved FAPH over v17a but retained the same hard-negative/prefix collapse.
Consensus `v17a + v17b` still had 100% Mac hard-negative FPR, showing correlated
errors.

## Root cause found after training

2026-04-27 manual listening confirmed positive-data corruption:

- SSML positive dirs contained Neurokõne reading XML tags aloud.
- Kule SSML mirror had the same failure.
- XTTS positive sources were full command prompts, not isolated wake phrase.
- Some very short Mattias clips were prefix-only/corrupt.

## Interpretation

v17b is not deployable. It demonstrates that adding more positive data can make
the model worse when the positive class violates the intended label semantics.

## Next step

Do not continue from v17b directly. Train a clean v18 after quarantining known-bad
positive sources and enforcing positive duration/source validation. See
`wake-word/docs/POSITIVE_DATA_QUALITY_AUDIT_20260427.md`.
