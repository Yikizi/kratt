# Data Strategy

**Status:** Ülevaatekaart. Kronoloogiline ajalugu ja per-mudel kasutus on eraldi failides.  
**Last updated:** 2026-04-29

## Allikad (autoritatiivsed)

- **`wake-word/docs/DATA_TIMELINE.md`** — millal mis andmeallikas projekti tekkis.
- **`wake-word/evaluation/training_data_manifest.md`** — millised andmed igasse mudelisse treeningusse läksid.
- **`wake-word/docs/MODEL_LINEAGE.md`** — mudelite evolutsioon ja miks igal sammul andmeid muudeti.
- **`wake-word/docs/POSITIVE_DATA_QUALITY_AUDIT_20260427.md`** — v17 positive-label incident ja guard rails.
- **`wake-word/docs/V18_CLEAN_POSITIVE_EXPERIMENTS_20260427.md`** — v18 strict-positive matrix ja tulemused.

## Praegune strateegia (2026-04-29)

### Thesis-first policy

User testing + thesis writing are now higher priority than new data expansion. New training data work is allowed only if it directly supports the submitted thesis and does not threaten the 2026-05-18 deadline.

### Positives

- Valid future positives must be exactly the wake phrase: `kuule/kule kratt` (elongation/pronunciation variants allowed only if still the same two words).
- Exclude by default:
  - SSML/XML readout clips,
  - full-command XTTS positives,
  - prefix-only / too-short clips,
  - filler/context phrases,
  - reversed order (`kratt kuule`),
  - random positive crops that can create partial-phrase labels.
- Known-bad SSML and XTTS sources are quarantined by default. Use `--allow-known-bad-positives` only for historical reproduction.
- Future deploy-candidate runs should use the positive audit tooling and record all exclusions in manifests.

### Negatives / exact-phrase controls

The main open modelling problem is no longer only “more negative hours”. It is **exact two-word phrase selectivity**.

Current negative-control categories:

- general long-form speech/audio for FAPH: CV ET, LibriSpeech, DiPCo, MacBook background;
- hard negatives: Mac holdout, Isa XTTS hard negatives, v10 false-accept canary;
- prefix/confusable regression: `kuule/kule`-only, `kratt`-only, reversed order, `kuule/kule <not kratt>`.

If a v19-style run is attempted, partial and confusable phrases should be first-class negatives at a controlled ratio, with a separate holdout regression set.

### Current model implication

- `v16c` remains the stable single-model baseline / demo candidate.
- v17 showed that corrupted positives can break the model.
- v18 showed that clean positives alone do not solve exact phrase selectivity.
- checkpoint-FAPH showed that ambient-FAPH checkpointing alone can collapse recall.

## Eval policy

- Canonical metric: **streaming FAPH**, not clip-level FPR.
- Final model tables must report the trio together:
  - FAPH,
  - real/unseen-speaker recall,
  - hard-negative / prefix / confusable FPR.
- Thresholds for final claims must be frozen on validation/dev before final reporting.
- Prefix/confusable sets that overlap with training for a model family are useful diagnostics, but not final independent holdouts.

## Kriitilised reeglid (aktiivsed)

1. **Mic sümmeetria:** sama mikrofon peab olema nii positiivses kui negatiivses klassis — muidu mudel õpib mic'i fingerprinti.
2. **Test setid peavad olema disjunct** treeningandmetest; kui pole kindel, märgi tulemus diagnostic-only.
3. **Dedup on kohustuslik** — Neurokõne on deterministlik, genereerib identseid väljundeid.
4. **Andmeid ei kustutata** regenereerimiseks — luua juurde, lasta kasutajal otsustada.
5. **Positive quality gate** enne uut deploy-kandidaati.
6. **User-test audio** ei lähe treeningusse enne final-eval väiteid, kui thesis ei dokumenteeri eraldi train/test jaotust.

## Avatud probleemid

- 🎯 Real-speaker user-test data: 20-30 participants, labelled trials + optional audio consent.
- 🎯 Threshold freeze for final reporting.
- ⏳ Exact manifests for v17/v18/checkpoint runs should be archived when available.
- ⏳ Wilson CI / small-N uncertainty should be included in final tables.
- 🧊 Large negative-pool expansion (MUSAN/CV/VOiCES/podcasts) is deferred unless thesis schedule is safe.
- 🧊 v19 phrase-selectivity training is optional and should not displace user testing/writing.

Vaata ka: `docs/PROJECT_TODO.md` operatiivseks taskide järjekorraks.
