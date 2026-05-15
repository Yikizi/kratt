---
source_prompt: Riskid.txt
prompt_type: generative-evaluative (riskianalüüs)
generated: 2026-05-07
---

# Riskianalüüs: eestikeelse äratussõna lahendus \enquote{Kuule Kratt}

Käesolev analüüs lähtub esitatud lõputöö mustandist (sissejuhatus, metoodika, tulemused/arutelu, kokkuvõte ning eesti- ja ingliskeelne abstrakt). Lahendus koosneb äratussõna mudelist (\texttt{microWakeWord}, \texttt{v16c} aktiivne kandidaat; ekspertide \texttt{expert-a + expert-b2} konsensus), ESP32-S3 / ESPHome \texttt{voice\_assistant} sihtseadmest, Home Assistanti integratsioonist ning planeeritud 20--30 osalejaga kasutajatestist. Riskid on liigitatud nelja kategooriasse, hinnatud tõenäosuse ja mõju lõikes ning igale on pakutud konkreetne maandamismeede.

---

## 1. Tehnilised ja turvariskid

### 1.1 Klipi-tasandi hindamise andmeleke kordub uue korpuse lisamisel

* **Risk:** Töö ise dokumenteerib, et varasem v6 mudeli FPR 0,4\% oli mälu, mitte üldistuse mõõt, kuna Common~Voice klipid sattusid samaaegselt nii treeningusse kui hindamisse. Sama risk taastekib iga kord, kui projekti lisandub uus korpus (nt täiendav eestikeelne kõnekorpus, kasutajatesti audio) ilma, et kohustuslik disjointsuskontroll oleks osa pakikonveierist (\emph{pipeline}).
* **Hinnang:** Tõenäosus: Keskmine | Mõju: Kõrge
* **Maandamisstrateegia:** Lisada \texttt{kratt} käsureatööriistadesse kohustuslik eelkontroll, mis blokeerib treeningu käivitamise, kui treeningu- ja testikomplekti faili räsisummade (SHA-256) kaudu tuvastatakse kattuvus. Lisaks võtta kasutusele kõneleja-tasandi (mitte klipi-tasandi) jaotus, kuna sama kõneleja erinevad ütlused jagavad akustilist allkirja.

### 1.2 \texttt{microWakeWord} ja \texttt{ESPHome} kui kolmandate osapoolte üksikud sõltuvused

* **Risk:** Kogu juurutusrada (treening, eksport TFLite, käitamine ESP32-S3-l) tugineb kahele aktiivselt arendatavale, ent väikesele avatud lähtekoodiga projektile. Tagasiühildumatu API muutus, mahajätt või vea sissetoomine eksportijasse mõjutab nii \texttt{v16c} kandidaati kui ka kasutajatesti taasmängu tööriista \texttt{kratt replay-user-test}.
* **Hinnang:** Tõenäosus: Keskmine | Mõju: Keskmine
* **Maandamisstrateegia:** Külmutada konkreetne \texttt{microWakeWord} ja \texttt{ESPHome} versioon (commit-hash) kasutajatesti aktiivseks vooruks; säilitada kohalik peegelpilt repositooriumist (vendored mirror); kontrollida igal CI-käitusel, et eksporditud TFLite-mudeli baidi-tasandi räsi vastab varem fikseeritule.

### 1.3 Kvantiseerimisjärgse mudeli käitumise drift seadme peal

* **Risk:** Töö raporteerib FAPH ja tuvastamismäära skriptitud taasmängu (\emph{scripted offline}) kaudu, kuid juurutusplatvorm on ESP32-S3 koos liuakna keskmise ja võimaliku VAD-iga. Töö ise eristab nelja FAPH-varianti ja hoiatab, et need pole otse võrreldavad. Risk on, et kvantiseeritud INT8 mudeli käitumine seadmes erineb taasmängu tulemustest piisavalt, et juurutuslävi (cutoff $\geq$ 0,97) lakkab vastamast kavandatud sihile.
* **Hinnang:** Tõenäosus: Kõrge | Mõju: Keskmine
* **Maandamisstrateegia:** Enne kasutajatesti läve külmutamist mõõta sama 20-minutilise kontrollkorpuse peal nii \emph{scripted offline} kui ka \emph{field}-FAPH samal Korvo-2 seadmel; dokumenteerida läve kalibreerimine eraldi tabelina ning siduda \texttt{v16c} manifest unikaalse \texttt{tensor\_arena} suurusega (lähtuvalt §\ref{subsec:quantization} 45--50~KB).

### 1.4 \emph{Single point of failure} kasutajatesti ühe häälseadme näol

