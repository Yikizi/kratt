---
source_prompt: /Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/02_Ülesandepüstitus/Ülesandepüstituse_kontroll.txt
prompt_type: evaluative
generated: 2026-05-07
---

# Ülesandepüstituse kontroll — raport

Hinnatav dokument: `/Users/mattias/kratt/docs/thesis/thesis-tex-estonian/ylesandepystitus.tex` (peamine ülesandepüstituse fail). Toetava kontekstina vaadati ka `chapters/introduction.tex` ja eesti-/inglisekeelseid resümeesid, et kontrollida, kas ülesandepüstituses esitatud sihid ja eesmärgid vastavad töö praegusele suunale.

---

## 1. Päise kontroll (metaandmed)

Tiitellehel (`titlepage`) on olemas:

- **Töö tüüp** — ,,Bakalaureusetöö ülesandepüstitus'' (rida 41). **OLEMAS.**
- **Esialgne pealkiri** — `\thesisTitleEst` makrokäsuga (rida 37). Eeldatavasti pealkirja makro on defineeritud `config/config.tex` failis, st ülesandepüstituse mustandist endast pealkirja teksti otse ei näe; **vorminduslikult olemas, kuid mustandi lugejale läbipaistmatu** (vajab kontrolli, et `config.tex` sisaldab tegelikult lõplikku eestikeelset pealkirja, mitte näidisteksti).
- **Üliõpilane (autor)** — `\authorNameEst~\studentcodeEst` (rida 32). **OLEMAS** (eeldusel, et makrod on täidetud).
- **Juhendaja** — `\supervisorEst: \supervisorNameEst\\ \supervisortitleEst` (read 47–48). **OLEMAS**.

Märkus: Kuna kõik neli välja on makrokäskudena, ei saa otsustada, kas tegelikud stringid (autori täisnimi, juhendaja akadeemiline kraad, lõpliku pealkirja eesti vorming) on viimistletud. Soovitus: kinnita üks kord käsitsi, et `config/config.tex` sisaldab kõiki nelja välja **ilma näidisplatsiraha-tekstita** (nt ,,Eesnimi Perekonnanimi'').

---

## 2. Üldhinnang

Tugev tehniline ja sisuline alus: töö skoop (mikrokontrolleri-klassi eestikeelne äratussõna), eesmärk (mudel + lõimimine + valideerimine) ja piiritlus (ei käsitleta uut STT/TTS-i) on selgelt esitatud. Stiil on akadeemiline ja konkreetne. **Põhilised nõrkused** on aga kaks:

1. **Storytelling-loogika on osaliselt tagurpidi**: töö algab kohe ,,probleemiga'' (lokaalne nutikodu hääljuhtimine sõltub äratussõnast), aga **taust** (,,kuidas asju praegu tehakse?'') ja **motivatsioon** (,,miks see oluline on?'') jäävad implitsiitseks. Kui võrrelda `introduction.tex`-iga, siis seal on taust palju paremini välja kirjutatud (Picovoice/openWakeWord ei toeta eesti keelt, eesti ASR-il on korpused olemas, äratussõna on lünk) — see materjal tasub tõsta ka ülesandepüstitusse.
2. **Allikaid on ainult 4** (Kiirkirjutaja, microWakeWord, openWakeWord, Home Assistant). Nõue on **vähemalt 5**, ja praegu puuduvad metoodilised viited (nt deep KWS ülevaade, Speech Commands, FAPH-i kasutuse kohta).

Lisaks on **uurimisküsimus on sõnastatud, kuid ainult ühe lausega** (jaotis ,,Probleem'') ning töö ei vasta selgelt PICO/FINER-le. Ülesandepüstituses pole alaküsimusi nagu sissejuhatuses (introduction.tex sisaldab nelja alamküsimust, mis võiks ka siia üle tuua).

**Hinne praeguses seisus**: ,,hea alus, kuid ei ole ,suurepärane' — vajab täiendamist mahus 1–2 lehekülge ja viidete kasvatamist''.

---

## 3. Struktuuri analüüs (6 kohustuslikku elementi)

