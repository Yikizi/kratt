---
source_prompt: 03_Lõputöö_alamosad/Litsenseerimine.txt
prompt_type: generative (litsentside soovitamine avaldatavatele artefaktidele)
generated: 2026-05-07
---

# Litsenseerimissoovitused projekti \"Kratt\" digitaalsetele artefaktidele

## Sissejuhatav märkus

Allolev analüüs põhineb lõputöö peatükkide sissejuhatusel, metoodikal ja arutelul ning ülesandepüstitusel. Töö kirjeldab konkreetselt järgmiseid digitaalseid komponente: \texttt{microWakeWord}-põhine treeningu- ja hindamistoru, ESP32-S3 ESPHome integratsioon, Home Assistanti \texttt{voice\_assistant}-liides, Androidi rakendus valevallandumiste logimiseks, käsureatööriistad \texttt{kratt user-test}, \texttt{kratt validate-user-test}, \texttt{kratt replay-user-test} ja \texttt{kratt summarize-user-test}, treenitud TFLite-mudelid (sh \texttt{v16c}, \texttt{expert-a}, \texttt{expert-b2}, \texttt{v6-residual}, \texttt{v10}, \texttt{v15}), kasutajatesti küsimustik (sh UMUX-Lite kaks väidet) ning lõputöö LaTeX-allikas. Litsentsisoovitused on esitatud iga sellise tuvastatud tulemuse kohta eraldi ploki kujul.

Eraldi tuleb rõhutada ohutuskontrolli (sanitization) põhimõtet: ükski avalikustatav komponent ei tohi sisaldada Home Assistanti pikajalisi pääsutõendeid (\emph{long-lived access token}), Wi-Fi paroole, kõnelejate isikutuvastust võimaldavaid metaandmeid ega Tartu Neurokõne, XTTS- või Fish-S2-Pro teenuste API-võtmeid. Kasutajatesti audio puhul kehtib lisaks lõputöös kirjeldatud kaheastmeline nõusolekumudel: pseudonüümsete tehniliste tulemuste avaldamine on lubatud minimaalse nõusoleku põhjal, samas kui märgendatud heliklippide avaldamine eeldab eraldi audio-opt-in nõusolekut ning tõenäoliselt ka eetikakomitee positiivset arvamust. Kahtluse korral tuleb hoida heliartefaktid avaldamata, kuni nõusolekuprotseduur on dokumenteeritud.

---

### Tulemus: \texttt{microWakeWord}-põhine treeningu- ja hindamistoru (Python-koodibaas)

**1. Kirjeldus:**
Pythoni skriptide ja konfiguratsioonifailide kogum, mis taastoodab lõputöö treeningu-, ekspordi- ja hindamisprotsessi: \texttt{Speech Commands} kontrollkatse, andmete teisendus \texttt{mmap}-vormingusse, treeningu-, valideerimise-, testimise- ja \texttt{validation\_ambient}/\texttt{testing\_ambient} jaotuste moodustamine, MixedNet/MixConv arhitektuuri konfiguratsioon, FAPH ja FRR voogedastushindamine ning Wilsoni ja Poissoni-Garwoodi usaldusvahemike arvutus. Sisaldab nelja FAPH-i variandi (raamistiku, skriptitud taasmängu, välitingimuste ja kasutajatesti taasmängu) loendusreegleid.

**2. Avaldamise põhjendus:**
See on lõputöö metoodilise põhipanuse --- mitmemõõtmelise valideerimisprotokolli --- otsene operatsionaliseering. Avaldamine võimaldab teistel madala ressursiga keelte uurijatel reprodutseerida andmelekke audit, sõltumatu kõrvalejäetud komplekti kontroll ning komposiitne kontrollpunkti valikukriteerium. Ilma koodita jääks lõputöö metoodiline panus tõestatavaks ainult tekstis kirjeldatud kujul, mis on vastuolus reprodutseeritavuse põhimõttega.

