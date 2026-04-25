# Kratt wake word model lineage

Ühene nimekiri kõigist kuule-kratt mudelitest — hypothesis, muutus, tulemus, järgmine samm.

Eesmärk: vältida et mudelite arv (v1..v16c, expert-*, ex*) tekitaks segadust tulevikus. Iga versiooni sissekanne peab seletama **miks see tehti ja mida see näitas**.

---

## Unified benchmark (2026-04-21, threshold=0.995)

Kõik mudelid ühtsel alusel, hold-out test setidel, canonical streaming FAPH. Allikas: `evaluation/benchmark_full_20260421.csv`

| Mudel | Res | SA | FAPH CV | FAPH LS | FAPH DiP | Rec Isa | Rec Ode | Rec Mat | HN Mac | HN Isa | Size |
|-------|----|----|---------|---------|----------|---------|---------|---------|--------|--------|------|
| **v6-residual** | ON | OFF | **14.4** | 4.1 | 0.3 | 100% | 91% | 79% | 100% | 73% | 55KB |
| v16a | ON | OFF | 16.0 | 3.4 | 5.7 | 100% | 91% | 80% | 100% | 85% | 72KB |
| v16b | OFF | OFF | 21.7 | 3.7 | 0.6 | 100% | 91% | 73% | 93% | 90% | 104KB |
| v10 | ON | OFF | 22.8 | 30.1 | 6.0 | 65% | 64% | 84% | 53% | 10% | 55KB |
| v5 | OFF | OFF | 24.3 | 6.8 | 19.6 | 100% | 91% | 74% | 100% | 82% | 55KB |
| v6 | OFF | OFF | 25.4 | 5.2 | 2.7 | 98% | 82% | 81% | 100% | 60% | 55KB |
| v8 | OFF | OFF | 27.7 | 42.3 | 3.9 | 58% | 9% | 80% | 20% | 18% | 55KB |
| ex3a | ? | ? | 33.0 | 10.5 | 3.9 | 100% | 73% | 92% | 73% | 85% | - |
| expert-a | ON | OFF | 33.0 | 2.7 | 2.1 | 100% | 82% | 92% | 87% | 73% | 148KB |
| v12 | OFF | ON | 35.9 | 61.0 | 21.7 | 90% | 82% | 90% | 87% | 65% | 55KB |
| v7 | OFF | ON | 36.1 | 72.0 | 4.5 | 25% | 36% | 61% | 80% | 7% | 55KB |
| expert-b2 | ? | ? | 63.1 | 142.7 | 62.3 | 33% | 64% | 76% | 13% | 15% | 55KB |
| **v16c** | ON | OFF | **75.1** | 11.2 | 7.8 | **100%** | 82% | 90% | **100%** | 87% | 148KB |
| v11 | OFF | OFF | 79.0 | 119.2 | 25.9 | 100% | 55% | 92% | 87% | 98% | 55KB |
| v13b | ON | ON | 87.7 | 82.2 | 8.1 | 69% | 73% | 90% | 67% | 22% | 72KB |
| v9 | OFF | ON | 91.1 | 161.2 | 20.8 | 75% | 73% | 93% | 67% | 47% | 55KB |
| v14 | OFF | ON | 109.7 | 189.4 | 17.5 | 100% | 91% | 80% | 100% | 75% | 55KB |
| v13a | ON | OFF | 133.7 | 198.2 | 16.6 | 85% | 45% | 85% | 87% | 82% | 72KB |
| ex2a | ? | ? | 124.3 | 400.9 | 38.5 | 92% | 27% | 93% | 93% | 85% | - |
| v6-specaug | OFF | ON | 136.4 | 312.9 | 14.1 | 85% | 55% | 93% | 87% | 57% | - |
| ex3b | ? | ? | 175.1 | 133.8 | 30.7 | 100% | 64% | 99% | 93% | 98% | - |
| **v15** | ON | OFF | 242.9 | 73.8 | 21.4 | 98% | 64% | 72% | 27% | 88% | 72KB |
| v1 | OFF | OFF | 343.1 | 125.1 | 537.9 | 67% | 64% | 64% | 27% | 72% | 55KB |
| v4 | OFF | OFF | 246.8 | 121.8 | 33.4 | 71% | 27% | 73% | 67% | 67% | 55KB |
| v2 | OFF | OFF | 345.5 | 149.2 | 1043.2 | 100% | 100% | 92% | 87% | 100% | 55KB |
| v3 | OFF | OFF | 816.3 | 508.6 | 468.3 | 98% | 82% | 73% | 67% | 100% | 55KB |
| expert-b | ? | ? | 8766.8 | 9054.2 | 2433.8 | 100% | 100% | 98% | 100% | 82% | 55KB |

