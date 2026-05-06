# Kratt repo kokkuvõte ja esitlusbrief

See fail on mõeldud kahele kasutusele:

1. anda NotebookLM-ile või mõnele teisele abivahendile kogu projekti kompaktne kontekst;
2. anda autorile endale selge narratiiv 10-minutilise vahekaitsmise jaoks.

## Ühe lõiguga kokkuvõte

Kratt on bakalaureusetöö projekt, mille eesmärk on luua eestikeelne äratussõna mudel fraasile "Kuule Kratt" ja lõimida see Home Assistanti lokaalsesse hääljuhtimisse ESP32-S3-Korvo-2 seadme abil. Projekti käigus selgus, et põhiprobleem ei olnud ainult väikese keele andmepuudus, vaid ka see, kuidas wake word mudelit metodoloogiliselt korrektselt hinnata. Töö tulemusena rekonstrueeriti ja parandati microWakeWord-põhine treeningu- ja hindamistoru, valideeriti see avaliku `marvin` sanity-check eksperimendiga, ehitati iteratiivne eestikeelne andmestik ning treeniti kaheksa järjestikust mudeliversiooni. Vahekaitsmise ajal tundus v6 olevat parim mudel, kuid hilisem audit avastas hindamises süstemaatilise andmelekke (test set kattus treeningandmetega). Korrigeeritud truly-held-out hindamine näitab, et v7 saavutab parima FAPH (96 vs v6 154 tunni kohta CV ET 3,82h voogedastusrajal) ja v8 parima foneetilise eristuse reaalsetel hard negatiivsetel (33% vs v6 100%). Selle metoodikalise vea avastamine ja parandamine on töö üks olulisemaid leide. Lisaks saadi mudel tööle ESP32-S3-Korvo-2 peal ning ehitati eraldi recorder firmware uute pärisandmete kogumiseks.

## Mis selles repos tegelikult oluline on

### Põhikomponendid

- `wake-word/`
  - mudeli arendus, andmete ettevalmistus, treening, evaluatsioon
- `hardware/esp32/`
  - ESPHome konfiguratsioonid ja Korvo-2 firmware katsed
- `stt-integration/`
  - lokaalse STT poole katsetused ja Kiirkirjutaja sidumine
- `docs/thesis/`
  - lõputöö tekst, tulemused ja esitlusmaterjalid
- `notes/`
  - tööpäevik ja eksperimendimärkmed

### Mis EI ole peamine panus

- täiemahuline STT/TTS süsteem
- pilveassistendid
- backend või laiem rakenduseökosüsteem
- kogu varane katseajalugu kui eraldi tulemus

Need olid kas toetavad eksperimendid või kõrvalharud.

## Git ajaloo põhjal projekti arengufaasid

### 1. Probleemi sõnastamine ja varased katsed

**Detsember 2025 - jaanuar 2026**

Olulisemad sammud:
- esialgne README ja probleemikirjeldus
- varased Whisper/STT eksperimendid
- erinevate voice assistant lahenduste kaardistus

Mida see faas andis:
- probleem sai sõnastatud kui "eestikeelne lokaalne wake word", mitte üldine voice assistant.

Mida see faas EI andnud:
- töötavat wake word süsteemi
- usaldusväärset andmestrateegiat

### 2. Monorepo ja töö formaliseerimine

**4.-5. veebruar 2026**

Olulisemad sammud:
- monorepo struktuur
- ülesandepüstitus
- wake-word skriptide migratsioon
- iteratiivse andmekogumise strateegia
- Neurokõne API ja TTS pipeline

Mida see faas andis:
- projekt muutus ad hoc katsetest teadlikult struktureeritud tööks.

Risk:
- liiga suur ulatus. Repos oli korraga palju suundi, kuid praktiline fookus polnud veel piisavalt kitsas.

### 3. Esimene päris riistvarakatse Korvo-2 peal

