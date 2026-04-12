# Kratt - Project TODO

> **Persistent task list** - source of truth for ongoing work across Claude Code sessions.
> When a task moves to `in_progress` or `completed`, update both this file and the session task list.
> Last updated: 2026-04-07

## Status legend

- ⏳ pending
- 🔄 in_progress
- ✅ completed
- ❌ blocked / abandoned
- 🎯 critical path

---

## EVALUATION METHODOLOGY (the foundation - April 2026 fix)

### Completed

- ✅ Audit what each model was trained on (`evaluation/training_data_manifest.md`)
- ✅ Build `evaluation/test_sets.py` central registry with disjointness assertions
- ✅ Add `pos_isa_xtts` (48 clips) - cross-version unseen-speaker recall
- ✅ Add `pos_mac_mattias` (30 clips) - cross-device recall (v1-v7 only, leaked for v8)
- ✅ Add `hard_neg_mac_holdout` (15 clips, real)
- ✅ Add `hard_neg_isa_xtts` (60 clips)
- ✅ Add `faph_cv_et` (3.82h, indices 5000-7000 of CV ET)
- ✅ Rewrite `compare_models.py` to use only registry + skip leaked combinations
- ✅ Sync v1-v5 models from HPC and re-evaluate all 8 versions
- ✅ Update thesis §2 with corrected tables and "data leakage discovery" subsection
- ✅ Mark vahekaitsmine slides with post-presentation correction note
- ✅ Compile evaluation methodology research doc (`docs/research/wake-word-evaluation-methodology.md`)

### Pending

- 🎯 ⏳ **Record fresh KORVO-2 hold-out negative session** (~30 min, user does this evening) - CRITICAL for proper KORVO-2 FPR test
  - 15 min solo speech (varied content, no wake word)
  - 5 min dialog with another person
  - 5 min phonetically hard Estonian words deliberately
  - Save to `data/raw/korvo2_holdout_session/` (NOT into negative_korvo2)
- ⏳ Add KORVO-2 hold-out to `test_sets.py` registry once recorded
- ⏳ Re-run cross-version comparison with KORVO-2 dimension added
- ⏳ Implement proper threshold selection (validation split vs test split)
- ⏳ Compute Wilson 95% confidence intervals for small test sets (<100 clips)
- ⏳ Add ROC AUC reporting (currently we only report fixed-threshold metrics)

---

## DATA EXPANSION (5h → 100h+ negative pool)

The biggest gap vs industry standards: openWakeWord uses ~31,000h of negatives, we have ~5h.
Goal: get to 100-150h before final thesis evaluation.

### High priority - already on HPC, no download needed

- 🎯 ⏳ **Add MUSAN speech subdir** to negative pool (~16h, currently unused)
- 🎯 ⏳ **Add MUSAN music subdir** to negative pool (~42h, currently unused)
- ⏳ Convert next 22,000 CV ET clips (~30h additional Estonian speech, currently just 5K converted for training + 2K for FAPH test)
- ⏳ Symlink VOiCES dataset (20K clips) into negative pool (English, but tests cross-language robustness)

### Medium priority - need to download

- ⏳ Find and download free Estonian podcast feeds (Vikerraadio, Kuku Raadio, ERR podcasts) for ~50-100h of in-domain speech
- ⏳ LibriSpeech test_clean subset for additional FAPH testing (English, used by Picovoice)

### Low priority - optimizations

- ⏳ Generate Room Impulse Response (RIR) augmented versions of all negatives using BIRD or MIT IR datasets
- ⏳ Multi-TTS voice mixing: blend XTTS speaker embeddings to create synthetic novel voices (more positive variety)

---

## MODEL TRAINING

### Active

- 🔄 **v9 in training** (started 2026-04-07): v8 retsept + SpecAugment + TTS hard neg in hard_negative feature set
  - Hypothesis: should match v7 FAPH (~96) AND v8 hard neg discrimination (~33%)
  - Notification will arrive via Pushcut

### Planned

