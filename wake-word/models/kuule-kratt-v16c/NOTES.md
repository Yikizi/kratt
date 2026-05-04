# kuule-kratt-v16c notes

**Status:** Stable single-model baseline / active-demo candidate, not production-proven.

## Evidence used

- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/docs/MODEL_LINEAGE.md`

## Data / config

- Positives: 2241
- Negatives: 10228
- Hard negatives: 0
- Ambient: 1002
- Architecture role: widest v16 mixednet, residual ON, SpecAug OFF
- Checkpoint objective in archived config: accuracy (`target_minimization: 0.0`)

## Observed role

Unified benchmark @0.995 reports FAPH CV 75.1, Rec Isa 100%, Rec Ode 82%,
HN Mac 100%, HN Isa 87%. `MODEL_LINEAGE.md` currently treats it as the stable
single-model baseline / active-demo candidate.

## Caveat

Not production-ready exact-phrase detection. Later v17/v18/checkpoint tests
showed unresolved prefix/confusable phrase-selectivity problems.
