---
source_prompt: 01_Ideede_genereerimine/Ideede_genereerimine.txt
prompt_type: generation
generated: 2026-05-07
---

# Sissejuhatav märkus

Viip on mõeldud lõputöö teema *valimise* etapiks. Käesolev töö \enquote{Eestikeelse äratussõna mudeli ehitamine ja hindamine ESP32-S3 nutikodu satelliidil} on juba kirjutamise lõppfaasis (kaitsmise tähtaeg 2026-05-18) ja täidetud profiili sisestamine \enquote{tagasiulatuvalt} oleks tehislik. Seetõttu olen viipa rakendanud kahel viisil:

1. **Tagasivalideerimine.** Hindan, kas praegust lõputöö teemat oleks viipa kasutades üldse \enquote{suurepärasele hindele} kandidaadina sõnastatud.
2. **Alternatiivide genereerimine.** Pakun kolm naabruskonnas asuvat (kuid praegusest teemast eristuvat) lõputöö teemat, mida sama autor võiks edasi arendada magistriõppes või järgmise iteratsioonina, lähtudes käesoleva töö avatud küsimustest (§\ref{sec:fourth-round}, §\ref{sec:future-cascade}, §\ref{sec:user-test-methodology}). See annab juhendajale ja võimalikule magistritöö juhendajale konkreetse pildi, kuhu projekt edasi liigub.

Kasutatav profiil (tegelik):

* Õppetase: Bakalaureuseõpe (alternatiivide juures eeldatud Magistriõpe, kus see on metoodiliselt tugevam)
* Ülikool ja teaduskond: Tallinna Tehnikaülikool, Infotehnoloogia teaduskond
* Õppekava: Informaatika
* Õppekava eesmärgid (kokkuvõtlikult, ÕIS-i originaali asemel): rakendusliku tarkvarainseneri ettevalmistus, võime iseseisvalt analüüsida, projekteerida ja realiseerida arvutisüsteeme, kasutada teadusliku uurimistöö meetodeid ja eristada toore tehnilise teostuse oma teaduslikust panusest.
* Huvipakkuv valdkond: kohalikult töötav (\emph{on-device}) eestikeelne kõnetehnoloogia --- spetsiifiliselt äratussõna tuvastus, hindamismetoodika ja nutikodu integratsioon.

---

# 0. Tagasivalideerimine: kas praegune töö ise vastab \enquote{suurepärase} kriteeriumitele?

Praegune töö (vt sissejuhatus, II--III peatükk, kokkuvõte) sõnastab probleemiks: \enquote{kuidas luua ja hinnata eestikeelset äratussõna tuvastust piiratud ressursiga nutikodu mikrokontrolleril}. PICO/FINER raamistikus:

* **P** (Population/sihtkontekst): eestikeelne kasutaja nutikodu satelliidi ees, ESP32-S3 klassi seade.
* **I** (Intervention): \texttt{microWakeWord} põhine treening- ja hindamistoru fraasile \enquote{Kuule Kratt}, koos sõltumatu \emph{hold-out} hindamisega ja FAPH-keskse voogedastusprotokolliga.
* **C** (Comparison): \texttt{openWakeWord} (sama äratusfraas, suurem hostsiht), klipi-tasemeline FPR vs.\ voogedastus-FAPH, üksikmudel vs.\ ekspertkonsensus.
* **O** (Outcome): pidevvoo FAPH~$<$~1 Common~Voice~ET hold-out korpusel ja lähikõne tuvastamismäär~$\geq$~0{,}95; tegelikkuses saavutatud konsensusel FAPH~$=$~0{,}79, kuid \enquote{Kule}-hääldusel jäi tuvastamismäär madalamaks (vt sissejuhatus, kokkuvõte).

FINER:

* **Feasible**: jah, tõestatud --- toru on otsast lõpuni reprodutseeritav, mudel jookseb ESP32-S3 peal.
* **Interesting**: jah, sest avab esimese eesti äratussõna avaliku tõendusbaasi ja paljastab benchmark-realsuse lõhe (§\ref{sec:benchmark-gap}).
* **Novel**: piiratult --- mitme-mõõdikuline hindamine pole tööstuses uudne (§\ref{sec:contribution-transferability}), kuid \emph{eesti keelele kohandatud lokaalse äratussõna tõendusprotokoll} on. Töö ise sõnastab uudsuse mõõduka kandena (\enquote{esimene eesti äratussõna mudel} on tõsi, kuid \enquote{tehniline maht on tagasihoidlik tööstuslike süsteemidega võrreldes}).
* **Ethical}: jah, GDPR/opt-in raamistik kasutajatestiks (§\ref{sec:user-test-methodology}).
* **Relevant**: jah, väikese keele lokaalse hääljuhtimise kasutatavusele.

