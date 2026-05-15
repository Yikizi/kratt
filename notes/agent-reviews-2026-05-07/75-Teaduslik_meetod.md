---
source_prompt: "/Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/07_Teadusartikkel/Teaduslik_meetod.txt"
prompt_type: "teadusfoorumi_metoodika_analuus"
generated: 2026-05-07
---

# Teadusliku meetodi kaart Krati lõputöö jaoks

## Piirang ja tõlgendus

Algses viibas on teadusfoorumi nimi jäetud täitmata (`<Sisesta ajakirja või konverentsi nimi>`) ning siin keskkonnas ei ole Google Searchi ega muud veebipäringut. Seetõttu ei saa ma ausalt väita, et olen teinud konkreetse ajakirja või konverentsi 2010+ publikatsioonide bibliomeetrilise analüüsi ega kontrollinud Google'i abil iga näite värsket olemasolu.

Alljärgnev on seega **parim võimalik metoodiline kaardistus** lõputöö tegeliku teemavälja põhjal: äratussõna tuvastus, keyword spotting (KWS), kõnetehnoloogia, servaseadme/embedded inference ja nutikodu hääljuhtimine. Realistlikud foorumid, mille avaldamiskultuuriga see töö kõige rohkem haakub, on eeskätt **ICASSP**, **Interspeech**, kõnetehnoloogia ajakirjad nagu **IEEE/ACM TASLP**, üldisemad ülevaatefoorumid nagu **IEEE Access** ning reaalse kasutuse/privaatsuse suunal ka **IMWUT**, **Computer Speech & Language** ja turvakonverentsid. Järjestus allpool ei ole ühe foorumi loendusel põhinev sagedusväide, vaid valdkonna ja lõputöös kasutatud kirjanduse põhjal hinnatud tõenäoline meetodite levimus.

## Lühijäreldus lõputöö suhtes

Krati lõputöö paikneb metodoloogiliselt eelkõige **eksperimentaalse KWS-süsteemi hindamise** traditsioonis, kuid selle eristuv panus on data-centric ja hindamisprotokolli-põhine: töö ei väida peamiselt uut arhitektuuri, vaid näitab, kuidas väikese ressursiga keele äratussõna puhul tuleb vältida andmeleket, mõõta pidevvoo FAPH-i, eristada positiivseid/negatiivseid/taustaheli andmeid ning lisada sihtfraasiga sarnaste ja prefiksi-tüüpi valekäivituste kontrollid.

### 1. Experimental Evaluation / Benchmarking (eksperimentaalne võrdlushindamine)

* **Kirjeldus:** KWS ja wake-word kogukonnas tähendab see tavaliselt mudeli või treeninguseadistuse hindamist kontrollitud andmekorpustel. Tüüpilised elemendid on treeningu-, valideerimis- ja testjaotus; avalikud või projektispetsiifilised korpused; ROC/DET-laadsed kõverad; FRR, FPR, recall ja valeaktiveeringute mõõdikud; lävevalik valideerimisandmetel; mudeliversioonide õiglane võrdlus samadel testikomplektidel; sageli ka arhitektuuri- või treeninguablatsioonid.
* **Miks levinud:** Kõnetuvastuse ja signaalitöötluse foorumites peab väide olema mõõdetav. Äratussõna süsteemis ei piisa kvalitatiivsest demost: tuleb näidata, milline on tabamismäär, kui palju on valeaktiveeringuid ja milline kompromiss tekib läve muutmisel. Krati töö põhimetoodika — Speech Commands `marvin` kontrollkatse, hiljem disjoint hold-out komplektid, FAPH, Wilsoni ja Poissoni usaldusvahemikud — kuulub sellesse paradigmasse.
* **Näidisartiklid/tööd:**
  * Guoguo Chen, Carolina Parada ja Georg Heigold (2014). "Small-footprint keyword spotting using deep neural networks". — Klassikaline small-footprint KWS eksperimentaalne mudelihindamine; lõputöös kasutatud taustkirjandusena.
  * Tara N. Sainath ja Carolina Parada (2015). "Convolutional neural networks for small-footprint keyword spotting". — CNN-põhine small-footprint KWS töö; tüüpiline arhitektuuri + võrdlushindamise formaat.
  * Pete Warden (2018). "Speech Commands: A Dataset for Limited-Vocabulary Speech Recognition". — Andmestiku ja baseline'i roll; Krati töös kasutati Speech Commands `marvin` ülesannet toru otsast-lõpuni valideerimiseks.
