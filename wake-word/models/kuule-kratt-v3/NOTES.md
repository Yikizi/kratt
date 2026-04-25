# v3 — valley of degradation

**Loodud:** 2026-03-21 06:01 (HPC run `20260321-060132`)

## Hypothesis

Kas sama-seadme (Korvo-2) negatiivide lisamine parandab generaliseerimist?

## Erinevused v2-st

| Parameeter | v2 | v3 |
|------------|-----|-----|
| Positives | 915 (silence-trimmed) | **identne** |
| Negatives CV | 3928 | **identne** |
| **Negatives K-2** | 0 | **+109** (sessioon 1, VAD-ga lõigatud) |
| Negatives kokku | 3928 | **4037** |
| **Ambient K-2** | 0 | **+72** segmenti (6.2h background) |
| Ambient kokku | 930 (MUSAN) | **1002** |
| Arhitektuur | mixednet 32+48×4, residual OFF, SpecAug OFF | identne |
| Hyperparameetrid | 10k steps, lr 0.001, bs 128, pos_w=1, neg_w=20 | identne |

## Tulemus

**Esmane vaade (contaminated võrdlus — erinevad test setid):**
- Klipi-taseme FPR v1 66.4% → v3 94.0% = näiliselt katastroof
- See võrdlus oli vale: v1 test set sisaldas ainult CV klippe, v3 test sisaldas ka K-2 neg

**Õiglane võrdlus identsetel test setidel (250 mic1 + 250 mic2 pos + 250 CV neg + 109 K-2 neg, cutoff=0.99):**

| Mõõdik | v1 | v3 | Delta |
|--------|-----|-----|-------|
| Recall (mic1) | 92.8% | **98.8%** | +6pp |
| Recall (mic2) | 94.8% | 98.0% | +3pp |
| **FPR (CV)** | 8.0% | **98.0%** | +90pp (katastroof) |
| FPR (Korvo-2) | 13.8% | 24.8% | +11pp |

**Mudel ei ole täpsem — ta on ülevallandunud.** Ta annab peaaegu igale sisendile kõrge aktivatsiooniskoori.

## Tõlgendus

Park et al. 2024 \cite{park2024adversarial} kirjeldab KWS mudelitele tekkivat **valley of degradation**-it: kui domeenisiseste andmete osakaal jääb **2-10% vahemikku**, halveneb mudel võrreldes nii puhta domeenivälise kui ka suure domeenisisesega.

v3-l oli sama-seadme andmete osakaal **2.7% (109/4037)** — täpselt orgus. Mudel nägi kahte akustilist klastrit (CV ja Korvo-2), kuid 109 näitest ei piisanud stabiilse otsustuspiiri õppimiseks.

## Metodoloogiline leid (kogu projekti jaoks)

**Versioone tohib võrrelda ainult identsete hindamiskomplektide peal.** v3 kogemus (fake katastroofi näiv seis) näitas et erinevate test setide numbrid ei ole võrreldavad. See muutis kogu edaspidise evaluation-metoodika — alates siit läbi `test_sets.py` registreeritud ja `assert_disjoint_from_training()` kontrollitud.

## Järgnev

v4 skaleerib K-2 negatiive **1311-le** (25% osakaal) et pääseda orust välja — Park et al. näitas et üle 10% osakaalu mudel paraneb.

Vaata ka: `wake-word/docs/MODEL_LINEAGE.md`