**3. Litsentside analüüs:**
*   **1. valik (Soovituslik):** Apache License 2.0 --- kuna toru sõltub TensorFlow ökosüsteemist (samuti Apache 2.0) ja \texttt{microWakeWord}-raamistikust ning kasutab agentpõhise arenduse käigus loodud koodi, mille üksikute mustritele võivad olla taotletud patendid; Apache 2.0 sisaldab selgesõnalist patendigarantii klauslit, mis kaitseb nii autorit kui ka taaskasutajat ning säilib kokkusobivuse hilisemate \texttt{microWakeWord} versioonidega.
*   **2. valik:** MIT --- annab maksimaalse vabaduse ja minimaalse kohustuse; sobib siis, kui patendigarantii pole hädavajalik. Puudus võrreldes Apache 2.0-ga on patendiklausli puudumine.
*   **3. valik:** BSD 3-Clause --- funktsionaalselt MIT-iga sarnane; lisaks keelab autori nime kasutamise kinnituse andmiseks ilma loata, mis võib bakalaureusetöö autori jaoks olla isikukaitse seisukohast meeldiv lisa.

---

### Tulemus: ESP32-S3 ESPHome konfiguratsioon ja \texttt{voice\_assistant}-integratsioonimuster

**1. Kirjeldus:**
ESPHome YAML-manifest ja sellega seotud konfiguratsioon, mis kirjeldab \texttt{v16c} (148\,KB TFLite-mudel) või väiksema (${\sim}57$\,KB) mudeli käivitamist ESP32-S3-Korvo-2 plaadil koos ${\sim}45$--$50$\,KB \texttt{tensor\_arena}-ga ja sidumist Home Assistanti \texttt{voice\_assistant}-liidesega lokaalse kõnetöötlusahela esimese astmena.

**2. Avaldamise põhjendus:**
Lõputöö üheks deklareeritud panuseks on ESP32-S3 ja Home Assistanti integratsioonimuster lokaalse nutikodu satelliidi näitel. Manifesti avaldamine annab Home Assistanti kogukonnale konkreetse, eestikeelsele äratussõnale optimeeritud lähtepunkti ning vähendab kordustehnoloogia loomise vajadust teiste väikeste keelte kogukondades.

**3. Litsentside analüüs:**
*   **1. valik (Soovituslik):** Apache License 2.0 --- kooskõlas ESPHome-i (MIT) ja Home Assistanti (Apache 2.0) ökosüsteemiga; patendiklausel kaitseb mikrokontrolleri-spetsiifiliste optimeerimismustrite (kvantiseerimine, voogedastusrežiimi olek) reprodutseerimist.
*   **2. valik:** MIT --- lihtsam ja ESPHome-i komponentide seas levinum; sobib siis, kui konfiguratsiooni soovitakse hõlpsalt lisada laiemasse ESPHome-i mustrikogusse.
*   **3. valik:** CC0 1.0 --- kuna YAML-konfiguratsiooni autorlus on suuresti kombinatoorne (komponentide kokku panemine), võib autoriõiguse-vaba avaldamine olla õigustatud, kui soovitakse maksimaalset taaskasutust ja ühilduvust dokumentatsiooniga; puuduseks on garantiide täielik puudumine.

---

### Tulemus: \texttt{kratt}-CLI-tööriistad (\texttt{user-test}, \texttt{validate-user-test}, \texttt{replay-user-test}, \texttt{summarize-user-test})

**1. Kirjeldus:**
Käsureatööriistade komplekt, mis salvestab kasutajatesti katsete metaandmed faili \texttt{trials.jsonl}, valideerib salvestuse vahetult pärast sessiooni (katsete arv, kanalid, diskreetimissagedus, RMS-i hoiatused), taasesitab külmutatud lävega mitut varimudelit (sh \texttt{v16c}, \texttt{expert-a}, \texttt{expert-b2}, \texttt{v6-residual}, \texttt{v10}, \texttt{v15} ning konsensus \texttt{expert-a+expert-b2}) ning koondab tuvastamismäära ja FPR-i koos Wilsoni usaldusvahemikega.

