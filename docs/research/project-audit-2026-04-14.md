# Kratt Project Audit — 2026-04-14

> **Historical snapshot:** current status after v17/v18/checkpoint work is in `docs/PROJECT_TODO.md` and `docs/research/source-of-truth-apr-2026.md`.

Audit eesmärk: panna ühte kohta kokku projekti masinõppe areng, tegelik
timeline, git ajalugu, GitLabi tööpakid, Clockify ajakulu, hiljutised otsused,
aktiivsed töövood ja lahtised küsimused.

See ei asenda kitsamaid source-of-truth faile. See on süntees.

## Kasutatud allikad

- `git log`, `git status`, `git remote`, branchid, commitid
- `clockify-cli` projekti `Kratt` reportid
- GitLab `iaib` issue'd, milestones ja time tracking (`glab api`)
- `docs/PROJECT_TODO.md`
- `docs/research/source-of-truth-apr-2026.md`
- `docs/research/session-findings-apr-2026.md`
- `docs/research/wake-word-evaluation-methodology.md`
- `wake-word/docs/MODEL_LINEAGE.md`
- `wake-word/docs/DATA_TIMELINE.md`
- `wake-word/evaluation/training_data_manifest.md`
- `wake-word/evaluation/supervisor_table.md`

## TL;DR

Projekt on liikunud neljas faasis:

1. **Uurimisetapp / voice assistant prototüübid**  
   Detsember 2025. Fookus oli STT, Wyoming, HA voice pipeline, Whisper,
   olemasolevate lahenduste audit.

2. **Monorepo + TTS-andmestik + wake-word-first kitsendamine**  
   Veebruar 2026. Reaalne fookus nihkus "üldisest assistendist"
   eestikeelse wake-word'i poole.

3. **Päris wake-word pipeline + sama-seadme andmed + v1-v7**  
   Märts 2026. Treeningu/evaluatsiooni toru, Korvo-2 recorder firmware,
   esimene mudeliseeria ja sama-seadme andmete mõju õppimine.

4. **Metoodiline audit + benchmark rebuild + MoE konsensus**  
   Aprill 2026. Canonical streaming FAPH, held-out test setid, residual ja
   SpecAugment ablatsioonid, Android false-trigger logger, expert-mudelid.

Kõige olulisem sisuline järeldus:
- projekti suurim "läbimurre" ei olnud üksik mudel, vaid hindamismetoodika
  parandamine ja sealt edasi teadlik liikumine multi-model consensus suunas.

## Mis on siin juba küpsenud

### 1. Wake-word pipeline on nüüd päris uurimistoru

See ei ole enam katsekood.

Olemas on:
- treeninguskriptid ja HPC submit workflow'd
- held-out test set registry
- canonical streaming FAPH benchmark
- benchmark artefaktid (`supervisor_table.md`, `model_evaluation_results.json`)
- andme- ja mudeliajaloole eraldi kirjelduskihid

See tähendab, et projektil on nüüd reprodutseeritav uurimisloogika, mitte ainult
üksikud "good-looking" tulemused.

### 2. Instrumentatsioon päriselu jaoks on tugev

Kaks olulist väljatulekut:
- **ESP32-S3 Korvo-2 recorder / logger / speaker-test / wake-word-logger**
- **Android 24/7 false-trigger logger**

See on oluline, sest projekt ei sõltu enam ainult offline benchmarkidest.
Päris seadmelt saab koguda:
- uusi treeningandmeid
- false accept klippe
- deployment-domain signaali

### 3. Metoodiline baas on lukku löödud

Praegused püsivad otsused:
- baseline = **streaming FAPH**, mitte clip-level reset/FPR
- raporteeri koos: **FAPH + Recall + Hard-negative FPR**
- üks benchmark ei ennusta päris elu
- residual connections on treeningus vaikimisi **ON**
- programmiline suund = **multi-model consensus**

See on kirjas ka `source-of-truth-apr-2026.md` failis.

## Timeline

### Faas A — Detsember 2025: voice assistant probleemiruum

Git:
- `ca30635` init with readme
- `078f856` whisper experiments + gitlab time log script

Clockify:
- `29:54:07`

GitLab teemad:
- olemasolevate assistentide audit
- TalTech NLP ressursside kaardistus
- Whisper ja Kiirkirjutaja
- Wyoming / HA voice pipeline

Töö sisuline olemus:
- veel mitte wake-word projekt kitsas mõttes
- otsiti, mis osa eestikeelsest assistendist on puudu

Küpsenud järeldus:
- STT olemasolu tõttu ei ole peamine panus "veel üks STT", vaid wake word

### Faas B — Veebruar 2026: monorepo ja wake-word-first formaliseerimine

Git:
- `9267c43` / `8460996` / `efc0226` monorepo + migratsioon
- `e60825c` Neurokõne API
- `c8236d2` iteratiivne andmestrateegia
- `954f9f8` phase 1 dataset generation

Clockify:
- projekti `Kratt` all **0h**

