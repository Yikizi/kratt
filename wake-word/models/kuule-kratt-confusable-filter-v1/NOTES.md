# kuule-kratt-confusable-filter-v1 notes

**Status:** Diagnostic filter experiment with contaminated-input caveat; do not promote.

## Evidence used

- `analysis/dataset_summary.json`
- `analysis/training_config_snapshot.json`
- `wake-word/docs/POSITIVE_DATA_QUALITY_AUDIT_20260427.md`
- `wake-word/docs/MODEL_LINEAGE.md`

## Data / config

- Positives: 3385
- Negatives: 8637
- Ambient: 1002
- Training steps: 15000 + 5000
- Checkpoint objective in archived config: accuracy

## Caveat

The positive-data audit lists this as a side/ablation SSML-era model affected by
v8/current-era positives with corrupt SSML and/or raw XTTS positives.

## Use

Use only as diagnostic evidence that confusable filtering needed stricter data
governance. Do not cite as clean benchmark-best or deployable model evidence.
