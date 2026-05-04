# kuule-kratt-ex3b notes

**Status:** Expert-family benchmark artifact.

## Evidence used

- Local model directory contents
- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/docs/MODEL_LINEAGE.md`

## Data / config

- Positives: 1490
- Negatives: 9560
- Hard negatives: 0
- Ambient: 1002
- Training steps: 10000
- SpecAug: OFF in restored config (`freq_mask_count: [0]`, `time_mask_count: [0]`)
- Checkpoint objective: accuracy (`target_minimization: 0.0`, `maximization_metric: accuracy`)

## Observed role

Unified benchmark @0.995 reports FAPH CV 175.1, FAPH LS 133.8, FAPH DiPCo
30.7, Rec Isa 100%, Rec Ode 64%, Rec Mattias 99%, HN Mac 93%, HN Isa 98%.

## Caveat

Do not promote as a current candidate; use as expert-family comparison evidence.