* **Risk:** Kasutajatesti aktiivne süsteem on \emph{üks} külmutatud Korvo-2 seade. Riistvararike (mikrofon, USB-toide, flash-mälu degradatsioon, vale firmware-versioon) keset andmekogumist tähendab, et osa sessioonidest pole võrreldavad ülejäänud sessioonidega ja terve nišikaitsmise alus laguneb.
* **Hinnang:** Tõenäosus: Keskmine | Mõju: Kõrge
* **Maandamisstrateegia:** Hoida valmis ette flash-itud teine identne Korvo-2 \enquote{varuseade} koos sama firmware'i ja sama \texttt{v16c} manifestiga; iga sessiooni alguses käivitada lühike \enquote{tervisekontroll} (kümme kontrollitud äratust, RMS-i lävi, latentsuse mõõtmine) ning logida tulemus \texttt{trials.jsonl}-isse; vahetada seade kohe, kui tervisekontroll ebaõnnestub.

### 1.5 Salvestatud kasutajatesti audio terviklikkus ja säilitamine

* **Risk:** \texttt{kratt user-test} tööriist talletab nii \texttt{trials.jsonl} kui ka 16~kHz mono WAV-failid. Kui need failid lähevad teel arvutist projektihoidlasse kaduma, riknevad (failide poolik kirjutamine seansi katkestumisel) või sünkroonitakse ekslikult avalikku keskkonda, kannatab nii teaduslik reprodutseeritavus kui GDPR-vastavus.
* **Hinnang:** Tõenäosus: Keskmine | Mõju: Kõrge
* **Maandamisstrateegia:** Kirjutada iga sessiooni järel kohe kontrollsumma-fail (\texttt{sha256sums.txt}); hoida toorhelifaile vaid krüpteeritud mahul (FileVault või LUKS); lisada \texttt{.gitignore}-isse selgesõnaline blokeering kõigile \texttt{user-test}-i alamkaustadele; teha igapäevane krüpteeritud varukoopia välisele kandjale, mis hoitakse arvutist eraldi.

### 1.6 Skaleeritavus: pidevvoo FAPH lubadus tugineb piiratud korpusele

* **Risk:** Töö lubadus FAPH = 0{,}79 on punkthinnang Common~Voice ET kõrvalejäetud komplektil; töö ise tunnistab, et Poissoni 95\% vahemik on lai. Kui süsteem juurutatakse mitmesse erineva akustikaga koju (peresid 20--30), võivad tegelikud määrad olla suurusjärgu suuremad, kuna kodu sisaldab televiisorit, muusikat, köögihelisid ja teisi kõnelejaid teises ruumis.
* **Hinnang:** Tõenäosus: Kõrge | Mõju: Keskmine
* **Maandamisstrateegia:** Esitada FAPH alati koos täpse Poissoni-Garwoodi vahemikuga ja jälgitud tundide arvuga (T); raporteerida lõputöös ainult \emph{operatsiooniline siht} ($<$1 valeaktiveering tunnis), mitte universaalne lubadus; planeerida arutelu peatükis selgelt, et 99~h Android-välikatse FAPH (expert-a 2,79) on realistlikum ennustaja kui 0,79 punktväärtus.

---

## 2. Juriidilised ja vastavusriskid

### 2.1 GDPR --- biomeetriliste andmete (häälesalvestused) töötlemine

* **Risk:** Hääl on EL-i isikuandmete kaitse üldmääruse art 9 mõttes biomeetriline eriliik isikuandmeid, kui seda kasutatakse isiku tuvastamiseks. Käesoleva töö audio opt-in kogub lühikesi märgendatud heliklippe, mille seos osaleja identiteediga jääb pseudonüümseks, kuid mitte tingimata anonüümseks. Eraldi nõusoleku osa selle erikategooria kohta peab olema selgesõnaliselt dokumenteeritud, mitte kaudselt tuletatav.
* **Hinnang:** Tõenäosus: Keskmine | Mõju: Kõrge
* **Maandamisstrateegia:** Vormistada kahetasandiline nõusoleku vorm, mille teine tasand viitab konkreetselt art 9 erikategooriale; dokumenteerida säilituse aeg, eesmärk ja kustutamise kord; saata vorm enne andmekogumist TalTechi eetikakomiteele (eetika@taltech.ee); siduda iga osaleja pseudonüüm tagastatavalt vaid ühes krüpteeritud võtmefailis, mis hoitakse audio-andmestikust füüsiliselt eraldi.

### 2.2 Sünteetilise treeningandmestiku litsents ja autoriõigused