**12.-13. veebruar 2026**

Oluline katse:
- ESP32-S3-Korvo-2 + ESPHome voice satellite + microWakeWord

Mis töötas:
- UART flashimine
- WiFi ühendus 2.4 GHz võrgus
- sisseehitatud `okay_nabu` wake word
- HA voice satellite toru põhimõtteline toimimine

Mis ei töötanud:
- custom `kratt` mudel ei triggerdanud usaldusväärselt

Järeldus:
- probleem ei olnud ainult deploys; oli tugev kahtlus, et tegu on domeeninihkega päris seadme ja treeningandmete vahel.

Allikas:
- `notes/experiments/2026-02-12-esp32-s3-korvo2-voice-satellite.md`

### 4. Toru rekonstrueerimine ja sanity-check

**märtsi algus 2026**

Olulisemad sammud:
- treeningu- ja evaluatsioonitoru korrastamine
- `marvin` sanity-check avaliku Speech Commands andmestikuga
- ROC, threshold ja ambient-eval raportite automaatne genereerimine

Mis töötas:
- pärast parandusi tootis toru korrektsed mmap-id, TFLite mudeli ja analüüsiartefaktid

Mis ei töötanud enne seda:
- varasemad "head tulemused" olid osaliselt eksitavad, sest `testing_ambient` tugi oli katki või puudulik

Miks see on oluline:
- see faas muutis töö metoodiliselt kaitstavaks
- pärast seda ei saanud enam iga ebaõnnestumist automaatselt toru süüks ajada

Allikad:
- `wake-word/docs/microwakeword-sanity-check.md`
- `docs/thesis/thesis-tex-estonian/chapters/second_chapter.tex`

### 5. Eestikeelse mudeli iteratiivne arendus

**märtsi keskpaik - lõpp 2026**

Treeniti järjestikused versioonid:
- `v1`: baseline ainult Common Voice negatiividega
- `v3`: lisati väike kogus sama-seadme negatiive
- `v4`: lisati palju rohkem sama-seadme negatiive
- `v5`: lisati TTS positiivsed ja TTS hard negatives
- `v6`: lisati veel teine sama-seadme negatiivsete sessioon

Peamine leid:
- väike kogus sama-seadme negatiivseid tegi olukorra hullemaks
- piisavalt suur sama-seadme negatiivsete hulk ja hard negatives viisid läbimurdeni

See on kooskõlas "valley of degradation" nähtusega.

Allikad:
- `docs/thesis/thesis-tex-estonian/chapters/second_chapter.tex`
- `wake-word/models/kuule-kratt-v*/analysis/*`

### 6. Recorder firmware andmekogumiseks

**16.-17. märts 2026**

Eesmärk:
- ehitada Korvo-2 peale eraldi salvestusseade, millega koguda sama riistvara pealt uusi treeningandmeid

Mis töötas:
- SD-kaardile salvestamine
- kahe mikrofoni WAV-failid
- nuppudega juhtimine

Mis oli raske:
- TDM sloti kaardistus
- 16-bit vs 32-bit andmeformaat
- tegeliku sample rate'i ja bit clock'i viga

Miks see on oluline:
- see ei olnud lihtsalt firmware kõrvalprojekt, vaid kriitiline samm kvaliteetse sama-seadme andmestiku kogumiseks

Allikas:
- `notes/experiments/2026-03-16-korvo2-recorder-firmware.md`

## Peamised tehnilised asjad, mis töötasid

- `okay_nabu` töötas Korvo-2 peal, mis kinnitas seadme ja pipeline'i baasfunktsionaalsust
- public `marvin` sanity-check kinnitas, et local microWakeWord toru on paranduste järel toimiv
- v6 mudel saavutas tugeva tulemuse nii Common Voice kui sama-seadme negatiivsetel
- v6 mudel töötas ka MacBook Pro mikrofoniga esialgses ristseadme katses
- ESP32-S3-Korvo-2 deploy on olemas
- recorder firmware kaudu on võimalik koguda uut pärisandmestikku