**Vahekokkuvõte:** praegune teema vastab kriteeriumitele, kuid uudsus toetub eelkõige metoodikale ja tõendusdistsipliinile, mitte mudeliarhitektuurilisele läbimurdele. Ohukoht juhendaja seisukohast: kui retsensent loeb \enquote{esimene eesti äratussõna mudel}-väidet üksinda, ilma metoodilise panuse argumendita, võib uudsus tunduda tagasihoidlik. Töö praegune sõnastus (II ja III ptk) seda riski adresseerib eksplitsiitselt --- see on tugevus, mida kaitsmisel rõhutada.

---

# 1. Alternatiiv: \enquote{Kahetasandiline kaskaadarhitektuur eesti äratussõna tuvastuseks: \enquote{kuule}/\enquote{kratt} eraldatud teine aste lokaalsel hostil}

## 1.1 Probleemipüstitus ja uudsus
Käesoleva bakalaureusetöö §\ref{sec:future-cascade} sõnastab konkreetse järgmise sammu: kaskaad, kus mikrokontrolleri esimene aste annab kandidaadi ja Pi-klassi teine aste kontrollib eraldi \enquote{kuule} ja \enquote{kratt} sõnade kohalolu ning järjekorda. Tööstuses on kaskaad levinud (Apple, Google), kuid avatud lähtekoodiga, eestikeelse, kahe sõna struktuurset järjekorda kontrolliva teise astme avalikku realisatsiooni ei eksisteeri. Uudsus on \emph{struktuurtundlik teine aste väikese keele jaoks}, mitte kaskaad ise.

## 1.2 Uurimisküsimused (PICO + FINER)
1. *Kas struktuurtundlik teine aste vähendab Krati \enquote{kuule}/\enquote{kule}-prefiksist tingitud valeaktiveerimisi ilma päris tuvastamismäära kaotamata?*
   * P: Krati esimese astme kandidaadid; I: kahe-sõna järjekorda kontrolliv teine aste (CTC- või forced-alignment-põhine); C: ühetaseme \texttt{v16c} ja ekspertkonsensus; O: FAPH \emph{ja} reaalsete kõnelejate tuvastamismäär kasutajatesti taasmängul.
2. Kuidas mõjutab teise astme arvutuskulu ja latents lokaalse Pi 5 satelliidi otsast-lõpuni viivitust?
   * P/C/O täidetud Wyoming-protokolli mõõtmistega.
3. Kas teine aste taastab \enquote{Kule}-hääldajate tuvastamismäära, mis bakalaureusetöös jäi juurutuslävel <0{,}95?
4. Kas süsteem üldistub teisele kahesõnalisele eesti äratusfraasile (nt \enquote{Tere Kratt}) ilma uue treeningandmestiku kogumiseta esimesele astmele?

FINER: feasible (esimese astme baseline on käesolevast tööst olemas), interesting (lahendab dokumenteeritud kitsaskoha), novel (struktuur + väike keel), ethical (sama opt-in raamistik), relevant (otsene kasutajakogemuse mõju).

## 1.3 Metoodika ja tegevuskava
1. **Esimese astme freezimine**: võtta käesoleva töö \texttt{v16c} ja ekspertkonsensus baseline'iks; külmutada nende lävi ja kandidaatlogi.
2. **Teise astme arhitektuur**: kohandada väike CTC-baseline (nt Wav2Vec2-XLSR-53 destilleeritud variant või Whisper-tiny eestikeelsele kõnele peenhäälestatud) töötama 1{,}5--2~s lõikudega Pi 5-l.
3. **Treening- ja kalibreerimisandmed**: kasutada käesoleva töö positiivseid klippe \emph{ainult} kalibreerimiseks; lisaks Common~Voice~ET ja partial-keyword/swapped-order negatiivid (vt \cite{shrivastava2021optimize}).
4. **Hindamine**: rakendada käesolevas töös defineeritud mitme-mõõdikulist protokolli (§\ref{sec:eval-evolution}) lõpp-süsteemile, *sealhulgas} \enquote{kuule}/\enquote{kule}/\enquote{kratt} eraldatud testid.
5. **Valideerimine kasutajatestiga (kriitiline samm):** korrata käesoleva töö 20--30 osalejaga sessiooniprotokolli (§\ref{sec:user-test-methodology}) külmutatud kahe-astmelise süsteemiga; raporteerida tuvastamismäär, FAPH ja end-to-end latents 95\% Wilsoni/Poissoni vahemikuga; võrrelda paari kaupa sama osaleja samade WAV-failidega ühe-astmelise baseline'iga (paired McNemar/exact-binomial test).
6. **Riistvara stress-test**: 24~h pidev töö Pi 5-l, soojuse ja CPU koormuse logimine, võrdlus üheastmelise süsteemiga.