* **Risk:** Treeningandmetes kasutatakse XTTS-kloonitud hääli ja Tartu Neurokõne sünteesitud kõnet (lisaks Common~Voice, MUSAN, VOiCES). Kui mõni TTS-allikas litsentseerib oma väljundi mitte-äriliseks kasutuseks ja töö tulemus avalikustatakse koolitatud mudelina avatud litsentsi all, võib tekkida derivatiivteose litsentsivastuolu.
* **Hinnang:** Tõenäosus: Keskmine | Mõju: Keskmine
* **Maandamisstrateegia:** Auditeerida kõik treeningus kasutatud TTS-allikad eraldi \texttt{LICENSE\_AUDIT.md} failis koos viidetega litsentsi punktidele; kui mõni allikas keelab derivatiivteose levitamise, treenida lõplik avalikustatav mudel ilma selleta või paigutada mudel litsentsi alla, mis ühildub kõige rangema sisendiga.

### 2.3 Common~Voice ja avalike korpuste kasutustingimuste järgimine

* **Risk:** \texttt{Common Voice} eestikeelne osa on CC0, kuid taustaheli ja segatud kasutusel \texttt{MUSAN}, \texttt{VOiCES} ja \texttt{Speech Commands} on erinevate litsentside all (CC BY 4.0, CC BY-SA, jt). Töö viitab korpustele tsiteerimise tasandil, kuid juurutatud mudeli levitamine ei kanna alati edasi vajalikku omistuste ahelat.
* **Hinnang:** Tõenäosus: Madal | Mõju: Keskmine
* **Maandamisstrateegia:** Lisada lõplikku mudelipaketti \texttt{NOTICE} fail, kus on selgesõnaliselt loetletud iga korpus, selle litsents ja vajalik omistus; viidata samale failile lõputöö lisas.

### 2.4 Eetikakomitee kinnituse ajastus

* **Risk:** Kasutajatest kogub helilõike ja küsimustikuvastuseid 20--30 osalejalt. Kui eetikakomitee kinnitus saabub pärast esimest sessiooni, kaotavad enne saadud andmed teadusliku väärtuse ja võivad olla GDPR-i mõttes ebaseaduslikult kogutud.
* **Hinnang:** Tõenäosus: Madal | Mõju: Kõrge
* **Maandamisstrateegia:** Külmutada andmekogumise algus selgelt eetikakomitee kinnituse saamise järele; pidada kogu eelnev töö \emph{piloodiks}, mis on selgesõnaliselt eraldatud lõpphindamisest; säilitada e-kirjavahetus eetikakomiteega lõputöö lisas.

---

## 3. Kasutatavuse ja protsessiriskid

### 3.1 Sõltuvus spetsiifilisest riistvarast (ESP32-S3-Korvo-2 + Pi 5)

* **Risk:** Töö lubab \enquote{ühe seadme lokaalse juurutuse}, kuid eeldab nii ESP32-S3-Korvo-2 arendusplaati (mille saadavus ja hind on 2026.~aasta seisuga muutlik) kui ka Raspberry Pi 5 keskust koos Home Assistantiga ja Kiirkirjutaja STT-ga. Lugeja, kes soovib lahendust kodus järele teha, on seotud konkreetse riistvarakombinatsiooniga.
* **Hinnang:** Tõenäosus: Kõrge | Mõju: Madal (lõputöö enda kaitsmise jaoks; juurutuse jaoks Keskmine)
* **Maandamisstrateegia:** Dokumenteerida lõputöö lisas selgesõnaliselt riistvaraline pinge: minimaalne mälunõue (\texttt{tensor\_arena} 45--50~KB, mudel 148~KB), kõik testitud variandid; loetleda mitte-testitud, ent põhimõtteliselt ühilduvad alternatiivid (nt M5Stack Atom Echo) eraldi \enquote{mitte valideeritud} tähistusega, et vältida valeväiteid ülekantavuse kohta.

### 3.2 Kasutajaliidese keerukus tavakasutaja jaoks

* **Risk:** Lahenduse paigaldamine eeldab Home Assistanti, ESPHome'i \texttt{voice\_assistant} liidese, Wyoming protokolli ja Kiirkirjutaja konteineri seadistamist. Iga komponendi vahel on integratsioonipunkt, kus tavakasutaja võib kinni jääda.
* **Hinnang:** Tõenäosus: Kõrge | Mõju: Madal (lõputöö raames)
* **Maandamisstrateegia:** Ehitada \enquote{ühe käsuga} paigaldusskript (\texttt{kratt setup}) ning dokumenteerida lõputöö \texttt{user-guide} kaustas täpne otsast-lõpuni protseduur; lõputöös piirata väiteid \enquote{lihtsa juurutuse} kohta, kuna empiirilist usability-mõõtmist installiprotsessi kohta töö ei sisalda.