| # | Element | Olemas? | Kommentaar |
|---|---------|---------|------------|
| 1 | **Taust** (,,kuidas asju praegu tehakse'') | OSALISELT | Mainitakse, et microWakeWord ja openWakeWord on olemas (jaotis ,,Olemasolevate lahenduste analüüs''), kuid ei selgitata, kuidas eestikeelseid äratussõnu **praegu** tehakse (vastus: ei tehta lokaalselt — seda fakti tasub eraldi nimetada). Picovoice ja eestikeelsete keeleruumi tugi puuduvad allikatest täielikult. |
| 2 | **Motivatsioon** (,,miks oluline'') | NÕRK | Esimese lõigu lõpus mainitud privaatsus / lokaalsus, kuid mitte selgelt. Tuleks lisada lause-paar selle kohta, miks väikeste keelte (eesti) lokaalse hääljuhtimise tugi on oluline (privaatsus, sõltumatus pilvest, ligipääsetavus). |
| 3 | **Probleem (gap)** | OLEMAS | Jaotis ,,Probleem'' ütleb selgelt, et eestikeelse treeningandmete vähesus takistab olemasolevate lahenduste otsekasutamist. Hea, aga võiks olla teravam: ,,**eesti keel ei kuulu ühegi avatud raamistiku jaotatud äratussõna mudelite hulka**'' on tugevam ja tõestatav väide. |
| 4 | **Lahendus / Keerukus** | OLEMAS | Peatükk ,,Metoodika'' katab andmestiku, mudeliarenduse, lõimimise ja valideerimise. Tehniline keerukus (kvantiseerimine, sünteesitud andmete kvaliteedikontroll, MixConv) on välja toodud. |
| 5 | **Uudsus / Kasu** | OLEMAS | Peatükk ,,Oodatav panus'' — kahetine panus (tehniline + praktiline avatud lähtekoodiga väljund). Hea, kuid võiks lisada **kellele** see kasulik on (Eesti nutikodu kasutajad, eesti keele tehnoloogia kogukond, microWakeWord raamistiku kasutajad teiste väikeste keelte jaoks). |
| 6 | **Valideerimine** | OLEMAS | Peatükk ,,Tulemuste valideerimine'' kirjeldab kahetasandilist hindamist (tehniline + kasutuspõhine). **Puudub aga konkreetne mõõdik** (FAPH, recall) ja sihtväärtus, mis sissejuhatuses on välja toodud (FAPH < 1, recall ≥ 0,95). Ülesandepüstituse tasemel võiks vähemalt nimetada peamise mõõdiku. |

**Kokkuvõte**: 4/6 elementi on tugevalt olemas, 2 elementi (taust, motivatsioon) vajavad tugevdamist.

---

## 4. Uurimisküsimuste audit (PICO / FINER)

Ülesandepüstituses on **üks** uurimisküsimus jaotises ,,Probleem'':

> ,,kuidas töötada välja eestikeelse äratussõna lahendus, mis on ühtaegu tehniliselt täpne, süsteemselt lõimitav ja praktiliseks kasutuseks sobiv.''

### PICO-analüüs

- **P (Population)** — implitsiitne (eesti keele kasutajad / nutikodu kasutajad). **Ei ole sõnastatud**, peaks olema selge: ,,eesti keelt kõnelevad nutikodu kasutajad'' või veel täpsemalt ,,eestikeelsed kõnelejad ESP32-S3 klassi seadme mikrofonis''.
- **I (Intervention)** — ,,eestikeelse äratussõna lahendus'' (mudel + lõimimine). **Olemas, kuid ebamäärane** — peaks ütlema, et tegu on \texttt{microWakeWord}-baasil treenitud mudeliga.
- **C (Comparison)** — **PUUDUB**. Ei ole öeldud, mille vastu võrreldakse: olemasolev pilvepõhine lahendus? openWakeWord ingliskeelne mudel? Sissejuhatuses on viidatud \texttt{marvin}-kontrollkatsele ja Picovoice'i avalikele võrdlusalustele — see oleks loomulik C.
- **O (Outcome)** — ,,tehniliselt täpne, süsteemselt lõimitav ja praktiliseks kasutuseks sobiv'' on **liiga abstraktne**. Sissejuhatus annab konkreetsed mõõdikud (FAPH < 1, recall ≥ 0,95) — need tasub ülesandepüstituse uurimisküsimusse tuua, et O oleks mõõdetav.