* **Seos Krati tööga:** Väga tugev. Töö suurim metoodiline nihe on just see, et esialgne klipi-taseme hindamine osutus ebapiisavaks ning asendati sõltumatute kõrvalejäetud komplektide, pidevvoo FAPH-i ja kontrollitud lävepõhise võrdlusega.
* **Kindlus:** kõrge valdkonna tasemel; madal konkreetse foorumi sagedusjärjestuse suhtes, sest foorumi nime ei antud ja otsingut teha ei saanud.
* **Lüngad:** Puudub Google'iga kontrollitud loend konkreetse venue kõigist 2010+ KWS artiklitest; näited on võetud lõputöö bibliograafiast ja tekstist, mitte uuest süstemaatilisest otsingust.

### 2. On-device System Prototyping and Deployment Evaluation (servaseadme-süsteemi prototüüpimine ja juurutushindamine)

* **Kirjeldus:** See lähenemine käsitleb äratussõna mudelit mitte ainult klassifikaatorina, vaid töötava süsteemi osana. Uuritakse, kas mudel mahub seadme mällu, töötab voogedastusrežiimis, saab kvantiseerida, annab sobiva latentsuse, integreerub firmware'i või häälassistendi toruga ning säilitab kvaliteedi päris mikrofoni ja akustilise keskkonna korral. Terminoloogia on tavaliselt *on-device keyword spotting*, *small-footprint KWS*, *streaming inference*, *quantization*, *cascade*, *voice trigger* ja *deployment evaluation*.
* **Miks levinud:** Wake-word detektor on alati-aktiivne komponent. Seetõttu on arvutuskulu, mälu, latentsus ja valeaktiveeringud sama olulised kui mudeli offline täpsus. Krati töö ESP32-S3, TensorFlow Lite INT8, ESPHome ja Home Assistantiga kuulub otseselt sellesse süsteemitehnilisse traditsiooni.
* **Näidisartiklid/tööd:**
  * Apple Machine Learning Research (2017). "Hey Siri: An On-device DNN-powered Voice Trigger for Apple's Personal Assistant". — Tööstuslik on-device voice-trigger süsteemi kirjeldus; lõputöös kasutatud võrdlusena suurte süsteemide negatiivandmete ja kaskaadse hindamise kohta. Märkus: see on tööstuslik tehniline artikkel, mitte klassikaline eelretsenseeritud konverentsipaber.
  * Shubham Kundu jt (2023). "HEiMDaL: Highly Efficient Method for Detection and Localization of Wake-Words". — Tõhususe ja kaskaadse/mitmeastmelise detektsiooni suund, mida Krati töö seostab ekspertmudelite konsensusega.
  * Kevin Ahrendt (2026). "microWakeWord" ja David Scripka (2026). "openWakeWord". — Avatud lähtekoodiga raamistike näited, mis on Krati töö praktilised võrdluspunktid. Need ei ole samas mõttes eelretsenseeritud artiklid, kuid on projekti ja kogukonnapraktika seisukohalt olulised artefaktid.
* **Seos Krati tööga:** Väga tugev praktilisel tasandil. Kratt ei arenda ainult mudelit, vaid hindab raamistikku, TFLite eksporti, ESP32-S3 sobivust, `tensor_arena`/flash-mälupiiranguid ning Home Assistanti lõimimist. Samas lõputöö enda põhitõend ei ole veel lõplik seadmevalideerimine laia kasutajaskonnaga, vaid prototüübi ja hindamismetoodika dokumentatsioon.
* **Kindlus:** keskmine kuni kõrge valdkonna tasemel; keskmine konkreetsete näidete suhtes, sest osa võrdluspunktidest on tööstuslikud või open-source artefaktid, mitte venue-publikatsioonid.
* **Lüngad:** ESP32-S3 runtime'i lõplik töömälu/latentsuse ja kasutajatesti tulemused on lõputöös veel piiranguna märgitud; foorumipõhist levimust ei saa ilma otsinguta tõendada.

### 3. Data-centric Robustness Evaluation / Hard-negative and Synthetic-data Study (andmepõhine robustsuse hindamine, rasked negatiivid ja sünteetiline kõne)