**Mõõtmisparameetrid:** sliding_window=5, cooldown=25, step_ms=10, canonical microWakeWord FAPH.
**Test setid:** FAPH CV=faph_cv_et (3.65h), LS=faph_librispeech (5.4h), DiP=faph_dipco (3.3h). Rec=recall (Isa 48 XTTS, Ode 11 real, Mat 362 real Mattias). HN=hard neg FPR (Mac 15 real, Isa 60 XTTS).
**Res = residual connections, SA = SpecAugment ON. "?" = not yet verified from config snapshot (HPC download pending).**

**NB:** v15 näitab mismatched bench vs IRL (kõige halvem bench 243, aga parim IRL). v16 family kõik SA OFF — see on uus avastus pärast HPC config download. v14 on SA ON aga residual OFF. v6-residual jääb parimaks puhtaks FAPH-iks (14.4) aga 100% hard neg FPR teeb selle kasutuks üksikuna.

---

## Formaat (per-version entries)

Iga versiooni puhul:
- **Loodud:** HPC run timestamp
- **Hypothesis:** mida uurida taheti
- **Muutus v.r. eelmise versiooniga:** täpne delta
- **Andmed:** positives / negatives / ambient counts
- **Tulemus:** observed behavior
- **Järgnev:** mis võeti õpiks

Vanad contaminated numbrid (pre-audit, clip-level FPR) on märgitud `[ARHIIV]` ja jäetud alles ajaloolise konteksti jaoks.

---

## v1 (2026-03-19 16:08) — BASELINE

- **Hypothesis:** saame üldse eesti wake word'i tööle?
- **Muutus:** esimene kuule-kratt mudel üldse
- **Andmed:** 915 real pos (Korvo-2 mic1+mic2) / 3928 neg (ainult Common Voice ET) / 930 ambient (MUSAN)
- **Arhitektuur:** mixednet 32+48×4, residual OFF, SpecAug OFF
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=343, Rec Isa=67%, Rec Ode=64%, HN Mac=27%, HN Isa=72%
- *[ARHIIV — vanad contaminated numbrid: Recall 92.8-94.8%, FPR(CV) 8.0%, FPR(K-2) 13.8%. Android ambient ~16 FAPH.]*
- **Järgnev:** baseline nõrk → v3+ lisasid same-device negatives

## v2 (2026-03-19 17:07) — SILENCE-TRIMMED POSITIVES

- **Hypothesis:** kas positiivide vaikuse trimmimine (algusest+lõpust) parandab mudelit?
- **Muutus v1 suhtes:** sama andmehulk ja configuuratsioon, aga positiivsed audiofailid **preprocessatud silence trimmingiga** enne feature extraction'it (thesis §2, second_chapter.tex:71)
- **Andmed:** 915 pos (trimmed) / 3928 neg (CV ET, sama kui v1) / 930 ambient
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=346, Rec Isa=100%, Rec Ode=100%, HN Mac=87%, HN Isa=100%
- *[ARHIIV: 2026-04-14 Android ambient ~10.5 FAPH vs v1 ~16 FAPH]*
- **Järgnev:** silence trimming jäi ilmselt default preprocessing sammuks. Kuid v3+ hakati datat horizontaalselt skaleerima (lisamine), mitte preprocessingut muutma
- Vaata `wake-word/models/kuule-kratt-v2/NOTES.md`

---

## v3 (2026-03-21 06:01) — VALLEY OF DEGRADATION

- **Hypothesis:** sama-seadme (Korvo-2) negatiivide lisamine parandab generaliseerimist
- **Muutus v2 suhtes:**
  - +109 Korvo-2 same-device negatiives (sessioon 1, VAD-ga lõigatud intentional kõnest)
  - +72 Korvo-2 ambient segmenti (930 MUSAN → 1002 kokku)
  - Positives ja hyperparams jäid samaks