### FINER-test

- **F (Feasible)** — JAH. Riistvara, raamistikud ja andmed on olemas; töö on faasis ,,User Testing & Thesis Writing'', st suurem osa on juba teostatud.
- **I (Interesting)** — JAH. Teema on Eesti keeleruumis lünga lahendamine.
- **N (Novel)** — JAH, **kuid uudsus pole tekstis selgelt välja toodud**. Tuleks lisada lause: ,,Käesoleva töö teadaolevalt esimene avalik eestikeelne äratussõna mudel mikrokontrolleri klassi seadmele.''
- **E (Ethical)** — Töö maandab privaatsusriske toorsalvestuste mitte-avalikustamisega (mainitud peatükis ,,Oodatav panus''). Hea. **Kasutajauuringu nõusoleku ja andmekaitse korraldus** võiks olla siiski lühidalt nimetatud, kui selles töös tehakse kasutajatestid.
- **R (Relevant)** — JAH. Vastab Home Assistanti ja eesti keele tehnoloogia kogukonna konkreetsele lüngale.

**Kokkuvõte uurimisküsimuste kohta**: küsimus on uuritav, kuid selle mõõdetavus (O) ja võrdluspunkt (C) on liiga lahjad. Soovitus: tõsta sissejuhatuse alaküsimuste loend (introduction.tex read 10–15) **ka** ülesandepüstitusse — neljast alamküsimusest annab kolm konkreetse mõõdetava väljundi.

---

## 5. Keeleline ja vormistuslik tagasiside

Üldine keelekvaliteet on hea — laused on selged, mitte kantseliitsed. Mõned konkreetsed kohad, mis vajavad ülevaatamist:

1. **Pikk ja koormatud lause peatükis ,,Probleem''** (rida 63):
    > ,,Lokaalse nutikodu hääljuhtimise kasutatavus sõltub suurel määral sellest, kas äratussõna tuvastus on stabiilne ja usaldusväärne. Eesti keele ja teiste väikeste keeleruumide kontekstis on tegemist olulise probleemiga, kuna spetsiifiliste treeningandmete vähesus takistab olemasolevate lahenduste otsekasutamist ja need ei taga samaaegselt piisavat mudeli kvaliteeti, süsteemi lihtsat lõimitavust ja reprodutseeritavat kasutuselevõttu.''

    *Probleem*: teine lause ahelduab kolm erinevat puudujääki (kvaliteet, lõimitavus, kasutuselevõtt) ühe ,,ja''-ga.
    *Parandus (näide)*: ,,Eesti keele ja teiste väikeste keeleruumide kontekstis on tegemist olulise probleemiga: spetsiifiliste treeningandmete vähesus takistab olemasolevate lahenduste otsekasutamist. Samal ajal ei taga ükski avalikult saadaolev mudel korraga piisavat tuvastustäpsust, lihtsat süsteemset lõimitavust ega reprodutseeritavat kasutuselevõttu.''

2. **Sõna ,,demonstreerival'' on kohmakas** (rida 73):
    > ,,mudeli rakendamist demonstreerival riistvaral''
    *Parandus*: ,,mudeli rakendamist sihtriistvaral (ESP32-S3-Korvo-2)'' — täpsem ja vähem kantseliitne.

3. **Tagasi-alustamine** peatükis ,,Töö eesmärk'' (rida 68):
    > ,,Töö eesmärk on töötada välja eestikeelne äratussõna mudel ...''

    Sõnakordus: ,,Töö eesmärk on töötada välja''. *Parandus*: ,,Käesoleva töö eesmärk on luua eestikeelne äratussõna mudel ...'' või ,,... arendada välja eestikeelne ...''.

4. **,,erilahendusi nõudva käsitööta''** (rida 86) — väljend on ebatäpne. Mida tähendab ,,käsitöö''? Kas mõeldakse käsitsi konfigureerimist? *Parandus*: ,,ilma kasutajapoolset eelteadmist või manuaalset konfiguratsiooni nõudmata''.

5. **,,Lisaks valideerimise tulemustele tuuakse välja ka lahenduse piirangud, riskid ja üldistatavuse ulatus.''** (rida 93) — see lause on lisatud peatüki ,,Tulemuste valideerimine'' lõppu, kuid kuulub pigem peatükki ,,Oodatav panus'' või ,,Töö piiritlemine''. Soovitus: viia paigast.