**2. Avaldamise põhjendus:**
Need tööriistad operatsionaliseerivad lõputöö kasutajatesti metoodikat (vt §\ref{sec:user-test-methodology}). Avaldamine võimaldab teistel uurijatel kasutada sama protokolli oma keele või äratusfraasi jaoks, ilma et oleks vaja sissejuurdnud salvestus- ja taasesitustaristut nullist üles ehitada. Eriti kasulik on osa, kus kõik mudelivariandid taasesitatakse \emph{identse} helisisendi peal, mis välistab vajaduse iga mudeli jaoks osalejate ütluste kordamise järele.

**3. Litsentside analüüs:**
*   **1. valik (Soovituslik):** Apache License 2.0 --- ühtlustamise põhjustel sama litsents kui treeningutoru; tagab, et kogu \texttt{kratt}-koodibaas on litsentside-tasemel ühilduv ning patendiklausel katab võimalikud konsensuse-/kaskaadarhitektuuri-spetsiifilised optimeerimisleiutised.
*   **2. valik:** MIT --- lihtne ja CLI-tööriistade kontekstis levinud; sobib, kui soovitakse minimaalset litsentsiteksti.
*   **3. valik:** GNU GPLv3 --- ainult juhul, kui autor soovib nõuda, et kõik tuletatud kasutajatesti tööriistad oleksid omakorda avatud lähtekoodiga. Käesoleva töö kontekstis on see tõenäoliselt liiga piirav, sest takistab integreerimist suletud-lähtekoodiga uuringutoodetega; mainitud üksnes täielikkuse huvides.

---

### Tulemus: Androidi rakendus valevallandumiste logimiseks

**1. Kirjeldus:**
Kotlinis kirjutatud Androidi rakendus, mis on viidatud kui ${\sim}99$~h välikatse tööriist ning agentpõhise arenduse keskne demonstratsioon. Rakendus salvestab valevallandumiste sündmusi koos vastavate helilõikudega päris kasutusolukorras, võimaldades koguda korpustes esinematuid negatiivseid näiteid.

**2. Avaldamise põhjendus:**
Rakendus tõendab lõputöö väidet, et standardsed KWS võrdlusalused ei ennusta reaalse kasutuse FAPH-i ning et kaasavad päris keskkonna logijad on hädavajalikud. Lähtekoodi avaldamine annab teistele madala ressursiga keele projektidele konkreetse stardilauad, et koguda oma välikatse-andmeid samaväärsel viisil. Avaldamise eel tuleb veenduda, et koodibaasis ei oleks paigaldatud Wi-Fi võrgu nimesid, isiklikke API-võtmeid ega kasutajate seadme-tuvastusandmeid.

**3. Litsentside analüüs:**
*   **1. valik (Soovituslik):** Apache License 2.0 --- Androidi ökosüsteemi de facto litsents (AOSP ise on Apache 2.0); patendiklausel on Androidi platvormil eriti oluline mobiili-spetsiifiliste aktiveerimismustrite tõttu.
*   **2. valik:** MIT --- ühtlasem \texttt{kratt}-koodi ülejäänud osaga, kui valitakse MIT-rada; pakub vähem patendikaitset.
*   **3. valik:** GNU GPLv3 --- sobiks juhul, kui soovitakse, et tuletatud kommertstoode peab olema avatud; käesolevas kontekstis on see ebatõenäoline tee, kuna rakendus on uurimisvahend, mitte lõpptarbijatoode.

---

### Tulemus: Treenitud äratussõna mudelid TFLite/ONNX-formaadis (\texttt{v16c}, \texttt{expert-a}, \texttt{expert-b2}, \texttt{v6-residual}, \texttt{v10}, \texttt{v15})

**1. Kirjeldus:**
Lõputöös kirjeldatud kvantiseeritud TFLite-mudelid ja nende dokumentatsioon (NOTES.md ning \texttt{wake-word/docs/MODEL\_LINEAGE.md}). Mudelid on treenitud \texttt{microWakeWord} raamistikuga, sisendiks 40-mõõtmeline mel-spektrogramm 1500\,ms aknal, väljundiks ühe äratussõna tõenäosus voogedastusrežiimis. Sisalduv reprodutseeritav teave: ablatsioonid (residuaalühendused, SpecAugment), arhitektuurivalikud, kontrollpunktide valikukriteerium.

