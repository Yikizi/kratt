# Training data manifest per model version

**Last updated:** 2026-04-29

This document records what each model version was trained on, with exact manifests where available and explicit caveats where newer HPC manifests are not yet archived locally.
Source: `processed/experiments/kuule_kratt_v*/manifest.json` on HPC.
A test set is considered TRULY HELD-OUT for a model only if it shares
zero files with this model's training pool.

Historical models in this manifest used:
- `seed=42`, `test_split=0.15` (positives only)
- `negative_limit=5000` (CV ET clips)
- exclude_words = `["kratt", "kuule"]` for v1-v16-era CV negatives. Current training defaults keep `kuule` as ordinary negative speech and exclude only `kratt`, because excluding `kuule` contributed to prefix-only triggering.

## Thesis provenance roles (paper wording, updated 2026-04-29)

- **Deployment-proven/package-proven (currently):** `v11` (Android packaging/deployment evidence explicitly present).
- **Stable single-model baseline / active-demo candidate:** `v16c`. It is not deployment-proven and not production-quality on prefix/confusable regression sets.
- **Historical v1-v16 benchmark balance:** `v16c` (per 2026-04-21 unified hold-out benchmark in `MODEL_LINEAGE.md`).
- **Diagnostic only:** `v17a/v17b`, `v18*`, and `checkpoint-faph*` families. They are important evidence, but should not be promoted as final deploy candidates.

Korvo/custom deploy proof is separate from Android packaging and must be called out before any model is presented as deployment-proven.

## Positives

| Ver | Source dirs | pos_train | pos_test (held out) |
|-----|-------------|-----------|---------------------|
| v1  | mic1+mic2                                      | 915  | 161 |
| v2  | mic1+mic2                                      | 915  | 161 |
| v3  | mic1+mic2                                      | 915  | 161 |
| v4  | mic1+mic2                                      | 915  | 161 |
| v5  | mic1+mic2 + positive_tts                       | 2241 | 395 |
| v6  | mic1+mic2 + positive_tts                       | 2241 | 395 |
| v7  | mic1+mic2 + positive_tts + positive_tts_ssml   | 3067 | 541 |
| v8  | mic1+mic2 + positive_tts + positive_tts_ssml + raw/mattias/positive + augmented/positive_mattias_mac + xtts_clones/{marta,annam,ema}/positive | 3343 | 589 |

**IMPORTANT**: Because the file LIST passed to `random.shuffle(seed=42)` differs per
model (different sources combined), the held-out 15% set is **DIFFERENT for each
model**. Each model's `test_positive_samples` dir is its own canonical hold-out.

---

## Positives v9-v16c (sourced from dataset_summary.json + training_config_snapshot.json)

| Ver | Sources | pos_train | pos_test | Architecture | Residual | SpecAug | Notes |
|-----|---------|-----------|----------|--------------|----------|---------|-------|
| v9  | mic1+mic2 + positive_tts + positive_tts_ssml + raw/mattias + augmented/mattias_mac + xtts_clones | 3343 | ? | 4×48f | OFF | **ON** | 8123 hard neg 3× set |
| v10 | sama mis v8 | 3343 | ? | 4×48f | **ON** | OFF | MUSAN glob bug (0 files ingested) |
| v11 | sama mis v8 | 3343 | ? | 4×48f | OFF | OFF | Riigikogu shuf bug |
| v12 | sama mis v8 | 3343 | ? | 4×48f | OFF | **ON** | larger neg pool (16853) |
| v13a | sama mis v12 | 3343 | ? | 4×48f | **ON** | OFF | **SA abl pair** with v13b |
| v13b | sama mis v12 | 3343 | ? | 4×48f | **ON** | **ON** | **SA abl pair** with v13a |
| v14 | sama mis v12? | 3343 | ? | 4×48f | OFF | **ON** | reduced neg pool (11204) |
| v15 | mic1+mic2 + positive_tts (**NO** Mac/XTTS) | **2241** | ? | 4×48f | **ON** | OFF | best IRL balance |
| v16a | same as v15 | **2241** | ? | 4×48f | **ON** | OFF | reduced neg (10728) |
| v16b | same as v15 | **2241** | ? | wider (4×96f, 104KB) | OFF | OFF | wider filters |
| v16c | same as v15 | **2241** | ? | widest (4×96f, 148KB) | **ON** | OFF | stable baseline / demo candidate |

**THESIS CAVEAT:** `manifest.json` ei ole alla laetud v9-v16c jaoks. Täpne positiivide allikad ja held-out test set suurused vajavad HPC-st alla laadimist. Võimalik et v12-v16 kasutavad laiemat CV ET (mitte ainult 5000 esimest).

