---
source_prompt: 01_Ideede_genereerimine/Uurimisküsimuste_genereerimine.txt
prompt_type: generative
generated: 2026-05-07
---

# Uurimisküsimuste genereerimine

## Sisendi kokkuvõte

- **Töö tüüp ja tase:** Bakalaureusetöö (TalTech, informaatika), eestikeelne, esitamise tähtaeg 2026-05-18.
- **Töö eesmärk ja taust:** Töötada välja ja hinnata eestikeelne äratussõna ("Kuule Kratt") tuvastamine piiratud ressursiga nutikodu mikrokontrolleril (ESP32-S3) lokaalselt, ilma pilveteenuseta. Praktiline lähtekoht: eestikeelse kõnetuvastuse jaoks on lokaalsed lahendused olemas, kuid eesti keelt ei toeta avatud raamistikud (`openWakeWord` jaotatud mudelid, Picovoice Porcupine), mistõttu äratussõna kiht jääb katmata. Töö rekonstrueeris `microWakeWord` baasil treeningu- ja hindamistoru, validseeris selle avalikul `Speech Commands` korpusel, treenis 15+ eestikeelse mudeli versiooni (v1--v16, sh ekspertmudelite konsensus) ning avastas selle käigus mitmeid hindamismetoodika probleeme (andmeleke, fraasi-prefiksi õppimine, kontrollpunkti valiku lühiteed). Töö konkurentsivõimeline väide ei ole "parim eesti äratussõna mudel", vaid **väikese ressursiga keele kohaliku äratussõna mitmemõõtmelise valideerimise protokoll** (sõltumatu taustaheli FAPH, päriskõneleja tuvastamismäär, sarnaste negatiivnäidete FPR, fraasistruktuuri kontrollivad mõõdikud).
- **Lisamaterjalid:** Sissejuhatus, metoodika peatükk, tulemuste peatükk (sh §\ref{sec:data-leakage}, §\ref{sec:expert-consensus}, §\ref{sec:cross-mic-asymmetry}), arutelu peatükk (sh §\ref{sec:benchmark-gap}, §\ref{sec:eval-evolution}), kokkuvõte, eesti- ja ingliskeelne resümee, ülesandepüstitus.

---

## Märkus küsimuste arvu kohta

Bakalaureusetöö maht ja ühe autori ressurss eeldavad piiratud arvu konkreetseid uurimisküsimusi, mitte doktoritöö-mõõtmes laia küsimustepuud. Allpool on viis põhiküsimust, mis katavad töö dokumenteeritud panuse neli telge (treeningutoru valideerimine, hindamismetoodika, mudeliperekondade kompromiss, kasutusvalideerimine) ning üks meta-tasandi küsimus tööviisi kohta. Iga küsimus on läbinud FINER kontrolli; küsimusi, mis kontrolli ei läbinud, on PICO komponente kitsendades muudetud (vt iteratsiooniloogika allpool, jaotis "Kõrvalejäetud kandidaadid").

---

### 1. Uurimisküsimus

**"Mil määral võimaldab `microWakeWord` raamistikul põhinev treeningu- ja hindamistoru, mille korrektsus on validseeritud avalikul `Speech Commands` `marvin` kontrollkatsel, treenida ESP32-S3 sihtseadmele paigaldatava eestikeelse äratussõna ("Kuule Kratt") mudeli, mis saavutab sõltumatutel kõrvalejäetud komplektidel projekti-spetsiifilise sihi pidevvoo FAPH < 1 ja päriskõnelejate tuvastamismäär >= 0,95?"**