**2. Avaldamise põhjendus:**
\enquote{Kuule Kratt} on eestikeelne äratussõna avalikus mütoloogias üldlevinud terminist, mis ei kuulu ühelegi konkreetsele isikule. Mudelite avaldamine tagab, et eestikeelse nutikodu hääljuhtimise puudujääki (vt sissejuhatus) saab kogukond iseseisvalt täita ning et ekspertmudelite konsensus (\texttt{expert-a}~+~\texttt{expert-b2}, FAPH~$=$~$0{,}79$) on uuesti reprodutseeritav. Enne avaldamist tuleb veenduda, et treeningandmestik ei sisaldaks tuvastatavate kõnelejate isikuandmeid sellisel kujul, mis võimaldaks mudelist kõnelejaid taastada.

**3. Litsentside analüüs:**
*   **1. valik (Soovituslik):** Apache License 2.0 --- mudelifailid ise on käsitletavad tarkvarana selles mõttes, et neid kasutatakse järeldamiseks koos koodibaasiga; sama litsents tagab, et kogum (kood + mudel) on litsentsidehierarhias ühene. Apache 2.0 patendiklausel kaitseb arhitektuurispetsiifiliste järeldamis-mustrite eest.
*   **2. valik:** Creative Commons Attribution 4.0 (CC BY 4.0) --- kasutusel paljudes avalikes mudelite jaotustes (nt \texttt{openWakeWord}); sobib siis, kui mudelifaile käsitletakse pigem andme-laadse artefaktina kui koodina. Nõuab autorite ja muudatuste märkimist.
*   **3. valik:** OpenRAIL-M (Responsible AI License, mudelite variant) --- sisaldab piirangulausekesi pahatahtliku kasutuse vältimiseks (nt järelevalve-otstarbel); puuduseks on, et see ei ole \emph{permissive} klassikalises mõttes ja võib piirata taaskasutust akadeemilises ökosüsteemis. Mainitud üksnes juhuks, kui autor peab oluliseks seada eetilisi piiranguid äratussõna mudeli juurutamisele.

---

### Tulemus: Sünteetiliste positiivsete näidete genereerimise koodibaas

**1. Kirjeldus:**
Skriptid, mis kasutavad Tartu Neurokõne, XTTS v2 ja Fish S2 Pro lahendusi sünteetiliste \enquote{Kuule Kratt} näidete genereerimiseks koos andmete deduplitseerimise (Neurokõne on deterministlik), mikrofoni-sümmeetria ja siltide-kontrolli loogikaga (vt v7-st õpitud teist järku sildistusprobleem).

**2. Avaldamise põhjendus:**
Sünteetilise andmestiku roll on lõputöö üks neljast võrdlusteljest \texttt{microWakeWord} ja \texttt{openWakeWord} vahel. Genereerimisskriptide avaldamine võimaldab teistel madala ressursiga keelte projektidel taasesitada sama lähenemise, ilma et nad peaksid avastama uuesti samad veaohud (kuule-prefiksi õppimine, dubleeritud klippide ülerepresenteerimine, mikrofoni-asümmeetria). Toorsalvestusi ega TTS-teenuste väljundeid \emph{ennast} sellesse repositooriumisse ei lisata, kooskõlas ülesandepüstituses kirjeldatud privaatsusriski vältimisega.

**3. Litsentside analüüs:**
*   **1. valik (Soovituslik):** Apache License 2.0 --- ühtlustatud kogu \texttt{kratt}-koodibaasi raames; käsitleb skripti ennast, mitte selle väljundeid (TTS-teenuste väljundid alluvad nende teenuste kasutustingimustele).
*   **2. valik:** MIT --- sobib, kui soovitakse võimalikult väikest litsentsiteksti, eriti kui skriptid on lühikesed.
*   **3. valik:** CC0 1.0 --- juhul kui skripte käsitletakse ennekõike juhendmaterjalina, mille puhul autoriõiguse-piirangud on liigsed; puuduseks garantiide puudumine.

---

### Tulemus: Kasutajatesti küsimustik ja sessiooniprotokoll (UMUX-Lite kaks väidet, uurija küsimused, salvestusprotseduur)

