# Data Timeline — millal mis andmeallikas tekkis

Kronoloogiline ajalugu sellest **millal** iga andmeallikas projekti jõudis, mitte millal see treeningusse sattus. Eesmärk: näidata millised andmed olid igal hetkel saadaval mudeleid treenides.

Vaata ka:
- `wake-word/evaluation/training_data_manifest.md` — per-mudel mis kasutati treeningus
- `wake-word/docs/MODEL_LINEAGE.md` — per-mudel hypothesis + tulemus

## Timeline

### Pärand (eeldatavalt alla laetud varem)
- **2018-03-28** (downloadi timestamp): **Google Speech Commands v2** (74,885 clips) — `data/processed/speech_commands/`
- **2018-03-28**: **Speech Commands `negative_samples`** (6000) — `data/processed/negative_samples/`

### Faas 1 — TTS sissejuhatus (veebruar 2026)
- **2026-02-05:** **Neurokõne phase 1** — 758 TTS "Kuule Kratt" klippi, 13 eesti kõnelejat. ESIMENE Kratt-spetsiifiline andmeallikas.
- **2026-02-13:** `positive_samples/` (133 clips) — varased katse/eksperimendi salvestused, ei jõudnud v1+ treeningusse
- **2026-02-28:** `experiments/` — prototüübi märkmed

### Faas 2 — Korvo-2 andmete kogumine (märts 2026)
- **2026-03-19:** **`positive/`** 1076 klippi (mic1+mic2 real Korvo-2) → v1 treeningu alus (915 train + 161 test)
- **2026-03-20:** 
  - `neurokone_phase2/` (948 TTS, laiendatud variant)
  - **`negative_korvo2/`** (109) — sessioon 1 **intentional speech** → lisati v3-le
  - **`ambient_korvo2/`** (72 segmenti) — sessioon 1 background → lisati v3-le
- **2026-03-21:**
  - `korvo2_session1/` raw (5 pikka wav-i, 6.2h) — toorandmed session 1-st
  - **`negative_korvo2_extra/`** (1203) — sessioon 1 taustakõne VAD-lõigatud → lisati v4-le (→1311 K-2 neg kokku)
  - **`negative_korvo2_session2/`** (3345) — **sessioon 2** täispikk 2.8h chunked → lisati v6-le (läbimurde andmed)
- **2026-03-24:**
  - **`neurokone_ssml_positives/`** (972 SSML prosodic variants)
  - **`neurokone_hard_neg_v2/`** (5999) — **laiendatud TTS hard neg** → lisati v7-le (+6090)
  - `macbook_negatives/` (14) — Mac salvestus katse

### Faas 3 — Cross-device + voice cloning (aprill 2026)
- **2026-04-05:**
  - **`voice_references/`** (5 clips — annam, ema, isa, marta, marta take2) — XTTS cloning refid
  - **`xtts_clones/`** (886 klippi) — XTTS v2 cloned positives + hard negs 3 pereliikmelt
  - **`mattias/`** (40 positives) — sinu päris Mac mic salvestused
  - **`hard_neg/`** (69 päris salvestus hard negs — sh `hard_neg_test/` 15 held-out)
- **2026-04-07:**
  - **`faph_test_cv_et/`** (2000 CV ET clips, ~3.65h) — canonical FAPH test set
  - `negative_macbook_segmented/` (556) — Mac negatiivid VAD-lõigatud
  - **Methodology fix:** streaming FAPH eval (commit `6e76e0a`)

### Faas 4 — Production mining (aprill 2026)
- **2026-04-10:**
  - **`negative_mined_false_accepts_v10_train/`** (21) — v10 live testimisest mined false accepts (klaviatuuri, muusika patterns)
  - **`test_neg_false_accepts_v10_canary/`** (5) — eraldi regression canary set
- **2026-04-12:**
  - **`ode_kuule_kratt/`** (11) — õe päris salvestused (too few — CI ±27pp, vajab laiendust)
  - **`android_captures/`** (1230) — 24/7 Android logger falsed accepts (sinu enda)
- **2026-04-13:**
  - `ex3a/ex3b_positives_normalized/` — MoE expert training input
- **2026-04-14:**
  - **`benchmarks/`** (2628 LibriSpeech + DiPCo) — cross-language FAPH benchmarks
  - **`mattias-short/`** (50) — uus katse sinu positiivide laiendus

