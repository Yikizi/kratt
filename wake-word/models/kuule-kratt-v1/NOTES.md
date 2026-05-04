# kuule-kratt-v1 notes

**Status:** Historical baseline only.

## Evidence used

- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/docs/MODEL_LINEAGE.md` unified 2026-04-21 benchmark table

## Data / config

- Positives: 915
- Negatives: 3928
- Ambient: 930
- Training steps: 10000
- Checkpoint objective in archived config: accuracy (`target_minimization: 0.0`)

## Observed role

First archived `kuule-kratt` baseline. Benchmark @0.995 reports FAPH CV 343.1,
Rec Isa 67%, Rec Ode 64%, HN Mac 27%, HN Isa 72%.

## Caveat

Do not use old contaminated pre-audit numbers as current evidence. This model is
only useful as the starting point for the lineage story.