### 3.3 Kasutajatesti protokolli tundlikkus uurija eelistustele

* **Risk:** Töö kirjeldab nelja-osalist sessiooni (5 puhast äratust, 5 sarnast negatiivfraasi, 6 skriptitud käsku, 1 vabaülesanne) ning märgib, et UMUX-Lite kaks väidet on valideeritud, ülejäänud uurija koostatud küsimused on \emph{diagnostilised}. Risk on, et uurija küsimuste sõnastus suunab vastust positiivsemaks (kallutatuse oht) ning et viie ütluse kordusarv on liiga väike statistiliselt usaldusväärseks tuvastamismäära hindamiseks ühe osaleja tasandil.
* **Hinnang:** Tõenäosus: Keskmine | Mõju: Keskmine
* **Maandamisstrateegia:** Lisada lõputöös selgesõnaline lahtiütlus, et uurija küsimused ei ole valideeritud ja neid analüüsitakse ainult kvalitatiivselt; arvutada tuvastamismäär osalejate koondvalimi tasandil (Wilsoni vahemikuga), mitte üksiku osaleja täpsusena.

### 3.4 Osalejate värbamise eelarvamuste risk

* **Risk:** Kui 20--30 osalejat värvatakse autori tutvusringist või TalTechi informaatika kogukonnast, kaldub valim olema noor, tehniliselt pädev ning eesti keelt lähedalt sihtmurdele kõnelev. See võimendab töö enda dokumenteeritud \enquote{Kule vs Kuule} hääldusriski ühes suunas.
* **Hinnang:** Tõenäosus: Kõrge | Mõju: Keskmine
* **Maandamisstrateegia:** Dokumenteerida värbamise allikad eraldi tabelina; üritada katta vähemalt kolm vanusvahemikku (alla 25, 25--50, üle 50) ja mõlemad sookategooriad; raporteerida demograafia koondatuna ja esitada tuvastamismäär kihistatud kujul; tunnistada lõputöö piirangutes selgesõnaliselt, et valim ei ole esinduslik.

---

## 4. Eetilised ja sotsiaalsed riskid

### 4.1 Mudeli kallutatus kõnelejategrupi kasuks (\enquote{Kule} vs \enquote{Kuule})

* **Risk:** Töö ise dokumenteerib (vt projekti mälu \emph{Kule vs Kuule training bias}), et 86\% positiivsetest treeningnäidetest ütleb \enquote{Kuule}, samas kui reaalsed kõnelejad kasutavad sageli redutseeritud vormi \enquote{Kule}. See kallutus on süsteemne tuvastamismäära langus konkreetse hääldusrühma vastu --- algoritmi kallutatus, mis võib korduda lapse kõne, dialektikõnelejate ja eakate puhul.
* **Hinnang:** Tõenäosus: Kõrge (juba dokumenteeritud) | Mõju: Kõrge
* **Maandamisstrateegia:** Tasakaalustada positiivne andmestik nii, et \enquote{Kule}-vorm moodustab vähemalt 30--40\%; raporteerida tuvastamismäär eraldi \enquote{Kule}- ja \enquote{Kuule}-rühmadele; lisada lõputöö arutellu eraldi alajaotus algoritmi kallutatuse kohta koos viidetega kirjandusele \cite{park2024adversarial} ning käesoleva töö §\ref{sec:benchmark-gap} tähelepanekutele.

### 4.2 Privaatsuse riive: alati kuulav mikrofon kodus

* **Risk:** Lokaalne juurutus \emph{vähendab}, kuid ei \emph{kaota} privaatsuse riske. Pidev kuulamine tekitab ka olukordi, kus mitte-osaleja (külaline, laps, naaber) räägib mikrofoni läheduses, ilma teadliku nõusolekuta. Kui valeaktiveering pikendab heli sünteetiliselt STT-sse, kaardistub osa sellest kõnest tekstilogisse.
* **Hinnang:** Tõenäosus: Keskmine | Mõju: Keskmine
* **Maandamisstrateegia:** Tagada, et ESPHome konfiguratsioon ei salvesta vaikimisi STT-järgseid transkripte kettale ja Home Assistanti logi tase on seatud nii, et kõnetekst on logist välja lülitatud; dokumenteerida juurutusjuhendis \enquote{külalise režiim} (mikrofoni füüsiline summutamine); lõputöös raporteerida eraldi, milline valeaktiveeringu järelheli pikkus on (\texttt{voice\_assistant} VAD järellõpp).

