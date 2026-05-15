---
source_prompt: 04_Kontrollimine/Konkreetsed_vead/Sisu/Kontrolli_lahendust.txt
prompt_type: evaluative
generated: 2026-05-07
---

# Tehnilise lahenduse audit (\enquote{kriitilise sõbra} vaade)

Käesolev audit hindab töös \enquote{Kratt: eestikeelne äratussõna mikrokontrolleril} kirjeldatud tehnilist lahendust kuue aspekti lõikes. Aluseks on sissejuhatus, ülesandepüstitus, metoodika (1.~peatükk), arutelu (3.~peatükk), kokkuvõte ja eesti- ning ingliskeelsed annotatsioonid. Tulemuste peatükki ei saanud tervikuna lugeda mahupiirangu tõttu; seetõttu on aspektid 3--6 hinnatud nende viidete ja metoodikakirjelduste põhjal, mis 3.~peatükis ja sissejuhatuses tulemuste peatükile osutavad.

---

## 1. Teostatavus ja mõistlikkus (Feasibility \& Sanity Check)

* **Hinne:** 8/10
* **Analüüs:**
    Pakutud arhitektuur --- \texttt{microWakeWord} (TFLite~INT8) MixedNet ESP32-S3 peal, ESPHome \texttt{voice\_assistant} liidese kaudu Home Assistanti --- on antud probleemile (lokaalne eestikeelne äratussõna nutikodu satelliidil) hästi kalibreeritud. Mudeli maht (${\sim}57$\,KB põhiseeria, 148\,KB \texttt{v16c}) ja tensor-arena (${\sim}45$--$50$\,KB; kokku $<200$\,KB) mahuvad ESP32-S3 piirangutesse. Kahe raamistiku (\texttt{microWakeWord} + \texttt{openWakeWord}) hoidmine annab võrdlusvõimaluse ilma teist sihtplatvormi kohustuslikuks tegemata --- see on mõõdukas, mitte ülekonstrueeritud lahendus.

    Üksiku autori ja 2026-05-18 deadline'i kontekstis on aga **scope-risk** reaalne. Töö toob lisaks põhitorule sisse: (a) Androidi valevallandumiste logija, (b) skriptitud taasmängu hindamistoru, (c) konsensusmudelid, (d) ekspert A/B2 jaotuse, (e) v6-residual ablatsiooni, (f) v13a/v13b SpecAugment ablatsiooni, (g) kaskaadarhitektuuri kavandi, (h) 20--30~osalejaga kasutajatesti koos eraldi CLI-tööriistadega (\texttt{kratt user-test}, \texttt{validate}, \texttt{replay}, \texttt{summarize}). See on bakalaureuse mahule lähemal magistritööle. Töö ise tunnistab seda implitsiitselt agentpõhise arenduse osas, mis on aus, kuid ei vabasta riskist, et kasutajatest --- mille puudumist 3.~peatükk ise nimetab \enquote{neljandaks ringiks} --- jääb deadline'i tõttu poolikuks.

    Mõistlik on disainivalik mitte ehitada täielikku STT/TTS toru, vaid kasutada Kiirkirjutajat ja olemasolevat HA-pinu. \enquote{Kuule Kratt} fraasi valik on foneetiliselt põhjendatud (lühike plahvatus /k/ + pikem vokaaltrajektoor), mis sobib MixedNeti mitmeskaalalisele tuumade jaotusele $[5,9,13,21]$.

* **Soovitused parandamiseks:**
    * Sõnastage 3.~peatüki \enquote{neljanda ringi} osas selgemalt, milline kasutajatesti **minimaalne maht** veel mahub deadline'i (nt $n=10$ piloodi tulemused) ja milline laiendus kuulub edasiste tööde alla. Praegu jääb lugejale mulje, et 20--30~osalejat on \enquote{järgmine kriitiline samm}, mis 11~päeva jooksul ei pruugi olla mõõdetav.
    * Lisage sissejuhatusse või peatükki üks lause, mis ütleb, et \texttt{v16c} pole tootmisotsus, vaid stabiilne baasjoon piloodiks --- see on kokkuvõttes olemas, aga sissejuhatuses puudub ja võib lugejat eksitada.

---

## 2. Põhjendatus ja alternatiivide analüüs (Justification)