## Peamised asjad, mis ei töötanud või osutusid eksitavaks

- varased custom `kratt` mudelid ei toiminud päris seadmel usaldusväärselt
- algne hinnang mudelitele oli osaliselt vigane, sest evaluatsioon ei olnud identne ega piisava ambient-toega
- v3 mudel näitas, et väike kogus in-domain negatiive võib mudeli ülevallandada
- ainult clip-level mõõdikutega ei ole wake word kvaliteeti usaldusväärne hinnata
- kogu probleem ei lahene lihtsalt "rohkemate andmetega"; andmetel peab olema õige roll

## Peamised sisulised õppetunnid

1. Wake word töö usaldusväärsus sõltub sama palju evaluatsioonist kui mudelist.
2. Päris seadme akustiline domeen peab olema treeningandmetes esindatud.
3. Sama-seadme andmete osakaal ei tohi jääda "natuke lisatud" tsooni.
4. Hard negatives on väikese sõnavaraga fraasi puhul väga väärtuslikud.
5. Riistvaraga seotud arendus ei olnud kõrvalteema, vaid otseselt seotud andmestiku kvaliteediga.

## Praegune hetkeseis

### Olemas

- töötav treeningu- ja raportitoru
- avaliku sanity-check'iga valideeritud pipeline
- kuus eestikeelset mudeliiteratsiooni
- tugev v6 mudel
- ESP32-S3-Korvo-2 deploy
- Home Assistanti lõimimise baas
- recorder firmware sama-seadme andmete kogumiseks

### Veel puudu

- suurem kasutaja- ja kõnelejatest
- laiem ristseadme test
- lõplik openWakeWord võrdlus
- täisteksti kirjutamise lõpetamine
- lõplik kasutajapõhine valideerimine

## Soovitatud 10 minuti narratiiv

Kui seda projekti esitleda 10 minutiga, siis kõige tugevam lugu on järgmine:

### 1. Probleem

Eestikeelse lokaalse voice assistant'i jaoks puudub äratussõna.

### 2. Tehniline väljakutse

Väikese keele ja mikrokontrolleri piirangute tõttu ei piisa olemasoleva ingliskeelse lahenduse kopeerimisest.

### 3. Metoodiline pööre

Selgus, et enne lõpliku mudeli arendamist tuli parandada treeningu- ja evaluatsioonitoru ennast.

### 4. Peamine leid

Sama-seadme negatiivsed andmed aitavad ainult siis, kui neid on piisavalt palju; liiga väike kogus viib degradatsiooni orgu.

### 5. Tulemus

v6 mudel töötab hästi ja on jooksutatud ESP32-S3-Korvo-2 peal.

### 6. Miks see töö on kaitstav juba praegu

Sest olemas on:
- töötav prototüüp,
- dokumenteeritud iteratsioon,
- selge metoodiline leid,
- reprodutseeritav tee, kuidas väikese keele wake word'i edasi arendada.

## Mida mitte üle rõhutada esitluses

- kogu monorepo struktuur
- varased STT kõrvalharud
- kõik commitid eraldi
- liiga detailne firmware debug
- kogu remaining work tabel minuti kaupa

Need on head küsimuste vooruks, aga mitte põhiloole.

## Kui seda faili kasutada NotebookLM-is

Parim kombinatsioon oleks:

- see fail
- `docs/thesis/presentation/vahekaitsmine-slaidid.md`
- `docs/projekti_kirjeldus.md`
- `wake-word/docs/microwakeword-sanity-check.md`
- `notes/experiments/2026-02-12-esp32-s3-korvo2-voice-satellite.md`
- `notes/experiments/2026-03-16-korvo2-recorder-firmware.md`
- `docs/thesis/thesis-tex-estonian/chapters/second_chapter.tex`