**1. Kirjeldus:**
Tekstidokument, mis kirjeldab umbes 10-minutilist ühe-nutipirni sessiooni (viis puhast äratussõna ütlust, viis sarnast negatiivfraasi, kuus skriptitud pirnikäsku, üks vabas vormis valgusülesanne), kaheastmelist nõusolekumudelit ning sessioonijärgset küsimustikku usaldusväärsuse, kiiruse, käskude loomulikkuse ja kodus kasutamise valmisoleku kohta. Sisaldab valideeritud UMUX-Lite kaht väidet ning uurija koostatud diagnostilisi küsimusi.

**2. Avaldamise põhjendus:**
Protokolli avaldamine on osa metoodikateemalisest panusest: see näitab, kuidas \emph{kontrollida} äratussõna mudelit kasutuskogemuse-tasandil ilma osalejate ütluste kordamise vajaduseta mudeliversioonide vahel (taasesitus külmutatud lävel). Teised väikese ressursiga keelte projektid saavad protokolli kasutada otse või kohandatuna.

UMUX-Lite kahe väite osas tuleb arvestada, et need on \cite{lewis2013umuxlite,sauro2009seq} põhjal valideeritud lühiskaala; avaldamine peab säilitama autoriõiguse-mainimise nõuded ning ei tohi lugeda neid väiteid omaenda panuseks.

**3. Litsentside analüüs:**
*   **1. valik (Soovituslik):** Creative Commons Attribution 4.0 (CC BY 4.0) --- standardlitsents akadeemilise tekstilise materjali jaoks; säilitab autori atribuudi nõude ning lubab tõlkimist, kohandamist ja taasavaldamist.
*   **2. valik:** Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0) --- tagab, et tuletatud küsimustike-versioonid jäävad samuti avatuks; sobib, kui autor soovib nakkav-mehhanismiga julgustada teisi protokolle ka avatuna avaldama.
*   **3. valik:** CC0 1.0 --- juhul kui autor loeb küsimustiku-vormistamise loomingulist panust marginaalseks; UMUX-Lite väiteid see siiski ei kataks, sest need on eraldi õigusliku staatusega.

---

### Tulemus: Pseudonüümsed kasutajatesti tehnilised tulemused (\texttt{trials.jsonl}-laadne andmestik)

**1. Kirjeldus:**
Iga osaleja sessiooni kohta üks fail, mis sisaldab katsete metaandmeid (katse tüüp, ajatempel, mudel-skoorid, kontrollläve juures aktiveerumise tulemus), kuid mitte heli, ja mille väljad on pseudonüümitud (osaleja-ID, mitte nimi). Saadakse \texttt{kratt user-test} ja \texttt{kratt summarize-user-test} koondamise tulemusena.

**2. Avaldamise põhjendus:**
Tehniliste pseudonüümsete tulemuste avaldamine on hõlmatud minimaalse nõusoleku tasemega (vt §\ref{sec:user-test-methodology}). See annab teistele uurijatele võimaluse taasesitada koondmõõdikud (tuvastamismäär, FPR koos Wilsoni vahemikega) ning kontrollida lõputöös esitatud arve, ilma et oleks vaja heli ennast jagada. Enne avaldamist tuleb käivitada lõplik valideerimisring, mis kontrollib, et failidesse ei oleks juhuslikult sattunud osaleja-tuvastatavaid välju (nt seadme-MAC-aadress või täpne ajatempel, mis võimaldaks taastada osaleja sessiooni asukohaga sidumist).

**3. Litsentside analüüs:**
*   **1. valik (Soovituslik):** Creative Commons Attribution 4.0 (CC BY 4.0) --- akadeemilises andmevahetuses (sh teadusandmete arhiivides nagu Zenodo) levinuim litsents; säilitab atribuudi.
*   **2. valik:** Creative Commons CC0 1.0 (Public Domain Dedication) --- maksimaalne taaskasutus, eriti kui andmehulk on väike ja kogumis-rolli atribuudikohustus muutuks bürokraatlikult koormavaks. Eelistatud, kui osalejate teadlikku nõusolekuvormi tõlgendatakse nii, et autoriõigus on mõõdiku-tasandil minimaalne.
*   **3. valik:** Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0) --- ainult juhul, kui eetiline raamistik nõuab kommertskasutuse keelamist (nt ETAG-i poolt soovitatud piirang); puuduseks on, et see piirab taaskasutust paljudes õiguspärastes uuringukontekstides ning ei sobi täielikult \emph{open science} põhimõttega.