Oluline märkus:
- see ei tähenda, et tööd polnud; git näitab palju tegevust
- pigem on siin time tracking lünk või kasutati tol hetkel teist projekti/logimisrada

Sisuline nihe:
- "üldine voice assistant" -> "Kuule Kratt" wake word kui põhikontribuution
- TTS-andmed ja iteratiivne data strategy said põhisambaks

### Faas C — Märts 2026: toru rekonstrueerimine, firmware, v1-v7

Git:
- `bab6de9` wake-word training pipeline + eval tooling
- `802987d` Korvo-2 recorder/test firmware
- `d3565d4` kuule-kratt training pipeline + data tools

Clockify:
- `57:37:26`

Peamised sündmused:
- Korvo-2 recorder firmware ja audio debugging
- v1/v2 baseline mudelid
- sama-seadme negatiivide lisamine (v3, v4)
- TTS positives + hard negatives (v5)
- v6 "läbimurre"
- v7 SpecAugment + suurem hard-neg pool

Sisulised leiud:
- väike kogus sama-seadme negatiive võib teha asja hullemaks
- hard negatives annavad päris sisulist kasu
- clip-level mõõdikud on ohtlikult eksitavad

### Faas D — Aprill 2026: metoodika audit ja MoE

Git:
- `371bc3f` streaming FAPH benchmark + held-out test sets
- `6e76e0a` canonical FAPH fix
- `3b125ea`, `7a090d1` Android false-trigger logger
- `7c3ed4c` residual ON by default

Clockify:
- `74:45:00` seisuga 2026-04-14 õhtu

Peamised sündmused:
- hindamismetoodika audit ja leakage avastus
- benchmark rebuild
- residual ja SpecAugment ablatsioonid
- `expert-a`, `expert-b2` ja konsensuskatsetused
- patched openWakeWord path
- Android logger + benchmark ingestion tooling

Peamine sisuline järeldus:
- üksainus väike mudel ei paista suutvat korraga anda väga madalat FAPH-i,
  head recall'i ja head hard-neg rejection'it
- seetõttu on praegune suund **tahtlikud eksperdid + consensus**

## Masinõppe arengujoon

### Andmete areng

Andmetes on olnud neli suurt lainet:

1. **Neurokõne TTS**
2. **Korvo-2 päris andmed**
3. **Mac + XTTS family clone data**
4. **Mined false accepts + benchmark corpora**

Põhitrend:
- algne optimism TTS suhtes on asendunud palju ettevaatlikuma kasutusega
- reaalkõne peab domineerima vähemalt gatekeeper tüüpi mudelites
- hard negatives peavad olema eraldi käsitletud dimensioon, mitte lihtsalt
  "veel negatiive"

### Mudelite areng

Lineage'i järgi:
- `v1-v2`: baseline ja preprocessing
- `v3-v4`: sama-seadme negatiivide osakaal
- `v5-v6`: hard negatives + KORVO session2
- `v7`: konservatiivne tradeoff, parem FAPH, halb recall
- `v8-v10`: paradigma vahetus andmejaotuses
- `v6-residual`, `v13a`, `v13b`: puhtad ablatsioonid
- `v14-v16`: hard-neg ratio, laiemad mudelid, erinevad andmekombinatsioonid
- `expert-a`, `expert-b2`, `ex2a`, `ex3a/b`: spetsialiseeritud ekspertmudelid

### Benchmark snapshot

`supervisor_table.md` põhjal:
- parimad üksikud FAPH mudelid ei ole automaatselt parimad päriselus
- `v6-residual` on tugev single-model kandidaat
- `expert-a` on tugev gatekeeper
- `expert-b2` on tugev verifier hard-neg suhtes
- `ex3a + expert-a + expert-b2` tüüpi consensus read näitavad, et
  sub-1 FAPH on võimalik, aga recall jääb probleemiks

## Mis on praegu küpsemas

Praegune dirty worktree näitab kolme aktiivset fronti.

### 1. Android liigub multi-model detektsioonile

Tööpuus:
- `WakeDetector.kt` eemaldub
- asemele `MultiDetector.kt` + `ModelRunner.kt`
- service/UI/logging liiguvad mitme mudeli score'ide ja trigger-modeli salvestamise suunas

Tähendus:
- Android ei ole enam ainult single-model false logger
- sellest saab consensus deployment / field benchmark tööriist

### 2. openWakeWord on aktiivne, aga patchitud kõrvalharu

Tööpuus:
- config dokumenteerib upstream probleeme
- submit skript teeb 16kHz resample koopiad
- patched train script parandab Piper importi, batch configi, validation featuresi jne

Tähendus:
- openWakeWord ei ole peamine rada
- aga seda kasutatakse võrdlusraamistiku ja võimaliku alternatiivse
  arhitektuuri kontrollimiseks

### 3. Benchmarking ja source-of-truth docs kasvavad kiiresti

Untracked / local artefaktid:
- `source-of-truth-apr-2026.md`
- `session-findings-apr-2026.md`
- `next-steps-apr-2026.md`
- `MODEL_LINEAGE.md`, `DATA_TIMELINE.md`
- benchmark tabelid, curves, JSON tulemused

