---
source_prompt: 04_Kontrollimine/Konkreetsed_vead/Sisu/Kontrolli_uurimisküsimusi.txt
prompt_type: evaluative + generative (PICO + FINER + ümbersõnastamine)
generated: 2026-05-07
---

# Uurimisküsimuste süvaanalüüs (PICO + FINER)

Allpool on analüüsitud bakalaureusetöö sissejuhatuses (`introduction.tex`, lõik 9–14) sõnastatud üks põhiküsimus ja neli alamküsimust. Iga küsimus on hinnatud eraldi plokina prompti vormingu järgi. Hinnangud on tehtud rangelt, ent õiglaselt, vastandades küsimuse sõnastust töös tegelikult kirjeldatud panusele (sissejuhatus, 1.–3. peatükk, kokkuvõte).

---

### Analüüsitav küsimus nr 1 — põhiküsimus

**Algne sõnastus:** "Kuidas luua ja hinnata eestikeelset äratussõna tuvastust nii, et see oleks usaldusväärne nutikodu mikrokontrolleri piiratud ressursi tingimustes?"

**1. Algne PICO ja FINER analüüs**
*   **PICO:**
    *   **P:** eestikeelne äratussõna tuvastus piiratud ressursiga nutikodu mikrokontrolleril (konkreetselt ESP32-S3 klassi seade, äratusfraas „Kuule Kratt").
    *   **I:** `microWakeWord`-põhise treening- ja hindamistoru rakendamine ning täiendamine (mitmemõõtmeline hindamisprotokoll, FAPH-keskne voogedastushindamine).
    *   **C:** Puudub eksplitsiitse võrdluskätkujana küsimuses endas; töös kasutatakse kaudsete võrdlustena `openWakeWord`-i (loobutud sihtplatvormi mõttes), avalikku `marvin`-kontrollkatset ja klipi-tasemel vs. voogedastushindamist. Selline võrdluse puudumine küsimuses nõrgestab küsimuse analüütilisust.
    *   **O:** „usaldusväärsus" — töös operationaliseeritud sihiga FAPH < 1 ja lähikõne tuvastamismäär ≥ 0,95; lisaks fraasistruktuuri ja sarnaste negatiivnäidete eristus.
*   **FINER hinnang:**
    *   **F (Feasible):** *Osaliselt.* Mudeliarendus ja torufunktsioonide ehitus on jõukohased ning töös teostatud, kuid „usaldusväärsuse" mõõtmiseks vajalik kasutajatest (20–30 osalejat, vt §\ref{sec:user-test-methodology}) on töö esitamise hetkeks veel käimas, mis nõrgestab teostatavust just tähtaja poolelt (deadline 2026-05-18).
    *   **I (Interesting):** *Jah.* Madala ressursiga keele MCU-äratussõna on rahvusvaheliselt tühi nišš (ei `openWakeWord` ega Picovoice ei toeta eesti keelt).
    *   **N (Novel):** *Osaliselt.* „Esimene eestikeelne äratussõna" on faktiliselt uudne, kuid mitmemõõtmeline hindamisprotokoll ise pole metoodikana rahvusvaheliselt uudne (vt §\ref{sec:contribution-transferability}: „mitmemõõdikuline äratussõna hindamine ei ole tööstuses uudne"). Töö ise tunnistab, et uudsus seisneb mitte hindamisparadigmas, vaid selle kohandamises väikese keeleruumi tingimustele.
    *   **E (Ethical):** *Jah.* Kahetasandiline nõusolekumudel, GDPR-teadlik, eraldi audio opt-in.
    *   **R (Relevant):** *Jah.* Otsene lünk TalTechi/Eesti keeletehnoloogia stack'is (Kiirkirjutaja STT olemas, äratussõna puudub).
    *   **Kriitiline puudus:** „usaldusväärne" on küsimuses operationaliseerimata. Töö ise lisab tagantjärele konkreetse sihi (FAPH < 1, recall ≥ 0,95), kuid küsimuse sõnastus ei sunni autorit seda eksplitsiitselt välja ütlema, mistõttu küsimus jätab mulje pehmemast eesmärgist kui töö tegelikult lubab.

**2. Otsus:** Vajab parandamist.

