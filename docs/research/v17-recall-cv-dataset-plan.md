# v17 recall-cv dataset plan

> **Superseded / historical (2026-04-29):** v17a/v17b were run and then failed the prefix/confusable checks. The follow-up audit found corrupt SSML/XML and full-command positive sources. Keep this file as the pre-run design record, not as current training guidance. Current guidance lives in `docs/PROJECT_TODO.md`, `docs/research/source-of-truth-apr-2026.md`, `wake-word/DATA_STRATEGY.md`, and `wake-word/docs/MODEL_LINEAGE.md`.

**Status:** historical implementation plan + script validation notes  
**Purpose:** define the original pre-user-test training sprint for a model that prioritized high real wake recall and low general Estonian speech FAPH, without over-optimizing on large hard-negative corpora.

## Motivation

The current candidates expose a deployment gap:

- `expert-a` has strong Android field FAPH and recall, but can trigger on prefix-only `kuule`, which is not acceptable UX.
- `v16c` is safer as a full-phrase candidate, but its CV ET FAPH is not competitive enough for a mission-critical false-trigger metric.
- Earlier hard-negative-heavy runs show that small microWakeWord models can become confused when large confusable corpora dominate training.

The v17 sprint therefore changes the objective:

> learn `Kuule Kratt` and `Kule Kratt` as valid wake variants, while minimizing false accepts on broad continuous speech and real mined false-trigger patterns. Avoid large hard-negative feature sets.

## High-level training objective

Primary objective:

- reduce `faph_cv_et` while preserving high positive recall.

Required qualitative behavior:

- should not trigger on prefix-only `kuule`;
- should not trigger on acoustic nuisances already observed in Android/Mac mined false accepts;
- may be imperfect on `kuule rott`-style hard negatives if the recall/FAPH trade-off is better overall.

## New dataset preset

Implemented preset:

```bash
--dataset-preset recall-cv
```

Main properties:

- includes both `kuule kratt` and `kule kratt` positives;
- includes broad general negatives;
- includes Android/Mac mined false accepts;
- excludes the canonical CV FAPH test set by resolved path;
- excludes `kratt` from CV negative transcripts, but **does not exclude `kuule`**;
- disables separate hard-negative feature set;
- disables folded hard-negative corpora;
- disables TTS hard negatives;
- disables CV-OHEM mined negatives by default to avoid poisoning `faph_cv_et`.

## Positive data included

The preset passes these positive source directories to `prepare_kuule_kratt_experiment.py`.
The prep script now scans positive dirs recursively, so nested speaker folders are included.

| Source | Role | Local WAV count observed | Notes |
|---|---:|---:|---|
| `DATASETS/kuule-kratt/positive/mic1` | real base positives | HPC/external | original Korvo-2 mic1 recordings |
| `DATASETS/kuule-kratt/positive/mic2` | real base positives | HPC/external | original Korvo-2 mic2 recordings |
| `processed/positive_tts` | legacy TTS positives | local 0 | kept for HPC compatibility; may be flat on HPC |
| `processed/positive_tts_ssml` | legacy SSML positives | local 0 | kept for HPC compatibility; may be flat on HPC |
| `raw/neurokone_ssml_positives` | `Kuule Kratt` TTS/SSML positives | 972 | nested by speaker; now included recursively |
| `raw/neurokone_ssml_kule` | `Kule Kratt` TTS/SSML positives | 969 | key new recall variation |
| `raw/mattias/positive` | real MacBook positives | 30 | all Mattias raw Mac positives |
| `augmented/positive_mattias_mac` | augmented Mattias positives | 150 | Mac domain augmentation |
| `raw/mattias-short/positive` | short/fast `kule/kuule kratt` positives | 362 | key practical recall data |
| `raw/kule_vs_kuule_test` | small `kule`/`kuule` pronunciation set | 8 | included as positive variation |
| `raw/xtts_clones/marta/positive` | cloned voice positives | local present | broadens voice variation |
| `raw/xtts_clones/annam/positive` | cloned voice positives | local present | broadens voice variation |
| `raw/xtts_clones/ema/positive` | cloned voice positives | local present | broadens voice variation |

Local raw-positive count for the explicitly local sources above is at least:

```text
972 + 969 + 30 + 150 + 362 + 8 = 2491 WAVs
```

plus base mic1/mic2 and any HPC-flat `processed/positive_tts*` directories.

### Held-out positives not included

Do not include these in v17 training:

- `processed/test_pos_xtts_isa` — primary unseen-speaker positive test set;
- `raw/ode_kuule_kratt` — useful real-speaker recall proxy;
- user-test recordings — future final evidence/training data after consent.

## Negative data included

| Source | Role | Local count observed | Notes |
|---|---:|---:|---|
| Common Voice ET train subset | broad Estonian speech | `negative_limit=5000` before exclusions | excludes `kratt`, keeps `kuule` |
| `processed/negative_korvo2` | same-device negatives | 109 | legacy Korvo-2 negatives |
| `processed/negative_korvo2_extra` | same-device negatives | 1202 | larger Korvo-2 negative set |
| `processed/negative_korvo2_session2` | same-device negatives | 3345 | important same-device speech/ambient |
| `processed/negative_macbook_segmented` | MacBook negatives | 555 | Mac domain negative speech/noise |
| `processed/negative_mined_false_accepts_v10_train` | real mined false accepts | 21 | important Mac/live false-trigger patterns |
| `raw/mined_false_accepts` | Android/Mac mined false accepts | local nested dirs currently 0 direct WAVs | included recursively for HPC/data compatibility |
| MUSAN speech | broad non-wake speech | HPC dataset | enabled |
| MUSAN music | broad music/audio nuisance | HPC dataset | enabled |
| Riigikogu subset | Estonian parliament speech | 50 files by default | broad continuous Estonian speech |

