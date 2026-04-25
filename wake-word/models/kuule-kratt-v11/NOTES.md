# v11 — deployed production model (Android + ESP32)

**Loodud:** 2026-04-11 08:27

**Deployed on:** Android Pixel 8a (false-trigger logger), ESP32-S3 Korvo-2 (voice satellite firmware)

## Discrepancy

`model_evaluation_results.json` kirjutab "residual" aga `training_config_snapshot.json` näitab `residual_connection: "0,0,0,0"` = **OFF**. Training config on ground truth.

## Arhitektuur

- mixednet 4×48f, **residual OFF**, SpecAugment OFF
- 2 feature setti (positive + negative), **ilma** eraldi hard_neg setita
- 10k steps, lr 0.001, batch 128

## Andmed

| Parameeter | Väärtus | vs v8 |
|------------|---------|-------|
| Positives | 3343 | sama |
| Negatives | 9160 | +576 |
| Hard neg (eraldi) | 0 | v8 oli 480 |
| Ambient | 1002 | sama |

## Bug: Riigikogu shuf failure (session-findings §3.6)

```bash
shuf --random-source=<(echo 42) | head -n 50
```

`echo 42` annab ainult 3 baiti entroopiat. GNU `shuf` vajab rohkem 1001 elemendi jaoks → fails silently → tühi Riigikogu subset. Lisaks: script globis `*.wav` aga Riigikogu failid on FLAC. **v11 treeniti ilma Riigikogu andmeteta.**

## Tulemus (benchmark 2026-04-21 @0.995)

| Mõõdik | Väärtus |
|--------|---------|
| FAPH CV | 79 |
| FAPH LS | 119 |
| FAPH DiP | 26 |
| Rec Isa | 100% |
| Rec Ode | 55% |
| Rec Mat | 92% |
| HN Mac | 87% |
| HN Isa | 98% |

DET: FRR@1FA/h = 0% — mudel on liiga permissiivne ("too permissive"). Triggerib liiga kergelt.

## Miks see deployed on

v11 oli esimene mudel mis "töötas piisavalt" real-time testimisel:
- Recall Isa 100% + Rec Mat 92% — enamik päris ütlusi läbib
- FAPH 79 — talutav kodukasutuses (~1.3 valetriggerit minutis → ärritav aga mitte katastroof)

Pole parim üheski mõõdikus, aga oli "good enough" hetkel kui deploy vajati.

## Tõlgendus

v11 on sisuliselt **v8-era andmed + rohkem neg + ilma hard_neg feature setita + 2 bugi** (Riigikogu puudub, residual discrepancy docs-is). Hoolimata bugiist on see praktikas OK sest:
1. Riigikogu polnud vajalik (v10 MUSAN bug näitas et massive neg scaling pole peamine faktor)
2. Hard_neg feature seti puudumine tähendab et mudel on permissiivne (HN Mac 87%, HN Isa 98%) aga see tuleb recalli kasuks

## Järgnev

v12 proovib peegelda v11 configi parandades bugi (Riigikogu + FLAC glob). v11 jääb deployed kuni konsensuse-põhine lähenemine on valmis.

Vaata ka: `wake-word/docs/MODEL_LINEAGE.md`