* **Hinne:** 8/10
* **Analüüs:**
    Põhjendatus on töö üks tugevamaid külgi. Iga oluline tehniline valik on seotud konkreetse alternatiiviga ja selle kõrvalejätmise põhjusega:

    * **Raamistik:** \texttt{microWakeWord} vs.\ \texttt{openWakeWord} võrreldakse neljal teljel (treenimiskeerukus, mudeli kvaliteet, integreeritavus, eesti keele laiendatavus); Picovoice Porcupine on **teadlikult välja jäetud** suletud lähtekoodi ja eesti keele toe puudumise tõttu. See on metoodiliselt korrektne ja erineb tavalisest \enquote{kasutame X-i, sest X on populaarne} põhjendusest.
    * **Arhitektuur:** MixedNet on põhjendatud SVDF-tausta kaudu (\cite{alvarez2019svdf,chen2014smallfootprint,sainath2015cnn}), residuaalühendused BC-ResNeti tulemusega \cite{choi2021bcresnet}.
    * **Mõõdik:** FAPH valik klipi-tasemelise FPR ees on detailselt põhjendatud (\cite{lopezespejo2021deepkws}, openWakeWord ja Picovoice praktika), sealhulgas selgitus, miks $<\!1$~FAPH on \emph{projekti-spetsiifiline} siht, mitte universaalne standard.
    * **Usaldusvahemikud:** Wilson klipi-mõõdikutele \cite{wilson1927probable,brown2001interval}, Garwood/Poisson FAPH-ile \cite{garwood1936fiducial,ulm1990poisson}, kolme reegel nullsündmustele \cite{hanley1983ruleofthree} --- see on bakalaureuse kohta erakordselt põhjalik statistiline põhjendus.

    **Nõrk koht:** kasutajatesti küsimustiku valikuline UMUX-Lite \cite{lewis2013umuxlite,sauro2009seq} on mainitud, kuid \enquote{uurija koostatud küsimusi} ei ole põhjendatud alternatiivide (NPS, SUS-Lite) vastu. Subjektiivse rahulolu mõõtmise alternatiivid jäävad lahti.

    **Teine nõrk koht:** kontekstiakna 1500~ms valik on põhjendatud fraasi loomuliku kestusega, kuid 2000~ms-i ainult mainitakse, mitte ei testita ablatsiooniga. Kuna prefiksi-õppimise probleem ($\enquote{kuule}$/$\enquote{kule}$ üksinda käivitab) on töö üks dokumenteeritud probleeme, võiks pikem aken olla otsene mehhaniline mitigatsioon ja vääriks vähemalt kvalitatiivset arutelu.

* **Soovitused parandamiseks:**
    * Lisage §\,\ref{sec:user-test-methodology} alla üks lause, miks UMUX-Lite ei kata kõiki vajalikke konstrukte ja miks oli vaja täiendavaid uurija koostatud väiteid.
    * Lisage §\,\ref{subsec:clip-duration} lõppu üks lõik selle kohta, miks 1500~ms ablatsioon ei toimunud (ressursid, deadline) või kui see toimus, siis tulemus.

---

## 3. Tegelik teostus (Implementation)