## v17 positive-data incident (2026-04-27)

v17a/v17b were trained before the positive-data audit. Their exact HPC manifests
are not yet archived locally, but the `recall-cv` preset at that time included
known-bad sources:

- `processed/positive_tts_ssml` and `raw/neurokone_ssml_positives`: confirmed
  corrupt SSML/XML read-aloud audio.
- `raw/neurokone_ssml_kule`: confirmed corrupt Kule SSML mirror.
- `raw/xtts_clones/{marta,annam,ema}/positive`: full command prompts rather
  than isolated wake phrase.
- `raw/mattias-short/positive`: mostly OK, but very short prefix-only/corrupt
  clips were present.

After the audit, `submit_hpc_kuule_kratt.sh` quarantines known-bad positive dirs
by default and `prepare_kuule_kratt_experiment.py` records positive source dirs
and duration/path exclusions in `manifest.json`.

## v18 clean-positive and checkpoint-FAPH families (2026-04-27..29)

Exact per-run HPC manifests should still be archived when available. Current
high-confidence summary:

- v18 rebuilt training around a strict positive policy: exactly `kuule/kule kratt`, no SSML/XML readout, no filler/context, no full-command XTTS positives, no random positive cropping, and a duration gate.
- Strict generated positives were built from Neurokõne phase1/phase2 + `kule_vs_kuule_test` (709 accepted in the local count documented in `V18_CLEAN_POSITIVE_EXPERIMENTS_20260427.md`).
- v18 single models were **not** promoted: clean labels reduced one failure mode but did not solve prefix/confusable triggering.
- checkpoint-FAPH models reused the v18d clean-positive / 96-filter setup and changed checkpoint selection toward `ambient_false_positives_per_hour`.
- `checkpoint-faph-v18d-clean96-pw96x4` has very low ambient FAPH but near-total external recall collapse.
- `checkpoint-faph10-v18d-clean96-pw96x4` is a better ambient gate, but still fails real-speaker generalization and confusable rejection.

Treat all v18/checkpoint results as diagnostic unless a later manifest + frozen-threshold user-test evaluation says otherwise.

## Negatives v9-v16c (sourced from dataset_summary.json)

| Ver | Negatives (total) | Hard neg (separate 3× set) | Known issues |
|-----|------------------|----------------------------|--------------|
| v9  | 9139 | 8123 | hard neg overdose (47% ratio) |
| v10 | ~17k+ (actual: no MUSAN due to glob bug) | 0 | MUSAN non-recursive glob |
| v11 | 9160 | 0 | Riigikogu shuf failure + FLAC glob |
| v12 | 16853 | 0 | bug fixes applied, but neg_class_weight=20 |
| v13a | 17203 | 0 | same dataset as v13b (clean ablation pair) |
| v13b | 17203 | 0 | same dataset as v13a (clean ablation pair) |
| v14 | 11204 | 0 | reduced neg pool (hard neg ratio ~18%) |
| v15 | 11728 | 0 | pos=2241 (no Mac/XTTS positives) |
| v16a | 10728 | 0 | |
| v16b | 10228 | 0 | |
| v16c | 10228 | 0 | |

**NB:** v15-v16c neg pool on ~10-11K, vähendatud v14 11K-lt. Positiivid on samuti vähendatud 3343 → 2241. Põhjus: Mac/XTTS positiivid eemaldatud, mis tõenäoliselt ka negative pool-i mõjutas (vähendatud neg kuna Mac augments ei olnud enam treeningus).

## Negatives (NO train/test split — all of these were trained on)

| Ver | CV ET | KORVO-2 | KORVO-2 extra | KORVO-2 sess2 | TTS hard | TTS hard v2 | XTTS hard (sep set) | Mac hard (sep set) | Total |
|-----|-------|---------|---------------|---------------|----------|-------------|---------------------|---------------------|-------|
| v1  | 3928  | 0       | 0             | 0             | 0        | 0           | 0                   | 0                   | 3928  |
| v2  | 3928  | 0       | 0             | 0             | 0        | 0           | 0                   | 0                   | 3928  |
| v3  | 3928  | 109     | 0             | 0             | 0        | 0           | 0                   | 0                   | 4037  |
| v4  | 3928  | 109     | 1311          | 0             | 0        | 0           | 0                   | 0                   | 5348  |
| v5  | 3928  | 109     | 1311          | 0             | 1644     | 0           | 0                   | 0                   | 6992  |
| v6  | 3928  | 109     | 1311          | 3345          | 1644     | 0           | 0                   | 0                   | 10337 |
| v7  | 3928  | 109     | 1311          | 3345          | 1644     | 6090        | 0                   | 0                   | 16427 |
| v8  | 3928  | 109     | 1311          | 3345          | 0        | 0           | 180                 | 300                 | 9173  |

