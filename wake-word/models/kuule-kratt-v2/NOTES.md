# v2 — audio preprocessing experiment (silence trimming)

**Allikas:** `docs/thesis/thesis-tex-estonian/chapters/second_chapter.tex:71`

> "Versiooni v1 ja v2 andmestik oli identne; v2 erines ainult heli eeltöötluse poolest (vaikuse trimmimine klippide algusest ja lõpust)."

## Erinevused v1-st

| Parameeter | v1 | v2 |
|------------|-----|-----|
| Arhitektuur | identne | identne |
| Treeningusamplite arv | 915 pos / 3928 neg / 930 ambient | **identne arv** |
| Positiivsete audio | raw salvestused | **silence trimmed** (vaikus lõigatud algusest ja lõpust) |
| Hyperparameetrid | identsed | identsed |
| HPC run dir | `..-v1-20260319-160814` | `..-v2-20260319-170749` |

Config snapshotid on "identsed" sest preprocessing toimus FEATURE EXTRACTION ETAPIS enne mmap genereerimist — training flags ei tea sellest.

## Hypothesis

Kas silence trimming positiividel parandab mudelit? (vähem vaikuse pealt müra õppimist)

## Tulemus

- 2026-04-14 ambient sessioon (~34 min):
  - v1: 9 triggerit (~16 FAPH)
  - v2: 6 triggerit (~10.5 FAPH)
- v2 triggeris **vähem** kui v1 — silence trimming aitas natuke

**Kaveat:** erinevus võib olla kombinatsioon kahest asjast:
1. Silence trimmingu tegelik efekt
2. Training variance (sama recipe kaks korda annab erinevat tulemust)

Ilma seed-variance mõõtmiseta ei saa eristada. Kui silence trimming oleks olnud puhas ablatsioon, oleks vaja N seedi per config.

## Järgnev

v3 alates hakati lisama same-device (Korvo-2) negatiive — see oli peamine data scaling suund. Silence trimming jäi ilmselt permanent preprocessing-sammuks edaspidi (tasub kontrollida v3+ preprocessing pipelinest).

Vaata ka: `wake-word/docs/MODEL_LINEAGE.md`