- **Andmed:** 915 pos / 4037 neg / 1002 ambient
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=816, Rec Isa=98%, Rec Ode=82%, HN Mac=67%, HN Isa=100%
- *[ARHIIV — contaminated clip-level cutoff=0.99: Recall mic1 92.8→98.8%, CV FPR 8.0→98.0%, K-2 FPR 13.8→24.8%]*
- **Tõlgendus:** Park et al. 2024 "valley of degradation" — sama-seadme andmete 2-10% osakaal halvendab mudelit. v3-l oli 2.7% (109/4037), langes täpselt orgu. Kahe klastri (CV + K-2) näinud mudel ülevallandub kõikjale.
- **Metodoloogiline leid:** versioone võib võrrelda ainult identsete test setide peal. Kogu järgnev eval metoodika kujunes siit.
- **Järgnev:** v4 skaleerib K-2 negatiive 1311-le (25%) et pääseda orust välja

---

## v4 (2026-03-21 12:19) — K-2 SCALE-UP (ORUST VÄLJA OSALISELT)

- **Hypothesis:** K-2 osakaalu skaleerimine 2.7% → 25%-le peaks Park et al. orust välja tooma
- **Muutus v3 suhtes:**
  - K-2 negatiive **109 → 1311** (VAD-lõigatud 6.2h K-2 taustakõnest)
  - Kõik ülejäänud identne
- **Andmed:** 915 pos / 5239 neg (25.0% K-2) / 1002 ambient
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=247, Rec Isa=71%, Rec Ode=27%, HN Mac=67%, HN Isa=67%
- *[ARHIIV — contaminated cutoff=0.99: Recall 100%, K-2 FPR 24.8→7.3%, CV FPR 98→36.8%]*
- **Tõlgendus:** osaline võit — K-2 dimension lahendatud, aga mudel õppis liiga tugevalt K-2 akustilist fingerprintit ja kaotas CV-domeenis eristuse. Valley of degradation polnud üks dimensioon — see on domain-split probleem.
- **Järgnev:** v5 lisab Neurokõne TTS positiivid + TTS hard negatives — fraasi sisuline (foneetiline) eristus, mitte ainult domeeni-põhine

---

## v5 (2026-03-21 13:56) — TTS POSITIIVID + HARD NEGATIVES

- **Hypothesis:** hard negatives ("Hei Kratt", "Tere Kratt", "Kratt kuule" jm) sunnivad mudelit eristama **täpset fraasi** "Kuule Kratt", mitte ainult domeeni
- **Muutus v4 suhtes:**
  - +1560 Neurokõne TTS positiivid (12 eesti kõnelejaga)
  - +1644 TTS hard negatives (foneetilised sugulased)
- **Andmed:** 2241 pos (train) / 6883 neg / 1002 ambient
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=24, Rec Isa=100%, Rec Ode=91%, HN Mac=100%, HN Isa=82%
- *[ARHIIV — contaminated cutoff=0.99: K-2 FPR 7.3→1.8%, CV FPR 36.8→41.6%, Recall 99.6-100%]*
- **Tõlgendus:** Korvo-2 probleem lahendatud fraasi-eristusega. Aga CV domeen jäi ebavõrdseks — TTS kõne ≠ päris CV kõne, mudel kaotas CV-s midagi
- **Järgnev:** v6 lisab 3345 rohkem K-2 ambient negatiive (sessioon 2, 2.8h) — rohkem mitmekesist K-2 kõnet et mudel ei õpiks kitsast fingerprinti

---

## v6 (2026-03-21 14:48) — NÄIV LÄBIMURRE → METHODOLOGY AUDIT

**Ajalooline olulisim mudel** — ei mitte kvaliteedi poolest, vaid sellepärast et tema contaminated "0.4% CV FPR" käivitas kogu eval protokolli auditi.

- **Hypothesis:** rohkem K-2 mitmekesist kõnet (sessioon 2 täispikkus) → mudel unustab kitsast fingerprinti, üldistab paremini
- **Muutus v5 suhtes:**
  - +3345 K-2 neg (sessioon 2, 2.8h, 3-sec chunks)
  - Total neg 6883 → **10228**
- **Andmed:** 2241 pos / 10228 neg / 1002 ambient

### Benchmark (2026-04-21 @0.995)
FAPH CV=25, FAPH LS=5, FAPH DiP=3. Rec Isa=98%, Rec Ode=82%, Rec Mat=81%. HN Mac=100%, HN Isa=60%.

