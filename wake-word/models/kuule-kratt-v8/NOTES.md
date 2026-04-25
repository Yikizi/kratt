# v8 — paradigma vahetus: TTS hard neg → päris hard neg + eraldi feature set

**Loodud:** 2026-04-07 12:57 (HPC run `20260407-125744`, v7-st 2 nädalat hiljem)

**2-nädalane vahe:** voice reference recording (Apr 5), XTTS clone gen (Apr 5), Mac recordings (Apr 5), methodology audit + FAPH fix (Apr 7).

## Hypothesis

Kas **päris inimeste hard negatives** (Mac + XTTS family) eraldi feature setis kõrgema karistusega (`penalty_weight=3.0`) annavad parema foneetilise eristuse kui sünteetilised TTS hard negs üldises pools?

## Struktuuriline innovatsioon — kolm feature setti

```
v5-v7: kaks feature setti
  positive:  penalty=1.0, sampling=2.0
  negative:  penalty=1.0, sampling=10.0  (kõik neg + hard neg segatud)

v8: KOLM feature setti
  positive:      penalty=1.0, sampling=2.0
  negative:      penalty=1.0, sampling=10.0  (ainult üldised neg)
  hard_negative: penalty=3.0, sampling=4.0  ← UUS! 3× karistus
```

`penalty_weight=3.0` tähendab: mudel kaotab 3× rohkem kui ajab hard neg'i positiiviga segamini. Sundib eristust foneetiliste sugulaste vahel.

## Erinevused v7-st

**Eemaldatud:**
- 7734 TTS hard negatiive (Neurokõne) — kõik maha
- SpecAugment — tagasi OFF (v7-s oli ON)

**Lisatud:**

| Allikas | Tüüp | Feature set | Arv |
|---------|------|-------------|-----|
| Mattias Mac mic positives | real | positive | ~40 |
| Augmented Mac positives | augmented real | positive | ~60 |
| XTTS marta/annam/ema positives | voice clone | positive | ~180 |
| Augmented Mac hard negs | augmented real | **hard_negative (3×)** | 300 |
| XTTS marta/annam/ema hard negs | voice clone | **hard_negative (3×)** | 180 |

## Andmed

- Positive: 3343 train + 589 test (v7 3067 → +276 uued speakerid)
- Negative (üldised): 8584 (v7 16227 → **−47%**, TTS hard negs eemaldatud)
- Hard negative (eraldi, 3×): **480** (300 Mac augmented + 180 XTTS family)
- Ambient: 1002 (12.2h, sama)
- SpecAugment: OFF
- Residual: OFF

## Tulemus (hold-out, cutoff=0.97)

| Mõõdik | v7 | **v8** | Delta | Suund |
|--------|-----|--------|-------|-------|
| FAPH (CV ET) | **96** | 141 | +47% | halvem |
| Recall Isa XTTS unseen | 43.8% | **68.8%** | +25pp | parem |
| Recall Mac unseen | 100% | --- | contaminated | (Mac pos treeningus) |
| FPR Mac hard neg | 80% | **33.3%** | **−46.7pp** | suur paranemine |
| FPR Isa XTTS hard neg | 25% | **21.7%** | −3.3pp | parim seerias |

## Tõlgendus

**v8 vahetas trade-off'i suuna v7 suhtes:**
- v7: parim FAPH (96), halb recall (43.8%) — üle-konservatiivne
- v8: halvem FAPH (141), parem recall (68.8%) + **parim hard neg discrimination** (33.3% Mac, 21.7% Isa)

**Mis töötas:**
- `hard_negative` feature set 3× penaltyga — mudel pöörab erilist tähelepanu foneetilistele sugulastele
- Päris hääled (Mac + XTTS family) vs sünteetilised — päris hard negs õpetavad päris eristust
- Multi-speaker positives (XTTS family) — speaker diversity → recall paranes

**Mis ei töötanud:**
- FAPH regress (96 → 141) — TTS hard neg eemaldamine kahandas negatiivse varieeruvust
- Mac recall contaminated — Mac positives läksid treeningusse → selle mic'i recall pole enam mõõdetav

**SpecAugment küsimus jäi lahtiseks:** v8 lülitas SpecAugmenti välja, aga samal ajal muutis ka andmeid. Puhast "v7 ilma SpecAugmentita" ei ole. Thesis soovitab: "kaks parandust (real hard neg ja SpecAugment) tasub kombineerida tuleviku versioonis."

## v8 kui lähtekoht

v8 on viimane versioon mida `training_data_manifest.md` dokumenteerib. Kõik hilisemad (v9+) on v8-l põhinevad variandid mis v8 andmestikust edasi arendati. v8 on "last documented baseline" — v9+ andmestike kohta tuleb info lisada.

Vaata ka: `wake-word/docs/MODEL_LINEAGE.md`, `wake-word/evaluation/training_data_manifest.md`
