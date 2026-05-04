# kuule-kratt-v13a notes

**Status:** SpecAugment ablation baseline; not a deployment candidate.

## Evidence used

- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/docs/MODEL_LINEAGE.md`
- `wake-word/docs/research/session-findings-apr-2026.md`

## Data / config

- Positives: 3343
- Negatives: 17203
- Hard negatives: 0
- Ambient: 1002
- Architecture role: residual ON, SpecAug OFF
- Checkpoint objective in archived config: accuracy (`target_minimization: 0.0`)

## Observed role

Clean pair with v13b: same data, SpecAug OFF here and SpecAug ON in v13b.
Unified benchmark @0.995 reports FAPH CV 133.7, Rec Isa 85%, Rec Ode 45%,
HN Mac 87%, HN Isa 82%.

## Caveat

Use this as ablation evidence only. `session-findings-apr-2026.md` reports the
same ablation in a separate run context as FAPH 113.6 -> 75.6, so always keep
the source/report context with the exact number.