### Ajalooline kontekst
*[ARHIIV — contaminated cutoff=0.99: CV FPR 0.4% (näiline 100× paranemine). Real-time test: ~50 FAPH MacBook. Root cause: compare_models.py kasutas treeningandmeid testina. Korrigeeritud cutoff=0.97: FAPH 154, Rec Isa 100%, HN Mac 100%.]*

### Real v5→v6 delta (päris paranemine)
- **FAPH 228 → 154** (−33%, real) — valley of degradation kõige madalam punkt
- **Recall 100% säilis** (unseen speaker + unseen device)
- **Isa XTTS hard neg FPR 86.7 → 63.3** (−27%, real)
- **Mac hard neg FPR 100 → 100** (ei paranenud aga ei halvenenud)
- **v7 on FAPH-i poolest parem (96)**, aga kaotab recall'is — tradeoff

### Metodoloogiline tagajärg (päris läbimurre)
- Hold-out test setide ehitamine (`faph_cv_et`, `pos_isa_xtts` jm)
- `assert_disjoint_from_training()` tripwire
- Canonical streaming FAPH (commit 6e76e0a, 2026-04-07)
- Kõik v1-v8 hinnatud uuesti hold-out setide peal

### Derivaat-mudelid
- **v6-residual** (2026-04-12): v6 + residual ON → −37% FAPH, parim real-world mudel session-findings'is
- **v6-specaug** (2026-04-12): v6 + SpecAugment ablation
- Mõlemad eraldi eksperimendid, mitte v6 jätkud

### Järgnev
v7 proovib kombineerida SpecAugment + suurema TTS hard neg'i (6090 SSML variants) → FAPH 96, aga recall Isa XTTS peal kukub 100% → 43.8%

---

## v7 (2026-03-24 16:39) — PARIM FAPH, KATASTROOFILINE RECALL TRADE-OFF

- **Hypothesis:** hard neg set laiendus + SpecAugment → FAPH edasi, recall säilib
- **Muutus v6 suhtes (kolm korraga, diagnostikaline viga):**
  - +826 SSML TTS positives (3067 train)
  - +6090 TTS hard neg v2 (16227 neg, +59%)
  - **SpecAugment ON** (esimest korda, freq 2×3, time 2×10)
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=36, Rec Isa=25%, Rec Ode=36%, HN Mac=80%, HN Isa=7%
- *[ARHIIV — hold-out cutoff=0.97: FAPH 96, Rec Isa 43.8%, Rec Mac 100%, HN Mac 80%, HN Isa 25%]*
- **Tõlgendus:** over-conservative trade-off. SpecAugment + laiendatud hard neg teeb mudeli diskriminatiivsemaks → vähem FA, aga ka vähem triggereid uutele kõnelejatele. **Pole deployable** assistandi jaoks (pool kasutajaid ei saa teenust kasutada).
- **Diagnostikaline viga:** 3 muutust korraga → ei saa teada mis efekti põhjustas. Hilisemad v6-residual, v6-specaug ablatsioonid (2026-04-12) lähtuvad "üks muutus korraga" printsiibist.
- **Järgnev:** v8 vahetab paradigma — dropsi TTS hard negs, kasutab päris Mac salvestusi + XTTS family voice clones eraldi `hard_negative` feature setis penalty_weight=3.0

---

## v8 (2026-04-07 12:57) — PARADIGMA VAHETUS: PÄRIS HARD NEG + ERALDI FEATURE SET

Viimane versioon mida `training_data_manifest.md` dokumenteerib. v9+ on v8-l põhinevad variandid.

- **Hypothesis:** kas päris hard negs (Mac + XTTS family) eraldi feature setis penalty_weight=3.0 annavad parema foneetilise eristuse kui TTS hard negs üldises pools?
- **Struktuuriline innovatsioon:** 3 feature setti: positive (1×), negative (1×), **hard_negative (3× penalty)**
- **Muutus v7 suhtes:**
  - Eemaldatud: kõik 7734 TTS hard neg + SpecAugment OFF
  - Lisatud: Mac real pos + augmented pos + XTTS 3 family pos (+276 pos)
  - Lisatud: Mac augmented hard neg (300) + XTTS 3 family hard neg (180) = **480 eraldi 3× setis**