Tähendus:
- projekt on jõudnud faasi, kus mõte on rohkem süstematiseerida,
  koondada ja otsuseid kinnistada

## Hiljutised lukku löödud otsused

Need paistavad välja nii docs'ist kui ka hiljutisest gitist:

1. **Canonical streaming FAPH** on uus baas
2. **Residual ON by default**
3. **Consensus > single best model**
4. **Eval ingestion peab olema recursive (`rglob`)**
5. **Mõõtmised tuleb salvestada artefaktidesse**
6. **Mic symmetry + dedup + "Kuule Kratt only" label guardrails jäävad**

## Lahtised küsimused

### Teaduslik / ML

- Kuidas tõsta recall'i ilma FAPH-i uuesti lõhkumata?
- Kas consensus arhitektuur jääb 2 eksperdi peale või vajab 3-astmelist gate'i?
- Kui suur roll on VTLP-l ja augmentationi parandustel võrreldes lihtsalt
  suurema speaker-diversityga?
- Kas openWakeWord annab päriselt lisaväärtust või ainult võrdlusmaterjali?

### Andmestik

- KORVO-2 truly held-out negatiivne sessioon on puudu
- päris kõnelejaid on liiga vähe
- Android capture'id vajavad labeling'ut
- `training_data_manifest.md` ja lineage ei kata veel kogu uut mudeliseeriat

### Thesis / delivery

- taustapeatükk on ametlikult veel lahti
- user testing on endiselt kriitiline tee
- osa source-of-truth dokumente elab veel untracked tööpuus, mitte main branchis

## Töövood

Praegune praktiline töövoog näib olevat selline:

1. **Andmekogumine / data prep**
   - Korvo-2 recorder
   - XTTS / TTS tooling
   - Android false accept mining

2. **Treening**
   - `kratt train` / HPC submit
   - mitmed dataset presetid, negatiivsete allikate lülitid

3. **Evaluatsioon**
   - held-out test set registry
   - streaming FAPH benchmark
   - supervisor tabel / DET curve / JSON artefaktid

4. **Live deployment checks**
   - `kratt live`
   - Android logger
   - ESP32 / ESPHome / Korvo-2

5. **Decision capture**
   - `source-of-truth` docs
   - thesis update
   - GitLab issue'd

## Git / Clockify / GitLab audit

### Git

Commitid kuude lõikes:
- 2025-12: 7
- 2026-01: 1
- 2026-02: 20
- 2026-03: 17
- 2026-04: 25

See kinnitab, et kõige intensiivsem tehniline areng on toimunud aprillis.

### Clockify

Projekti `Kratt` ajakulu seisuga 2026-04-14 õhtu:
- **kokku:** `162:16:33`
- **2025-12:** `29:54:07`
- **2026-03:** `57:37:26`
- **2026-04:** `74:45:00`
- **2026-02:** `0:00:00` project-level reportis

Oluline tähelepanek:
- veebruari 0h on ilmselgelt tracking anomaly võrreldes giti ja docs'iga

### GitLab

`iaib` issue time tracking:
- **kokku:** `181h 9m`
- aktiivne milestone: **Lõputöö 12 EAP (312h)**, due `2026-06-01`
- estimates on tugevalt alahinnatud: progress on `227%`

Suurimad tööpakid:
- `#18` Wake-word pipeline hardening and ambient evaluation — `72h`
- `#19` Thesis drafting and framework comparison — `21h`
- `#20` Home Assistant voice pipeline seadistamine — `13h`
- `#24` Multi-engine TTS ablation — `8h`
- `#25` Streaming FAPH methodology and multi-domain benchmark — `8h`
- `#27` Multi-model consensus (MoE) — `8h`

### Backfill 2026-04-14 auditikäigus

Clockify'sse lisati konservatiivselt:
- `2026-04-13 11:00-15:00`  
  `ML state audit, source-of-truth docs consolidation, benchmark/consensus findings review, README/CLAUDE alignment`
- `2026-04-14 17:30-21:15`  
  `Repo+ML+timeline audit, hidden Claude/Serena state review, Git/Clockify/GitLab reconciliation, README refresh`

Pärast backfilli:
- `2026-04-13` + `2026-04-14` kokku = `17:15:00`

## Kokkuvõte

Kui väga lühidalt öelda, siis:

- projekt **ei ole enam prototüüp**
- projekt **ei ole veel valmis toode**
- projekt on praegu tugevas uurimis-küpsemise faasis, kus
  metoodika, benchmarkid ja instrumentatsioon on juba tugevad,
  kuid deployment-quality recall ja lõputöö viimased nõuded on endiselt lahti

Praegune suurim sisuline küsimus ei ole enam:
- "kas eestikeelne wake word on üldse võimalik?"

vaid:
- "millise arhitektuuri ja andmestrateegiaga saab deployment-kõlbuliku
  recall/FAPH/hard-neg tasakaalu päris kõnelejatel?"
