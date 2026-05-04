# kuule-kratt-v6-residual-r4-exact notes

**Status:** Residual exact/control side branch; do not promote.

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
confirmed corrupt SSML/XTTS positives. The directory name suggests an exact
variant, but this note only claims what the archived summary/config can support.

## Use

Side evidence for exact/control residual behavior only.
