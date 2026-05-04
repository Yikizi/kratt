# kuule-kratt-v13b notes

**Status:** SpecAugment ablation pair with v13a; not a deployment candidate.

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
- Architecture role: residual ON, SpecAug ON
- Checkpoint objective in archived config: accuracy (`target_minimization: 0.0`)

## Observed role

Clean pair with v13a: same data, SpecAug ON here and SpecAug OFF in v13a.
Unified benchmark @0.995 reports FAPH CV 87.7, Rec Isa 69%, Rec Ode 73%,
HN Mac 67%, HN Isa 22%.

## Caveat

Use this as ablation evidence only. `session-findings-apr-2026.md` reports the
same ablation in a separate run context as FAPH 113.6 -> 75.6, so always keep
the source/report context with the exact number.