### Faas 5 — Positive data quality audit (aprill 2026)
- **2026-04-27:** v17 prefix-trigger failure (`kuule`/`kule` alone) led to a manual positive-data audit.
  - **Confirmed corrupt:** `processed/positive_tts_ssml`, `raw/neurokone_ssml_positives`, `raw/neurokone_ssml_kule` — Neurokõne read SSML/XML tags aloud (5-14s clips).
  - **Quarantined:** XTTS positive full-command prompts (`raw/xtts_clones/*/positive` and `positive_16k`) until manually segmented/validated.
  - **Filtered:** very short `mattias-short` clips (~0.42s) via positive duration gate.
  - Added guard rails in `prepare_kuule_kratt_experiment.py`, `submit_hpc_kuule_kratt.sh`, and `data/validation/audit_positive_sources.py`.
  - Full report: `docs/POSITIVE_DATA_QUALITY_AUDIT_20260427.md`.

### Faas 6 — Clean positives, exact-phrase diagnostics, checkpoint-FAPH (aprill 2026)
- **2026-04-27/28:** v18 strict-positive matrix trained after the audit.
  - Strict generated positives from Neurokõne phase1/phase2 + `kule_vs_kuule_test`.
  - New prefix/exact-phrase regression sets under `data/processed/prefix_regression_test/`.
  - Result: clean labels were necessary but not sufficient; v18 single models still failed prefix/confusable selectivity.
  - Full report: `docs/V18_CLEAN_POSITIVE_EXPERIMENTS_20260427.md`.
- **2026-04-29:** checkpoint-FAPH v18d family evaluated.
  - `checkpoint-faph-v18d-clean96-pw96x4`: very low ambient FAPH, but recall collapse.
  - `checkpoint-faph10-v18d-clean96-pw96x4`: stronger ambient gate, but poor Friend1 recall and confusable FPR.
  - Full report: `evaluation/benchmark_checkpoint_models_20260429_analysis.md`.
- **2026-04-29:** user-test labelled recorder exists: `kratt user-test` / `tools/user-testing/run_user_test.py`.

## Kolm paralleelset arcid

### A — Positives arc
1. Päris K-2 (v1-v4, 915): 2026-03-19
2. + Neurokõne TTS (v5, +1560): 2026-03-20
3. + SSML TTS (v7): 2026-03-24
4. + Mattias Mac + XTTS family (v8): 2026-04-05
5. v17 expanded positives exposed corrupt SSML/XML and full-command sources: 2026-04-26/27
6. v18 strict-positive rebuild: only exact two-word `kuule/kule kratt` sources: 2026-04-27/28

### B — Negatives arc (sh hard negs)
1. CV ET (v1, 3928): enne 2026-02
2. + K-2 intentional (v3, 109): 2026-03-20
3. + K-2 background VAD (v4, 1202 more): 2026-03-21
4. + TTS hard neg (v5, 1644): 2026-03-20
5. + K-2 session 2 (v6, 3345): 2026-03-21
6. + TTS hard SSML v2 (v7, 6090): 2026-03-24
7. **Paradigma vahetus v8:** dropsi TTS hard negs → Mac augmented (300) + XTTS family (180): 2026-04-05

### C — Ambient arc
1. MUSAN alone (v1-v2, 6.2h): olemas algusest
2. + K-2 ambient (v3+, 12.2h): 2026-03-20

### D — Eval test sets arc
1. Held-out pos_test (v1+, seed=42 split): 2026-03-19+
2. **Streaming FAPH methodology + `faph_test_cv_et`**: 2026-04-07
3. **Cross-language benchmarks** (LibriSpeech, DiPCo): 2026-04-14
4. **Ground truth XTTS pos_isa_xtts**: 2026-04-05
5. **Mined canary set** (v10 adversarial): 2026-04-10
6. **Prefix/confusable regression sets** after v17 incident: 2026-04-27
7. **Friend1 real-speaker recall probe** used in v18/checkpoint analysis: 2026-04-28/29
8. **Labelled user-test recorder** for future real-speaker data: 2026-04-29

## Praegu (2026-04-29)

**Vajab kogumist:**
- 20-30 user-test participant sessions using `docs/user-testing/ten-minute-shadow-demo-protocol.md` and `kratt user-test`.
- Threshold-frozen shadow/replay analysis on the recorded user-test audio.
- Optional only if thesis schedule allows: v19 phrase-selectivity data split with explicit partial/confusable negatives and independent holdout.

**Olemas aga caveat'iga:**
- v17/v18/checkpoint artifacts prove important failure modes, but none is a final deploy candidate.
- Prefix/confusable regression sets are essential diagnostics; some overlap with training sources for specific v18 variants, so mark those results accordingly.
- Android captures and older mined clips remain useful field evidence, but user-test data is now higher priority.
