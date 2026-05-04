# kuule-kratt-expert-b notes

**Status:** Superseded verifier prototype; contaminated-input caveat.

## Evidence used

- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/evaluation/model_evaluation_results.json`
- `wake-word/docs/POSITIVE_DATA_QUALITY_AUDIT_20260427.md`
- `wake-word/docs/MODEL_LINEAGE.md`

## Data / config

- Positives: 3343
- Negatives: 4045
- Hard negatives: 0
- Ambient: 1002
- Evaluation-record role: mixednet 4x48f residual, SpecAug ON verifier prototype
- Training steps: 10000
- Checkpoint objective: accuracy (`target_minimization: 0.0`, `maximization_metric: accuracy`)

## Observed role

Unified benchmark @0.995 reports FAPH CV 8766.8, FAPH LS 9054.2, FAPH DiPCo
2433.8, Rec Isa 100%, Rec Ode 100%, Rec Mattias 98%, HN Mac 100%, HN Isa 82%.
`model_evaluation_results.json` marks it as superseded by expert-b2.

## Caveat

The positive-data audit lists expert-b among SSML-era side/ablation models
affected by corrupt SSML and/or raw XTTS positives. Do not use as clean model
evidence.
