# Kratt

Monorepo eestikeelse wake-word projekti jaoks. Praegune praktiline fookus on
fraasil **"Kuule Kratt"**: mudelite treenimine, korrektne evaluatsioon,
Android/ESP32 välitestid ja lõputöö kirjutamine.

See repo ei ole enam ainult "bakalaureusetöö skeleton". See on aktiivne
uurimis- ja tööjaam, kus koos elavad:
- wake-word treening ja benchmarkid
- Android false-trigger logger
- ESP32-S3 / ESPHome deploy
- demo pipeline (wake word -> STT -> LLM -> action)
- thesis / research docs

## Praegune seis

- Canonical evaluatsioon on **streaming FAPH**, mitte clip-level FPR.
- Mudeleid võrreldakse **FAPH + recall + hard-negative FPR** kombinatsioonina,
  samal deployment thresholdil.
- Suund on nihkunud ühe "parima universaalse mudeli" otsimiselt
  **multi-model consensus** lahenduste poole.
- Päris seadme ja päris maailma mõõtmine toimub peamiselt
  **Android false-loggeri** ja **ESP32-S3 Korvo-2** peal.
- `home-assistant/` on praegu pigem plaan / blueprint; päris deploy tee käib
  peamiselt `hardware/esp32/esphome/` ja demo tooling'u kaudu.

## Source Of Truth

Kui tahad enne uut tööd kiiresti joonduda, loe neid selles järjekorras:

1. [docs/PROJECT_TODO.md](docs/PROJECT_TODO.md)
2. [docs/research/source-of-truth-apr-2026.md](docs/research/source-of-truth-apr-2026.md)
3. [docs/research/wake-word-evaluation-methodology.md](docs/research/wake-word-evaluation-methodology.md)
4. [docs/research/session-findings-apr-2026.md](docs/research/session-findings-apr-2026.md)
5. [wake-word/CLAUDE.md](wake-word/CLAUDE.md)

Dokumentatsiooni reegel:
- `docs/` = hooldatud, jagatav, pikema elueaga dokumentatsioon
- `notes/` = tööpäevik, katsed, visandid, vahepealsed mõtted

## Repo Kaart

Peamised kaustad päris kasutuses:

- `wake-word/`  
  Projekti tuum: data, training, evaluation, versioneeritud mudelid.

- `cli/`  
  `./cli/kratt` gateway enamiku igapäevaste töövoogude jaoks.

- `android/`  
  Pixel/Android false-trigger logger, mis jookseb TFLite mudelitega ja kogub
  `events.jsonl` + WAV snippet'e.

- `hardware/esp32/`  
  ESPHome voice satellite configid ja ESP-IDF firmware utiliidid
  (`recorder`, `wake-word-logger`, `speaker-test`, `mic-test`, jne).

- `tools/`  
  Demo pipeline, WiZ kontroll, TTS server, LLM/STT benchmarkid.

- `stt-integration/`  
  Kiirkirjutaja Wyoming/STT integratsiooni materjal.

- `docs/`  
  Research, thesis, user-testing, ADR-id, esitlusmaterjalid.

- `notes/`  
  Eksperimendimärkmed ja töölogi.

- `external-repos/`  
  Vendordatud / peegeldatud sõltuvused nagu `microWakeWord`,
  `openWakeWord` ja vana `iaib-proto`.

- `output/`  
  Pullitud Android capture'id, demo logid ja muud jooksu-artefaktid.

Kaustad, mida vanad dokid veel mainivad, aga mis pole enam päriselt top-level
osas aktiivsed: `backend/`, `experiments/`, `tests/`.

## Kohalikud Peidetud Kaustad

Need on tööriistade artefaktid, mitte toote osa:

- `.claude/`  
  Claude Code local hook'id, settings ja worktree snapshotid.

- `.serena/`  
  Serena projektikonf + lühikesed püsivad mälud/strateegiamärkmed.

Oluline tähelepanek:
- `.claude/worktrees/agent-adf0f5ad/` on vana worktree snapshot, mis on
  praegusest `main`-ist maas. Seda ei tasu võtta source-of-truth'ina.

## Setup

Eeldused:
- Python `3.10` kuni `3.12`
- `uv`
- vajadusel `adb`, `esphome`, `ssh`, `ollama`

Põhiline setup:

```bash
git clone <repo-url> kratt
cd kratt

# Core Python env enamiku Python tooling'u jaoks
cd wake-word
uv sync
cd ..

# microWakeWord env, mida kasutavad live/compare skriptid
./wake-word/training/scripts/setup_microwakeword_env.sh

# Vaata saadaval käske
./cli/kratt help
./cli/kratt models
```

Andmeradade loogika:
- lokaalselt on vaikimisi data juur `wake-word/data/`
- HPC peal saab seda üle kirjutada `KRATT_DATA` env var'iga
- teised abikaustad (`processed`, `datasets`, `training/runs`) tulenevad sellest

## Levinud Töövood

```bash
# Võrdle mudeleid held-out test setidel
./cli/kratt compare v15 v16a -t 0.997

# Live test MacBooki mikrofoniga
./cli/kratt live v16c 0.997

# Saada uus treening HPC-sse
./cli/kratt train v17 --steps 15000 --mem 64G

# Build + install Android false-logger
./cli/kratt android install

# Tõmba Android capture'id ja analüüsi need ära
./cli/kratt android pull

# Flashi mudel ESP32-S3 Korvo-2 peale
./cli/kratt flash v16c --cutoff 0.997

# Käivita täis demo pipeline
./cli/kratt demo --wiz --models v15
```

Märkused:
- `kratt train` eeldab SSH ligipääsu TalTech HPC-sse.
- `kratt compare` ja `kratt live` kasutavad `.venv-microwakeword` env'i.
- `kratt android pull` teeb lisaks automaatselt indekseerimise ja FAPH kokkuvõtte.

## Evaluatsiooni Põhireeglid

Need on repo tänase tööviisi jaoks sisuliselt invariandid:

- Ära mõõda treeningandmetel; test setid peavad olema held-out.
- FAPH mõõda pideval voolul, mitte reset-per-clip loogikaga.
- Sama thresholdi juures raporteeri koos:
  `FAPH`, `Recall`, `Hard-negative FPR`.
- Benchmark üksi ei ennusta päris elu; live-domain mõõtmine on kohustuslik.

Vaata:
- [wake-word/evaluation/test_sets.py](wake-word/evaluation/test_sets.py)
- [wake-word/evaluation/compare_models.py](wake-word/evaluation/compare_models.py)
- [wake-word/evaluation/run_faph_test.py](wake-word/evaluation/run_faph_test.py)

## Dokumentatsioon Kiireks Orienteerumiseks

- [docs/research/android-false-trigger-logger-mvp-plan.md](docs/research/android-false-trigger-logger-mvp-plan.md)
- [docs/user-testing/portable-setup.md](docs/user-testing/portable-setup.md)
- [hardware/esp32/esphome/README.md](hardware/esp32/esphome/README.md)
- [stt-integration/README.md](stt-integration/README.md)
- [external-repos/README.md](external-repos/README.md)

## Lühikokkuvõte

Kui sa alustad nullist, siis õige vaimne mudel on:

1. `wake-word/` on projekti tuum.
2. `./cli/kratt` on praktiline sissepääs.
3. `docs/PROJECT_TODO.md` ja `docs/research/source-of-truth-apr-2026.md`
   on kõige olulisemad joondusdokid.
4. `android/` ja `hardware/esp32/` annavad päris maailma signaali sellest,
   kas mudel on kasutatav või ainult benchmark'is ilus.
