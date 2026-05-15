---
source_prompt: 07_Teadusartikkel/Kuhu_saata.txt
prompt_type: generative
generated: 2026-05-07
---

# Kuhu saata: ajakirjade soovituste nimekiri

## Sisuline analüüs (lühikokkuvõte)

**Valdkond.** Töö asub kahe valdkonna ristumiskohas: (a) väikeste ja madala ressursiga keelte kõnetehnoloogia ning (b) servaseadmetel käivituv võtmesõna/äratussõna tuvastus (KWS, ingl *keyword spotting* / *wake-word detection*) mikrokontrolleritel (TinyML, on-device ML).

**Uudsuse tase ja peamised panused.**
1. Esimene avalikult dokumenteeritud eestikeelne äratussõna mudel (\enquote{Kuule Kratt}) ja selle reprodutseeritav treeningu- ning hindamistoru ESP32-S3 + ESPHome + Home Assistant integratsiooniga.
2. **Mitmemõõtmeline hindamisprotokoll** väikese ressursiga keele kohaliku äratussõna jaoks: kõrvalejäetud taustaheli FAPH, päriskõnelejate tuvastamismäär, TTS-allikate tuvastamismäär, sarnaste negatiivnäidete FPR ning fraasistruktuuri (prefiks, üksik sõna, pööratud järjekord, kuule/kule segiajamine) testid.
3. Empiiriline juhtumiuuring sellest, kuidas standardsete KWS võrdlusaluste tulemused lahknevad reaalse kasutuskogemusega — andmelekke audit, positiivse klassi sildistuse audit, kontrollpunkti valikukriteeriumi audit (\enquote{kolm valideerimisringi}).
4. Konsensus-/kaskaadarhitektuuri praktiline juhtum (Common~Voice ET hold-out FAPH~$=$~0{,}79 ekspertmudelite konsensusel).
5. Refleksioon agentpõhise tarkvaraarenduse rollist tõendusmaterjali hankimise vs. tööriistastiku ehitamise eristamisel.

**Metoodika.** microWakeWord (TFLite INT8, MixedNet/SVDF arhitektuur, ${\sim}22\,000$ parameetrit, ${\sim}57$--$148$\,KB), avalik kontrollkatse Speech~Commands \texttt{marvin}-iga, voogedastushindamine FAPH-iga (Poissoni-Garwoodi usaldusvahemikud, kolmereegel), Wilsoni vahemikud klipi-tasemel mõõdikutele, kasutajatest 20--30 osalejaga (planeeritav, ülesehitus dokumenteeritud).

**Tugevused.** Tõendusdistsipliin, ausalt fikseeritud piirid (\enquote{võimalik neljas ring}), reprodutseeritavus, väikese keeleruumi kontekstuaalne relevantsus, töövoo (mh agentpõhine arendus) refleksioon. **Nõrkused publitseerimise vaates.** Kasutajatesti tulemused on töö lõpuks veel kogumisel, üksiku äratusfraasi ulatus, statistilise valimi piiratus.

**Ebaõnnestumise riskid:** kui esitada \enquote{esimese eesti äratussõnamudelina}, riskib töö madala teadusliku uudsusega; kui esitada \enquote{universaalse hindamisprotokollina}, vajab tugevamat ülekantavust teistele keeltele. Optimaalne nurk on **väikese ressursiga keele äratussõna mitmemõõtmelise hindamise juhtumiuuring** — see on uudne, ülekantav ja empiiriliselt põhjendatud.

---

## Olulised kaalutlused enne nimekirja