* **PICO analüüs:**
    * **P:** Eestikeelne äratussõna "Kuule Kratt" mikrokontrolleri-klassi seadmel (ESP32-S3, ~22 000 parameetrit, INT8 TFLite).
    * **I:** Rekonstrueeritud ja validseeritud `microWakeWord` treeningutoru, mis sisaldab disjointness-kontrolli, mitmest allikast pärit positiivseid (sh TTS-kloonid) ning sihtkeele- ja sihtseadme-spetsiifilisi negatiivseid näiteid.
    * **C:** Töö enda projekti-spetsiifiline sihtmäär (FAPH < 1; tuvastamismäär >= 0,95) ning suundades võrdluseks suurte ingliskeelsete süsteemide (microWakeWord "okay nabu", openWakeWord "hey jarvis", Picovoice "alexa") avaldatud FAPH-suurusjärk; tegemist ei ole rangelt vastavate korpuste vahelise võrdlusega, vaid suurusjärgu kontekstiga.
    * **O:** Pidevvoo FAPH `faph_cv_et` kõrvalejäetud komplektil (skriptitud taasmäng), tuvastamismäär `pos_speaker_*` kõrvalejäetud komplektidel, mõlemad koos 95% usaldusvahemikega (Wilson, Poisson-Garwood).
* **FINER hinnang:**
    * **Teostatav** --- toru, kõrvalejäetud komplektid, ekspertmudelite konsensus ja avaliku kontrollkatse tulemus on töö tulemuste peatükis juba olemas; küsimus pole spekulatiivne, vaid paneb senised tulemused selgesse hindamisraami.
    * **Huvitav** --- näitab, kas väikese ressursiga keele lokaalne äratussõna on mikrokontrolleril realistlikult saavutatav, mitte pelgalt teoreetiliselt mõeldav.
    * **Uudne** --- autori teadaolevalt esimene avaldatud eestikeelse mikrokontrolleri-suunalise äratussõna projekt; kasutab varem eesti KWS-kontekstis rakendamata jäetud ASR-mahus kõnekorpusi negatiivse materjalina.
    * **Eetiline** --- kasutab avalikke korpusi, autori enda salvestusi ning pseudonüümitud kõnelejate näiteid; sünteetiline kõne (Neurokõne, XTTS) eraldab töö isikutuvastuse riskist treeningfaasis.
    * **Asjakohane** --- vastab otse ülesandepüstituse kesksele eesmärgile ja töö pealkirjas sõnastatud probleemile; tulemus on kasutatav järgmiste eestikeelsete häälassistendi-projektide alusena.

---

### 2. Uurimisküsimus

**"Kuidas mõjutab äratussõna mudeli kvaliteedihinnangut see, kas kasutatakse klipi-tasemel valepositiivsete määra (FPR) versus pidevvoo FAPH-i koos sõltumatute kõrvalejäetud komplektidega, ning millisel määral selgitab esimene mõõdik tegelikku reaalajas käitumist?"**

* **PICO analüüs:**
    * **P:** Käesoleva töö 15+ eestikeelse äratussõnamudeli versioon (v1--v16, ekspertmudelid), mille jaoks on olemas nii varem kasutatud klipi-tasemel hindamiskomplektid kui ka korrigeeritud kõrvalejäetud komplektid (`faph_cv_et`, `pos_speaker_a_xtts`, `hard_neg_mac_holdout` jt).
    * **I:** Kahe hindamisparadigma kõrvuti rakendamine sama mudelite hulga peal: (a) klipi-tasemel FPR/Recall, (b) pidevvoo FAPH koos disjointness-kontrolli ja Poissoni usaldusvahemikega.
    * **C:** Empiiriline lahknevus mõõdikute vahel (nt v6: CV FPR 0,4%, kuid MacBook FAPH ~50; v3: CV FPR 98%, kuid streaming FAPH 542) ning mudelite ümberjärjestumine, kui üle minna ühelt mõõdikult teisele.
    * **O:** Mudelite järjestuste vahelise kooskõla (Spearman / Kendalli tau) hinnang, kvalitatiivne kategoriseering "lühitee-tüüpi" eksimusteks (andmeleke, prefiksi õppimine, kontrollpunkti valiku lühitee), ning operatsionaalne disainireegel järgmistele projektidele.
