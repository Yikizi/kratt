# Wake Word

Last updated: 2026-04-29

`wake-word/` on Kratti põhikaust: andmestik, treeningskriptid, evaluatsioon ja
versioneeritud mudelid fraasile **"Kuule Kratt"**.

Kiire joondus enne uut tööd:

1. `../docs/PROJECT_TODO.md`
2. `../docs/research/source-of-truth-apr-2026.md`
3. `docs/MODEL_LINEAGE.md`
4. `DATA_STRATEGY.md`
5. `CLAUDE.md`

## Current State

- Canonical baseline is **streaming FAPH**, not clip-level FPR.
- Model choice is judged by the trio: `FAPH + Recall + Hard/prefix/confusable FPR`.
- `v16c` is the stable single-model baseline / active demo candidate.
- v17/v18/checkpoint runs are diagnostic:
  - v17 exposed positive-label corruption,
  - v18 showed clean positives are necessary but not sufficient,
  - checkpoint-FAPH showed that low ambient FAPH can come with recall collapse.
- No current model should be described as production-ready without final user-test evidence.
- User testing is now the main data path; see `../docs/user-testing/ten-minute-shadow-demo-protocol.md`.

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
./cli/kratt compare v16c expert-a -t 0.995
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

Benchmark subset:

```bash
cd wake-word
uv run python evaluation/benchmark_all_models.py --models v16c expert-a expert-b2
```

Saada uus microWakeWord treening HPC-sse ainult siis, kui thesis schedule lubab:

```bash
cd ..
./cli/kratt train v19a --dataset-preset recall-cv --dry-run
```

Labelled user-test recording:

```bash
cd ..
./cli/kratt user-test P01 --active-model v16c --new-session-subdir
```

Android loggeri capture'ite analüüs:

```bash
cd ..
./cli/kratt android pull
```

## Data / Training Layout

Olulised alajaotused:

- `data/collection/` — salvestus-, TTS- ja andmeettevalmistuse skriptid.
- `data/validation/` — positive audit, strict-positive builder, prefix/confusable regression builder.
- `training/configs/` — microWakeWord ja openWakeWord konfiguratsioonid.
- `training/scripts/` — mmap generation, HPC submitid, treeningu wrapperid.
- `evaluation/` — benchmarkid, Android capture labeling, DET/FAPH raportid.
- `models/` — mudeliversioonid koos `.tflite` failide ja `analysis/` kokkuvõtetega.
- `docs/` — wake-word-spetsiifiline taustainfo nagu model lineage ja auditid.

Kui treenid HPC peal, kasuta `KRATT_DATA` andmejuurt. Treeningskriptid eeldavad,
et `processed`, `datasets`, `training/features` ja `training/runs` elavad selle
juure all.

## Non-Negotiable Evaluation Rules

- Ära mõõda treeningandmetel.
- FAPH mõõda pideval voolul, mitte reset-per-clip loogikaga.
- Sama thresholdi juures raporteeri koos `FAPH`, `Recall` ja `Hard/prefix/confusable FPR`.
- Thresholdid tuleb final-claimi jaoks enne test-seti raporteerimist külmutada.
- Hoia benchmarki tulemused artefaktides, mitte ainult sessioonijutus.
- Märgi diagnostic-only tulemused selgelt, kui test set võib treeningallikaga kattuda.

## Documentation

- `CLAUDE.md` — lühike operator context selle kausta jaoks.
- `docs/MODEL_LINEAGE.md` — mudeliversioonide kronoloogiline areng.
- `evaluation/training_data_manifest.md` — mida mingi mudel või benchmark tegelikult kasutas.
- `DATA_STRATEGY.md` — current data/quality policy.
- `../scripts/docs_freshness_audit.py` — kiire kontroll, mis aitab märgata vananenud setup-juhiseid ja protsessidokke.