- **Live Search piirang.** Selle ülesande täitmise kontekstis ei olnud Google Search ega ajakohased bibliomeetrilised andmebaasid (Scimago, Clarivate JCR, Scopus) reaalajas kättesaadavad. Allpool olevad numbrilised näitajad (IF, CiteScore, h5, kvartiilid, CORE-järk) on **viimati avalikult teadaolevate väärtuste põhjal** (kuni 2024--2025; uusimaid 2025/2026 väärtusi tuleb autoril enne esitamist Scimago/JCR-st kontrollida). Iga kirje juures on see ka eraldi märgitud (\enquote{kontrollida}). Mitte ükski väärtus pole välja mõeldud, kuid enne esitamist on **autori kohustus** need vahetult valideerida — eriti kvartiil ja kõige värskem IF.
- **Bakalaureusetöö $\rightarrow$ artikkel.** Bakalaureusetööst saab tüüpiliselt kirjutada ühe pikema ajakirjaartikli või ühe konverentsi-pikkuse paberi. Allpool on eelistatud need väljaanded, kus üliõpilastöö-mahuga tulemus on realistlikult vastuvõetav. Tippkonverentsid (ICASSP, INTERSPEECH) on kaasatud, kuid neil on **CORE A/A\*** tase ja vastuvõtumäärad madalad — autori jaoks soovitatav esitada koos juhendaja kaaspublitseerimisega.
- **Röövajakirjad.** Nimekirjast on välja jäetud kõik MDPI-välised tundmatud kirjastajad ja \enquote{rapid publication} ajakirjad ilma usaldusväärse indekseerimiseta. MDPI väljaanded (\textit{Applied Sciences}, \textit{Sensors}, \textit{Electronics}, \textit{Information}) on Scopus/WoS-indekseeritud ja Q1/Q2 tasemel; neid mõnikord kritiseeritakse kõrgete vastuvõtumäärade tõttu, kuid \enquote{röövajakirja} määratlust ei vasta.
- **Sorteerimisreegel.** Sorteeritud sobivuse järgi kahanevalt; võrdsete skooride korral IF kahanevalt.

---

## Nimekiri (sorteeritud sobivuse järgi)

### 1. Computer Speech \& Language

* **Kirjastus:** Elsevier
* **Fookus (Scope):** Arvutuslik kõne- ja keeletehnoloogia: kõnetuvastus, kõnesüntees, võtmesõna tuvastus, madala ressursiga keelte töötlus, hindamismetoodika.
* **Sobivuse hinnang:** 9{,}5/10
* **Miks sobib:** See on üks vähestest ajakirjadest, kus väikese keeleruumi äratussõna tuvastuse metodoloogiline panus mahub fookusesse loomulikult --- nii KWS, madala ressursiga keelte tehnoloogia kui ka hindamisprotokollid on ajakirja regulaarne teema. Lopez-Espejo et~al.\ (\enquote{Deep Spoken Keyword Spotting: An Overview}) ülevaade ilmus selle ajakirja perekonnas; käesoleva töö metoodiline panus on selle ülevaate empiiriline järjekestev arendus.
* **Soovituslik artikli nurk (Spin):** \enquote{A multi-criteria evaluation protocol for low-resource on-device wake-word detection: an Estonian case study}. Rõhuta hindamisprotokolli ülekantavust ja andmelekke/positiivse klassi/kontrollpunkti audi-tide üldistatavust; mudel ja arvud on illustratiivne juhtum, mitte peapanus.
* **Kvaliteedinäitajad (Hinnangulised/Leitud --- kontrollida):**
    * *Kvartiil (Quartile):* Q1 (SJR, Linguistics and Language; Computer Science Applications)
    * *Impact Factor (IF):* ~3{,}1 (2023; kontrollida 2024/2025 JCR)
    * *CiteScore:* ~7--8 (2023; kontrollida)
    * *h5-index:* ~30--35 (kontrollida Google Scholar Metrics)
    * *CORE Ranking:* N/A (ajakiri, mitte konverents)

### 2. Speech Communication

* **Kirjastus:** Elsevier
* **Fookus (Scope):** Kõnetehnoloogia laiemalt: kõnetöötlus, kõnetuvastus, kõnesüntees, akustiline modelleerimine, hindamismetoodika.
* **Sobivuse hinnang:** 9/10
* **Miks sobib:** Klassikaline kõnekogukonna ajakiri, mis avaldab nii metodoloogilisi kui rakenduslikke artikleid. Madala ressursiga keelte ja hindamise teemad on alalises rotatsioonis. Sobib eriti, kui artikli rõhk asetatakse akustilis-foneetilisele analüüsile (kuule/kule segiajamine, prefiksi-tuvastus, koartikulatsiooni mõju streaming-režiimile).
* **Soovituslik artikli nurk (Spin):** \enquote{Phrase-structure-aware evaluation of small-footprint wake-word detection in low-resource Estonian}. Rõhk fonotaktikal ja sellel, miks ühe-mõõdiku FAPH ei piisa, kui sihtfraas on liitsõna/lühike fraas.
* **Kvaliteedinäitajad (Hinnangulised/Leitud --- kontrollida):**
    * *Kvartiil:* Q1--Q2 (SJR, Linguistics and Language)
    * *Impact Factor (IF):* ~2{,}9 (2023; kontrollida)
    * *CiteScore:* ~6--7 (kontrollida)
    * *h5-index:* ~30 (kontrollida)
    * *CORE Ranking:* N/A

