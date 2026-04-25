# Kratt - Project TODO

> **Persistent task list** - source of truth for ongoing work across Claude Code sessions.
> When a task moves to `in_progress` or `completed`, update both this file and the session task list.
> Last updated: 2026-04-23

## Status legend

- ⏳ pending
- 🔄 in_progress
- ✅ completed
- ❌ blocked / abandoned
- 🎯 critical path

---

## MODEL TRAINING (current state: v16c complete, MoE consensus breakthrough)

### Completed

- ✅ v1-v9 training + evaluation (all have entries in MODEL_LINEAGE.md)
- ✅ v10: residual ON + massive neg scale (MUSAN bug discovered post-training)
- ✅ v11: deployed on Android + ESP32 (Riigikogu shuf bug discovered post-training)
- ✅ v12: 16,853 neg pool, no hard neg, residual OFF
- ✅ v13a: v10 data + residual ON + SpecAug OFF (SA ablation clean)
- ✅ v13b: v10 data + residual ON + SpecAug ON (SA ablation paired)
- ✅ v14: residual ON, no hard neg (0.8h MacBook background)
- ✅ v15: residual ON + 1500 hard neg v2 (best IRL balance per session findings)
- ✅ v16a/b/c: iterative refinements, v16c is latest production candidate
- ✅ Expert A: gatekeeper model (96f, residual ON, no hard neg, mic-only positives) — 0.79 FAPH @ 0.996
- ✅ Expert B v2: verifier model (48f, residual OFF, SA ON, 80% hard neg + 20% general) — 13% hard neg FPR @ 0.996
- ✅ **MoE Consensus (Expert A + Expert B v2)**: sub-1 FAPH achieved (0.79 @ 0.996/0.996)
- ✅ Canonical streaming FAPH methodology (commit 6e76e0a)
- ✅ Unified benchmark on all models (benchmark_full_20260421.csv)
- ✅ Evaluation methodology fix (held-out test sets, FAPH metric)
- ✅ Augmentation settings fixed (PitchShift 0.4, BGNoise 0.5, RIR 0.3)
- ✅ Training defaults updated (residual ON, neg_class_weight 5, LR schedule)

### Model ranking (benchmark 2026-04-21, threshold=0.995)

Best FAPH on CV ET (lower is better):

| Rank | Model | FAPH CV | Recall Isa | HN Mac | Notes |
|------|-------|---------|-----------|--------|-------|
| 1 | v6-residual | 14.4 | 100% | 100% | Best single-model FAPH |
| 2 | v16a | 16.0 | 100% | 100% | Current production candidate |
| 3 | v16b | 21.7 | 100% | 93% | |
| 4 | v10 | 22.8 | 65% | 53% | MUSAN bug, good IRL balance |
| 5 | v5 | 24.3 | 100% | 100% | |
| 6 | v6 | 25.4 | 98% | 100% | |
| 7 | v8 | 27.7 | 58% | 20% | |
| 8 | expert-a | 33.0 | 100% | 87% | MoE gatekeeper |
| 9 | ex3a | 33.0 | 100% | 73% | |
| 10 | v12 | 35.9 | 90% | 87% | |
| ... | ... | ... | ... | ... | |
| MoE | A+B2@0.996 | **0.79** | 100% | 13% | Consensus = best overall |

**Key insight (session-findings-apr-2026.md):** Benchmark FAPH does NOT predict real-world performance. v15 was worst on bench (243) but best IRL (73% recall, 20% HN). Three-metric eval required: FAPH + Recall + Hard Neg FPR.

### Pending

- ⏳ Deploy v16c to ESP32 + Android
- ⏳ Evaluate MoE consensus on real device (not just benchmark)
- ⏳ Threshold tuning for v16c (dev vs test split)
- ⏳ Fresh KORVO-2 hold-out negative session (~30 min recording)

---

## EVALUATION METHODOLOGY

### Completed

- ✅ Audit what each model was trained on (`evaluation/training_data_manifest.md`)
- ✅ Build `evaluation/test_sets.py` central registry with disjointness assertions
- ✅ Add `pos_isa_xtts` (48 clips) - cross-version unseen-speaker recall
- ✅ Add `pos_mac_mattias` (30 clips) - cross-device recall
- ✅ Add `hard_neg_mac_holdout` (15 clips, real)
- ✅ Add `hard_neg_isa_xtts` (60 clips)
- ✅ Add `faph_cv_et` (3.82h, indices 5000-7000 of CV ET)
- ✅ Rewrite `compare_models.py` to use only registry + skip leaked combinations
- ✅ Sync v1-v8 models from HPC and re-evaluate all versions
- ✅ Compile evaluation methodology research doc (`docs/research/wake-word-evaluation-methodology.md`)
- ✅ Canonical streaming FAPH (sliding_window=5, cooldown=25, step_ms=10)
- ✅ Wilson 95% CI for small test sets (methodology doc)
- ✅ DET curve reporting (det_curves_20260422.json)

