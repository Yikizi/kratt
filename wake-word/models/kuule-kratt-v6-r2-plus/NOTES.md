# kuule-kratt-v6-r2-plus notes

**Status:** Side-branch plus-positive artifact; do not promote.

## Evidence used

- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/docs/POSITIVE_DATA_QUALITY_AUDIT_20260427.md`
- `wake-word/docs/MODEL_LINEAGE.md`

## Data / config

- Positives: 2559
- Negatives: 16803
- Hard negatives: 0
- Ambient: 1002

## Caveat

The positive-data audit says this family likely includes extra Mac/XTTS/full-
command positives, but exact manifest evidence is pending. Treat the plus
branch as contaminated/uncertain until a manifest proves otherwise.

## Use

Side evidence for positive-source sensitivity only. Do not cite as clean model
evidence.
