# kuule-kratt-v6-residual-novtlp notes

**Status:** Residual side-branch control artifact; do not promote.

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
confirmed corrupt SSML/XTTS positives. That does not make it a current candidate
or a fully revalidated manifest.

## Use

Side evidence for residual/no-VTLP controls only.
