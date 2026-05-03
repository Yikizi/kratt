# Negative data split plan for scaled Kratt runs (2026-04-29)

> **Status:** optional / future-work plan. Do not start broad scaled-negative training before user-test and thesis-writing critical path is safe. Current priority is `docs/PROJECT_TODO.md`.

Purpose: use available large negative corpora without leaking final FAPH/test audio
into training, checkpoint selection, threshold tuning, or augmentation.

## Why not put everything into `negative_samples/`?

Wake-word training needs three different negative roles:

1. **Training negatives** — teach the model ordinary non-wake audio.
2. **Checkpoint/dev ambient** — choose `best_weights` and deployment thresholds.
3. **Final FAPH/test sets** — report thesis numbers once, without tuning on them.

The same audio must not serve more than one of these roles for a final claim.
This includes not using final FAPH files as background-noise augmentation.

## Split policy

### Common Voice ET

Keep the historical final set frozen:

- final: seeded CV ET indices `5000..6999` (`faph_cv_et`, existing thesis anchor)
- dev/checkpoint: seeded indices `7000..8999`
- train: all remaining converted CV ET WAVs, excluding target-token transcripts

This unlocks the currently unused CV ET tail while preserving comparability with
old v1--v18 benchmarks.

### MUSAN

- `noise`: keep as training/checkpoint ambient and background augmentation resource.
- `speech`: split into train/dev/eval.
- `music`: split into train/dev/eval.

MUSAN is useful for robustness, but it is not a substitute for Estonian speech.
Report MUSAN eval as secondary FAPH, not the primary Estonian result.

### VOiCES

Split into train/dev/eval by deterministic file list unless session/room metadata
is available. VOiCES is valuable for far-field/reverberant/noisy speech and should
be a secondary robustness benchmark. It is mostly not Estonian, so it should not
replace Estonian radio/podcast negatives.

### Riigikogu

Split by audio file. Prefer whole-file splits to avoid adjacent chunks from the
same speech landing in train and test. Use only a bounded subset if feature
generation becomes too slow.

### Estonian podcasts/radio

Highest-value missing negative source. Split by **episode**, not by short clip,
so the same programme/episode does not leak into train and final FAPH. Use:

- train episodes: model training negatives;
- dev episodes: threshold/checkpoint tuning;
- final episodes: thesis FAPH by real Estonian broadcast/podcast speech.

## Tooling added

Materialize split directories on HPC:

```bash
kratt prepare-negative-splits scaled-v1 --dry-run
kratt prepare-negative-splits scaled-v1 --force \
  --convert-lossy \
  --podcast-root /gpfs/mariana/smbhome/malinh/kratt-data/datasets/estonian-podcasts
```

This creates:

```text
$KRATT_DATA/processed/external_negative_splits/scaled-v1/
  train_negatives/
  checkpoint_ambient/
  eval/
  manifest.json
```

Use the split in one training run by disabling automatic all-source duplicates and
passing the materialized train/dev dirs explicitly:

```bash
kratt train v19-scaled --steps 15000,5000 \
  --dataset-preset recall-cv \
  --negative-limit -1 \
  --no-musan \
  --no-riigikogu \
  --extra-negative-dirs /gpfs/mariana/smbhome/malinh/kratt-data/processed/external_negative_splits/scaled-v1/train_negatives \
  --extra-ambient-dirs /gpfs/mariana/smbhome/malinh/kratt-data/processed/external_negative_splits/scaled-v1/checkpoint_ambient \
  --recall-profile \
  --pointwise-filters 96,96,96,96 \
  --target-minimization 10 \
  --time 08:00:00
```

## Guardrails

- Do not train on `eval/` directories.
- Do not use `eval/` directories as augmentation resources.
- Use `checkpoint_ambient/` for checkpoint/threshold/dev decisions only.
- Keep `faph_cv_et` frozen as the legacy final Estonian FAPH anchor.
- Treat any threshold sweep on final sets as exploratory, not as the selected
  operating point.

## Thesis framing

If the scaled run succeeds, compare it to v16c/v18 as a **data-scale diagnostic**,
not as an open-ended new model search. If it fails or is time-boxed out, report the
split manifest and the unused-data gap as a limitation/future-work item.