### 3. IEEE/ACM Transactions on Audio, Speech, and Language Processing (TASLP)

* **Kirjastus:** IEEE / ACM
* **Fookus (Scope):** Heli, kõne ja keele signaali- ja masinõppemeetodid; KWS, ASR, akustiline modelleerimine, hindamine.
* **Sobivuse hinnang:** 8{,}5/10
* **Miks sobib:** Valdkonna lipulaev. Töö metoodiline panus (mitmemõõtmeline hindamisprotokoll, andmelekke audit, kontrollpunkti valikukriteerium) on TASLP fookuses. Risk: TASLP eelistab tugeva matemaatilise/empiirilise selgrooga töid suurte valimitega; bakalaureusetöö-mahus võib olla vaja täiendada eksperimente teise keele või laiema kõnelejate baasiga.
* **Soovituslik artikli nurk (Spin):** \enquote{Beyond accuracy: a contamination-, label-, and checkpoint-audit framework for small-footprint wake-word evaluation}. Rõhk metodoloogilisel rangusel, statistilisel hindamisel (Wilson, Poisson-Garwood, kolmereegel) ja generaliseeritavusel teistele madalresursilistele keeltele.
* **Kvaliteedinäitajad (Hinnangulised/Leitud --- kontrollida):**
    * *Kvartiil:* Q1 (SJR, Acoustics and Ultrasonics; Computational Linguistics)
    * *Impact Factor (IF):* ~4{,}1--5{,}4 (2023; kontrollida)
    * *CiteScore:* ~10--11 (kontrollida)
    * *h5-index:* ~60+ (kontrollida)
    * *CORE Ranking:* N/A

### 4. INTERSPEECH (konverents, ISCA)

* **Kirjastus:** ISCA (International Speech Communication Association)
* **Fookus (Scope):** Kõnetöötlus laiemalt: ASR, KWS, kõnesüntees, paralingvistika, madala ressursiga keeled, hindamine.
* **Sobivuse hinnang:** 8{,}5/10
* **Miks sobib:** Kõnekogukonna peamine konverents, kus väikese keele äratussõna juhtumiuuring on ootuspärane sobiv esitus. Palju varasemaid madala ressursiga keelte ja KWS-iga seotud paberid. Lehekülgede limiit (4--5 lk) sobib bakalaureusetöö ühe keskse panuse esitamiseks; ülejäänu saab edastada hilisemas ajakirjaversioonis.
* **Soovituslik artikli nurk (Spin):** \enquote{Estonian \enquote{Kuule Kratt}: an open, on-device wake-word with a multi-criteria evaluation protocol}. Rõhk avatud andmestikule/koodile/mudelile, reprodutseeritavusele ja keeleruumi panusele. Konverentsi-versioon võiks olla \enquote{INTERSPEECH 2026/2027} sihiga.
* **Kvaliteedinäitajad (Hinnangulised/Leitud --- kontrollida):**
    * *Kvartiil:* N/A (konverents)
    * *Impact Factor (IF):* N/A
    * *CiteScore:* N/A (konverentsi-toimetiste osas Scopus indekseerib eraldi)
    * *h5-index:* ~80--90 (Google Scholar; kontrollida)
    * *CORE Ranking:* **A** (CORE2023; kontrollida CORE2024)

### 5. ICASSP (IEEE International Conference on Acoustics, Speech and Signal Processing)