* **FINER hinnang:**
    * **Teostatav** --- kõik vajalikud mõõtmised on töö raames juba tehtud (vt §\ref{sec:data-leakage}, §\ref{sec:eval-evolution}); küsimus nõuab nende analüütilist sünteesi, mitte uut katset.
    * **Huvitav** --- adresseerib kirjanduses tunnustatud (Dubois et al. 2020, Sensory 2024) lahknevust standardsete benchmarkide ja reaalse kasutuse vahel.
    * **Uudne** --- pakub väikese ressursiga keele kontekstis konkreetseid lühitee-mehhanisme (andmeleke, sildistusprobleem, kontrollpunkti valiku objektiivi probleem), mis pole kirjanduses süsteemselt dokumenteeritud.
    * **Eetiline** --- analüüs, mis ei nõua täiendavat andmekogumist.
    * **Asjakohane** --- otseselt seotud töö enda väljaöeldud peamise panusega ("hindamisprotokoll, mitte üks parim mudel").

---

### 3. Uurimisküsimus

**"Millisel määral võimaldab kahe sihipäraselt projekteeritud ekspertmudeli (üldiste negatiividega väravavaht ja sarnaste negatiividega kontrollija) konjunktsioonipõhine konsensus saavutada eestikeelse "Kuule Kratt" äratussõna jaoks pidevvoo FAPH < 1 sihtkeele kõrvalejäetud korpusel ilma päriskõnelejate tuvastamismäära langetamiseta alla 0,80?"**

* **PICO analüüs:**
    * **P:** ESP32-S3 mahu sisse mahtuvad MixedNet ekspertmudelid (Ekspert A 148 KB, Ekspert B v2 55 KB) konsensusrežiimis.
    * **I:** Konjunktsioon-konsensus mõlema mudeli samaaegse läve ületamise nõudega; eraldi vaadeldakse läve operatsioonipunkte (0,90/0,90 kuni 0,997/0,997) ja Eksperdi B treeningandmete kalibreerimist (100% sarnased negatiivnäited vs 80% sarnased + 20% üldised).
    * **C:** Üksikmudelite parim FAPH ja tuvastamismäär samadel kõrvalejäetud komplektidel; suurusjärguliselt avaldatud ingliskeelsete süsteemide FAPH (microWakeWord 0,16 DiPCo; openWakeWord 0,187 DiPCo; Picovoice ~0,1 LibriSpeech), arvestades, et korpused ja loendusreeglid erinevad.
    * **O:** FAPH `faph_cv_et` kõrvalejäetud komplektil (Poissoni 95% UV), tuvastamismäär `pos_speaker_*` peal (Wilsoni 95% UV), sarnaste negatiivnäidete FPR Mac-mikrofoni komplektil; lisaks ESP32-S3 flash- ja töömälu mahutavus.
* **FINER hinnang:**
    * **Teostatav** --- konsensuse mõõtmistulemused (FAPH 0,8 lävel 0,997/0,997; tuvastamismäär 31--45%) on töös olemas; küsimus eraldab "FAPH-i langetamine" ja "tuvastamismäära säilitamine" kompromissi piirsimulatsiooni võimaluseks.
    * **Huvitav** --- pakub kasvavalt aktuaalse kaskaadarhitektuuride kirjanduse (Apple 2017, Kundu 2023 HEiMDaL) erijuhtumi eestikeelses madalressursi-kontekstis.
    * **Uudne** --- konjunktsiooni-konsensus *funktsionaalselt spetsialiseeritud* ekspertmudelite vahel (üldine vs sarnased negatiivnäited), mis erineb klassikalisest "väike + suur" kaskaadist.
    * **Eetiline** --- kasutab varem kogutud andmeid; uut isikukõnet ei nõua.
    * **Asjakohane** --- adresseerib töö praktilist juurutuskünnist (FAPH < 1 koduses kasutuses) konkreetse arhitektuurivalikuga.

---

### 4. Uurimisküsimus

**"Millisel määral kinnitavad 20--30 osalejaga lühike kasutajatest ja sama heli mitme varimudeli peal taasmängimine fikseeritud läve juures need tuvastamismäära ja sarnaste negatiivnäidete FPR-i hinnangud, mis on saadud kõrvalejäetud TTS- ja Mac-mikrofoni komplektidega?"**