---

# 2. Alternatiiv: \enquote{Avatud stsenaariumipõhine taustaheli korpus eesti nutikodu äratussõna hindamiseks}

## 2.1 Probleemipüstitus ja uudsus
§\ref{sec:benchmark-gap} dokumenteerib süstemaatilise lahknevuse standardsete KWS võrdlusaluste (Common~Voice tihe kõne, MUSAN müra) ja päris koduakustika vahel. Töö pakub välja \enquote{stsenaariumipõhise testimisvoo}, kuid \emph{ei avalda} sellist korpust. Magistritöö tasandi panus oleks: kureeritud, märgendatud, BY-CC-litsentsitud eesti kodu-akustika korpus (pikk vaikus, TV/raadio-eesti, taustamuusika, lapse hääl, köök, äratusfraasi-laadsed lausekonteksti negatiivid) koos hindamis-API-ga, mis annab võrreldavaid FAPH/recall/FPR-i 95\%~CI-ga. See on otsene panus eesti keeletehnoloogia ühisvarasse ja ülekantav teistele väikestele keeltele.

## 2.2 Uurimisküsimused (PICO + FINER)
1. Kas stsenaariumipõhine korpus eristab Krati v6, v16c ja ekspertkonsensuse mudeleid \emph{teisiti} kui Common~Voice~ET (P: samad mudelid, I: uus korpus, C: CV~ET, O: FAPH ja recall ranking-Spearman korrelatsioon)?
2. Milline on minimaalne salvestuse maht (tundides), et Poissoni 95\% CI FAPH~$<$~1 sihtmäära jaoks oleks võimalik kinnitada (vt \cite{hanley1983ruleofthree})?
3. Kuidas peegeldub TV/raadio-eesti foneetiline tihedus FAPH-i ülemääras, võrreldes ainult-vaikuse rajaga?
4. Kas korpus üldistub: kas teisel eesti äratusfraasil (nt \enquote{Tere Kratt}) säilib relatiivne mudelite paremusjärjestus?

FINER: feasible magistritasandil; novel (avalikku eesti äratussõna-spetsiifilist taustakorpust ei eksisteeri); ethical (eraldi peatükk salvestuste nõusoleku, isikutuvastuse ja TV-sisu copyright fair-use kohta --- konsulteerida TalTech eetikakomisjoni ja \texttt{eetika@taltech.ee}-ga juba enne kogumist); relevant (eesti keeletehnoloogia üldine ühishüvis).

## 2.3 Metoodika ja tegevuskava
1. **Korpuse kava ja eelregistreerimine**: stratifitseeritud kava (vaikus, TV-eesti, raadio-eesti, kodu-mittekõnelised helid, lausekonteksti äratussõna-laadsed negatiivid, mitme-kõnelejaga vestlus); registreerida OSF-is enne kogumist.
2. **Eetika ja litsents**: nõusolekuvormid, salvestuste anonümiseerimine (v.a TV/raadio osa), litsents CC-BY 4.0; arutelu \texttt{ETIS}-e ja Eesti Keeleressursside Keskusega (Sõnaveeb/EKI).
3. **Salvestus ja märgendus**: vähemalt 50~h, kahe seadmega (lähimikrofon ja ESP32-S3 \texttt{Korvo-2}), äratussõna esinemiste kuldstandard manuaalselt ajatempliga.
4. **Hindamis-API**: \texttt{kratt eval-corpus} CLI, mis võtab voo TFLite/ONNX mudeli, väljastab tabeli FAPH/recall/FPR Wilsoni+Poissoni CI-ga, koos automaatse \emph{leakage check} sammuga.
5. **Tulemuste valideerimine (kriitiline samm):** võrrelda korpust \emph{kasutajatesti taasmängu} kuldstandardiga (käesoleva töö §\ref{sec:user-test-methodology} salvestused) --- kas korpuse ennustatav mudelite järjestus korreleerub kasutajatesti tulemustega? Spearman~$\rho \geq 0{,}7$ tähistab korpuse välist valiidsust. Lisaks kontrollkatse: avaldatud korpus läbib reprodutseeritavuse-piloodi sõltumatu meeskonna (nt teine TalTech magistrant) käes.
6. **Avalikustamine ja juurdumine**: Zenodo DOI, dokumenteeritud schema, kaks sissejuhatavat näidist (Krati v16c ja avatud Porcupine-laadne baseline, et tagada võrreldavus üle raamistike).

---

# 3. Alternatiiv: \enquote{Õpilase-keskendunud andmekorraldus eestikeelse äratussõna jaoks: aktiivõppe ja madala-ressursi adapteerimise võrdlus}