* **Hinne:** 7/10 (osaliselt N/A)
* **Analüüs:**
    Hindamine on kallutatud, sest tulemuste peatükki (4.~peatükk, kus paiknevad tabelid \texttt{tab:fair-comparison-holdout}, \texttt{tab:expert-consensus}, \texttt{tab:checkpoint-headline}) ei saanud mahu tõttu lugeda. Allpool olev hinne tugineb 3.~peatüki refereeringutele ja sissejuhatuse arvudele.

    **Mis kirjeldatu põhjal töötab:**
    * Treening- ja hindamistoru on avaliku \texttt{marvin}/\texttt{Speech Commands} kontrollkatsega valideeritud (\cite{speechcommands2018}).
    * Andmeleke on tuvastatud ja parandatud --- esimene ring (kohalik FPR 0,4\,\% vs.\ MacBook FAPH ${\sim}50$) on aus dokumenteerimine, mis tugevdab töö tõendusväärtust, mitte ei nõrgenda seda.
    * Konsensus (expert-a + expert-b2) annab Common~Voice~ET kõrvalejäetud komplektil $0{,}79$~FAPH; v6-residual andis $0{,}58$~FAPH 98{,}97~h Android-välikatses.
    * \texttt{kratt} CLI-perekond (user-test, validate, replay, summarize) on kohalik tööriist, mis muudab kasutajatesti reprodutseeritavaks ja eraldab heli treening- ning hindamiskasutuse vahel.

    **Arhitektuursed kitsaskohad / lahtised teemad:**
    * Töö dokumenteerib \emph{benchmark vs.\ reaalsuse lõhe} (§\,\ref{sec:benchmark-gap}) ausalt, kuid ei lahenda seda --- 2-tunnine annoteeritud stsenaarium-salvestus on **kavand**, mitte teostus. Praegu on lugejale jäetud mulje, et metoodika on kõik, mida saab dokumenteerida, kuid uus mõõdikukomplekt pole veel reaalse keskkonna pikema saliseeria peal käivitatud.
    * \texttt{v16c} pole ESPHome + Korvo-2 peal lõpuni valideeritud (\enquote{lõplik compile/flash kontroll tehakse kasutajatesti aktiivse konfiguratsiooni peal}). Seega on seadme-sobivus tõendatud peamiselt mahuarvestusena, mitte täielikult lokaalse järeldamise mõõtmisega.
    * Neljas \enquote{FAPH-i variant} (kasutajatesti taasmäng) on **planeeritav**, mitte teostatud; sissejuhatuse kõige tugevam väide ($0{,}79$~FAPH) tugineb seega ühele variandile (Common~Voice~ET kõrvalejäetud).
    * \enquote{Üksikute juhtumite täheldamine} klaviatuuriklõpsudel/ninakahinal/muusikal on aus tunnistus, et **mittekõneliste helide aktivatsioonimäära ei ole süstemaatiliselt mõõdetud**. See jätab ühe stsenaariumi (köök, mehaanilised helid) tõenduspõhjata.

* **Soovitused parandamiseks:**
    * Lisage tulemuste peatükki üks lõik, mis selgesõnaliselt loetleb, mis on \emph{teostatud} (Speech Commands sanity, CV~ET hold-out FAPH, Android välikatse, ablatsioonid v6-residual ja v13a/v13b) vs.\ mis on \emph{kavandatud} (2~h annoteeritud stsenaarium, kasutajatesti taasmäng, kaskaadarhitektuur, mittekõnelised helid). Ilma selle eraldusena võib hindaja arvata, et stsenaariumipõhine voog on juba töötav.
    * Käivitage enne kaitsmist vähemalt üks **lõpust-lõpuni Korvo-2 + ESPHome compile/flash kontroll} ja raporteerige selle järeldamise latentsus + RAM-kasutus. See sulgeks teostuse seadme-spetsiifilise lünga.

---

## 4. Vastavus valdkonna standarditele (Standards Compliance)

* **Hinne:** 9/10
* **Analüüs:**
    Töö järgib valdkonna ja akadeemilisi standardeid distsiplineeritult.

    * **Protokolli-standardid:** Wyoming protokolli kasutamine HA-integratsioonis, ESPHome \texttt{voice\_assistant} liides, Home Assistanti avatud lähtekoodiga ökosüsteem. Need on koostalitluse jaoks õiged valikud.
    * **Andmeprotseduurid:** treeningandmete disjointsuskontroll, sõltumatud kõrvalejäetud komplektid --- vastab ML-i parimatele tavadele \cite{cawley2010overfitting}.
    * **Statistika:** Wilsoni \cite{wilson1927probable} ja Poisson-Garwood \cite{garwood1936fiducial} usaldusvahemikud on standardid binoom- ja loendusmõõdikutele; nende kasutamine on bakalaureuse jaoks ületäpne ja näitab metoodilist hoolt.
    * **FAPH-variantide selgesõnaline loendusreegel} (§\,\ref{subsec:faph-variants}) lahendab kirjanduses tuntud reprodutseeritavuse augu \cite{lopezespejo2021deepkws} --- iga tabel ja joonis identifitseerib kasutatud variandi. See on parem kui paljud retsenseeritud KWS-tööd.
    * **Privaatsus / GDPR:** kahetasandiline nõusolekumudel (minimaalne + audio opt-in) on kooskõlas väikese akadeemilise uuringu standardiga.

    **Lünga koht:** ametlikku **eelregistreerimist} (preregistration, OSF) kasutajatesti analüüsi-plaani jaoks ei ole mainitud. Kuna töö rõhutab läbivalt \enquote{lävi valitakse ainult valideerimisandmestikul} ja \enquote{külmutatud lävi}, oleks kasutajatesti-skoorimine loogiliselt selle vajalik järg.

