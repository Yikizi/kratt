# kuule-kratt-v16b notes

**Status:** Wider-architecture v16 family comparison model.

## Evidence used

- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/docs/MODEL_LINEAGE.md`

## Data / config

- Positives: 2241
- Negatives: 10228
- Hard negatives: 0
- Ambient: 1002
- Architecture role: wider mixednet, residual OFF, SpecAug OFF
- Checkpoint objective in archived config: accuracy (`target_minimization: 0.0`)

## Observed role

Unified benchmark @0.995 reports FAPH CV 21.7, Rec Isa 100%, Rec Ode 91%,
HN Mac 93%, HN Isa 90%.

## Caveat

Good comparison point for width/residual trade-offs, but not the documented
active baseline.
