# kuule-kratt-v6-r2 notes

**Status:** Side-branch artifact with snapshot ambiguity; do not promote.

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

The archived training config points at a `kuule-kratt-v6-r2-plus` features path,
so this directory has alias/snapshot ambiguity. The positive-data audit says
this family likely includes extra Mac/XTTS/full-command positives, but exact
manifest evidence is pending.

## Use

Side evidence for data/config sensitivity only. Do not cite as a clean
benchmark-best or deployment candidate.