**v8 details:**
- Removed `negative_tts_hard` and `negative_tts_hard_v2` from main negative pool
- Added 480 clips in a SEPARATE `hard_negative` feature set with penalty_weight=3.0:
  - `augmented/hard_neg_mattias_mac_train` (300 clips, real Mac voice augmented)
  - `xtts_clones/marta/negative` (60), `annam/negative` (60), `ema/negative` (60)
- Held out from training: 15 Mac hard neg + 60 Isa XTTS hard neg

## Ambient (no train/test split)

| Ver | MUSAN noise | KORVO-2 ambient | Total |
|-----|-------------|-----------------|-------|
| v1-v2 | 930 | 0  | 930  |
| v3+   | 930 | 72 | 1002 |

## Implications for evaluation

A test set is **truly held out** for a model only if it contains files
that this model's training pool does NOT include.

### Truly held out for current historical model set, unless caveated below

| Test set | Source | What it tests | N |
|---|---|---|---|
| `pos_isa_xtts` | data/processed/test_pos_xtts_isa | Recall on unseen male speaker (XTTS clone) | 48 |
| `hard_neg_mac_holdout` | data/processed/hard_neg_test | FPR on real recorded hard negatives | 15 |
| `hard_neg_isa_xtts` | data/processed/test_hard_neg_xtts_isa | FPR on unseen-speaker XTTS hard negatives | 60 |
| `faph_cv_et` | data/processed/faph_test_cv_et | FAPH on frozen legacy CV ET held-out slice (indices 5000-7000) | 2000 raw clips (3.65h raw; 3.82h canonical streaming track with 300 ms gaps) |
| `pos_ode_real` | data/raw/ode_kuule_kratt | Real-speaker recall proxy | 11 |
| `pos_friend1_real` | data/raw/friend1_20260414 | Real-speaker recall warning set | 145 |
| `faph_librispeech` | data/processed/benchmarks/librispeech-test-clean | FAPH on English speech (cross-language robustness) | 2620 (5.62h) |
| `faph_dipco` | data/processed/benchmarks/dipco | FAPH on DiPCo eval-session subset (not full 5.5h corpus) | 6 (3.32h) |

**Important:** v15-v16c positive set differs from v8-v14 (2241 vs 3343 — Mac/XTTS positives removed). Cross-version recall on `pos_isa_xtts` remains valid for the documented historical models since that set was never in any known training pool. For v17/v18/checkpoint families, prefer the newest run manifests and the caveats in the v17/v18 sections above before calling any source a final independent holdout.

### Held out for SOME models

| Test set | Held out for | Trained on by |
|---|---|---|
| `pos_mac_mattias` (Mac mic, real voice) | v1-v7 | v8-v16c |
| `pos_ode_real` (Ode real speaker) | all known model families | N/A — used as small-N real-speaker recall proxy |
| `pos_friend1_real` | all known model families | N/A — important real-speaker recall warning set |
| prefix/confusable regression sets | diagnostic for all; final holdout status varies | related sources may overlap for v17/v18e/v18f; label accordingly |

### Thesis caveats / not yet available (needs new collection)

| Test set | Source | Status |
|---|---|---|
| `neg_test_korvo2` (held-out KORVO-2 speech) | new recording session, never in training | **CAVEAT:** no held-out Korvo set yet (~30 min still needed) |
| `pos_real_20plus` (20+ real unseen speakers) | recruitment + recording | **CAVEAT:** pending user testing |
| Real-speaker recall with proper N>100 per condition | user testing | **CAVEAT:** CRITICAL for thesis |

## Notes

- The Mattias mic1+mic2 positive recordings are **all in training** for at least
  some portion (since seed=42 differs per version). For an honest cross-version
  recall comparison, we use `pos_isa_xtts` which is guaranteed unseen for documented historical models.
- The `faph_cv_et` 2000-clip set is a frozen legacy eval subset from CV ET indices 5000-7000.
  It is intentionally kept stable for final CI. CV ET 7000+ is a separate, available
  pool for train-time mining and future dev/final-split experiments.
- Use session-level disjointness for DiPCo: final-frozen FAPH uses S01/S03/S06/S07/S08,
  while S02/S04/S05/S09/S10 are for mining/dev and must never be mixed into final-eval.