* **Kirjastus:** IEEE
* **Fookus (Scope):** Akustika, kõne, signaalitöötlus, masinõpe heli- ja kõneandmete peal; KWS ja TinyML aktiivse treki teemad.
* **Sobivuse hinnang:** 8/10
* **Miks sobib:** ICASSP avaldab regulaarselt KWS- ja servaseadme-paberid (sealhulgas microWakeWord-tüüpi väikeseid arhitektuure). Sobiv, kui rõhk asetatakse mudelitehnikale ja signaalitöötlusele (SpecAugment, kvantiseerimine, voogedastusrežiim). Risk: madala ressursiga keele juhtumiuuring üksinda võib jääda kõrvale; tuleb tugevdada metoodilise panuse osa.
* **Soovituslik artikli nurk (Spin):** \enquote{Streaming-time evaluation gaps in small-footprint wake-word detection: empirical evidence and a multi-criteria fix}. Rõhk on streaming-konteksti vs. klipi-tasemel hindamise lahknevusel ja selle parandamise tehnilisel toel.
* **Kvaliteedinäitajad (Hinnangulised/Leitud --- kontrollida):**
    * *Kvartiil:* N/A (konverents)
    * *Impact Factor (IF):* N/A
    * *CiteScore:* N/A
    * *h5-index:* ~110+ (Google Scholar; kontrollida)
    * *CORE Ranking:* **A** (CORE2023; kontrollida CORE2024)

### 6. Sensors (MDPI), eriväljaanne tinyML / on-device audio AI

* **Kirjastus:** MDPI
* **Fookus (Scope):** Andurid, sealhulgas akustilised andurid; servaseadmete masinõpe (TinyML), reaalajas süsteemid, IoT.
* **Sobivuse hinnang:** 8/10
* **Miks sobib:** Töö praktiline pool (ESP32-S3, INT8 kvantiseerimine, voogedastusrežiim, mälueelarve, ESPHome integratsioon, Home~Assistant pipeline) sobib otse \textit{Sensors}-i tinyML/IoT-akustika rida pidi. Eriväljaande või alamteema kaudu on artikli nurk loomulik. Bakalaureusetöö-mahule sõbralik vastuvõtuprotsess; Q1/Q2 SJR.
* **Soovituslik artikli nurk (Spin):** \enquote{An end-to-end on-device Estonian wake-word voice satellite: hardware budget, INT8 model, and Home~Assistant integration}. Rõhk on süsteemi-disainil, mälueelarvel, latentsil ja praktilisel reprodutseeritavusel.
* **Kvaliteedinäitajad (Hinnangulised/Leitud --- kontrollida):**
    * *Kvartiil:* Q1 (SJR, Instrumentation; Q2 Engineering)
    * *Impact Factor (IF):* ~3{,}4 (2023; kontrollida)
    * *CiteScore:* ~7--8 (kontrollida)
    * *h5-index:* ~110+ (kontrollida)
    * *CORE Ranking:* N/A

### 7. EURASIP Journal on Audio, Speech, and Music Processing (Springer Nature)

* **Kirjastus:** Springer Nature (avatud juurdepääs)
* **Fookus (Scope):** Heli- ja kõne signaalitöötlus, kõnetuvastus, akustiline modelleerimine, hindamine.
* **Sobivuse hinnang:** 8/10
* **Miks sobib:** Avatud juurdepääsuga ajakiri, mis avaldab regulaarselt KWS-i ja madala ressursiga kõnetöötluse paberid. Pikem formaat võimaldab katta nii andmestiku, mudeli, hindamise kui ka süsteemiintegratsiooni. Vähem rangem metodoloogiline lävi kui TASLP, kuid endiselt soliidne Q2 ajakiri.
* **Soovituslik artikli nurk (Spin):** \enquote{Reproducible low-resource wake-word development: data leakage, label discipline, and checkpoint selection in Estonian \enquote{Kuule Kratt}}. Rõhk reprodutseeritavusel, avatud koodil/andmestikul ja audi-tide protseduuril.
* **Kvaliteedinäitajad (Hinnangulised/Leitud --- kontrollida):**
    * *Kvartiil:* Q2 (SJR, Acoustics and Ultrasonics; Computer Science Applications)
    * *Impact Factor (IF):* ~1{,}7--2{,}5 (kontrollida)
    * *CiteScore:* ~4--5 (kontrollida)
    * *h5-index:* ~25 (kontrollida)
    * *CORE Ranking:* N/A