## 3.1 Probleemipüstitus ja uudsus
Käesoleva töö §\ref{sec:user-test-methodology} ja kokkuvõte tunnistavad, et järgmine peamine risk pole enam toru, vaid \emph{andmestiku kvaliteet ja kõnelejate mitmekesisus} --- eriti \enquote{Kule}-hääldajate puhul. Magistritöö tasandi küsimus: kuidas valida 200~lauset 200~kõneleja ringist (või 1000~klippi 50~kõneleja ringist) nii, et äratussõna mudel paraneks maksimaalselt --- aktiivõpe vs.\ klastritud-juhuvalim vs.\ kõnelejate-balansseeritud kvoot? See on PICO-puhas eksperiment ja annab andmekogumise eelarve-soovituse, mida käesolev bakalaureusetöö ei suuda anda.

## 3.2 Uurimisküsimused (PICO + FINER)
1. *Kas aktiivõppe valikustrateegia (nt mudeli ebakindlus + foneetiline mitmekesisus) annab N=500 klipi pealt kõrgema reaalse kõneleja tuvastamismäära kui sama-suurune juhuvalim?*
   * P: 50--100 eesti kõnelejat (sh \enquote{Kule}-hääldajad); I: ebakindluse + DPP-põhine valik; C: juhuvalim; O: tuvastamismäär hold-out kõnelejate peal.
2. Kas eestikeelse mudeli sünteetilise (XTTS, Neurokõne) kõne osakaal on positiivse marginaalse panusega ainult kuni teatud kvoodini, mille ületamine põhjustab käesoleva töö §\ref{sec:benchmark-gap} kirjeldatud TTS-bias'i?
3. Kas adapteerimine (LoRA-laadne pea-peenhäälestus) Picovoice/openWakeWord ingliskeelsest baasmudelist annab parema tulemuse kui treening nullist sama eelarve juures?
4. Milline on minimaalne kõnelejate arv, et tuvastamismäära CI ei lõikuks lävega 0{,}95 (statistilise võimsuse arvutus enne andmekogumist)?

FINER: feasible (200 kõnelejat saavutatav vabatahtlike võrgustikuga ja Tartu Ülikooli koostöös); novel (väikese keele aktiivõppe äratussõna kontekstis pole avalikku võrdlust); ethical (selge GDPR-i raam, opt-in audio); relevant (igale järgmisele eesti äratussõna projektile: kuidas planeerida andmekogumise eelarvet).

## 3.3 Metoodika ja tegevuskava
1. **Statistiline võimsusarvutus** ja eelregistreerimine OSF-is: oodatav efektisuurus, hold-out kõnelejate arv, esmane lõppmõõdik (recall hold-out kõneleja peal).
2. **Andmekogumise infrastruktuur**: laiendada käesoleva töö \texttt{kratt user-test} tööriista veebiversiooniga (PWA), Wilson-skoorimeetodi näitamine reaalajas, audit-logide märgendus.
3. **Kolm haru paralleelselt**:
   (a) juhuvalim (kontroll),
   (b) aktiivõpe (epohhide vahel ümberhinnatud klipid),
   (c) foneetiliselt balansseeritud kvoot (\enquote{Kule} vs \enquote{Kuule}, ealised rühmad, murderühmad).
4. **Sõltumatu hindamine**: hold-out kõnelejad, käesoleva töö stsenaariumipõhine korpus + kasutajatesti taasmäng.
5. **Tulemuste valideerimine (kriitiline samm):** kolme haru paari-kaupa võrdlemine McNemar-testi ja \emph{paired bootstrap}-iga, raporteerida 95\%~CI; *eelregistreeritud} hüpotees, et aktiivõpe ületab juhuvalimit recall'is vähemalt 5~pp; lisaks kvalitatiivne väike-N intervjuu \enquote{Kule}-hääldajatega selle kohta, miks juurutuslävi nende peal kukub.
6. **Reprodutseeritavus**: avaldatakse mudelid, valikulogid ja anonümiseeritud klippid (opt-in alusel) Zenodos.

---

# Kokkuvõtlikult juhendajale

* **Praegune bakalaureusetöö** vastab kriteeriumitele (FINER), uudsus toetub metoodikale --- mida tuleks kaitsmisel selgelt rõhutada.
* **Alternatiiv 1** (kaskaad) on kõige loomulikum jätk magistritööks ja kasutab käesoleva töö esimese astme baseline'i otsekohe ära.
* **Alternatiiv 2** (avatud taustakorpus) annab kõige suurema välismõjuga panuse eesti keeletehnoloogia kogukonnale, kuid nõuab eetikakomisjoni varast kaasamist.
* **Alternatiiv 3** (andmekorraldus) on PICO-puhtaim eksperiment, kõige kindlamini publitseeritav (CHI/Interspeech), kuid kõige logistikamahukam (kõnelejate värbamine).