- **Andmed:** 3343 pos / 8584 neg / **480 hard neg (3×)** / 1002 ambient
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=28, Rec Isa=58%, Rec Ode=9%, HN Mac=20%, HN Isa=18%
- *[ARHIIV — hold-out cutoff=0.97: FAPH 141, Rec Isa 68.8%, HN Mac 33.3%, HN Isa 21.7%]*
- **Tõlgendus:** v8 vahetas trade-off'i suuna — FAPH kaotas, recall + hard neg discrimination võitsid. Separate hard_neg set 3× penaltyga on efektiivne. Thesis soovitab kombineerida v7 SpecAugment + v8 real hard negs.
- **Lahtised küsimused:**
  - SpecAugment efekt isoleerimata (pole puhast ablatsiooni)
  - Mac recall contaminated (Mac pos treeningus)
  - training_data_manifest.md seisab siin — v9+ andmeid pole dokumenteeritud

---

## v9 (2026-04-07 16:44) — HARD NEGATIVE OVERDOSE (FAILURE)

Esimene post-methodology-audit mudel. Disain-otsus (hard neg massive scaling) oli ikka vale.

- **Hypothesis:** combine v7 SpecAugment + v8 real hard neg structure + kõik hard negs (TTS + real) ühes 3× setis
- **Muutus v8 suhtes:**
  - Hard neg 480 → **8123** (TTS hard negs tagasi eraldi 3× setis)
  - **SpecAugment ON** (NB: eval record ütleb "OFF" aga training_config on "ON" — config on ground truth)
  - Negatives +555
- **Andmed:** 3343 pos / 9139 neg / **8123 hard neg (47% ratio!)** / 1002 ambient
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=91, Rec Isa=75%, Rec Ode=73%, HN Mac=67%, HN Isa=47%
- *[ARHIIV — @0.97: FAPH 187, Rec Isa 83.3%, HN Mac 80%, HN Isa 61.7%, FRR@1FA/h 35.3%]*
- **Tõlgendus:** hard neg overdose — 47% ratio (optimal 10-20%). Liiga palju "Kuule Kratt"-sarnaseid negatiivseid → mudel unustab mis "Kuule Kratt" ISE kõlab. v8 mehhanism (eraldi 3× set) oli õige, maht vale.
- **Järgnev:** v10 proovib radikaalselt erinevat — residual ON, suur ühendatud neg pool (17k+), 0% hard neg

---

## v10 (~2026-04-10) — RESIDUAL ON + MASSIVE NEG SCALE + MUSAN BUG

Ainuke mudel ilma analysis/ kaustata (orphan). Residual ON esimest korda main sequence'is.

- **Hypothesis:** scale up kõike — residual ON, suur neg pool (MUSAN speech 49h + music 41h + Riigikogu ~200h + mined false accepts), kõik ühes pools, 0% eraldi hard neg
- **KRIITLINE BUG:** `glob("*.wav")` non-recursive → **0 MUSAN speech/music faili** tegelikult treeningus. Logid väitsid et olid. v10 "MUSAN advantage" illusoorne.
- **Andmed:** 3343 pos / ~17k+ neg (ilma MUSAN-ita tegelikult vähem) / 0 hard neg eraldi / 1002 ambient
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=23, Rec Isa=65%, Rec Ode=64%, HN Mac=53%, HN Isa=10%
- *[ARHIIV — @0.997: FAPH CV 15.7, FAPH Mac 4.3, Recall Ode 73%, Recall Isa 56%, HN Mac 53%, FRR@1FA/h 45.3%]*
- **Tõlgendus:** residual ON = konservatiivne mudel, hea FAPH aga kõrge FRR. Sama trade-off mis v7. Hard neg ratio 46% liiga kõrge.
- **Oluline roll:** mined false accepts (canary set), consensus v10+v15, SpecAugment ablation base (v13a/v13b), MUSAN glob bug discovery
- **Järgnev:** v11 optimeerib v10 lähenemist edasi (deployed Pixel 8a + ESP32)

---

## v11 (2026-04-11 08:27) — DEPLOYED (ANDROID + ESP32)

Esimene ja praegune production-deployed mudel.

