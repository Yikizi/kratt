# Positive data quality audit — SSML/XTTS corruption (2026-04-27)

## Summary

The v17 training round exposed a failure mode where the model triggers on the
single prefix words **"kuule"** / **"kule"**. Manual listening and duration/hash
audits found that the positive class was partially corrupted: several sources
labelled as wake-word positives did **not** contain a clean isolated wake phrase.

This is now treated as a data-quality incident, not merely a model architecture
problem.

## Confirmed bad positive sources

These directories must not be used for deploy-candidate training:

| Source | Problem | Evidence |
|---|---|---|
| `data/processed/positive_tts_ssml` | Neurokõne read XML/SSML tags aloud | 972 clips, median ~7.39s, max ~13.87s |
| `data/raw/neurokone_ssml_positives` | Same corrupt SSML audio as processed copy | exact duplicates with `positive_tts_ssml` |
| `data/raw/neurokone_ssml_kule` | Kule mirror of corrupt SSML prompt | 969 clips, median ~7.41s, max ~13.68s |
| `data/raw/xtts_clones/{marta,annam,ema}/positive` | Full command prompts, not isolated wake phrase | median ~3s; contains command tails |
| `data/raw/xtts_clones/{marta,annam,ema}/positive_16k` | Still not accepted as clean after listening; treat as unvalidated full-sentence crop | requires manual segmentation before use |
| `data/raw/mattias-short/positive` very short tail | Some ~0.42s clips contain only prefix/corrupt audio | filtered by duration gate |

The SSML scripts have been deprecated and now refuse to run unless an explicit
forensic flag is supplied:

- `data/collection/generate_neurokone_ssml_positives.py --allow-legacy-xml-text`
- `data/collection/generate_kule_ssml_mirror.py --allow-legacy-xml-text`

## Why this matters

microWakeWord trains on fixed windows (`clip_duration_ms`, historically 1500ms).
If a positive source is longer than the wake phrase or contains non-wake content,
random/windowed training can label the following as positive:

- only `kuule` / `kule`,
- only `kratt`,
- an XML tag being spoken,
- a command tail after the wake phrase,
- filler such as `no/ee/noh kuule...`.

The resulting binary classifier is then rewarded for detecting the prefix rather
than the full two-word sequence **"Kuule Kratt"**.

## Affected model inventory

Confirmed or highly likely affected deploy/experiment artifacts:

| Group | Models | Contamination type |
|---|---|---|
| Mainline SSML era | `v7`, `v8`, `v9`, `v10`, `v11`, `v12`, `v13a`, `v13b`, `v14` | corrupt SSML positives; v8+ also used XTTS/Mac expanded positives |
| Side/ablation SSML-era | `v6-specaug`, `expert-b`, `confusable-filter-v1` | v8/current-era positive set with corrupt SSML and/or raw XTTS positives |
| v17 incident | `v17a`, `v17b` | corrupt SSML + Kule SSML + raw/full XTTS + short-prefix positives |
| Likely XTTS/full-command affected, manifest pending | `v6-r2`, `v6-r2-plus`, `v6-residual-plus` | positive count suggests extra Mac/XTTS/Mattias positives; exact source manifest pending |

Models not known to include the confirmed corrupt SSML/XTTS positives:

- `v1`–`v6`, `v6-residual`, `v6-r2-novtlp`, `v6-residual-novtlp`,
  `v6-residual-r3`, `v6-residual-r4-exact`
- `v15`, `v16a`, `v16b`, `v16c`, `expert-a`

Caveat: `processed/positive_tts` itself contains casual variants such as
`Kule Kratt`, `Kuuule/Kuulee Kratt`, and filler-prefix prompts (`Ee/No/Noh kuule
Kratt`). These are not the XML-readout corruption, but they are still a policy
choice and should be separated if the target wake phrase must be exact.

## Guard rails added

### Training prep quality gates

`training/scripts/prepare_kuule_kratt_experiment.py` now supports:

- `--exclude-positive-wav-dirs`: quarantine entire known-bad positive dirs.
- `--positive-min-duration-s`: drop suspiciously short positive clips.
- `--positive-max-duration-s`: drop suspiciously long positive clips.