### 4.3 Kuritarvitamise võimalus: replay-rünnak ja ootamatu aktiveerimine

* **Risk:** Iga avalikult dokumenteeritud äratusfraas on samal ajal ka rünnakuvektor: televiisor, raadio või naabri kõne sama fraasiga aktiveerib seadet. Töö viitab \cite{dubois2020triggers} ja \cite{schoenherr2022accidental} kontekstis sarnasele probleemile kommertskõlaritel.
* **Hinnang:** Tõenäosus: Keskmine | Mõju: Madal
* **Maandamisstrateegia:** Dokumenteerida lõputöös selgesõnaliselt, et äratussõna ei ole turvameede; soovitada juurutuses turvarelevantsete tegevuste (uksed, alarmid) puhul lisakinnitust (PIN-koodi häälkinnitus või füüsiline nupp); lisada arutellu ühe lõigu pikkune lõik kuritarvitamise piiride kohta.

### 4.4 \enquote{Kratt} kui kultuuriliselt laetud nimetus

* **Risk:** Eesti mütoloogias on kratt olend, kes täidab oma peremehe käske; nimevalik kannab konnotatsiooni \enquote{automaatne tööline}. Kui projekt avalikustatakse laiemalt, võib see nimi tekitada arvustusi laiema diskursuse kontekstis (riigi \enquote{Krattide seadus}, e-Eesti retoorika).
* **Hinnang:** Tõenäosus: Madal | Mõju: Madal
* **Maandamisstrateegia:** Lisada sissejuhatusse lühike lõik nime valiku põhjuste kohta, et lugeja tõlgendaks seda foneetilise (mitte poliitilise) valikuna; mainida, et nimevalik on tehniline, mitte ideoloogiline.

### 4.5 Tõendite ülemüümine: \enquote{esimene eestikeelne äratussõna}

* **Risk:** Sissejuhatuse ja kokkuvõtte sõnastus kaldub kohati lähedale väitele, et tegemist on \enquote{esimese eestikeelse äratussõna mudeliga}. Kui mõni varasem akadeemiline projekt, magistritöö või avaldamata kommertslahendus seda fakti ümber lükkab, kannatab töö usaldusväärsus.
* **Hinnang:** Tõenäosus: Keskmine | Mõju: Keskmine
* **Maandamisstrateegia:** Asendada formuleering \enquote{esimene avaliku reprodutseeritava treeningu- ja hindamistoruga eestikeelne äratussõna} või sarnase, kontrollitavalt täpsema sõnastusega; teha sihiotsing nii ETIS-es kui ka rahvusvahelises kirjanduses (vähemalt Google Scholar otsingufraasidega \enquote{Estonian wake word}, \enquote{eestikeelne äratussõna}, \enquote{eesti keele KWS}); dokumenteerida otsingu kuupäev ja tulemused lõputöö lisas.

---

## Kõige kriitilisem risk, millega autor peaks tegelema esimesena

**Risk 2.1 (GDPR ja eetikakomitee kinnitus enne kasutajatesti algust), mis tehniliselt põimub riskiga 1.5 (audiosalvestuste terviklik säilitamine).**

Põhjendus: kõik teised tehnilised riskid (1.1--1.6, 3.x) on parandatavad iteratiivselt --- kui lävi ei kalibreeru, saab seda hiljem täpsustada; kui mudel on kallutatud (4.1), saab andmestikku tasakaalustada uues iteratsioonis. Kasutajatestide andmed seevastu on \emph{ühekordsed}: kui need on kogutud puuduliku või hilinenud nõusoleku alusel, ei saa neid tagantjärele \enquote{seadustada}. Selliseid andmeid ei tohi lõputöös kasutada ja kogu §\ref{sec:user-test-methodology} loodetav neljas valideerimiskiht (vt §\ref{sec:fourth-round}) jääks tühjaks. Lõputöö lubadus kahe nädala kaugusel olevaks tähtajaks (2026-05-18) seda riski võimendab: nõusolekuvormi mustand, eetikakomitee taotlus ja andmesäilituse tehniline toru (krüpteeritud kandja, räsisummad, \texttt{.gitignore} kontroll) peavad olema valmis enne esimese sessiooni algust, mitte selle järel.

Konkreetne tegevussamm järgmisteks päevadeks: vormistada eetikakomitee taotlus koos kahetasandilise nõusolekuga, viia läbi proovi-andmevoog ühe pereliikme või sõbra peal, kes \emph{ei} kuulu lõpphindamise valimisse, ning kontrollida, et kogu rada salvestusest \texttt{trials.jsonl}-isse ja edasi krüpteeritud varukoopiani toimib defektivabalt.