### 8. Applied Sciences (MDPI), eriväljaanne speech/audio või TinyML

* **Kirjastus:** MDPI
* **Fookus (Scope):** Lai rakendusteaduslik ajakiri; sealhulgas akustika, kõne, masinõpe, IoT.
* **Sobivuse hinnang:** 7{,}5/10
* **Miks sobib:** Sobiv, kui Sensors osutub mahukalt suletuks või kui artikkel rõhutab pigem rakenduslikku aspekti --- lokaalne hääljuhtimine privaatsus-fookusega nutikodu, GDPR-sõbralik andmekogumine. \textit{Applied Sciences} on Q1/Q2, indekseeritud, OA. Kõrge vastuvõtumäär nõuab autori poolset selget panuse-positsioneerimist, et artikkel ei mõjuks \enquote{generic-MDPI}.
* **Soovituslik artikli nurk (Spin):** \enquote{Privacy-first local voice control for small-language smart homes: an Estonian wake-word case study}. Rõhk privaatsusel, kohaldumisel teiste väikeste keelte vastu, kasutaja-kogemusel.
* **Kvaliteedinäitajad (Hinnangulised/Leitud --- kontrollida):**
    * *Kvartiil:* Q1--Q2 (SJR, Multidisciplinary Engineering)
    * *Impact Factor (IF):* ~2{,}5--2{,}7 (kontrollida)
    * *CiteScore:* ~5 (kontrollida)
    * *h5-index:* ~75+ (kontrollida)
    * *CORE Ranking:* N/A

### 9. Electronics (MDPI), eriväljaanne edge AI / embedded ML

* **Kirjastus:** MDPI
* **Fookus (Scope):** Elektroonika ja sisseehitatud süsteemid, sealhulgas ML servaseadmetel, mikrokontrollerid, IoT.
* **Sobivuse hinnang:** 7{,}5/10
* **Miks sobib:** Tugev sobivus riistvara/firmware aspekti rõhutavale versioonile: ESP32-S3, MixedNet/SVDF arhitektuur INT8-s, ESPHome stack, Wyoming protokoll, mälueelarve. Kui Sensors on hõivatud, on Electronics teine usaldusväärne MDPI-koridor.
* **Soovituslik artikli nurk (Spin):** \enquote{MixedNet on ESP32-S3: footprint, latency, and integration trade-offs for an Estonian wake-word voice satellite}. Rõhk arhitektuuri valikutel, footprint vs. recall kompromissil ja juurutuse tehnilisel terviklikkusel.
* **Kvaliteedinäitajad (Hinnangulised/Leitud --- kontrollida):**
    * *Kvartiil:* Q2 (SJR, Electrical and Electronic Engineering)
    * *Impact Factor (IF):* ~2{,}6--2{,}9 (kontrollida)
    * *CiteScore:* ~5--6 (kontrollida)
    * *h5-index:* ~50+ (kontrollida)
    * *CORE Ranking:* N/A

### 10. Language Resources and Evaluation (Springer)

* **Kirjastus:** Springer Nature
* **Fookus (Scope):** Keeleressursid, korpused, hindamismetoodika ja keele-spetsiifilised tööriistad; eriti hinnatud madala ressursiga keelte panus.
* **Sobivuse hinnang:** 7{,}5/10
* **Miks sobib:** Töö andmestiku- ja hindamis-protokolli pool sobib otseselt LRE skoopi --- avalik andmestiku- ja hindamis-pakk eesti äratussõna jaoks koos auditiprotokolliga on klassikaline LRE-stiilis panus. Kui rõhk on andmestikul (mitte mudelil) ja keeleressursi avaldamisel, on see õige kodu. Bakalaureusetöö-mahus realistlik vastu võtta.
* **Soovituslik artikli nurk (Spin):** \enquote{KuuleKratt-Eval: an open evaluation pack and audit protocol for Estonian wake-word detection}. Rõhk andmestikul, sildistuse audi-til, hindamiskomplektidel ja keele-spetsiifilistel fonotaktilistel testidel (kuule/kule, prefiks, järjekord).
* **Kvaliteedinäitajad (Hinnangulised/Leitud --- kontrollida):**
    * *Kvartiil:* Q1--Q2 (SJR, Linguistics and Language; Library and Information Sciences)
    * *Impact Factor (IF):* ~2{,}1 (kontrollida)
    * *CiteScore:* ~4--5 (kontrollida)
    * *h5-index:* ~25--30 (kontrollida)
    * *CORE Ranking:* N/A