### Pending

- ⏳ Wilson 95% CI implementation in `compare_models.py` (code)
- ⏳ ROC AUC reporting
- ⏳ Proper threshold selection (validation vs test split)
- ⏳ Real speaker diversity collection (root cause of recall limitation)

---

## DATA EXPANSION (5h → 100h+ negative pool)

### Completed

- ✅ MUSAN speech (~16h) and music (~42h) identified but not yet ingested
- ✅ 22,000 CV ET clips available (~30h additional)
- ✅ VOiCES dataset (~20K clips) identified
- ⚠️ MUSAN glob bug in v10 (non-recursive `glob("*.wav")` — fixed in code)

### Pending

- ⏳ Ingest MUSAN speech to negative pool
- ⏳ Ingest MUSAN music to negative pool
- ⏳ Convert more CV ET clips (current: 5K for train + 2K for FAPH test)
- ⏳ Symlink VOiCES dataset into negative pool
- ⏳ Find and download Estonian podcast feeds (Vikerraadio, Kuku Raadio)
- ⏳ RIR augmentation for all negatives
- ⏳ VTLP augmentation (speaker diversification — highest priority per Deka et al. 2025)

---

## THESIS WRITING

### Status by chapter

| Chapter | Status | Notes |
|---|---|---|
| §1 Sissejuhatus | ⏳ visand | Põhjalikum kirjutamine vajalik |
| §2 Taust ja eksperimendid | ✅ corrected | Andmelekke leid + methodology fix dokumenteeritud |
| §3 Metoodika | 🔄 in_progress | "16 mistakes checklist" + FAPH kirjeldus + threshold selection |
| §4 Implementatsioon | ⏳ visand | ESP32 + HA pipeline + MoE consensus kirjeldus |
| §5 Evalueerimine | ⏳ visand | Vaja koondada v16c numbrid + kasutajatestid + MoE results |
| §6 Kokkuvõte | ⏳ visand | |

### Specific TODO

- 🎯 ⏳ Lisa "16 mistakes checklist" (§5 wake-word-evaluation-methodology.md §5) §3 metoodika peatükki
- ⏳ Kirjuta korralik FAPH metoodika kirjeldus (sliding window, refractory, streaming inference)
- ⏳ Kirjuta korralik threshold selection metoodika (val vs test split)
- ⏳ Tunnista ausalt andmeskaala piirang (5h vs 31000h openWakeWord)
- ⏳ Lisa võrdlev tabel teiste KWS süsteemidega (Apple, Google, Picovoice, microWakeWord okay_nabu)
- ⏳ Update §2 H2 sektsiooni täielikult (andmelekkega seotud numbrid parandatud)
- ⏳ Kirjuta MoE consensus osa (§4 või §5)
- ⏳ Kasutajatestide tulemused pärast pilooti ja täistestimist

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
- ⏳ Update ESPHome config to v16c
- ⏳ Test MoE consensus E2E on real hardware
- ⏳ Document deployment in §4
- ⏳ Android logger deployment with v16c

---

## SCHEDULE OUTLOOK

```
April:    │ MoE breakthrough ✓ │ v16c ready ✓ │ Eval methodology ✓ │ §3 writing │ User test planning │
May:      │ User testing pilot │ Full user testing │ Data analysis │ §4-5 writing │
June:     │ §1 §6 polish │ Juhendaja feedback │ Final corrections │ KAITSMINE │
```

**Time pressure**: ~2 months remaining. User testing is the biggest unknown. MoE consensus needs real-device validation before thesis claim.

---

## EVENTS / DECISIONS LOG

- **2026-03-24**: Vahekaitsmine - presented v6 as breakthrough (numbers later found wrong due to data leakage)
- **2026-04-07**: Evaluation methodology audit revealed data leakage in `compare_models.py` (test set was training data)
- **2026-04-07**: Built `test_sets.py` with disjointness assertions; rewrote `compare_models.py`; added FAPH metric; corrected thesis §2
- **2026-04-07**: Discovered v7 (which we deprecated) is actually the best FAPH model (96 vs v6 154)
- **2026-04-12-13**: Session findings — v15 best IRL despite worst bench, augmentation bugs found, MoE consensus explored
- **2026-04-13**: MoE sub-1 FAPH breakthrough (Expert A + Expert B v2 @ 0.996 = 0.79 FAPH)
- **2026-04-21**: Unified benchmark on all models (v1-v16c, experts, consensus combos)
- **2026-04-23**: Documentation audit — PROJECT_TODO.md, MODEL_LINEAGE.md, training_data_manifest.md, wake-word/CLAUDE.md updated to reflect v16c state