* **Soovitused parandamiseks:**
    * Mainige §\,\ref{sec:user-test-methodology} all, kas analüüsi-plaan (mõõdikud, läved, läve külmutamise hetk) on **enne andmekogumist} kirjalikult fikseeritud. Kui jah, viidake sellele dokumendile (nt \texttt{notes/} või OSF). Kui ei, lisage üks lause, miks formaalset eelregistreerimist ei tehtud.
    * Kontrollige, et kõikides FAPH-tabelite pealkirjades on FAPH-variant tõepoolest nimetatud, nagu §\,\ref{subsec:faph-variants} lubab.

---

## 5. Vastavus parimatele praktikatele (Best Practices)

* **Hinne:** 9/10
* **Analüüs:**
    Töö rakendab mitut parimat praktikat seal, kus paljud bakalaureusetööd ei tee:

    * **Avalik kontrollkatse enne sihtkeele juurde minekut** (\texttt{marvin}) --- klassikaline \enquote{toru-valideerimise} muster ja töö metoodiline tugev punkt.
    * **Andmelekke audit ja selle tulemuse aus avalikustamine** (esimene ring §\,\ref{sec:three-rounds}) --- enesekriitiline lähenemine, mis tugevdab töö usaldusväärsust.
    * **Mitmemõõdikuline hindamine ja \enquote{lühitee} mõiste} (§\,\ref{sec:general-principle}) --- iga mõõdiku kohta dokumenteeritud, mida ta \emph{tahtis} mõõta vs.\ \emph{tegelikult} mõõtis.
    * **Ablatsioonid:** v6-residual (residuaalühenduse mõju), v13a/v13b (SpecAugmenti mõju). See näitab disainifaktorite eraldamist, mitte kõikide muudatuste korraga lükkamist.
    * **Mitmemõõdikuline kontrollpunkti valikukriteerium} (kolmas ring) --- otsene Goodharti seaduse mitigatsioon.
    * **CLI-instrumenteerimine} \texttt{kratt} all (kasutajatesti tööriistastik) --- modulaarne, korratav, hooldatav.
    * **Mudeliversiooni-dokumentatsioon} (NOTES.md + MODEL\_LINEAGE.md repo-tasemel) --- parim praktika \enquote{orphan-mudelite} vältimiseks.

    **Lünk:** \emph{seemnete (random seed) varieerimine} ei ole töös arutletud. Iga raporteeritud FAPH-arv (sh $0{,}79$) tugineb ühele treeningule, mitte $n$~seemne keskmisele $\pm$~standardhälbele. Väikse mudeli (${\sim}22$\,k parameetrit) ja väikse andmestiku puhul on seemne-varieeruvus tavaliselt suur ja võib mõõtmises olla suurem kui mõõdiku 95\%~Poissoni-vahemik.

* **Soovitused parandamiseks:**
    * Kui aega jääb, treenige \texttt{v16c} või konsensuse pari $3$~seemnega ja raporteerige FAPH ja saagis $\pm$~standardhälve. Kui mitte, lisage \enquote{Mida saab juba praegu väita} loendisse üks punkt, mis tunnistab, et raporteeritud arvud on **ühe-treeningu hinnangud}, mitte seemne-stabiilsuse karakteristika.
    * Kontrollige, kas tulemuste peatükis on iga FAPH-arvu juures märgitud Poissoni 95\%~vahemik (mitte ainult tekstis kirjeldatud, et see olemas on).

---

## 6. Halbade praktikate ja antimustrite puudumine (Anti-patterns)