* **PICO analüüs:**
    * **P:** 20--30 reaalset eesti kõnelejat (vanus, sugu, hääldusvariatsioon kontrollitud kvoodiga), kelle iga sessioon sisaldab viit puhast "Kuule Kratt" ütlust, viit foneetiliselt sarnast negatiivfraasi, kuut skriptitud käsku ja ühte vabavormilist ülesannet.
    * **I:** Külmutatud aktiivse mudeliga (`v16c`) salvestatud sessiooniheli taasmäng kõikide varimudelite peal (`v16c`, `expert-a`, `expert-b2`, `v6-residual`, `v10`, `v15`, konsensus `expert-a+expert-b2`) identse läve juures.
    * **C:** Samade mudelite varasemad kõrvalejäetud-komplektidel saadud tuvastamismäära ja sarnaste negatiivnäidete FPR-i punkthinnangud; UMUX-Lite kahe väite subjektiivne hinnang versus tehnilised mõõdikud.
    * **O:** Reaalsete kõnelejate tuvastamismäär (Wilsoni 95% UV), sarnaste negatiivnäidete FPR, valevallandumiste loend per session, kasutaja subjektiivne usaldushinnang. Lahknevuse suurus reaalsete kõnelejate ja TTS-positiivsete vahel.
* **FINER hinnang:**
    * **Teostatav** --- tööriistad (`kratt user-test`, `kratt validate-user-test`, `kratt replay-user-test`, `kratt summarize-user-test`) on olemas; sessioonipikkus ~10 min hoiab värbamise teostatava lävi all; tähtaeg 2026-05-18 lubab sihistatud välivõtu.
    * **Huvitav** --- lubab suure mahuga keelte tööstuslikele süsteemidele iseloomulikku kasutusvaliidsuse mõõtmist väiksema valimi tingimustes ka väikese keele puhul.
    * **Uudne** --- esimene autorile teadaolev eestikeelse äratussõna kasutusvaliidsuse mõõtmine sõltumatu valimiga; ühtlasi otsene "neljas valideerimiskiht" §\ref{sec:fourth-round} tähenduses.
    * **Eetiline** --- kaheastmeline nõusolek (minimaalne tehniline + audio opt-in), pseudonüümitud salvestused, sessioonijärgne küsimustik; vastavus GDPR-le ja TalTech eetikakomitee tavadele.
    * **Asjakohane** --- ainus hindamiskiht, mis suudab eraldada TTS- ja XTTS-positiivsete üle paisutatud tuvastamismäära reaalsete kõnelejate käitumisest (vt Park et al. 2024); määrab juurutusotsuse.

---

### 5. Uurimisküsimus

**"Kuidas piiritleb agentpõhine tarkvaraarendus ühe autori bakalaureusetöö raames teostatava äratussõna projekti tehnilise süsteemi (mõõte- ja tugivahendite kihi) ulatust ning kus paikneb piir, milleni see tööviis tõendusmaterjali (reaalsed kõnelejad, sõltumatud testikomplektid) ei laienda?"**

* **PICO analüüs:**
    * **P:** Üksiku autori läbi viidud bakalaureusetaseme äratussõna projekt (ressurss: kirjutamise ja katsete jaoks ~1 aasta; ühe autori käsitsiarendus klassikaliselt baseline).
    * **I:** Agentpõhine tööviis tarkvaraarenduses (Androidi logija, hindamisskriptid, andmete koondaja, taasmängu tööriistad, dokumentatsioon), mis on rakendatud paralleelsetes seanssides.
    * **C:** Ulatus, mille suudaks samasugune autor saavutada ilma agentpõhise tööviisita, ning komponendid, mille teostust agentpõhine tööviis võimaldab, kuid mille evidentsiaalne väärtus sõltub väljapoolt agendi mõjualast (reaalsete kõnelejate andmestik, eetikakomitee kinnitused, sõltumatud testijad).
    * **O:** Loend tehnilistest komponentidest, mis on agentpõhise tööviisita ebatõenäolised; loend väidetest, mille tugevus ei sõltu sellest, kes või mis koodi kirjutas; metoodikaline soovitus, kuidas eristada teostatavusvõimekust ja tõendusmaterjali kogumise võimekust järgmistes töödes.
