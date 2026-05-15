---
source_prompt: 03_Lõputöö_alamosad/Tasuvusanalüüs.txt
prompt_type: generative
generated: 2026-05-07
---

# Tasuvusanalüüsi peatükk Krati lõputööle — mustand ja tegevusplaan

## Kontekstualiseerimine ja lünga selgitus

Lõputöö praeguses struktuuris (sissejuhatus, metoodika, tulemused, arutelu, kokkuvõte) tasuvusanalüüsi (kogukulu / investeeringu tasuvus) peatükk hetkel eraldi puudub. Töö praktiline panus on äratussõna mudel, hindamisprotokoll ja kohaliku nutikodu satelliidi integratsioonimuster, mitte selgesõnaline finantskaalutlus. Kuna prompt on generatiivne, esitatakse allpool detailne mustand ja samm-sammuline plaan selleks, kuidas vähese ajaga (esitamiseni jäänud aeg ${\sim}10$ päeva, üks autor) lisada töösse minimaalne, akadeemiliselt korrektne tasuvusanalüüsi alapeatükk arutelu ossa või iseseisva lühipeatükina enne kokkuvõtet.

**Sisendpiirangute fikseerimine:**

| Parameeter | Väärtus |
|---|---|
| Aega esitamiseni | ${\sim}10$ päeva (deadline 2026-05-18) |
| Autorite arv | 1 |
| Töö iseloom | Tehniline BSc-lõputöö, mitte ärimudel |
| Olemasolev sisend | Lokaalne nutikodu äratussõna lahendus (ESP32-S3 + Home Assistant), võrdlusbaas pilve-/litsentsipõhised alternatiivid |

Kuna ajavaru on alla ühe kuu, peab analüüs prompti enda nõude kohaselt piirduma **suurusjärgu hinnanguga (ballpark estimate)** ja kvalitatiivse kasude kaardistusega. Diskonteeritud rahavoogude mudelid (NPV, IRR) on selles ajaraamis ülearu ja oleksid eksitavad — nende välja jätmine tuleb peatükis selgesõnaliselt põhjendada.

---

## 1. Juhendaja strateegiline sissejuhatus (peatüki preambul töö enda jaoks)

* **Valitud metoodika:** Võrdleme **lokaalse Krati lahenduse kogukulu (Total Cost of Ownership, TCO)** kahe alternatiiviga: (a) kommertspilve äratussõna teenus (nt Picovoice Porcupine kommertslitsents pluss kasutajatuvastus pilves) ja (b) "alternatiiv puudub" — eestikeelse äratussõna täielik puudumine, mis sunnib kasutaja füüsilisele lülitile või muukeelsele äratussõnale. Selline võrdlus sobib töösse seetõttu, et raamistab Krati panuse mitte tootena, vaid **eestikeelse hääljuhtimise tarbimiskuluna ühe nutikodu kohta 3-aastasel kasutusperioodil**.
* **Aja ja ressursi hinnang:** 10-päevase ajavaru ja ühe autori puhul piirdub analüüs kolme tabeliga (kulu, kasu, tasuvuspunkt) ning ühe kumulatiivse kulu graafikuga. Ühegi numbri pealt ei tehta investeeringuotsust — eesmärk on näidata komisjonile, et autor oskab tehnilise lahenduse paigutada ka majanduslikku raamistikku ja teadlikult markeerida, mida ei mõõdetud.

---

## 2. Samm-sammuline juhis analüüsi läbiviimiseks (tegemine)

### Samm 1 — kulude (Costs) kaardistamine

Kogukulu jaotub kolmeks: ühekordne arenduskulu, riistvarakulu ja jooksev töökulu. Numbrid leitakse järgmistest avalikest allikatest:

* **Riistvara:** ESP32-S3-Korvo-2 arendusplaadi jaehind (Espressifi ametlik müüja või Mouser/DigiKey kataloog), mikrofoni ja korpuse kulu. Raspberry Pi 5 hind, kui see on Home Assistanti hostina osa kogukomplektist.
* **Tarkvaralitsentsid:** microWakeWord, openWakeWord, ESPHome ja Home Assistant on avatud lähtekoodiga — litsentsikulu on null. See on **iseenesest oluline kasu**, mis tuleb peatükis selgesõnaliselt nimetada.
* **Treeningu arvutuskulu:** TalTech HPC kasutamine on tudengi jaoks rahalises mõttes "tasuta" (kaetud ülikooli infrastruktuurist), kuid varjatud kuluna tuleb hinnata samaväärne kommertshind: kasutatud GPU-tundide arv (lokaalsest treeningu logist) korrutatuna pilveteenuse hinnakirjaga (näiteks Google Cloud A100 või AWS g5/p4 spot-hind). Allikaks ametlikud hinnakirjad, mille URL ja kasutamise kuupäev tuleb viidetes fikseerida.
* **Tööjõukulu:** Kõige tundlikum number. Kasutatakse Statistikaameti **info ja side tegevusala** keskmist brutokuukuupalka (PA001 või vastav uuem tabel), mis arvutatakse tunnitasuks (jagatakse kuus 168 tunniga ja korrutatakse tööandja maksukoormusega ${\approx}1{,}338$). Töötundide hinnang võetakse Clockify/GitLab logidest (pin'itud projekti-mälus on millised tundide andmed olemas). Kui täpset logi pole, antakse väiksem ja suurem stsenaarium (näiteks 200 h vs 400 h) ning näidatakse tundlikkust.
* **Jooksev töökulu:** ESP32-S3 elektritarve (vatid $\times$ Eleringi avalik elektri keskmine hind) aastas ja Home Assistanti hosti elektritarve. See arvuga tuleb välja $<5\,\text{€/aastas}$ ja sama suurusjärk kui kommertsalternatiivi puhul, st praktiliselt taandub.

Konkreetseid eurohinnanguid **käesolevas mustandis ei genereerita**, kuna see nõuaks numbreid, mida saab ainult autori enda logi- ja arve\-andmetest; iga arv tuleb peatükis viidata päris allikale, mitte sünteesida.

### Samm 2 — kasude (Benefits) kaardistamine

Kasud jagunevad kvantitatiivseteks (rahasse tõlgitavateks) ja kvalitatiivseteks. Tehniline BSc-töö puhul on kvalitatiivne pool valdav ja seda tuleb peatükis ausalt rõhutada.

**Kvantifitseeritavad kasud:**

* **Litsentsisääst:** kommertsalternatiivi (näiteks Picovoice Porcupine) hinnang aasta\-litsentsi kohta ühe seadme või väikese juurutuse kohta. See on kõige otsesem rahalise kasu mõõtmise koht ning sobib ka ühe nutikodu kasutaja vaatesse.
* **Säästetud aeg / FTE-osa:** kui Krati lahendus asendaks pilveteenuse ja sellega seotud konfiguratsioonitööd, saab arvestada säästetud tunde aastas. Mahu hinnang peab olema väike ja konservatiivne (näiteks 2–4 h aastas), korrutatuna sama tunnitasuga, mida kasutati kuluarvestuses.
* **Andmesäilituskulu vältimine:** pilve\-äratussõna teenused tihti edastavad heli pilve. Kohaliku lahenduse puhul see kulu (sh GDPR-vastav nõusolekute haldus, andmete säilitamise leping) puudub. Selle eest peab tasuvusanalüüsi peatükk piirduma kvalitatiivse markeeringuga ("kulu väldib tekkimast"), mitte fiktiivse euroarvuga.

**Kvalitatiivsed kasud (kohustuslikud nimetada, kuid mitte kvantifitseerida):**

* eestikeelse äratussõna olemasolu kui keelelise ligipääsetavuse element nutikodus;
* privaatsuse-kasu lokaalsest järeldamisest (heli ei lahku seadmest);
* sõltumatus välisest litsentsiandjast (avatud lähtekoodi mõju projekti elueale);
* kohanduvus eesti hääldusvariatsioonidele ("Kuule" vs "Kule"), mida kommerts\-alternatiivid ei toeta üldse.

### Samm 3 — tasuvuspunkti arvutamine

Lihtsaim arvutus, mida BSc-töö ulatusele sobib:

$$
T_{\text{tasuvus}} = \frac{C_{\text{ühekordne}}}{B_{\text{aastane}}^{\text{kvantif.}}}
$$

kus $C_{\text{ühekordne}}$ on summa Sammust 1 (riistvara + arenduskulu kommertsväärtuses) ja $B_{\text{aastane}}^{\text{kvantif.}}$ on Sammu 2 kvantifitseeritud aastane kasu. Tulemus avaldatakse aastates, **koos selgesõnalise märkega, et see ei sisalda kvalitatiivseid kasusid ega arvesta Krati teadusliku panuse väärtusega lõputööna**. Kui tasuvuspunkt tuleb kõrgem kui kommertstoote eluiga (näiteks 5+ a), siis ka see on aus tulemus, mida tuleb arutelus käsitleda — see ei ole peatüki ebaõnnestumine, vaid lugeja jaoks oluline tõsiasi madala ressursiga keele lokaalse lahenduse kohta.

---

## 3. Samm-sammuline juhis tulemuste esitamiseks (kirjutamine)

### 3.1 Sissejuhatus / metoodika lõik

Mustand-sõnastus, mille saab töösse otse adapteerida (jättes alles sisukohad, kus konkreetsed numbrid sõltuvad autori andmetest):

> Käesolev alapeatükk hindab Krati lokaalse äratussõna lahenduse kogukulu (\emph{Total Cost of Ownership}, edaspidi kogukulu) ja võrdleb seda lähima realistliku alternatiiviga ühe nutikodu seadme kolmeaastasel kasutusperioodil. Diskonteeritud rahavoogude mudelid (NPV, IRR) jäetakse teadlikult välja, sest käesoleva BSc-töö ajavaru ja ühe autori ressurss ei toeta nende mudelite eelduste põhjendamist tasemel, mis muudaks tulemused tõsiseltvõetavaks. Eesmärk on suurusjärgu hinnang, mis võimaldab paigutada töö praktilise panuse majandusliku konteksti raami, mitte teha investeerimisotsust.

### 3.2 Eelduste ja piirangute tabel

Komisjon ootab näha, **mida arvutati ja mida ei arvutatud**. Soovitatav vorm:

| Element | Kaasatud | Allikas / hinnang | Märkus |
|---|---|---|---|
| ESP32-S3-Korvo-2 riistvara | Jah | jaehind 2026-05 | ühekordne kulu seadme kohta |
| Home Assistant host (Pi 5) | Osaliselt | jagatud nutikodu komponent | ainult osakaal omistatud Kratile |
| Avatud lähtekoodi tarkvara | Litsentsikulu null | OSS | kvalitatiivne kasu eraldi |
| Treeningu arvutuskulu | Pilveteenuse samaväärsena | AWS/GCP hinnakiri | TalTech HPC tegelik kulu varjatud |
| Autori töötunnid | Statistikaameti info ja side tegevusala keskmine | Clockify/GitLab logid | tundlikkusvahemik 200–400 h |
| Elektritarve | Hinnang $<5\,\text{€/a}$ | Eleringi keskmine elektrihind | praktiliselt taandub |
| Turundus, juriidika, kasutajatugi | **Välja jäetud** | — | mitte töö skoop |
| Kasutajatesti läbiviimise kulu | **Välja jäetud** | — | hõlmatud akadeemilise tööna |
| Kommertsalternatiivi tegelik nõudlus | **Välja jäetud** | — | turuanalüüs ei mahu BSc-töösse |

Tabeli alla kuulub lõik, mis selgitab, miks need välja jätmised on **teadlikud**, mitte vead — see on prompti enda nõue ja ühtlasi BSc-töö tasuvusanalüüsi peatüki kõige sagedasem hindamiskoht.

### 3.3 Tulemuste visualiseerimine

* **Tabel 1: kulustruktuur** — Krati lahendus vs kommertsalternatiiv vs "puudub eestikeelne äratussõna" stsenaarium, ridadel ühekordne / aastane / 3 a kogukulu.
* **Tabel 2: kasude kaardistus** — kvantifitseeritud kasud (eurodes/aastas) eraldatuna kvalitatiivsetest kasudest (loend).
* **Joonis 1: kumulatiivne kulu kolme aasta jooksul** — telg $x$ on kuud (0–36), telg $y$ on euro. Kaks joont: Krati ja kommertsalternatiiv. Tasuvuspunkt on ristumiskoht (kui see kolme aasta sisse mahub) või ekstrapoleeritav viide. Üks tundlikkusriba autori töötundide vahemiku kohta.

Graafikut ei ole vaja keerukamaks teha — komisjon hindab selgust, mitte detaili.

### 3.4 Järelduste sõnastamine

Mustand-sõnastus järelduslõigule:

> Kogukulu hinnang näitab, et Krati lahenduse rahaliseks tasuvuseks ühe nutikodu kasutaja vaates on $T_{\text{tasuvus}} \approx \dots$ aastat, mis on tundlik eelkõige autori töötundide hinnale ja kommertsalternatiivi litsentsiarvestusele. Kvantitatiivne tasuvus üksinda **ei õigusta lahenduse arendamist** ühe kasutaja tasemel, kuid see ei olegi peatüki sõnum: lahenduse tegelik panus on (a) eestikeelse äratussõna olemasolu kui keelelise ligipääsetavuse element, (b) lokaalse järeldamise privaatsuskasu ja (c) tehnoloogiaraamistiku reprodutseeritavus, mida ükski kommertsalternatiiv praegu ei kata. Need kasud ei mahu kogukulu valemisse, kuid moodustavad töö majandusliku põhjenduse koos tehnilise tulemusega.

See sõnastus seob säästetud eurod **töö üldise eesmärgiga** — eestikeelse lokaalse äratussõna olemasoluga — ja väldib ülemüümist.

---

## 4. Praktilised soovitused autorile (väljaspool peatüki teksti)

1. Enne peatüki kirjutamist tee 30-minutiline kontroll: kas Clockify/GitLab logist saab ekstraktida tegeliku töötundide arvu kuni dato. Kui ei, fikseeri ühe lausega "töötundide hinnang on autori enesehinnangul, suurusjärguline".
2. Kogu kõik avalikud hinnaviited (Statistikaamet, AWS, Espressif, Eleringi tariif) ühele lehele koos URL-i ja vaatamise kuupäevaga *enne* peatüki kirjutamist. See hoiab ära olukorra, kus peatükk jääb kirjutamata, sest üks number on puudu.
3. Hoia peatükk lühike — soovituslikult 2–3 lehekülge ühes lõputöö A4 vormingus. Üle selle on risk, et tasuvusanalüüs hakkab konkureerima tehnilise sisuga ja vähendab töö põhilist sõnumit.
4. Paigutus: lisada eraldi alapeatükina **arutelu peatükki** (näiteks "Lahenduse majanduslik kontekst") või eraldi lühipeatükina enne kokkuvõtet. Mõlema variandi puhul tee selgesõnaline vastastikune ristviide tehniliste tulemuste juurest, et lugeja teaks, millises kohas majanduslik raam paikneb.
5. Ära too peatükki sisse uusi mõisteid (NPV, IRR, WACC), mida hiljem ei kasutata — see häirib kaitsmisel komisjoni rohkem kui aitab.

---

## 5. Mida käesolev mustand teadlikult ei genereerinud

* Konkreetseid eurohinnanguid (riistvara, töötasu, litsentsihinnad). Põhjus: prompti vastavalt ei tohi numbreid ilma allikateta välja mõelda — iga arv peab olema viidatud päris hinnakirjale või autori logile, mida käesolev mustand ei näe.
* Lõplikku tasuvuspunkti aastates. Sõltub eelmisest punktist.
* Diskonteeritud rahavoogude mudelit. Põhjus: prompt ise soovitab seda alla 4-kuulise ajavaru korral mitte teha, ja praegune ajavaru on ${\sim}10$ päeva.
* Otseseid muudatusi lõputöö LaTeX-failidesse. Käesolev artefakt on planeerimisdokument, mitte töö enda osa.