**3. Parandatud uurimisküsimus**
**„Millisel määral suudab `microWakeWord`-i põhjal treenitud eestikeelne äratussõna mudel „Kuule Kratt" saavutada ESP32-S3 klassi mikrokontrolleril samaaegselt sõltumatu eesti taustaheli FAPH < 1 ja päriskõnelejate lähikõne tuvastamismäära ≥ 0,95, kui hindamine põhineb mitmemõõtmelisel protokollil (taustaheli FAPH, päriskõneleja recall, sarnaste negatiivnäidete FPR, fraasistruktuuri kontroll)?"**

*   **Uue versiooni selgitus:** Asendasin sõna „usaldusväärne" konkreetsete kirjanduses ja töö metoodikas dokumenteeritud operatsiooniliste sihtidega ning lisasin eksplitsiitse mitmemõõtmelise hindamiskriteeriumi, mis vastab §\ref{sec:eval-evolution} lõpetatud kolme valideerimiskihi loogikale. „Kuidas..." asendati „millisel määral..." vormiga, mis sunnib kvantitatiivset vastust ja sobib kokku töös juba kasutatud Wilson/Poisson-Garwood usaldusvahemike raporteerimisega.
*   **Uus PICO:** P: eestikeelne äratussõna „Kuule Kratt" ESP32-S3-l | I: `microWakeWord` MixedNet + mitmemõõtmeline hindamisprotokoll | C: kirjanduse soovituslikud sihid (FAPH < 1, recall ≥ 0,95) ning sama mudeli üksikmõõdiku-põhine hindamine (klipi-tasemel FPR) | O: empiiriline lahknevus üksiku sihi täitmise ja samaaegse mitme sihi täitmise vahel.

---

### Analüüsitav küsimus nr 2 — alamküsimus 1

**Algne sõnastus:** „kuidas valideerida treeningu- ja hindamistoru enne eestikeelse andmestiku juurde liikumist"

**1. Algne PICO ja FINER analüüs**
*   **PICO:**
    *   **P:** `microWakeWord`-põhine treeningu- ja hindamistoru, autori arenduskeskkond.
    *   **I:** avalik kontrollkatse (Speech Commands, sihtsõna `marvin`).
    *   **C:** „enne eestikeelse andmestiku juurde liikumist" implitseerib kaudset võrdlust hilisema eestikeelse fookusega — eksplitsiitset võrdlusbaasi pole.
    *   **O:** kinnitus, et vead nõrgas eesti tulemuses ei tulene torust.