* **FINER hinnang:**
    * **Teostatav** --- nõuab analüütilist refleksiooni, mitte uut katset; aluseks juba kirjeldatud arutelu peatüki vastav alapeatükk.
    * **Huvitav** --- adresseerib praeguse hetke (2026) aktuaalset bakalaureusetöö metoodika küsimust, kus agentpõhise tööviisi roll vajab eraldi positsioneerimist.
    * **Uudne** --- esimese isiku reflektsioon, mis seob konkreetse projekti panused (mõõtevahendite kiht) konkreetsete piirangutega (välise valiidsuse probleem); pakub raamistust järgmiste tööde jaoks.
    * **Eetiline** --- mõjutab tööde teadusliku ranguse hindamist; aus piiramine kaitseb agentpõhise tööviisi väärkasutuse vastu.
    * **Asjakohane** --- otse seotud bakalaureusetöö-tasemele esitatavate metoodiliste nõuetega ning töö enda eneseasendiga (tõendusmaterjali pudelikael ei lahene agendi-tööviisiga).

---

## Kõrvalejäetud kandidaadid (FINER iteratsioon)

Allpool on küsimused, mis tekkisid PICO konstrueerimise käigus, kuid mida ei väljastatud lõplikus loendis. Nende kõrvalejätmise põhjus on dokumenteeritud, et lugeja näeks, kuhu joon tõmmati.

1. **"Kas eestikeelne äratussõna saavutab sama FAPH-suurusjärgu kui ingliskeelsed tööstuslikud süsteemid samal kõnekorpusel?"** --- ei läbi **F**: nõuaks kallist kasutusõigust või suurusjärgus rohkem kõneandmeid; ei läbi **R**: tehniliselt ei ole sama korpus ingliskeelsete süsteemide treeningu mõttes võrreldav. Kitsenduse kaudu (suurusjärgu kontekst, mitte väide) integreeritud küsimustesse 1 ja 3.
2. **"Kas mudel käitub usaldusväärselt laste, vanurite ja erinevate murrete kõnelejate peal?"** --- ei läbi **F** bakalaureusetöö ressursi piires (eraldi värbamine, lapsuksonõusolek, eetikakomitee laiendus). Säilitatud küsimuses 4 kasutajatesti tulemuse piiranguna (welcomed limitations), mitte iseseisva küsimusena.
3. **"Kas avaldada Krati mudel ja andmestik avaliku kogukonnamudelina, ning millisel litsentsil?"** --- ei läbi **F** + **E**: nõuab eraldi nõusoleku ja juriidilist analüüsi, mis pole töö ulatuses adekvaatne. Suunatud edasiste tööde rajale.
4. **"Kuidas mõjutab äratussõna sõnavalik (Kuule Kratt vs alternatiivid) tuvastusveerategimist?"** --- ei läbi **N** + **F**: nõuaks alternatiivide treenimist samade ressurssidega, mis töö ulatust ületaks; lisaks on äratussõna valik töös kontseptuaalselt fikseeritud (Eesti mütoloogiline viide, foneetiline eristuvus).
5. **"Millisel määral parandab kolmas ekspertmudel (kõnelejate eristusele spetsialiseerunud) konsensuse tuvastamismäära?"** --- ei läbi **F** lõputöö tähtaja (2026-05-18) piires; säilitatud küsimuses 3 ja arutelu peatükis tulevase tööna (vt §\ref{sec:future-cascade}).

---

## Lõppmärkus

Need viis küsimust on käesoleva töö senise sisu (dokumenteeritud panus, kasutajatesti planeerimine, agentpõhise tööviisi reflektsioon) põhjal sõnastatud nii, et iga küsimus omab juba kogutud või kogumise käigus olevatest andmetest tulenevat vastust. Küsimused ei ole programmi-loomine tulevasele tööle, vaid struktuur senise empiirilise materjali esitamiseks bakalaureusetöö raames. Sihtkriteeriumid (FAPH < 1, tuvastamismäär >= 0,95, alternatiivlävi 0,80) on töö projekti-spetsiifilised otsustuskriteeriumid, mitte kirjanduses kehtestatud universaalsed standardid.
