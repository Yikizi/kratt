# v9 — hard negative overdose (failure)

**Loodud:** 2026-04-07 16:44 (HPC run `20260407-164404`, v8-st 4h hiljem)

**Esimene mudel mis treeniti post-methodology-audit awareness'iga** — FAPH fix oli juba tehtud, aga v9 disain-otsus (hard neg scaling) oli ikka vale.

## Hypothesis

Thesis soovitus: "combine v7 SpecAugment + v8 real hard neg architecture". Teeme seda PLUS paneme kõik olemasolevad hard negs (TTS v1 + TTS v2 + Mac + XTTS) eraldi 3× feature set'i.

## Erinevused v8-st

| Parameeter | v8 | v9 |
|------------|-----|-----|
| Positives | 3343 | 3343 |
| Negatives (üldised) | 8584 | 9139 (+555) |
| **Hard neg (3× set)** | 480 | **8123** (+7643, TTS hard neg tagasi) |
| **SpecAugment** | OFF | **ON** (freq 2×3, time 2×10) |
| Residual | OFF | OFF |

**Hard neg ratio: 47%** (8123 / 17262) — soovitusest (10-20%) üle 2× kõrgem.

## Tulemus

| Mõõdik | v8 | **v9** | Suund |
|--------|-----|--------|-------|
| FAPH CV ET @0.97 | 141 | **187.4** | halvem |
| Recall Isa XTTS @0.97 | 68.8% | **83.3%** | parem |
| FPR Mac hard neg @0.97 | 33.3% | **80.0%** | palju halvem |
| FPR Isa XTTS hard neg @0.97 | 21.7% | **61.7%** | palju halvem |
| FRR@1FA/h | — | 35.3% | esimene DET punkt |

## Tõlgendus

**Hard negative overdose.** 47% hard neg ratio tegi mudeli "liiga liberaalseks":
- Mudel nägi nii palju "Kuule Kratt"-sarnaseid fraase negatiivsena et ta kaotab ära kuidas "Kuule Kratt" ISE kõlab
- Paradoksaalselt: rohkem hard negs → halvem hard neg discrimination
- Session-findings §2.3 (Hou et al.): optimal hard neg ratio 10-20%, 2-4× sampling weight → 20-40% gradient contribution. Meie 47% on selgelt üle.

**v8 480 hard negiga töötas hästi** → probleem pole eraldi feature set (mehhanism) vaid **maht** (8123 on liiga palju).

## Discrepancy: SpecAugment

- `model_evaluation_results.json` kirjutab "no SpecAugment"
- `training_config_snapshot.json` näitab: freq_mask_count=2, time_mask_count=2 → **SpecAugment ON**
- **Config snapshot on ground truth.** Eval record on valesti kirja pandud.

## Õppetund

1. **Hard neg ratio on kriitiline tuning parameter**, mitte "rohkem = parem"
2. **v8 mehhanism oli õige** (eraldi 3× feature set), ainult maht vale
3. Edasi peab otsima sweet-spot'i: ~10-20% hard neg
4. SpecAugment efekt on selles katses confounded hard neg overdose'iga — ei saa isoleerida

## Järgnev

v10 proovib radikaalselt teist lähenemist: **residual ON**, suur ühendatud neg pool (17k+), hard neg maha (ratio 0%), MUSAN speech+music lisatud. Ehk "scale up everything + residual" paradigma.

Vaata ka: `wake-word/docs/MODEL_LINEAGE.md`
