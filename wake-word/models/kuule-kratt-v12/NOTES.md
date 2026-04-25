# v12 — v11 + SpecAugment + larger neg pool

**Loodud:** 2026-04-11 09:14 (HPC run `20260411-091445`, v11-st ~1h hiljem)

**Android default model** (`DEFAULT_MODEL = "kuule_kratt_v12.tflite"`)

## Discrepancy

`model_evaluation_results.json` ütleb "residual, no SpecAugment" aga `training_config_snapshot.json` näitab:
- `residual_connection: "0,0,0,0"` = **OFF**
- `freq_mask_count: [2]`, `time_mask_count: [2]` = **SpecAugment ON**

Config snapshot on ground truth. Eval record on topelt-vale (sama muster nagu v11).

## Erinevused v11-st

| Parameeter | v11 | v12 |
|------------|-----|-----|
| Positives | 3343 | 3343 |
| **Negatives** | 9160 | **16853** (+7693) |
| Hard neg eraldi | 0 | 0 |
| **SpecAugment** | OFF | **ON** (freq 2×3, time 2×10) |
| Residual | OFF | OFF |

2 muutust korraga — neg pool expansion + SpecAugment. Diagnostiline puhtus pole ideaalne (sama probleem mis v7-l), aga mõlemad on tõenäoliselt head muutused (neg scaling + regulariseerimine).

## Tulemus (benchmark 2026-04-21 @0.995)

| Mõõdik | v11 | **v12** | Delta |
|--------|-----|---------|-------|
| FAPH CV | 79 | **36** | −54% |
| FAPH LS | 119 | 61 | −49% |
| Rec Isa | 100% | 90% | −10pp |
| Rec Ode | 55% | **82%** | +27pp |
| Rec Mat | 92% | 90% | −2pp |
| HN Mac | 87% | 87% | sama |
| HN Isa | 98% | **65%** | −33pp |
| FRR@1FA/h | 0% | **10.3%** | (v11 liiga permissiivne) |

## Tõlgendus

**v12 on tugev paranemine v11 üle** — FAPH pool, Ode recall +27pp, HN Isa −33pp. Ainuke kadu on Isa recall −10pp (100→90%) mis on talutav kuna Isa XTTS oli "liiga kerge" test.

FRR@1FA/h = 10.3% on realistlik operating point — 90% recall korral 1 valetriggeri tunnis. v11 FRR 0% tähendas et mudel polnud ise thresholdi suhtes diskrimineeriv.

## Järgnev

v13a/v13b on SpecAugment ablatsioon v10 andmetel (mitte v12 andmetel). v14+ jätkab eksperimenteerimist.

Vaata ka: `wake-word/docs/MODEL_LINEAGE.md`
