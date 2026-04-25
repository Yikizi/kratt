# v6 — näiv läbimurre mis viis methodology auditini

**Loodud:** 2026-03-21 14:48 (HPC run `20260321-144848`, v5-st ~1h hiljem)

**Staatus:** Päris parandus mitmel mõõdikul — aga mitte nii dramaatiline kui contaminated numbrid näitasid. v5 → v6 päris delta:
- FAPH 228 → 154 (**−33%**, real improvement)
- Recall 100% unseen speaker + 100% unseen device (säilis)
- Isa XTTS hard neg FPR 86.7 → 63.3 (**−27%**, real improvement)
- Mac hard neg FPR 100 → 100 (ei paranenud aga ei halvenenud)

Vale polnud improvement ise vaid selle **suurus** — CV FPR 0.4% (contaminated) väitis 100× paranemist, päris number oli 33% FAPH paranemine.

## Hypothesis

v5 pärast K-2 FPR oli juba madal (1.8%), aga CV FPR endiselt kehv (41.6%). Kas **veel rohkem ja mitmekesisemat K-2 kõnet** treeningus aitaks mudelil K-2 fingerprinti unustada ja üldiselt paremini generaliseeruda?

## Erinevused v5-st

| Parameeter | v5 | v6 |
|------------|-----|-----|
| Positives | 2241 | identne |
| CV negatives | 3928 | identne |
| K-2 negatives | 1311 (sessioon 1) | **4656** (+3345 sessioon 2) |
| TTS hard neg | 1644 | identne |
| **Negatives kokku** | 6883 | **10228** |
| Ambient | 1002 | identne |
| Arhitektuur + hyperparams | identne | identne |

Lisatud 3345 K-2 segmenti pärinevad **sessioonist 2** — 2.8h pidev kõne, lõigatud 3-sekundilisteks chunk'ideks.

## Kaks narratiivi

### 🟢 Vahekaitsmise narratiiv (clip-level FPR, contaminated)

**Mõõdetud cutoff=0.99, compare_models.py kasutades:**

| Mõõdik | v5 | **v6** | Delta |
|--------|-----|--------|-------|
| Recall (mic1) | 99.6% | 99.6% | 0 |
| Recall (mic2) | 100% | 100% | 0 |
| **CV FPR** | 41.6% | **0.4%** | **−41.2pp (100×)** |
| Korvo-2 FPR | 1.8% | **0.9%** | −0.9pp |

See **paistis läbimurdena:**
- Esmakordselt kõik 4 mõõdikut korraga roheline
- CV FPR 0.4% oli parem kui v1 baseline (8%)
- Valley of degradation näis lõplikult ületatud
- Vahekaitsmisel esitati v6 parima mudelina

### 🔴 Audit avastus

Pärast vahekaitsmist alustati v6 real-time test MacBook Pro sisemiciga: mudel andis **~50 FAPH** tavakõnes. See on täiesti vastuolus 0.4% CV FPR väitega.

**Root cause:** `compare_models.py` kasutas test komplektina `data/processed/negative_samples/` — **täpselt samu 5000 CV klippi, mis olid treeningusse kasutatud**. Klipi-taseme FPR mõõtis mudeli mälu (kuidas ta treeningus pähe õppinud), mitte generaliseerimist.

Sama probleem kehtis K-2 negatiivide kohta — kõik kogutud klipid olid treeningus, hold-out'i polnud.

### 🟡 Korrigeeritud tulemused (cutoff=0.97, truly held-out)

Pärast hold-out setide ehitamist (`faph_cv_et` 3.82h, `pos_isa_xtts`, `hard_neg_mac_holdout`, `hard_neg_isa_xtts`):

| Mõõdik | v6 (real) | Kus koht |
|--------|-----------|----------|
| Recall (Isa XTTS unseen speaker) | **100%** | Parim (tied v2, v5) |
| Recall (Mac mic unseen device) | **100%** | Parim |
| FPR hard neg Mac real | **100%** | Halvim — triggerib igal fraasil |
| FPR hard neg Isa XTTS | 63.3% | Halb |
| **FAPH (CV ET 3.82h)** | **154** | Parem kui v1-v5 (>228), aga v7 = 96 |

## Tõlgendus

**Võidud:**
- **Recall on päriselt tugev** — 100% unseen speaker ja 100% unseen device. Need polnud contaminated (test setid olid hold-out).
- **FAPH 154** on real läbimurre valley of degradation'ist: v1=367, v2=472, v3=542 (põhi), v4=373, v5=228, **v6=154**. V-kuju selgelt näha FAPH-i poolest.
- **2.8h sessioon 2 lisa** tõesti andis mudelile rohkem K-2 variatsiooni → parem üldine generaliseerimine kui v5.

**Limiitid:**
- **v6 pole absoluutselt parim** — v7 FAPH = 96 (60% parem). v6 oli parim recall'i poolest aga polnud perfect.
- **Mac hard neg FPR ei paranenud** — jäi 100% (aga sama kehtis v5-s ka, probleem oli laiem kui üks mudel)
- **Contaminated "0.4% CV FPR" on invalid**, kogu vahekaitsmise peatükk tuleb ümber kirjutada numbritega päris 33% FAPH paranemine.

## Metodoloogiline läbimurre (päris)

v6 vale number käivitas protokolli auditi:
1. **Real-time testimine** kui usaldusväärsuse check (50 FAPH vs 0.4% CV FPR vastuolu)
2. **Hold-out test setide ehitamine** (`faph_cv_et`, `pos_isa_xtts` jne)
3. **`assert_disjoint_from_training()`** tripwire `test_sets.py`-s
4. **Canonical streaming FAPH** (commit 6e76e0a, 2026-04-07)
5. **Uuesti hinnatud kõik v1-v8** hold-out-setide peal

See on thesis'i metodoloogiline panus — mitte ainult mudel, vaid ka eval protokoll mis võimaldab valideerida et mudel on päriselt hea.

## Derivaat-mudelid

- **v6-residual** (2026-04-12): v6 arhitektuur + residual ON → −37% FAPH (session-findings'i parim real-world mudel)
- **v6-specaug** (2026-04-12): v6 + SpecAugment ablation
- Need on **eraldi eksperimendid**, mitte v6 jätkud — eesmärk puhtalt uurida üksikute arhitektuuriliste valikute mõju samal andmestikul

## Järgnev

- **v7:** lisab suurema TTS hard neg setti (6090 SSML variants) + SpecAugment → FAPH langes 154 → 96, aga recall kukkus Isa XTTS peal 100% → 43.8%
- **Auditi avastamine** tegi v6 thesis narratiivi ümber: see ei ole lõpp-punkt, vaid **pöördepunkt**

Vaata ka: `wake-word/docs/MODEL_LINEAGE.md`, `docs/research/session-findings-apr-2026.md`