## Negative data deliberately excluded by default

| Source | Reason |
|---|---|
| separate `hard_negative_samples` feature set | previous runs suggest hard-neg feature sets can hurt recall/FAPH balance |
| `negative_tts_hard`, `negative_tts_hard_v2` | large TTS hard-neg corpora likely over-constrain small models |
| `augmented/hard_neg_mattias_mac_train` | disabled in `recall-cv` to avoid hard-neg overdose |
| XTTS hard negatives | disabled in `recall-cv` to avoid hard-neg overdose |
| `data/mined/ohem_*_cv_et*` | likely mined from canonical CV FAPH test; opt-in only because it can poison `faph_cv_et` |
| `processed/faph_test_cv_et` | canonical FAPH benchmark; excluded by resolved path guard |

## CV negative policy

Previous models used:

```text
exclude_words = ["kratt", "kuule"]
```

v17 `recall-cv` uses:

```text
exclude_words = ["kratt"]
```

Rationale:

- `kratt` in a CV sentence risks being semantically close to the wake phrase and should stay out of generic negatives.
- `kuule` alone must appear in general negatives so the model learns that prefix-only `kuule` is not sufficient for wake.

## Script changes implemented

### `prepare_kuule_kratt_experiment.py`

- Positive dirs are now scanned recursively.
- Extra negative dirs are now scanned recursively for `.wav` and `.flac`.
- Added `--exclude-negative-wav-dirs` guard.
- Manifest now records `excluded_negative_by_path` and `excluded_negative_wav_dirs`.
- CV negative selection can now exclude held-out WAV dirs by resolved real path.

### `submit_hpc_kuule_kratt.sh`

- Added `--dataset-preset recall-cv`.
- Added `--dry-run`.
- Added `--include-ohem-cv-mined` opt-in flag.
- Added explicit `CV_EXCLUDE_WORDS=("kratt")` for `recall-cv`.
- Added `FAPH_CV_TEST_DIR` exclusion guard.
- Added `RAW_MINED_FALSE_ACCEPTS` as a recursive extra-negative source.
- Disabled hard-negative feature set and folded hard-negative sources for `recall-cv`.

### `train_microwakeword_experiment.sh`

- Dataset stamp/counts now count `.wav` and `.flac` for flat generated sample dirs.

### `kratt train`

- Now forwards unknown flags to `submit_hpc_kuule_kratt.sh`, enabling:

```bash
kratt train v17a --dataset-preset recall-cv --recall-profile --dry-run
```

## Recommended v17 runs

Primary run:

```bash
./cli/kratt train v17a \
  --steps 15000,5000 \
  --mem 64G \
  --dataset-preset recall-cv \
  --recall-profile
```

SpecAug paired run:

```bash
./cli/kratt train v17b \
  --steps 15000,5000 \
  --mem 64G \
  --dataset-preset recall-cv \
  --recall-profile \
  --spec-augment
```

Optional architecture ablation only if v17a/v17b are promising:

```bash
# submit script does not expose pointwise filters directly yet; use train script
# manually or add a wrapper flag if needed.
pointwise_filters = 64,64,64,64
```

## Comparison with earlier datasets

| Version family | Positive strategy | Negative strategy | Hard-neg strategy | Main observed issue |
|---|---|---|---|---|
| v1-v4 | real mic only | CV ET + small/same-device negs | none | poor FAPH / domain instability |
| v5-v7 | add TTS positives | CV/Korvo + TTS hard negs | large TTS hard negs in pool | v7 became too conservative, recall collapse |
| v8-v9 | add Mac/XTTS positives | CV/Korvo + separate hard-neg feature set | separate hard-neg 3× | hard-neg ratio/penalty too high |
| v10-v14 | larger neg pools / residual / SA experiments | broader negatives, bugs found | mostly no separate HN | mixed recall/FAPH, ingestion bugs |
| v15-v16c | reduced positives/negatives, no Mac/XTTS positives | ~10–11K negatives | no separate HN | v16c usable but CV FAPH still high |
| v17 recall-cv | `kuule` + `kule`, all important raw Mattias positives | broad general + Android/Mac mined, CV test excluded | no hard-neg overdose | intended to reduce CV FAPH while keeping recall |

## Evaluation plan after training

Run the same benchmark set as v1-v16c:

```text
faph_cv_et
faph_librispeech
faph_dipco
pos_isa_xtts
pos_ode
pos_mattias_short_v2 / available Mattias recall sets
hard_neg_mac_holdout (secondary)
hard_neg_isa_xtts (secondary)
```

Add a small prefix canary before user tests:

```text
kuule
kule
kuule ... ordinary sentence
```

Acceptance target before user testing:

```text
CV ET FAPH @ deployment threshold clearly below v16c
recall remains high on held-out positives
no obvious prefix-only `kuule` triggering
short Android/Mac live smoke is not noisy
```

## Validation notes

Local validation performed:

- `bash -n` on edited shell scripts.
- `submit_hpc_kuule_kratt.sh --dataset-preset recall-cv --dry-run` prints the expected plan.
- Synthetic prep test confirmed:
  - recursive positive discovery;
  - recursive extra-negative discovery;
  - CV `kuule` sentence kept when only `kratt` is excluded;
  - held-out WAV exclusion by resolved path works;
  - manifest records exclusion counts.

HPC validation still requires syncing these edited scripts to `~/kratt` on the cluster, then running:

```bash
bash ~/kratt/wake-word/training/scripts/submit_hpc_kuule_kratt.sh \
  --tag v17a \
  --training-steps 15000,5000 \
  --mem 64G \
  --dataset-preset recall-cv \
  --recall-profile \
  --dry-run
```