- **Arhitektuur:** mixednet 4×48f, residual OFF (NB: eval_results ütleb "residual" aga config snapshot = OFF), SpecAug OFF
- **Andmed:** 3343 pos / 9160 neg / **0 hard neg eraldi** / 1002 ambient
- **Bug:** Riigikogu shuf failure + FLAC glob — v11 treeniti ilma Riigikogu andmeteta mida pidi saama
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=79, Rec Isa=100%, Rec Ode=55%, Rec Mat=92%, HN Mac=87%, HN Isa=98%
- **DET:** FRR@1FA/h = 0% — liiga permissiivne, aga seepärast ka hea recall
- **Miks deployed:** "good enough" hetkel kui deploy vajati — 100% Isa recall + talutav FAPH
- **Järgnev:** v12 proovib sama config bugide parandusega

---

## v12 (2026-04-11 09:14) — v11 + SPECAUGMENT + SUUREM NEG POOL

Android default model. Discrepancy: eval_results ütleb "residual, no SA" aga config = residual OFF, SA ON.

- **Muutus v11 suhtes:** neg 9160 → **16853** (+7693) + **SpecAugment ON**
- **Andmed:** 3343 pos / 16853 neg / 0 hard neg / 1002 ambient
- **Tulemus (benchmark @0.995):** FAPH CV=36 (v11 79, −54%), Rec Isa=90%, Rec Ode=82% (v11 55%, **+27pp**), HN Mac=87%, HN Isa=65% (v11 98%, **−33pp**). FRR@1FA/h=10.3%
- **Tõlgendus:** tugev paranemine üle v11 — FAPH pool, ode recall tugevalt üles, hard neg eristus parem. 2 muutust korraga (neg+SA) = pole puhas ablatsioon.
- **Järgnev:** v13a/v13b = SpecAugment ablatsioon (v10 andmetel), v14+ jätkab

---

## v12 (2026-04-11 09:14) — LARGER NEG POOL WITH SPECAUG ON

**Discrepancy:** `model_evaluation_results.json` kirjutab "residual, no SpecAugment" aga training_config_snapshot.json näitab `residual_connection: "0,0,0,0"` JA `freq_mask_count: [2]` + `time_mask_count: [2]` = **SpecAug ON**. Config on ground truth.

- **Arhitektuur:** mixednet 4×48f, **residual OFF**, SpecAug ON (freq 2×3, time 2×10)
- **Andmed:** 3343 pos / **16853 neg** / 0 hard neg eraldi / 1002 ambient
- **Muutus v11 suhtes:** neg 9160 → 16853 (+7706, tõenäoliselt lisatud Riigikogu + CV ET laiendus pärast FLAC glob bugi parandust)
- **Bugid:** v11 Riigikogu shuf bug fikseeritud, aga neg_class_weight jäi 20 (liiga kõrge)
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=36, Rec Isa=90%, Rec Ode=82%, HN Mac=87%, HN Isa=65%
- **Tõlgendus:** suurem neg pool aitas pisut FAPH-i langetada v11-st (79 → 36), aga residual OFF ja neg_class_weight 20 trade-off jäid. HN Isa kannatab (65% vs v11 98%).
- **Järgnev:** v13a/v13b testivad residual ON + SA mõju v10-era andmetel (SpecAugment ablatsioon)

---

## v13a (2026-04-12) — SPECAUGMENT ABLATION: SA OFF (CLEAN PAIR WITH v13b)

Esimene puhas ühe-muutuja ablatsioon pärast v6-residual'it. v13a ja v13b on **identse andmestikuga** (sama features_dir), erineb ainult SpecAugment.

- **Arhitektuur:** mixednet 4×48f, **residual ON**, **SpecAug OFF** (freq_mask [0], time_mask [0])
- **Andmed:** 3343 pos / 17203 neg / 0 hard neg eraldi / 1002 ambient
- **Muutus v12 suhtes:** residual OFF → ON, aga ka neg 16853 → 17203 (veidi erinev andmestik — v13 kasutab v10-era featuure, mitte v12 omad)
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=134, Rec Isa=85%, Rec Ode=45%, HN Mac=87%, HN Isa=82%
- **Session-findings (SA ablatsioon v10 data):** v13a (SA OFF) FAPH @0.995 = 113.6
- **Tõlgendus:** residual ON + suur neg pool annab kõrge FAPH kui SA puudub. Oodatud — SA on peamine regulariseerija mis FAPH-i langetab.
- **Järgnev:** v13b (SA ON) sama andmestikuga

