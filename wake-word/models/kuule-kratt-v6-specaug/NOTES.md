# v6-specaug — VALESTI NIMETATUD (mitte puhas ablatsioon)

**Loodud:** 2026-04-12

## Hoiatus

See mudel EI OLE v6 + SpecAugment puhas ablatsioon. Andmed erinevad v6-st:

| | v6 | v6-specaug | Peaks olema |
|---|-----|-----------|-------------|
| Positives | 2241 | **3343** | 2241 |
| Negatives | 10228 | **9160** | 10228 |

v6-specaug kasutab v8-era andmeid (sisaldab Mac + XTTS family positives), mitte v6 andmeid.

## Mida v6-specaug tegelikult on

- v8-era data (3343 pos / 9160 neg / 1002 ambient)
- SpecAugment ON (freq 2×3, time 2×10)
- Residual OFF
- Ühtegi eraldi hard_negative feature setti pole

## Puhas SpecAugment ablatsioon on PUUDU

Vajalik: v6 täpne andmestik (2241/10228) + ainult SpecAugment ON/OFF erinev. Nimetada `v6-specaug-clean`. Üks HPC submit.

Vaata ka: `wake-word/docs/MODEL_LINEAGE.md`