---

### Tulemus: Kasutajatesti märgendatud heliklipid (audio-opt-in nõusolekuga osalejad)

**1. Kirjeldus:**
16~kHz mono WAV-klipid, mis on salvestatud kasutajatesti sessiooni ajal ja millele kasutaja on andnud eraldi audio-opt-in nõusoleku. Sisaldavad osaleja häält ja võivad sisaldada taustahelisid.

**2. Avaldamise põhjendus:**
Avaldamine on kõrge eetilise koormusega ning seda tuleks kaaluda \emph{ainult} juhul, kui (a) eetikakomitee (eetika@taltech.ee) on andnud positiivse arvamuse, (b) kõigi avaldatavate klippide osalejatelt on saadud kirjalik audio-opt-in koos selgesõnalise nõusolekuga avalikuks taasavaldamiseks, ning (c) klipid on auditeeritud isikuandmete (isikunimed, aadressid, terviseandmed) eemaldamise suhtes. Vastasel juhul tuleb klipid hoida ainult uurimisrühma sisesena ning need ei kuulu avaliku GitHub-repositooriumi alla.

**3. Litsentside analüüs:**
*   **1. valik (Soovituslik):** Creative Commons Attribution 4.0 (CC BY 4.0) --- kuna audio kvalifitseerub andmestikuna; eeldab, et eelnimetatud nõusoleku- ja eetikakomitee-tingimused on täidetud. Atribuut tuleb anda projektile, mitte üksikutele osalejatele (osalejate nimesid ei avaldata).
*   **2. valik:** Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0) --- annab täiendava kaitse kommertskasutuse vastu, mis on isikuandme-laadse heli puhul ettevaatlik vaikevalik; puuduseks on \emph{open science} põhimõttega osaline vastuolu.
*   **3. valik:** Mitte avaldada (puudub avalik litsents) --- kõige tõenäolisem ja eetiliselt kõige usaldusväärsem valik, kui mistahes ülaltoodud tingimustest jääb täitmata. See ei ole formaalne litsents, vaid teadlik otsus, mille lõputöö nõusolekumudeli kaheastmeline ülesehitus ette näeb.

---

### Tulemus: Lõputöö LaTeX-allikas (peatükid, \texttt{references.bib}, joonised)

**1. Kirjeldus:**
\texttt{docs/thesis/thesis-tex-estonian/} all paiknev LaTeX-tekstide, BibTeX-viidete ja jooniste kogum, mis moodustab lõputöö enda. Lõputöö kaitstakse 2026-05-18 tähtajaks TalTech-is.

**2. Avaldamise põhjendus:**
Töö on riikliku ülikooli bakalaureusetöö, mis muutub niikuinii TalTech-i raamatukogu kaudu kättesaadavaks. LaTeX-allika eraldi avaldamine GitHub-is võimaldab kogukonnal näha mitte ainult lõpptulemust, vaid ka töö versioneerimise ajalugu, mis on agentpõhise arenduse uurimisartefakti seisukohast eraldi väärtuslik. TalTech-il võivad olla töö avaldamise suhtes oma eeskirjad, mistõttu litsentsivalik tuleb kooskõlastada juhendaja ja instituudiga.

