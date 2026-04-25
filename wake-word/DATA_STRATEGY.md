# Data Strategy

**Status:** Ülevaatekaart. Kronoloogiline ajalugu ja per-mudel kasutus on eraldi failides.

## Allikad (autoritatiivsed)

- **`wake-word/docs/DATA_TIMELINE.md`** — millal mis andmeallikas projekti tekkis (chronological)
- **`wake-word/evaluation/training_data_manifest.md`** — millised andmed igasse mudelisse treeningusse läksid
- **`wake-word/docs/MODEL_LINEAGE.md`** — mudelite evolutsioon ja miks igal sammul andmeid muudeti
- **`wake-word/data/collection/`** — skriptid mis genereerivad/laadivad allikaid

## Praegune strateegia (2026-04-14)

### Treening
- **Positives:** 915 päris K-2 + 1560 Neurokõne TTS + 970 SSML TTS + 40 Mac Mattias + augmented Mac + XTTS 3 pereliiget (v8 baseline, ~3343 train + 589 test)
- **Negatives:** paradigma vahetatud v8-l — dropsi TTS hard negs, kasutab päris + voice-cloned hard negs eraldi `hard_negative` feature setis penalty_weight=3.0
- **Ambient:** 930 MUSAN + 72 K-2 = 1002 segmenti (12.2h kokku)

### Eval (alates 2026-04-07)
- **Canonical streaming FAPH** (sliding_window=5, cooldown=25 slices)
- **3 FAPH test setti:** `faph_cv_et` (3.65h), `faph_librispeech` (5.4h), `faph_dipco` (5.5h)
- **Recall test setid:** `pos_isa_xtts` (48, expanding to ~200 stochastic variants), `pos_mac_mattias` (30, v1-v7 only), `ode_kuule_kratt` (11, expanding to ~200 stochastic variants)
- **Hard neg test setid:** `hard_neg_mac_holdout` (15), `hard_neg_isa_xtts` (60), `hard_neg_v10_false_accept_canary` (5)
- **Disjointness check:** `test_sets.py::assert_disjoint_from_training()`

### XTTS recall expansion

- Use `wake-word/data/collection/generate_xtts_clones.py --positive-target 200 --skip-negatives` for speaker-specific stochastic recall-set growth.
- The generated plan is resumable and idempotent: reruns skip existing 16 kHz outputs and reuse `generation_manifest.json`.
- Recommended targets right now: `isa` and `ode`, about 200 additional positives each.

## Kriitilised reeglid (aktiivsed)

1. **Mic sümmeetria:** sama mikrofon peab olema nii positiivses kui negatiivses klassis — muidu mudel õpib mic'i fingerprinti
2. **Test setid peavad olema disjunct** treeningandmetest — igal test setil `held_out_for` list, tööriist kontrollib
3. **Dedup on kohustuslik** — Neurokõne on deterministlik, genereerib identseid väljundeid → peab dedupima
4. **Andmeid ei kustutata** regenereerimiseks — luua juurde, lasta kasutajal otsustada

## Avatud probleemid (TODO)

- **Recall test setid liiga väikesed** — 11 õde clippi annab CI ±27pp. Vaja kas (a) rohkem päris speakereid (3-5 × 30 clippi) või (b) metoodiliselt piiratud playback testimine
- **training_data_manifest.md seisab v8-l** — v9+ pole lisatud
- **v10 orphan** — analysis/ puudub täielikult
- **Android mined captures (1230 failid)** — pole veel STT labelitud positive/hard_neg/garbage'iks

Vaata ka: `docs/PROJECT_TODO.md` operatiivseks taskide järjekorraks.