*   **FINER hinnang:**
    *   **F:** *Jah.* Töös teostatud (vt 1. peatükk § „Avalikud andmekorpused" ja 2. peatükk § „Miks avalik kontrollkatse oli vajalik").
    *   **I:** *Osaliselt.* Tööriistakihi valideerimine üksinda pole rahvusvahelisele lugejale uudne; küll aga on huvi selle vastu, mida kontroll konkreetselt avastas (taustaheli komponendi puudujääk).
    *   **N:** *Ei.* Tööriistakihi „smoke test" avaliku korpuse peal pole metoodiliselt uudne.
    *   **E:** *Jah.*
    *   **R:** *Jah.* Töö narratiivi seisukohalt keskne.
    *   **Kriitiline puudus:** Küsimus on enesetaolik *protseduuriline* küsimus („kuidas teha"), mitte uurimisküsimus. PICO-s puudub mõõdetav tulemus — „valideerida" ei ole iseenesest mõõdik. Lisaks on küsimus *suletud* selles mõttes, et autor on otsuse („kasutame `marvin`-kontrollkatset") sissejuhatuses juba teinud.

**2. Otsus:** Vajab parandamist.

**3. Parandatud uurimisküsimus**
**„Millised treening- ja hindamistoru tehnilised puudused ilmnevad avaliku Speech Commands `marvin`-kontrollkatse läbiviimisel ning millises ulatuses muudaksid need eestikeelse mudeli tulemuste tõlgendust, kui kontrollkatset poleks tehtud?"**

*   **Uue versiooni selgitus:** Muutsin protseduurilise „kuidas valideerida" küsimuse uurimuslikuks „milliseid puudusi avastame ja milline oleks olnud tagajärg ilma selleta" küsimuseks, mis on (a) avatud, (b) sisaldab vastandvaate (kontrafaktuaalse) elementi ja (c) annab mõõdetava tulemuse (puuduste loend + nende mõju ulatus). See vastab tegelikult sellele, mida 2. peatüki § „Miks avalik kontrollkatse oli vajalik" tegelikult väidab.
*   **Uus PICO:** P: `microWakeWord` toru autori keskkonnas | I: Speech Commands `marvin`-kontrollkatse | C: kontrafaktuaalne stsenaarium (otse eesti andmete peale liikumine) | O: identifitseeritud tehnilised piirangud (nt taustaheli komponendi puudumine voogedastushindamises) ja nende kvantifitseeritud mõju mõõdikutele.

---

### Analüüsitav küsimus nr 3 — alamküsimus 2

**Algne sõnastus:** „millist rolli mängivad positiivsed, negatiivsed ja taustaheli-andmed äratussõna mudeli kvaliteedi hindamisel"

**1. Algne PICO ja FINER analüüs**
*   **PICO:**
    *   **P:** äratussõna mudeli hindamiskiht.
    *   **I:** kolme andmeliigi (positiivsed, negatiivsed, taustaheli) eraldi käsitlemine.
    *   **C:** kaudne — võrreldakse stsenaariumiga, kus ainult positiivseid ja negatiivseid eristatakse (vrd 2. peatüki §\ref{sec:eval-evolution} kolm valideerimiskihti).
    *   **O:** määratlus, milline mõõdik (recall, FPR, FAPH) sõltub millisest andmeliigist.
*   **FINER hinnang:**
    *   **F:** *Jah.*
    *   **I:** *Osaliselt.* Kolme andmeliigi roll on kirjanduses (Lopez-Espejo 2021) juba selgelt sõnastatud.
    *   **N:** *Ei.* Töös endas nimetatakse seda baasjaotuseks (1. peatükk § „Andmeliikide eristamine").
    *   **E:** *Jah.*
    *   **R:** *Jah.* — töö narratiivile vajalik.
    *   **Kriitiline puudus:** Küsimus on liiga lai ja kirjeldav. Nii nagu sõnastatud, küsib see õpiku-vastust, mitte uurimusliku väite tõestust. Töö tegelik panus ei seisne kolme andmeliigi rolli väljaütlemises (mis on teada), vaid selles, et *positiivse klassi sisuline audit* (§\ref{sec:positive-audit}) avastas teist järku sildistusprobleemi, mida kolme-andmeliigi-paradigma üksi ei taga.

**2. Otsus:** Vajab parandamist.

**3. Parandatud uurimisküsimus**
**„Millisel määral suudab kanooniline kolme-andmeliigi (positiivsed, negatiivsed, taustaheli) jaotus üksinda eristada „õpitud äratussõna"-mudelit „õpitud akustilise lühitee"-mudelist, ning milliseid täiendavaid sisulisi audite (positiivse klassi terviklikkus, fraasistruktuuri kontroll) on vaja sellest piisamaks?"**

*   **Uue versiooni selgitus:** Selline sõnastus seab andmejaotuse rolli *katsetatava väite alla*: kas see *on* piisav, mitte ainult *kirjeldav*. Vastus on töös juba olemas (§\ref{sec:eval-evolution} näitab, et ei ole, vaja oli teist ja kolmandat ringi). Küsimus muutub avatuks ja diagnostiliseks.
*   **Uus PICO:** P: äratussõna hindamise andmejaotus | I: standardne 3-andmeliigi jaotus | C: laiendatud protokoll (sisuline positiivse klassi audit, fraasistruktuuri testid, kontrollpunkti komposiitkriteerium) | O: lühitee-käitumiste avastatavus mudelites.

---

### Analüüsitav küsimus nr 4 — alamküsimus 3

**Algne sõnastus:** „kuidas eristada andmestikust tulenevaid probleeme toru tehnilistest piirangutest"

**1. Algne PICO ja FINER analüüs**
*   **PICO:**
    *   **P:** äratussõna mudeli arendusprotsess väikese keeleruumi tingimustes.
    *   **I:** diagnostiline metoodika, mis omistab vea allika kas andmestikule, torule või mudelile.
    *   **C:** Puudub eksplitsiitselt; kaudselt vrd „mitmediagnostiline omistamine" vs. „üks põhjus seletab kõike".
    *   **O:** vea-omistamise reeglistik või auditi-tehnikate kogum.
*   **FINER hinnang:**
    *   **F:** *Jah.*
    *   **I:** *Jah.* — see on töö üks tugevamaid panuseid ülekantavuse mõttes.
    *   **N:** *Osaliselt.* Andmeleke vs. tehniline puudujääk on ML-kirjanduses üldine teema, kuid äratussõna-spetsiifilises väikese keeleruumi kontekstis vähem dokumenteeritud.
    *   **E:** *Jah.*
    *   **R:** *Jah.* — kogu 2. peatüki §\ref{sec:eval-evolution} on selle ümber üles ehitatud.
    *   **Kriitiline puudus:** Sõnastus on jätkuvalt kirjeldav („kuidas eristada"), mitte hinnatav. Lisaks puudub *esinemissageduse* mõõde — kas eristamine kunagi *ebaõnnestus* töö enda kogemuses? (Jah, esimese ringi v6 puhul: paistis CV ET 0,4% FPR, tegelikult ~50 FAPH MacBook Pro mikrofonis. Vt §\ref{sec:cross-mic-asymmetry}.) See empiiriline tõendus tuleks küsimusse sisse tuua.

**2. Otsus:** Vajab parandamist.

**3. Parandatud uurimisküsimus**
**„Millised konkreetsed audititehnikad (treening-test disjointsuskontroll, sõltumatu kõrvalejäetud taustaheli komplekt, ristmikrofoni FAPH-kontroll, positiivse klassi sildiaudit) on praktikas vajalikud, et eristada andmelekkest või andmestiku puudusest tulenevaid mudelivigu treening- ja hindamistoru tehnilistest piirangutest, ning millises mõõdikus väljendub iga tehnika diagnostiline lisandväärtus?"**

*   **Uue versiooni selgitus:** Konkretiseerib „kuidas eristada" küsimuse loendiks tehnikatest, mille mõju on töös juba dokumenteeritud (v1–v8 vs. v6-residual ablatsioon, MacBook Pro 40-min test, marvin-kontrollkatse). Lisab mõõdetava tulemuse („diagnostiline lisandväärtus mõõdikus"), mis muudab küsimuse hinnatavaks.
*   **Uus PICO:** P: äratussõna arendustöövoog | I: nelja-tehnikaline auditipakett | C: ühekomponendiline diagnostika (ainult standardne klipi-FPR) | O: vigade omistamise täpsus ja iga tehnika eraldiseisev panus.

---

### Analüüsitav küsimus nr 5 — alamküsimus 4

**Algne sõnastus:** „kas treenitud mudel saavutab eestikeelsel taustaheli korpusel pidevvoo FAPH < 1 ja lähikõne tuvastamismäära ≥ 0,95 sihi"

**1. Algne PICO ja FINER analüüs**
*   **PICO:**
    *   **P:** parim treenitud mudel (varimudelid `v16c`, `expert-a`, `expert-b2`, `v6-residual`, `v10`, `v15` ja konsensus `expert-a + expert-b2`).
    *   **I:** mudeli rakendamine eesti taustaheli korpusel pidevvoo FAPH-i jaoks ja päriskõnelejate klippidel recall'i jaoks.
    *   **C:** sihtväärtused (FAPH < 1, recall ≥ 0,95) — projekti-spetsiifilised, mitte universaalne standard.
    *   **O:** kaks Booleani vastust (jah/ei kummalegi sihile) ning nende usaldusvahemikud (Wilson, Poisson-Garwood).
*   **FINER hinnang:**
    *   **F:** *Osaliselt.* Common Voice ET kõrvalejäetud korpus on olemas (konsensus 0,79 FAPH), kuid recall ≥ 0,95 päriskõnelejatel on otseselt sõltuv kasutajatestist, mis pole töö sõnul veel täielikult lõpetatud (vt sissejuhatuse jääkpiirang ja §\ref{sec:user-test-methodology}). Seega vastust pole töö submissioniks veel täielikult olemas.
    *   **I:** *Jah.*
    *   **N:** *Osaliselt.* „Numbri x kättesaamine" iseenesest pole metoodiliselt uudne; uudne on selle kontekst (esimene eesti äratussõna, sõltumatu hold-out).
    *   **E:** *Jah.*
    *   **R:** *Jah.* — see on lubatud konkreetne empiiriline järeldus.
    *   **Kriitiline puudus:** Küsimus on *suletud* (Jah/Ei) ja *binaarne*. See ei jäta ruumi tegelikult dokumenteeritud kompromissi käsitlemiseks (FAPH-i lõdvendamine paranes recall ainult osaliselt, vt kokkuvõte). Praeguse vastuse on töö ise sõnastanud nüansseeritult: konsensusena 0,79 FAPH on saavutatud, kuid recall'i pool jääb juurutuslävel päris kõnelejatel madalamaks; üksikmudel ei suuda mõlemat sihti samaaegselt täita.

**2. Otsus:** Vajab parandamist.

**3. Parandatud uurimisküsimus**
**„Millises ulatuses suudab üks treenitud mudel või mudelite konsensus saavutada samaaegselt sõltumatul eesti taustaheli korpusel pidevvoo FAPH < 1 (Poisson-Garwood 95% UV) ning päriskõnelejate lähikõne tuvastamismäära ≥ 0,95 (Wilson 95% UV), ning kui samaaegne saavutamine ei õnnestu, milline on dokumenteeritud kompromiss FAPH-sihi lõdvendamise ja recall'i paranemise vahel?"**

*   **Uue versiooni selgitus:** Muudab suletud Jah/Ei küsimuse avatud „millises ulatuses" küsimuseks. Lisab eksplitsiitselt usaldusvahemikud (vastavad töös tegelikult kasutatud meetoditele). Lisab teise klausli kompromissi kohta, mis vastab kokkuvõttes ja §\ref{sec:fourth-round} sõnastatud tegelikule leiule. See teeb küsimuse vastuse keelduvalt mitte-triviaalseks: isegi kui esimese poole vastus on „ei", on töö tulemuseks tähenduslik kompromissikõver, mitte tühi ebaõnnestumine.
*   **Uus PICO:** P: parim üksikmudel ja konsensus | I: pidevvoo hindamine eesti hold-out korpusel + päriskõnelejate hindamine | C: projekti-spetsiifilised sihid (FAPH < 1; recall ≥ 0,95) ning nendelt lõdvendatud operatsioonipunktid | O: samaaegse saavutuse tõenäosus + kompromissikõvera kuju.

---

## Üldine kokkuvõte

**Põhitähelepanekud kõigi viie küsimuse kohta:**

1. **Suletud sõnastused.** Kolm viiest alamküsimusest on sõnastatud suletult („kuidas valideerida", „kas saavutab", „kuidas eristada"); ainult küsimus 2 (alamküsimus 1) on tegelikult *vaba* küsimus selles mõttes, et küsib mitmevariantsust.
2. **Operationalisatsiooni puudujääk põhiküsimuses.** Põhiküsimuse võtmemõiste „usaldusväärne" pole küsimuses endas defineeritud; töö tekst defineerib selle *tagantjärele* (FAPH < 1, recall ≥ 0,95). Selline operationalisatsioon kuulub uurimisküsimusse, mitte taustlõiku.
3. **Võrdluse (PICO „C") puudumine.** Ühelgi küsimusel pole eksplitsiitset võrdluskäsitlust. See on oluline puudus, sest töö tegelik panus ehitub *vastandlustele* (klipi-tasemel vs. voogedastus, üksikmudel vs. konsensus, ühe-mõõdikuline vs. mitme-mõõdikuline), kuid küsimuste sõnastus seda kompositsiooni ei kanna.
4. **Tugevad küljed:** Kõik küsimused on selgelt eetilised (E), valdkonnale relevantsed (R) ja peamiselt teostatavad. Töö tegelik teostus läheb küsimustest mitmes kohas kaugemale (eriti §\ref{sec:eval-evolution} kolmeringiline analüüs ja §\ref{sec:contribution-transferability} ülekantavuse argument), mis viitab sellele, et küsimused on tegeliku panusega võrreldes *alaambitsioonikad*.
5. **Soovituslikud parendused on minimaalse ulatusega.** Iga küsimuse kohta esitatud parandatud sõnastus säilitab töö tegeliku struktuuri ja tulemused; need on pigem *küsimuse-tasemel uuesti raamimine*, mitte uue uurimuse nõue. Töö ise ei vaja sisulisi muutusi — küsimuste sõnastus tuleks lihtsalt sissejuhatuses täpsemalt vastavusse viia sellega, mida 2. ja 3. peatükk tegelikult vastavad.

**Konkreetsed soovitused autorile (mitte töö muutmiseks, vaid teadmiseks):**
*   Põhiküsimuse parandatud versioon (vt nr 1) ühendaks paremini sissejuhatuse lubaduse ja Tulemuste peatüki tegeliku raporteerimise.
*   Alamküsimustes 2 ja 3 võiks järgmine iteratsioon viidata otse „lühitee-käitumisele" (§\ref{sec:general-principle}), mis on töö üks tugevamaid sisulisi panuseid, kuid mida praegu küsimuste tasandil ei mainita.
*   Alamküsimuses 4 võiks suletud Jah/Ei vorm asenduda kompromissi-kõvera vormiga, mis vastab kokkuvõttes ausalt esitatud nüansile (FAPH-i lõdvendamise ja recall'i osalise paranemise vahel).