- ⏳ **v10**: v9 + MUSAN speech + MUSAN music + 22K more CV ET clips
- ⏳ **v11 (optional)**: v10 + RIR augmentation
- ⏳ **v12 (optional)**: Two-stage cascade (coarse "kuule kr*" detector + fine "kratt vs kraam" verifier)
- ⏳ **v13 (optional)**: GraphemeAug systematic confusables (edit distance 3 variants of "kuule kratt")

---

## THESIS WRITING

### Status by chapter

| Chapter | Status | Notes |
|---|---|---|
| §1 Sissejuhatus | ⏳ visand | Põhjalikum kirjutamine vajalik |
| §2 Taust ja eksperimendid | 🔄 ~70% | Korrigeeritud andmelekkega; vaja lisada metodoloogia checklist |
| §3 Metoodika | ⏳ visand | **CRITICAL**: päris suur osa metoodikat tuleb research/wake-word-evaluation-methodology.md põhjal kirjutada |
| §4 Implementatsioon | ⏳ visand | ESP32 + HA pipeline kirjeldus |
| §5 Evalueerimine | ⏳ visand | Vaja koondada uued numbrid + kasutajatestid kui valmis |
| §6 Kokkuvõte | ⏳ visand | |

### Specific TODO

- 🎯 ⏳ Lisa "16 mistakes checklist" (vt research/wake-word-evaluation-methodology.md §5) §3 metoodika peatükki
- ⏳ Kirjuta korralik FAPH metoodika kirjeldus (sliding window, refractory, streaming inference)
- ⏳ Kirjuta korralik threshold selection metoodika (val vs test split)
- ⏳ Tunnista ausalt andmeskaala piirang (5h vs 31000h openWakeWord)
- ⏳ Lisa võrdlev tabel teiste KWS süsteemidega (Apple, Google, Picovoice, openWakeWord)
- ⏳ Update §2 H2 sektsiooni täielikult (osaliselt tehtud)

---

## USER TESTING (CRITICAL PATH for thesis)

20-30 osalejat on lõputöö nõue, ~3-4 nädalat puhast tööd.

- 🎯 ⏳ **Kasutajatestide planeerimine** - kes osalejad, ankeet, ajakava
- ⏳ Eetikakomiteele kandideerimine kui vajalik (TalTech AEK)
- ⏳ Valmista nõusolekuvorm (GDPR)
- ⏳ Pilot 3-5 osalejat (esimesed bugid välja)
- ⏳ Tegelik testimine 20-30 osalejaga
- ⏳ Andmete analüüs ja tulemuste kirjutamine §5

---

## HARDWARE / DEPLOYMENT

- ✅ ESP32-S3-Korvo-2 firmware (recorder)
- ✅ ESP32-S3-Korvo-2 firmware (wake-word-logger / FAPH counter)
- ✅ ESPHome integration with v6
- ⏳ Update ESPHome config to use parima mudeliga (v7 või v9 sõltuvalt tulemustest)
- ⏳ Test full pipeline E2E with new model
- ⏳ Document deployment in §4

---

## SCHEDULE OUTLOOK

```
April:    │ Eval methodology fix ✓ │ v9-v10 training │ User test planning │
May:      │ User testing pilot │ Full user testing │ Data analysis │ §3-5 writing │
June:     │ §1 §6 polish │ Juhendaja feedback │ Final corrections │ KAITSMINE │
```

**Time pressure**: ~2 months remaining. User testing is the biggest unknown.

---

## EVENTS / DECISIONS LOG

- **2026-03-24**: Vahekaitsmine - presented v6 as breakthrough (numbers later found wrong due to data leakage)
- **2026-04-07**: Evaluation methodology audit revealed data leakage in `compare_models.py` (test set was training data)
- **2026-04-07**: Built `test_sets.py` with disjointness assertions; rewrote `compare_models.py`; added FAPH metric; corrected thesis §2
- **2026-04-07**: Discovered v7 (which we deprecated) is actually the best FAPH model (96 vs v6 154)
- **2026-04-07**: v9 submitted (v8 + SpecAugment + TTS hard neg in hard set)
