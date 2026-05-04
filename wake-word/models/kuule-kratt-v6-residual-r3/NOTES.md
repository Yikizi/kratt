# kuule-kratt-v6-residual-r3 notes

**Status:** Residual rerun/control side branch; do not promote.

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
confirmed corrupt SSML/XTTS positives. That is not the same as a full current
benchmark endorsement.

## Use

Side evidence for residual rerun/control behavior only.
