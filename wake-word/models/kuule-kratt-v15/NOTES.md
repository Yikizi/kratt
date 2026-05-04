# kuule-kratt-v15 notes

**Status:** Historical benchmark-vs-field mismatch marker.

## Evidence used

- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/docs/MODEL_LINEAGE.md`
- `wake-word/docs/research/session-findings-apr-2026.md`

## Data / config

- Positives: 2241
- Negatives: 11728
- Hard negatives: 0
- Ambient: 1002
- Architecture role: residual ON, SpecAug OFF
- Checkpoint objective in archived config: accuracy (`target_minimization: 0.0`)

## Observed role

Unified benchmark @0.995 reports FAPH CV 242.9, Rec Isa 98%, Rec Ode 64%,
HN Mac 27%, HN Isa 88%. Session findings recorded it as worst on benchmark but
best in a MacBook field-style balance test: about 73% recall and 20% hard-neg
FPR.

## Caveat

Do not cite this as "best model" without saying which evaluation context is in
scope. Its value is the benchmark-vs-field mismatch lesson.
