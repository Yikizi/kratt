# kuule-kratt-v16a notes

**Status:** Low-FAPH v16 family comparison model.

## Evidence used

- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/docs/MODEL_LINEAGE.md`

## Data / config

- Positives: 2241
- Negatives: 10728
- Hard negatives: 0
- Ambient: 1002
- Architecture role: residual ON, SpecAug OFF
- Checkpoint objective in archived config: accuracy (`target_minimization: 0.0`)

## Observed role

Unified benchmark @0.995 reports FAPH CV 16.0, Rec Isa 100%, Rec Ode 91%,
HN Mac 100%, HN Isa 85%.

## Caveat

Strong historical FAPH/recall balance, but not the current active baseline. Use
v16c for the documented stable single-model baseline role.