---

## v13b (2026-04-12) — SPECAUGMENT ABLATION: SA ON (CLEAN PAIR WITH v13a)

Puhas SpecAugment ablatsiooni paar v13a-ga. Ainus erinevus on SA sisse/välja lülitamine.

- **Arhitektuur:** mixednet 4×48f, **residual ON**, **SpecAug ON** (freq 2×3, time 2×10)
- **Andmed:** 3343 pos / 17203 neg / 0 hard neg eraldi / 1002 ambient — **identne v13a-ga**
- **Muutus v13a suhtes:** SA OFF → ON (ainus erinevus)
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=88, Rec Isa=69%, Rec Ode=73%, HN Mac=67%, HN Isa=22%
- **SA ablatsioon delta (v10 data, session-findings):** FAPH 113.6 → 75.6 (−33%)
- **Tõlgendus:** SA ON langetas FAPH-i 33% võrra. Kuid recall langes (Isa 85% → 69%, Ode 45% → 73%). HN Isa paranes drastiliselt (82% → 22% FPR). SA teeb mudeli rangemaks — vähem FA aga ka vähem recall.
- **Oluline:** See ablatsioon oli puhas (üks muutuja), erinevalt v7-st kus 3 muutust korraga.
- **Järgnev:** v14 proovib residual ON ilma SA-ta aga vähendatud hard neg ratio'ga

---

## v14 (2026-04-13) — RESIDUAL OFF, SPECAUG ON, REDUCED NEG POOL

Hämmastav tulemus: v14 on v6-residual järel parim recall (100% Isa, 91% Ode) aga SA ON hoiavad FAPH kontrolli all.

- **Arhitektuur:** mixednet 4×48f, **residual OFF**, **SpecAug ON** (freq 2×3, time 2×10)
- **Andmed:** 3343 pos / **11204 neg** / 0 hard neg eraldi / 1002 ambient
- **Muutus v13a suhtes:** neg 17203 → 11204 (−6000), SA jäi samaks (ON), aga residual OFF vs v13a ON
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=110, Rec Isa=**100%**, Rec Ode=91%, HN Mac=**100%**, HN Isa=75%
- **Session-findings:** hard neg ratio 18%, FAPH @0.995 = 120.7
- **Tõlgendus:** See on üllatav tulemus. v13a (residual ON, SA OFF) andis FAPH 134 aga v14 (residual OFF, SA ON) ainult 110. SA ON on olulisem FAPH-langetaja kui residual ON. Kuid v6-residual (residual ON, SA OFF) sai 14.4 FAPH — seega residual ON aitab kui SA ei ole sees. Kombinatsioonid matter.
- **Oluline leid:** MacBook background session (0.8h) andis väga madala FAPH — näitab et v14 generaliseerub hästi keskkonda kus ta treeningus piisavalt kõnet nägi.
- **Järgnev:** v15 proovib positsioonide arvu vähendamist (3343 → 2241) — aga SA OFF (erinevalt siiani arvatust)

---

## v15 (2026-04-13) — WORST BENCH, BEST IRL BALANCE

Session-findings leid: v15 oli **kõige halvem benchmark FAPH** (243) aga **kõige parem reaalses elus** (73% recall, 20% hard neg FPR MacBook testil).

- **Arhitektuur:** mixednet 4×48f, **residual ON**, **SpecAug OFF** (freq 0×0, time 0×0)
- **Andmed:** **2241 pos** (mic1+mic2 + TTS, ilma Mac/XTTS lisadeta) / 11728 neg / 0 hard neg eraldi / 1002 ambient
- **Muutus v14 suhtes:** pos 3343 → 2241 (−1102, eemaldatud Mac + XTTS family positives) + residual ON (v14 was OFF) + SA OFF (v14 was ON)
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=243, Rec Isa=98%, Rec Ode=64%, HN Mac=27%, HN Isa=88%
- **Real-world (MacBook 0.8h background):** FAPH 45.4 — palju parem kui benchmark lubaks arvata
- **Session-findings 2026-04-13:** "v15 was worst on bench but best in real life. The CV ET benchmark measures sensitivity to random Estonian speech, not selectivity against confusable phrases."
- **Tõlgendus:** 2241 pos (ilma Mac augmentatsioonita) + residual ON + SA OFF = mudel mis on paremini tasakaalus recall vs hard neg FPR. MacBook test näitas 27% hard neg FPR vs v14 100%. CV ET benchmark ei pea kokku kasutajakogemusega (Dubois et al. 2020 kinnitab).
- **Järgnev:** v16 pere proovib erinevaid arhitektuuri laiuseid