6. **,,toorsalvestuste avalikustamisest tulenevaid privaatsusriske''** (rida 96) — hea, aga **viide GDPR-ile ja TalTech eetikakomisjonile puudub**, kuigi projektis (CLAUDE.md järgi) on need konkreetselt arvestatud.

7. **Numbri kirjapilt**: ,,ESP32-S3-Korvo-2'' (rida 86) — kontrolli, et kogu töös oleks ühtne kirjapilt (ESP32-S3-Korvo-2 vs. ESP32-S3 Korvo-2). Sissejuhatuses on ,,ESP32-S3''.

---

## 6. Puuduvad allikad

**Olemasolevaid allikaid: 4** (Kiirkirjutaja, microWakeWord, openWakeWord, Home Assistant Voice Control). **Nõue: vähemalt 5.**

**Lisaks** on viited tekstis vormistatud käsitsi numbritega (,,[2]'', ,,[3]'', ,,[1]'') ehk ei kasutata BibTeX-i (`\cite{}`) nagu ülejäänud töös (introduction.tex kasutab `\cite{microwakeword2026}` jne). See on **ebajärjepidev** — ülesandepüstituses võiksid olla samad bibikuvad nagu sissejuhatuses, et töö oleks ühest tervikust.

**Soovituslikud lisaallikad** (kõik on juba sissejuhatuses olemas, lihtne üle tuua):

1. López-Espejo et al. (2021) ,,Deep Spoken Keyword Spotting: An Overview'' — `lopezespejo2021deepkws`. Annaks deep KWS metoodilise raami.
2. Speech Commands andmestiku artikkel (Warden 2018) — `speechcommands2018`. Kontrollkatse põhjenduseks.
3. Picovoice'i avalik võrdlusalus — `picovoice-benchmark2026`. Kvantitatiivne C-võrdluspunkt.
4. ESPHome — `esphome2026`. Tehnilise teostuse alus.
5. TalTech ASR andmed / Riigikogu stenogrammid — `taltech-asr-data2024`, `riigikogu-stenograms2025`. Eesti keele tehnoloogia kontekst.

Vähemalt **3 nendest tuleks lisada**, nii et allikate koguarv tõuseb 7–8-le. Soovitus: kasuta **sama** \texttt{references.bib} faili, mis sissejuhatus, ja `\cite{}` käske.

---

## Konsolideeritud parandussoovitused (prioriteetsuses)

1. **Lisa vähemalt 1, soovitavalt 3–4 viidet** (López-Espejo, Speech Commands, Picovoice, ESPHome) ja vii need BibTeX-vormingusse, et oleks järjepidev sissejuhatusega.
2. **Kirjuta uurimisküsimus ümber PICO-täielikuks**: lisa konkreetne population (eesti keele kõnelejad), võrdluspunkt (avalikud raamistikud / pilvelahendused) ja mõõdetav outcome (FAPH < 1, recall ≥ 0,95).
3. **Tugevda peatükki ,,Probleem''** kahe lausega taustast (eesti keel ei ole avatud raamistike toetatud keelte hulgas) ja motivatsioonist (privaatsus + väikeste keelte ligipääsetavus).
4. **Tõsta uurimisalaküsimused** sissejuhatuse väljast (introduction.tex) ka ülesandepüstitusse — see annab töö skoobile struktuuri.
5. **Lisa eetika- ja privaatsuskorraldus** (kasutajatestide nõusolek, TalTech eetikakomisjon, GDPR) lühidalt peatükki ,,Töö piiritlemine'' või ,,Oodatav panus''.
6. **Paranda 5. jaotuses loetletud keelelisi konarusi** (sõnakordused, kohmakad väljendid, lause sobimatu paigutus).
7. **Kontrolli `config/config.tex`**, et kõik makrod (autor, juhendaja, pealkiri) sisaldavad tegelikku eesti vormingut, mitte näidisteksti.

---

*Raport koostatud `Ülesandepüstituse_kontroll.txt` viiba alusel; analüüs põhineb ülesandepüstituse mustandil ja kõrvutatud sissejuhatusega.*