* **Hinne:** 8/10
* **Analüüs:**
    Klassikalisi \enquote{koodilõhnu} on töös vähe ja need on enamasti teadvustatud. Allpool on identifitseeritud konkreetsed jääkriskid.

    **Tuvastatud antimustrid (väikesed):**
    * **\enquote{Vaikiv} mudelivalik kõikide mittekõneliste signaalide suhtes} (kolmas ring): see on \emph{Goodharti antimuster} --- optimeerimine FAPH minimum'i vastu kuni mudel \enquote{õpib mitte rääkima}. Töö **dokumenteerib} selle ja kohandab kriteeriumi komposiitseks; antimuster on tuvastatud, mitte aktiivne.
    * **TTS-andmetega treenitud + TTS-andmetega hinnatud topelt-paisutus} (§\,\ref{sec:benchmark-gap} põhjus 1): jälle dokumenteeritud Park~et~al.\ kontekstis \cite{park2024adversarial}, mitigatsioon (kasutajatest reaalsete kõnelejatega) on plaanitud.
    * **Punkt-hinnangu fetišeerimine ($0{,}79$~FAPH):} sissejuhatus tunnistab, et \enquote{Poissoni 95\%~vahemik on lai}, mis on aus, kuid annotatsioonis ja kokkuvõttes võiks see lai vahemik samuti olla nimetatud, mitte ainult punktarv. Praegu jääb pinnapealsel lugemisel mulje, et $0{,}79$ on stabiilne tulemus.
    * **\enquote{Üksiku autori} laine ehitus} (agentpõhine arendus): risk, et abivahendite kiht (Android-rakendus, hindamisskriptid) ei ole pärast kaitsmist hooldatav. Töö tunnistab seda \enquote{tehnilise võla} kontekstis kaudselt, kuid ei dokumenteeri **mis komponendid jäävad eluks ajaks projekti tugiosaks ja millised on ühekordsed eksperimentaal-tööriistad}.

    **Mis ei ole antimuster, kuigi võib esmapilgul tunduda:**
    * Kahe raamistiku samaaegne hoidmine (microWakeWord + openWakeWord) --- see ei ole \enquote{tehnoloogia-hülgemine} (\emph{shotgun stack}), sest kumbki on selgelt määratletud rolliga (sihtseade vs.\ võrdlus).
    * \enquote{15+ mudeliversiooni} --- see ei ole \enquote{magic-iteration}, sest iga versioon on dokumenteeritud (NOTES.md + MODEL\_LINEAGE.md) ja muudatuse delta on konkreetne.

    **Mis võib olla varjatud antimuster (ei saa ilma 4.~peatüki täismahuta välistada):**
    * Kui tulemuste peatükk valib mudeliversiooni hinnangu \emph{post-hoc} mitme mõõdiku peale (\enquote{see versioon võitis A, see versioon võitis B}), võib tekkida \enquote{cherry-picking-kompromiss}. Kolmanda ringi komposiitne kriteerium peaks selle välistama, kuid kontroll on lugejal vaja teha 4.~peatüki tabelite peal.

* **Soovitused parandamiseks:**
    * Lisage annotatsioonidesse (eesti ja inglise) FAPH $0{,}79$ kõrvale Poissoni 95\%~ülempiir (nt $0{,}79$ {[}~LO,~HI~{]}). Praegu on punktarv eraldatud oma usaldusvahemikust ja võib lugejat eksitada.
    * Lisage \enquote{Töö piiritlemine} või \enquote{Edasised suunad} alla üks lõik **agentpõhise tugitarkvara hoolduskohustuse} kohta: millised \texttt{kratt} CLI-osad jäävad reprodutseerimist toetama, milliseid kasutati ühekordselt.
    * 4.~peatüki tabelite juures veenduge, et komposiitne kriteerium (FAPH + saagis + sarnaste FPR + fraasistruktuur) on **enne mudelivaliku-otsust} fikseeritud, mitte tabeli vaatamise järel kalibreeritud.

---

## Üldhinnang

Kaalutud üldmulje: tehniline lahendus on **distsiplineeritult põhjendatud, mõõdetult ehitatud ja enesekriitiliselt dokumenteeritud}. Töö kõige tugevam panus on \enquote{kolme valideerimisringi} muster ja FAPH-variantide eksplitsiitne loendusreegel --- need on metoodiliselt küpsemad kui keskmise bakalaureuse tehniline aparaat. Kõige selgem jääkrisk on, et kasutajatest (\enquote{neljas ring}) ja stsenaariumipõhine 2~h salvestus on **kavandid, mitte teostused}, ning et $0{,}79$~FAPH-i numbrit kasutatakse mõnikord ilma usaldusvahemikuta. Need on enne kaitsmist parandatavad ilma uue katsekäiguta.