* **Kirjeldus:** See lähenemine uurib, kuidas andmestiku koostis, domeeninihe, sünteetiline kõne, hard-negative näited ja päris kasutusolukorra helid mõjutavad KWS mudeli töökindlust. Meetod ei seisne ainult uue mudeli testimises, vaid selles, et ehitatakse või auditeeritakse andmestikke: positiivsed klipid, üldised negatiivid, taustaheli, foneetiliselt sarnased fraasid, prefiksi-only juhud, pööratud järjekord ja kuule/kule segiajamine. Tüüpilised märksõnad on *hard negative mining*, *synthetic data*, *TTS overfitting*, *domain mismatch*, *false trigger analysis*, *real-world evaluation gap*.
* **Miks levinud:** Pärast seda, kui small-footprint KWS arhitektuurid muutusid tugevaks, nihkus suur osa praktilisest kvaliteediprobleemist andmetele ja hindamisele. Äratussõna süsteemis võib mudel näida hea kitsal testil, kuid vallanduda teleheli, sarnaste fraaside, teise mikrofoni või teise kõneleja peale. Krati lõputöö põhiline teaduslik panus on just selles suunas: andmeleke, positiivsete näidete reostus, TTS/reaalkõne lõhe, sihtkeelsed negatiivid ja fraasi-täielikkuse mõõdikud.
* **Näidisartiklid/tööd:**
  * Iván López-Espejo jt (2021). "Deep Spoken Keyword Spotting: An Overview". — Ülevaade, mis toetab FAPH/FA-per-hour tüüpi mõtlemist ja näitab, et KWS hindamine ei piirdu klipi-taseme täpsusega.
  * Jingyong Hou jt (2020). "Mining Effective Negative Training Samples for Keyword Spotting". — Hard-negative suuna näide; Krati töös vastab sellele sihtfraasiga sarnaste negatiivide ja prefiksi-/segiajamiskomplektide vajadus.
  * Hyun Jin Park jt (2024). "Adversarial Training of Keyword Spotting to Minimize TTS Data Overfitting". — Sünteetilise kõne ja päriskõne lõhe näide; Krati töös ilmneb sama risk TTS-positiivide, XTTS-kloonide ja reaalsete kõnelejate erinevuses.
  * Emmanuel Dubois ja Juan Pablo Carrascal (2020). "Unintended Triggers: Characterising Accidental Activations of Smart Speakers". — Reaalse kasutuse valeaktiveeringute uuring; Krati arutelu kasutab seda standardsete benchmark'ide ja tegeliku kasutuse lõhe põhjendamiseks.
* **Seos Krati tööga:** Kõige tugevam töö originaalpanuse mõttes. Krati töö ei saa praegu väita, et üks mudel lahendas kõik eesmärgid, kuid saab tugevalt väita, et andmestiku- ja hindamisprotokolli audit muutis nähtavaks riskid, mida tavaline KWS benchmark ei näita.
* **Kindlus:** kõrge Krati töö sobivuse suhtes; keskmine valdkonna üldise "kolmanda koha" suhtes, sest data-centric töid on palju, kuid nende osakaal sõltub valitud venue'st.
* **Lüngad:** Vajalik oleks venue-põhine otsing, et eristada, kas konkreetses foorumis domineerivad rohkem arhitektuuri-, süsteemi- või andmestikutööd. Samuti vajab Krati lõplik väide sõltumatut 20--30 osalejaga kasutajatesti.

## Soovitus lõputöö positsioneerimiseks

Kui lõputööd tuleb hiljem siduda ühe konkreetse teadusfoorumiga, oleks kõige konservatiivsem valida **Interspeech** või **ICASSP**, sest lõputöö viidatud KWS põhitööd ja terminoloogia sobituvad nende kõne- ja signaalitöötluse avaldamiskultuuriga. Sellisel juhul tuleks metoodikat kirjeldada mitte kui üldist "kasutajauuringut" või ainult "tarkvaraarendust", vaid kui:

1. **small-footprint / on-device KWS experimental evaluation**,
2. **streaming false-accept evaluation with held-out negative audio**, ja
3. **data-centric robustness audit for low-resource wake-word detection**.

Krati töö peamine kaitstav väide on metoodiline: väikese ressursiga keele äratussõna puhul ei ole piisav üks koondnumber ega üks ilus demo. Vajalik on mitmekihiline tõendusprotokoll, mis kontrollib sõltumatust treeningandmetest, pidevvoo FAPH-i, kõnelejate ja mikrofonide domeeninihet, sarnaseid negatiivfraase ning prefiksi-/järjekorra-/segiajamisvigu.