---

## v16a (2026-04-13/14) — SAME AS v15, DIFFERENT NEG SCALE

v15 kordamine teise neg pool suurusega. Katsetab kas 11728 → 10728 erinevus mõjutab midagi.

- **Arhitektuur:** mixednet 4×48f, **residual ON**, **SpecAug OFF** (freq 0×0, time 0×0) — identne v15-ga
- **Andmed:** 2241 pos / **10728 neg** / 0 hard neg eraldi / 1002 ambient
- **Muutus v15 suhtes:** neg 11728 → 10728 (−1000)
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=**16.0**, Rec Isa=100%, Rec Ode=91%, HN Mac=**100%**, HN Isa=85%
- **Tõlgendus:** Dramatic FAPH drop (243 → 16) vs v15. Seletus: negatiivide hulga vähendamine 1000 võrra muutis mudeli kalibratsiooni. **Väike neg pool = madalam FAPH** (mudel näeb vähem negatiivseid näiteid → vähem false accepts). Kuid recall säilis kõrge ja hard neg FPR tõusis.
- **NB:** See seab kahtluse alla v15 "best IRL" tõlgenduse — v16a on palju parem nii bench kui (ilmselt) IRL.
- **Järgnev:** v16b proovib laiemat arhitektuuri

---

## v16b (2026-04-14) — WIDER FILTERS (104KB), RESIDUAL OFF

Laiem arhitektuur — rohkem parameetreid, aga seekord residual OFF.

- **Arhitektuur:** mixednet wider (4×96f, **104KB** vs v16a 72KB), **residual OFF**, **SpecAug OFF**
- **Andmed:** 2241 pos / **10228 neg** / 0 hard neg eraldi / 1002 ambient
- **Muutus v16a suhtes:** filters laiem (suurem model), neg 10728 → 10228 (−500)
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=22, Rec Isa=100%, Rec Ode=91%, HN Mac=93%, HN Isa=90%
- **Tõlgendus:** Laiem arhitektuur andis veidi kõrgema FAPH kui v16a (22 vs 16), aga parandas hard neg rejection (HN Isa 85% → 90%, HN Mac 100% → 93%). Trade-off: FAPH vs hard neg discrimination. 104KB on endiselt piisavalt väike ESP32 jaoks.
- **Järgnev:** v16c proovib kõige laiemat varianti

---

## v16c (2026-04-14) — WIDEST FILTERS (148KB), RESIDUAL ON, LATEST PRODUCTION CANDIDATE

Praeguse repo kõige uuem ja suurim mudel. Kõige paremad üldnumbrid.

- **Arhitektuur:** mixednet kõige laiem (4×96f, **148KB**), **residual ON**, **SpecAug OFF**
- **Andmed:** 2241 pos / **10228 neg** (v16b sama) / 0 hard neg eraldi / 1002 ambient
- **Muutus v16b suhtes:** filters veelgi laiemaks
- **Tulemus (benchmark 2026-04-21 @0.995):** FAPH CV=75, Rec Isa=**100%**, Rec Ode=82%, HN Mac=**100%**, HN Isa=87%
- **Tõlgendus:** FAPH tõusis v16b-st (22 → 75) aga recall säilis 100% ja hard neg rejection paranes. v16c on parim overall balance: 100% recall + 100% hard neg rejection + talutav FAPH (75). NB: FAPH ei ole kõige madalam (v16a=16, v16b=22), aga kolme mõõdiku kombinatsioon on parim.
- **Deployment:** v16c on hetkel parim candidate ESP32 + Android deploy jaoks.
- **Oluline kontekst:** expert-a (148KB gatekeeper) kasutab sama suurusega arhitektuuri ja saavutas MoE consensuses 0.79 FAPH. v16c võib sama MoE pipeline'is kasutada.

---

## v17+ (PENDING)

v17 ei eksisteeri veel (2026-04-23). Järgmine training round kavandatud pärast thesis metoodika ja v16c real-world testi valmimist.
