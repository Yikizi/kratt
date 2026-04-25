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

## Kolm paralleelset arcid

### A — Positives arc
1. Päris K-2 (v1-v4, 915): 2026-03-19
2. + Neurokõne TTS (v5, +1560): 2026-03-20
3. + SSML TTS (v7): 2026-03-24
4. + Mattias Mac + XTTS family (v8): 2026-04-05

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

## Praegu (2026-04-14)

**Vajab kogumist:**
- ≥3 speakerite päris Kuule Kratt salvestused (vaja täna õhtul, sihtimise 5× 20 ütlust)
- Isa ja Ode XTTS recall-seti laiendamine ~200 stochastic positsioonini kummalegi; workflow on nüüd resumable ja manifest-põhine
- Ode XTTS laiendamine (praegu 11 reaalset, CI liiga lai)

**Olemas aga valideerimata:**
- android_captures 1230 klippi — vaja STT labeling (positive vs hard neg vs garbage)
- mattias-short 50 klippi — uus batch, pole veel kontrollitud
