# kuule-kratt-v6-residual notes

**Status:** Historical low-FAPH anchor; not deployable alone.

## Evidence used

- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/docs/MODEL_LINEAGE.md`
- `wake-word/docs/research/session-findings-apr-2026.md`

## Data / config

- Positives: 2241
- Negatives: 10228
- Hard negatives: 0
- Ambient: 1002
- Architecture role: v6 with residual ON

## Observed role

Session findings recorded the residual ablation as a major FAPH improvement
over v6. Unified benchmark @0.995 reports FAPH CV 14.4, Rec Isa 100%,
Rec Ode 91%, HN Mac 100%, HN Isa 73%.

## Caveat

This is a low-FAPH diagnostic anchor, not a practical single model, because hard
negative / phrase-selectivity behavior remains unacceptable.
