# kuule-kratt-v14 notes

**Status:** Historical ablation / benchmark comparison model.

## Evidence used

- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/docs/MODEL_LINEAGE.md`

## Data / config

- Positives: 3343
- Negatives: 11204
- Hard negatives: 0
- Ambient: 1002
- Architecture role: residual OFF, SpecAug ON
- Checkpoint objective in archived config: accuracy (`target_minimization: 0.0`)

## Observed role

Reduced negative-pool / SpecAug ON branch. Unified benchmark @0.995 reports
FAPH CV 109.7, Rec Isa 100%, Rec Ode 91%, HN Mac 100%, HN Isa 75%.

## Caveat

This is a useful comparison point, not a current recommended model. Later v16
family and v17/v18 diagnostics changed the interpretation of what "good" means.