**3. Litsentside analüüs:**
*   **1. valik (Soovituslik):** Creative Commons Attribution 4.0 (CC BY 4.0) --- akadeemiliste tekstide jaoks levinud, lubab tõlkimist (sh inglise keelde) ja taasavaldamist atribuudiga.
*   **2. valik:** Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0) --- kindlustab, et kohandatud versioonid jäävad avatuks; sobib, kui töös sisalduvad ülevaatlikud osad (metoodika kirjeldus) on mõeldud edasiseks tuletatavaks materjaliks.
*   **3. valik:** Creative Commons Attribution-NoDerivatives 4.0 (CC BY-ND 4.0) --- juhul kui autor soovib säilitada teksti integreeritust kaitstud kvalifikatsioonitööna ja vältida valikulist tsiteerimist, kus tema väiteid moonutatakse. Puuduseks on tõlkimise ja kohandamise piiramine, mis on \emph{open science} mõttes tagasiminek.

---

## Üldised tähelepanekud ja ohutuskontrolli (sanitization) loend

Enne mistahes ülaltoodud artefakti avaldamist tuleb kontrollida järgmist:

1.  **Pääsutõendid ja API-võtmed.** Repositooriumis ei tohi olla Home Assistanti pikajalisi pääsutõendeid, Tartu Neurokõne / XTTS / Fish S2 Pro API-võtmeid, Wi-Fi paroole ESPHome manifestides ega TalTech-i HPC SLURM-i kasutaja-spetsiifilisi tunnuseid. Soovitatav on kasutada \texttt{git-secrets} või samaväärset eelkommiti kontrolli ning käivitada \texttt{trufflehog} või \texttt{gitleaks} kogu ajaloo peal enne avalikustamist.

2.  **Kõnelejate isikuandmed.** Treenitud mudelid ei tohi võimaldada kõnelejate taastamist (kõnelejate-tuvastuse rünne); andmekogumis-skripte avaldades tuleb veenduda, et toorsalvestused ei jõuaks repositooriumisse, kooskõlas ülesandepüstituse \enquote{toorsalvestuste avalikustamisest tulenevate privaatsusriskide vältimine} põhimõttega.

3.  **Kasutajatesti pseudonüümitus.} \texttt{trials.jsonl}-faili väljad peavad piirduma osaleja-pseudonüümi, katse tüübi, mudel-skoori ja ajatempliga sessiooni-relatiivsel skaalal; absoluutsed ajatemplid ja seadme-tuvastusandmed (MAC, hostname) tuleb eemaldada.

4.  **Litsentsitekstide ühilduvus.** Kui projekt valib \texttt{microWakeWord} alusel Apache 2.0, siis kõik koodi-tasemel artefaktid peaksid olema sama litsentsi all; \emph{andme-tasemel} artefaktid (mudelifailid kui andmed, küsimustik, mõõdikud) võivad olla CC BY 4.0 all, mis on Apache 2.0-ga kõrvuti kasutatav.

5.  **TalTech ja juhendaja.** Lõputöö LaTeX-allika ja kasutajatesti andmete suhtes tuleb saada juhendaja ning vajaduse korral instituudi nõusolek, eriti enne audio-opt-in heliklippide avaldamist; eetikaküsimustes tuleb pöörduda eetika@taltech.ee poole, nagu projekti varasemates juhistes märgitud.

## Kokkuvõte

Kogu \texttt{kratt}-koodibaasi (treeningutoru, ESPHome konfiguratsioon, CLI-tööriistad, Androidi rakendus, sünteetiliste näidete generaatorid) jaoks soovitatakse \textbf{Apache License 2.0} ühtlust ja patendikaitset silmas pidades. Mudelifailide jaoks on samuti eelistatud Apache 2.0, kuigi CC BY 4.0 oleks andme-laadse artefaktina mõistetav alternatiiv. Tekstilised artefaktid (küsimustik, lõputöö LaTeX-allikas, pseudonüümsed mõõdikud) sobivad \textbf{CC BY 4.0} alla. Kasutajatesti heliklippe \emph{ei} avaldata enne, kui audio-opt-in nõusolek, eetikakomitee positiivne arvamus ning isikuandme-audit on dokumenteeritud; sellise tingimuse täidetuse korral oleks litsentsisoovitus CC BY 4.0 (alternatiivina CC BY-NC 4.0). Eraldi nimekiri ohutuskontrolli sammudest (pääsutõendid, kõnelejate-tuvastus, pseudonüümitus) tuleb läbida iga repositooriumi avalikuks tegemise eel.
