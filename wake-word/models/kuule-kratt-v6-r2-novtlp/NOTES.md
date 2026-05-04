# kuule-kratt-v6-r2-novtlp notes

**Status:** Side-branch control artifact; do not promote.

## Evidence used

- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/docs/POSITIVE_DATA_QUALITY_AUDIT_20260427.md`
- `wake-word/docs/MODEL_LINEAGE.md`

## Data / config

- Positives: 2241
- Negatives: 16803
- Hard negatives: 0
- Ambient: 1002

## Caveat

The positive-data audit lists this model among models not known to include
confirmed corrupt SSML/XTTS positives. That is a negative finding, not a full
proof that every source manifest is independently verified.

## Use

Side evidence for v6-era data/config controls only. Do not cite as a current
candidate.