The manifest records:

- positive source dirs,
- candidate count,
- exclusions by path,
- exclusions by duration,
- examples of duration-rejected clips.

### HPC submit defaults

`training/scripts/submit_hpc_kuule_kratt.sh` now quarantines known-bad positive
sources by default and applies a positive duration filter. `submit_hpc_openwakeword.sh`
uses the same known-bad positive quarantine for its staging preflight.

- min duration: `0.80s` (raised after 2026-04-28 STT audit of `mattias-short` clips; <0.80s were prefix/tail/empty, not full wake phrase)
- max duration: `4.00s`

Known-bad positives can only be re-enabled with:

```bash
--allow-known-bad-positives
```

This flag is for historical reproduction only, not for deploy candidates.

### Positive windowing hardening

`training/scripts/generate_microwakeword_mmaps.py` no longer random-crops overlong
positive clips by default. Historical random positive cropping can be re-enabled
with `--positive-truncate-randomly`, but deploy-candidate runs should keep it
off. Random cropping positives was dangerous because it could turn a long
positive prompt into a prefix-only positive training window.

### Feature cache stamp hardening

`training/scripts/train_microwakeword_experiment.sh` now includes source directory
fingerprints, augmentation resource settings, and a schema version in the mmap
cache stamp. This reduces the risk of silently reusing stale feature mmaps when
the source file list or feature generation logic changes.

### Audit tool

Use this before any new training run:

```bash
cd wake-word
uv run python data/validation/audit_positive_sources.py \
  data/processed/positive_tts \
  data/raw/mattias/positive \
  data/raw/mattias-short/positive
```

`mattias-short` is expected to report some short clips; the training prep duration
gate filters them. Use `--fail-on-suspicious` only for directories that should
already be fully curated.

## Current clean-positive policy for next deploy candidates

Allowed by default:

- real Korvo-2 `mic1`/`mic2` positives,
- `data/processed/positive_tts` after audit (plain TTS, not SSML),
- manually listened real Mattias Mac positives,
- manually listened `mattias-short` positives after duration filtering (currently require >=0.80s unless manually whitelisted),
- tiny direct `kule_vs_kuule_test` only if the target policy intentionally
  accepts the full phrase "Kule Kratt" as a casual pronunciation variant.

Disallowed until separately fixed/segmented:

- all SSML-generated positives,
- XTTS full-sentence positives,
- any positive shorter than the duration gate unless manually whitelisted.

## Required next step before v18

Before training v18, run a dry-run and inspect the positive counts/exclusions:

```bash
wake-word/training/scripts/submit_hpc_kuule_kratt.sh \
  --dry-run \
  --tag v18-clean \
  --dataset-preset recall-cv \
  --recall-profile
```

Then verify the real HPC `manifest.json` after prep before trusting benchmark
results.

## Follow-up: v18 clean-positive training result (2026-04-28)

The overnight v18 pack used the new strict generated positive set and quarantined the known-bad SSML/XTTS positives. This was a necessary data-quality fix, but it did **not** by itself produce a deployable model.

Benchmark source: `wake-word/evaluation/benchmark_v18_clean_20260428_0214.md`.

Key single-model results at threshold `0.995`:

| model | Rec Isa | prefix-only FPR | single-Kratt FPR | confusable FPR | FAPH CV | verdict |
|---|---:|---:|---:|---:|---:|---|
| `v18a-clean48` | 100% | 97% | 99.5% | 99% | 515 | fail |
| `v18b-clean48-sa` | 96% | 100% | 98% | 99% | 132 | fail alone |
| `v18c-clean48-hn` | 31% | 82% | 100% | 94% | 85 | recall collapse |
| `v18e-clean48-tts-hn` | 75% | 85% | 99.5% | 89% | 356 | recall/FAPH fail |

Interpretation update: the v17 root cause remains a positive-data incident, but fixing positives alone does not force exact two-word selectivity. Future training needs explicit partial/confusable negative controls and independent holdouts.
