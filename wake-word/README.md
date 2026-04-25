# Wake Word

Last updated: 2026-04-23

`wake-word/` on Kratti põhikaust: andmestik, treeningskriptid, evaluatsioon ja
versioneeritud mudelid fraasile **"Kuule Kratt"**.

See README kirjeldab praegust töövoogu. Kui vajad kiiret joondust üle repo,
loe esmalt:

1. `../docs/PROJECT_TODO.md`
2. `../docs/research/source-of-truth-apr-2026.md`
3. `../docs/research/wake-word-evaluation-methodology.md`
4. `CLAUDE.md`

## Current State

- Canonical baseline on **streaming FAPH**, mitte clip-level FPR.
- Mudelite võrdlus käib koos mõõdikutega:
  `FAPH + Recall + Hard-negative FPR`.
- Üksik “parim mudel” ei ole enam põhiline eesmärk; suund on
  **multi-model consensus**.
- `v16c` on värskeim single-model kandidaat.
- `expert-a + expert-b2` konsensus saavutas sub-1 FAPH benchmarkis, aga vajab
  jätkuvalt päris seadme valideerimist.

## Setup

Põhikeskkond:

```bash
cd wake-word
uv sync
```

Mõned evaluatsiooni- ja live-skriptid kasutavad eraldi microWakeWord env'i:

```bash
cd ..
./wake-word/training/scripts/setup_microwakeword_env.sh
```

## Common Workflows

Võrdle mudeleid CLI kaudu:

```bash
cd ..
./cli/kratt compare v16a v16c -t 0.997
```

Live test ühe mudeliga:

```bash
cd ..
./cli/kratt live v16c 0.997
```

Live test mitme mudeli konsensusega:

```bash
cd wake-word
uv run python evaluation/multi_model_live_test.py --models expert-a expert-b2 --thresholds 0.996 0.996
```

Saada uus microWakeWord treening HPC-sse:

```bash
cd ..
./cli/kratt train v17 --steps 15000 --mem 64G
```

Android loggeri capture'ite analüüs:

```bash
cd ..
./cli/kratt android pull
```

## Data / Training Layout

Olulised alajaotused:

- `data/collection/`
  Salvestus-, TTS- ja andmeettevalmistuse skriptid.
- `training/configs/`
  microWakeWord ja openWakeWord konfiguratsioonid.
- `training/scripts/`
  mmap generation, HPC submitid, treeningu wrapperid.
- `evaluation/`
  benchmarkid, Android capture labeling, DET/FAPH raportid.
- `models/`
  mudeliversioonid koos `.tflite` failide ja `analysis/` kokkuvõtetega.
- `docs/`
  wake-word-spetsiifiline taustainfo nagu model lineage.

Kui treenid HPC peal, kasuta `KRATT_DATA` andmejuurt. Treeningskriptid eeldavad,
et `processed`, `datasets`, `training/features` ja `training/runs` elavad selle
juure all.

## Non-Negotiable Evaluation Rules

- Ära mõõda treeningandmetel.
- FAPH mõõda pideval voolul, mitte reset-per-clip loogikaga.
- Sama thresholdi juures raporteeri koos `FAPH`, `Recall` ja
  `Hard-negative FPR`.
- Hoia benchmarki tulemused artefaktides, mitte ainult sessioonijutus.

## Documentation

- `CLAUDE.md`
  lühike operator context selle kausta jaoks.
- `docs/MODEL_LINEAGE.md`
  mudeliversioonide kronoloogiline areng.
- `evaluation/training_data_manifest.md`
  mida mingi mudel või benchmark tegelikult kasutas.
- `../scripts/docs_freshness_audit.py`
  kiire kontroll, mis aitab märgata vananenud setup-juhiseid ja protsessidokke.