---

## Märkused autorile (mitte ajakirjade kohta, vaid esitamise kohta)

1. **Bibliomeetria värskendamine.** Enne esitamist kontrolli iga ajakirja kohta vahetult: (a) Scimago SJR praegune kvartiil, (b) JCR uusim IF, (c) Scopus CiteScore, (d) konverentside puhul CORE2024 reiting. Kõik ülaltoodud arvud on **viimati teadaolevate avalike väärtuste põhjal** ja vajavad kinnitust.
2. **Kahetasandiline esitamise strateegia (soovitus).** Lühem konverentsipaber INTERSPEECH 2026 (sobiv tähtaeg, tipptase, lai nähtavus eesti keele osas) + pikem ajakirjaversioon \textit{Computer Speech \& Language} või \textit{Speech Communication} jaoks (sügavam metodoloogiline panus, sealhulgas kasutajatesti tulemused, mis ei mahu konverentsi-paberisse).
3. **Kasutajatesti seis.** Kuna 20--30 osalejaga kasutajatest on töö lõpuks veel kogumisel/varasest analüüsist, võib esimese esitamise sihiks olla \textit{INTERSPEECH 2026 short paper} või \textit{Sensors} mahukam paper, mille ümberparandus sisaldab juba kogu kasutajatesti.
4. **Avatud lähtekood ja andmestik.** Kõikide ülaltoodud sihtide (eriti LRE, EURASIP, Sensors) jaoks tugevdab artikli profiili, kui mudel, treeningu-kood, hindamiskomplektid ja audit-skriptid avaldatakse koos artikliga.
5. **Välja jäetud sihid.** \textit{Nature}-perekonna ja \textit{Science Advances}-tüüpi väljaanded on välja jäetud, kuna töö uudsuse ulatus ei ulatu ühe väikese keele äratussõna juhtumiuuringust kaugemale --- need oleksid range mõttes \enquote{wrong fit}, isegi kui mõõdikud lubaksid. Samuti on välja jäetud paberid mille vastuvõtuteed ei ole läbipaistvad või millel on \enquote{predatory}-maine.

---

## Lühike sobivuse-kokkuvõte (sorteeritud)

| # | Ajakiri/konverents | Sobivus | Kvartiil/CORE | IF / h5 |
|---|---|---|---|---|
| 1 | Computer Speech \& Language | 9{,}5 | Q1 | ~3{,}1 |
| 2 | Speech Communication | 9 | Q1--Q2 | ~2{,}9 |
| 3 | IEEE/ACM TASLP | 8{,}5 | Q1 | ~4--5 |
| 4 | INTERSPEECH | 8{,}5 | CORE A | h5 ~80--90 |
| 5 | ICASSP | 8 | CORE A | h5 ~110+ |
| 6 | Sensors (MDPI) | 8 | Q1 | ~3{,}4 |
| 7 | EURASIP J. Audio, Speech \& Music | 8 | Q2 | ~1{,}7--2{,}5 |
| 8 | Applied Sciences (MDPI) | 7{,}5 | Q1--Q2 | ~2{,}5--2{,}7 |
| 9 | Electronics (MDPI) | 7{,}5 | Q2 | ~2{,}6--2{,}9 |
| 10 | Language Resources and Evaluation | 7{,}5 | Q1--Q2 | ~2{,}1 |

---

*Märkus läbipaistvuse mõttes: ajakirjade nimekiri on koostatud käesolevas keskkonnas ilma reaalaja Google Search'i / Scimago / JCR juurdepääsuta. Bibliomeetria väärtused on viimati avalikult teadaolevate andmete põhjal (~2023--2024) ning enne artikli esitamist tuleb need autoril kinnitada vastavast avalikust andmebaasist. Skoorid 1--10 on autori poolt antav kvalitatiivne sobivuse hinnang töö valdkonna, metoodika ja mahu sobivuse alusel.*
