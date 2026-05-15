---
source_prompt: 03_Lõputöö_alamosad/Tegevusplaani_koostamine/Valideerimise_plaan.txt
prompt_type: hybrid (evaluative audit + generative plan)
generated: 2026-05-07
---

# Valideerimisplaani audit ja optimeeritud tegevuskava

## Sisendparameetrite täpsustus (tekstist tuvastatud)

- **Töö tüüp:** Bakalaureusetöö (TalTech, IT-teaduskond).
- **Eesmärk:** Maksimaalne hinne; CLAUDE.md sõnastab ülemise sihina *cum laude*-tasemel kaitsmise.
- **Meeskonna suurus:** 1 inimene (üksikautor + juhendaja).
- **Aega jäänud:** ~10 päeva tekstilise sisu lõplikuks fikseerimiseks (kõva tähtaeg 2026-05-18; tänane 2026-05-07).
- **Kasutatav meetod (tekstist tuvastatud):** Töö ei nimeta otsesõnu Design Science Researchi, kuid praktiline ülesehitus on selgelt DSR-tüüpi: luuakse artefakt (treeningu- ja hindamistoru, mudel \texttt{v16c} / ekspertkonsensus, ESPHome-integratsioon), iteratiivselt valideeritakse (kolm \enquote{auditiringi}: andmeleke, positiivse klassi audit, kontrollpunkti audit) ning planeeritakse \emph{Human Risk \& Effectiveness}-tüüpi naturaalne kasutajatest. Sekundaarselt esineb ka \emph{Evaluation}-tüüpi panus Mary Shaw' tähenduses --- töö pakub uue hindamisprotokolli ja võrdleb seda vananenud lähenemisega.

---

## 1. Hetkeolukorra analüüs

### Hinnang

**Tugevused.**

1. *Mitmekihiline hindamisarhitektuur on juba sõnastatud.* Teine peatükk eristab nelja FAPH-i varianti (raamistiku, skriptitud taasmängu, välitingimuste, kasutajatesti taasmängu) ning fikseerib usaldusvahemike valiku (Wilson + Poissoni-Garwood + kolme reegli ühepoolne piir). See on metoodiliselt rangem kui enamik bakalaureusetööde valideerimisplaane.
2. *Treeningu- ja hindamistoru on otsast lõpuni valideeritud avaliku kontrollkatsega* (\texttt{Speech Commands} / \texttt{marvin}) ja andmelekke audit on dokumenteeritud --- see vastab Mary Shaw' \enquote{Validation: Analysis} kategooriale ja eemaldab kõige levinuma usutavust kahjustava riski.
3. *Kasutajatesti protokoll on operatiivselt valmis.* Olemas on käsureatööriistad (\texttt{kratt user-test}, \texttt{validate-user-test}, \texttt{replay-user-test}, \texttt{summarize-user-test}), külmutatud lävede ja varimudelite (\texttt{v16c}, \texttt{expert-a}, \texttt{expert-b2}, \texttt{v6-residual}, \texttt{v10}, \texttt{v15}, konsensus) komplekt ning kaheastmeline nõusolekumudel (minimaalne + audio-opt-in).
4. *Kompositsioonkriteerium on selgelt põhjendatud.* Kolmanda \enquote{auditiringi} arutelu näitab, miks ühte mõõdikut optimeerides tekib lühitee --- see on töö metodoloogiline põhipanus ning toimib *Rigour*-argumendina FEDS-i mõttes.
5. *Ausus piirangute osas on olemas.* Neljanda valideerimiskihi võimalikkus on tunnistatud, mis vastab Shaw' \enquote{Threats to validity} nõudele.

**Nõrkused.**

1. *Valideerimisplaan ei ole formaalse uurimismeetodi raamistuses esitatud.* Kuigi praktika on DSR-i, ei nimetata seda nii ega seota FEDS-i strateegiavalikuga. See on kaitsmiskomisjoni jaoks kerge sihtmärk: \enquote{millise meetodi järgi te valideerite?}.
2. *Kasutajatesti valim 20--30 osalejat on deklareeritud, kuid valimi koosseisu ja õigustuse põhjendus puudub.* Pole esitatud, milline on demograafiline ja akustiline jaotus (vanus, sugu, dialekt/aktsent), kas valim on mugavus- või kihistatud valim ning kuidas see seab piirid välisele valiidsusele.
3. *Statistilise võimsuse arvutus puudub.* 20--30 osalejal viie positiivse ütlusega sessioon annab 100--150 ütlust --- konkreetne Wilsoni vahemiku laius eeldatava saagise 0,80--0,95 juures pole kvantifitseeritud. See on \emph{Cum laude}-taseme kaitsmisel ootuspärane.
4. *Valideerimisetapid ei ole eksplitsiitselt seotud uurimisalamküsimustega.* Sissejuhatuses on neli alamküsimust, kuid plaan ei kaardista, milline samm vastab millisele küsimusele --- see on Shaw' kriteerium \enquote{kas pakutud tõend toetab väidet}.
5. *Eetika- ja andmekaitse menetlus on praktiliselt kirjeldatud, kuid ametlik kinnitus pole nähtavalt fikseeritud.* GDPR-i + ETAG/eetikakomitee viited eksisteerivad mälus, kuid plaanis ei seisa, kas TalTech eetikakomitee otsus on käes ja millise nõusolekuvormi alusel WAV-id säilitatakse.
6. *Pikaajaline välitingimuste FAPH (>24 h) puudub vaikimisi tõendite hulgast.* Põhipeatükkides mainitakse 99 h Android-välikatset, kuid see eelnes praeguse aktiivse mudeli (\texttt{v16c}) külmutamisele; kasutajatestil põhinev FAPH-tõend tuleb ainult 10-minutiliste seansside kaudu.
7. *Reprodutseeritavuspakett ei ole tagatisena fikseeritud.* Plaan ei sätesta, et kasutajatesti kogumise lõppedes avaldatakse külmutatud lävede, varimudelite hashide, sessioonide skeema ja taasmänguskripti versioonid ühe \texttt{git tag}-i all. *Cum laude*-kaitsmisel on see oodatud.

### Metodoloogiline vastavus

**Mary Shaw' raamistik.** Töö pakub kombinatsiooni *Method/Technique* (hindamisprotokoll), *Tool/Notation* (CLI-tööriistad), *Specific solution / Prototype* (\texttt{v16c} + ekspertkonsensus). Vastav nõutav valideerimine on Shaw' tabeli järgi *Analysis* + *Evaluation* + *Experience*. Praegune plaan katab Analyse'i (FEDS taustal andmestiku ja toru audit) ja Evaluation'i alguse (skriptitud taasmäng + kontrollkatse), kuid Experience-osa --- mille puhul on vaja \enquote{used in practice by independent users} --- on alles planeeritav. *Cum laude*-tasemel on Experience alustamine vajalik, kuid 10-minutiline seanss ei ole iseenesest pikaajaline kasutuskogemus, vaid \emph{controlled exposure} --- seda tuleks plaanis ka nii nimetada, mitte täiemahulise *Experience*-tõendusena.

**FEDS (Venable et al.).** Töö praegune valideerimine on hübriid:

- *Quick \& Simple* — esmane raamistike võrdlus ja avaliku andmestiku kontrollkatse;
- *Technical Risk \& Efficacy* — ekspertkonsensus ja taustaheli FAPH ühel korpusel;
- *Human Risk \& Effectiveness* — kasutajatest 20--30 osalejaga.

Strateegiate vahekord on kallutatud tehnilise valideerimise poole, mis on bakalaureusetöö ressursipiirangute juures õigustatud, kuid plaanis tuleks see eksplitsiitselt FEDS-keeles välja öelda, sest muidu jääb juhuslik tunne, et naturalistlik valideerimine on vähem oluline.

### Tuvastatud riskid

1. **Ajariski-konflikt kirjutamise lõppfaasi ja kasutajatesti vahel.** Kui osalejate kogumine venib pärast 12. mai, jääb numbrite peatükki sisseviimiseks alla nädala. Plaanis peab olema selge \enquote{andmete külmutamise} kuupäev, millest hiljem laekuvad osalejad lähevad ainult kaitsmise lisamaterjali, mitte trükipoognasse.
2. **Ühe kõneleja ekspositsioon Kule-vs-Kuule probleemile.** Kui valim koosneb peamiselt põhja-eestilistest \enquote{Kuule}-hääldajatest, ei lahendata teadaolevat treeningujaotuse kallutatust (mälust: 86\% \enquote{Kuule} treeninguandmes vs.\ valitsev \enquote{Kule} kõnes). Tulemus näib tugev, kuid ei tõenda kasutuskõlblikkust.
3. **Audio-nõusoleku madal määr lõikab varimudelite võrdluse jalust.** Kui ainult \texttt{trials.jsonl} ridade tuvastusotsused logitakse ja WAV-e ei säilitata, ei saa hiljem teha varimudeli taasmängu --- see kaotaks kogu kasutajatesti taasmängu FAPH-i analüüsi.
4. **Riistvaravalik kasutajatestil.** Kui osalejad testivad ainult ESP32-S3 Korvo-2 vaikemikrofoniga ühes ruumis, jääb akustilise üldistuse osa testimata. Plaani peab olema sisse kirjutatud vähemalt mikrofoni kauguse variatsioon (lähi vs.\ ~3 m).
5. **Statistiline alaülevaade.** 20-osalist valimit on \emph{cum laude}-kaitsmisel kerge rünnata: \enquote{milline efekt suurus on teie statistiline võimsus tabada?}. Vastus peab olema plaanis kirjas.
6. **Eetikakomitee otsus.** Kui ametlikku kooskõlastust pole hetkeks, kui salvestus algab, võib küsimus tõusta kaitsmisel; plaanis tuleb fikseerida juba saadetud taotluse number ja kuupäev.

---

## 2. Soovituslik valideerimisplaan (tegevuskava)

Järgnev plaan on jaotatud kolme etappi ja kalibreeritud üksikautori 10-päevase eelarve alla. Iga etapp viitab uurimisalamküsimustele (UAK1--UAK4 sissejuhatusest).

### Etapp 1 --- Ettevalmistus (07.--09.05.2026, 2--3 päeva)

**Eesmärk:** lukustada artefakti olek ja valideerimisinstrumendid enne andmete kogumist; täita FEDS-i \emph{ex ante} sisendid.

1. **Artefakti külmutamine.**
   - Tag \texttt{user-test-frozen-2026-05-07} kogu \texttt{kratt}-monorepole.
   - Külmutatud lävi cutoff $\geq$ 0{,}97 (või praegu kasutuses olev) kõikidel varimudelitel; hashid kirja sessioonimetainfosse.
   - \texttt{v16c}-i ESPHome-firmware kompileeritud kontrollsumma fikseeritud (UAK4).

2. **Valimi disain ja kihistus.**
   - Sihtvalim 24 osalejat (alampiir 20, ülempiir 30). Kihistus kahe telje järgi:
     a. dialekt/hääldusvariant: vähemalt 30\% \enquote{Kule}-tüüpi, vähemalt 30\% \enquote{Kuule}-tüüpi (mitigeerib treeningu kallutatust);
     b. sugu/häälekõrgus: ligikaudne tasakaal kõrge ja madala põhitooniga kõnelejate vahel.
   - Värbamiskanalid: TalTech IT-fakulteedi listid, isiklik võrgustik, üks väline kanal (nt eesti keelega seotud kogukond).

3. **Statistilise võimsuse hinnang (a priori).**
   - Saagise punkthinnang 0{,}90; Wilsoni 95\%~vahemik 100 ütluse korral on ligikaudu $\pm$0{,}06; 150 ütluse juures $\pm$0{,}05. See on kirja panna metoodikasse, et komisjon näeks, miks 24 osaleja $\times$ 5 ütlust = 120 ütlust on \emph{piisav vahemiku} jaoks $\pm$0{,}055.
   - FAPH kasutajatesti taasmängul: 24 sessiooni $\times$ 10 min = 4 h. Kolme reegli järgi annab nullsündmus 95\% ülempiiri $\sim$0{,}75 FAPH-i. Kui sihiks on FAPH $<$ 1, on see vahemik napp, kuid kaitstav, kui kombineerida pikemaid taustaheli korpuseid kasutajatesti taasmänguga (vt etapp 2.4).

4. **Eetika ja nõusolek.**
   - Veendu, et TalTech eetikakomitee taotlus (eetika@taltech.ee) on saadetud või kooskõlastatud; lisa taotluse number plaani.
   - Kahekihiline nõusolekuvorm: minimaalne (otsuste logi pseudonüümselt) + audio-opt-in (WAV-ide hilisem taasmäng, säilitustähtaeg 6 kuud peale kaitsmist).
   - Pilootkatse $n=2$: kontrolli, kas 10 minuti seanssi mahub ettenähtud ülesannete maht (5 positiivset, 5 negatiivset, 6 skriptitud, 1 vabavormiline) ning kas RMS-hoiatused tulevad kuhugi piirile.

5. **Hindamisinstrumendid.**
   - Lukusta lühiküsimustik (4 Likert-skaalat + 1 avatud + UMUX-Lite kaks väidet).
   - Veendu, et \texttt{kratt validate-user-test} kontrollib RMS-i, kanaleid ja diskreetimissagedust; vea korral session abandon, mitte vaikne logimine.
   - Mikrofoni kauguse manipulatsioon: pool ütlustest $\sim$0{,}7 m, pool $\sim$2{,}5 m kauguselt --- juhuslikus järjekorras --- katmaks akustilise üldistuse miinimum.

**Vastendus uurimisalamküsimustega:** UAK1 (toru valideerimine) on enne seda etappi juba lahendatud; etapp 1 valmistab ette UAK2 (positiivse/negatiivse rolli) ja UAK4 (FAPH$<$1 ja saagis$\geq$0{,}95) tõenduse.

### Etapp 2 --- Valideerimise läbiviimine (10.--14.05.2026, 5 päeva)

**FEDS-strateegia:** *Human Risk \& Effectiveness* põhiosa + *Technical Risk* täiendus.

1. **Naturalistlik kasutajatest (10.--13.05).**
   - 24 osalejat, $\sim$10 min seanss kummalgi.
   - Iga seanss: 5 puhast \enquote{Kuule Kratt}, 5 sihtsarnast negatiivi (sh \enquote{kuule rott}, \enquote{kuule kraam}, eraldi \enquote{kuule}, \enquote{kratt} eraldi, vahetatud järjekord), 6 skriptitud käsku, 1 vabavormiline pirniülesanne, kahel kaugusel.
   - Salvestus \texttt{kratt user-test} kaudu \texttt{trials.jsonl} + WAV (audio-opt-in korral).
   - Süsteemne valideerimine \texttt{kratt validate-user-test} igal seansil enne osaleja vabastamist; ebakvaliteetne seanss märgitakse, mitte ei kustutata (mälunõue: \enquote{never delete data}).

2. **Külmutatud süsteem demonstreerimisel.**
   - Kasutajale nähtav süsteem on \texttt{v16c} ühe mudelina; kõik teised varimudelid kasutavad sama heli taasmängul.
   - Sessioonijärgne küsimustik viiakse läbi paberil või tahvelarvutil, vastused seotakse osaleja ID-ga, mitte WAV-iga.

3. **Skriptitud taasmäng (12.--14.05, paralleelselt).**
   - Iga päev kogutud sessioonid lähevad samal õhtul \texttt{kratt replay-user-test} kaudu kuue varimudeli ja konsensuse läbi.
   - Logitakse iga ütluse kohta: tuvastatud lävel, maksimaalne skoor 1500 ms aknas, ajatempel relatiivselt sessiooni algusest.

4. **Pikaajaline taustaheli täiend (kogu nädala vältel taustal).**
   - Käivita ESPHome \texttt{v16c} satelliit ühes argielukeskkonnas (köök/elutuba) vähemalt 48 h.
   - Logi raamistiku FAPH (seadme-natiivne loendus) ja paralleelselt skriptitud taasmängu FAPH samalt mikrofonilt.
   - Eesmärk: \emph{välitingimuste FAPH} sai ühe korpuse, mis laiendab Poissoni vahemiku punkthinnangu sõltumatuks võrdluskohaks Common~Voice~ET kõrvale.

5. **Subjektiivne rahulolu.**
   - Sessiooni järel: 4 uurija küsimust (usaldusväärsus, kiirus, käskude loomulikkus, kodus kasutamise valmidus) Likert 1--7 skaalal + 1 avatud küsimus + UMUX-Lite kaks väidet.
   - UMUX-Lite raporteeritakse valideeritud koondskaalana; uurija küsimusi käsitletakse diagnostilistena (juba kirjas teises peatükis).

**Vastendus uurimisalamküsimustega:** UAK2 (andmeliikide roll) ja UAK3 (andmestiku vs.\ toru piirangute eristus) saavad kvantitatiivse tõenduse läbi varimudeli taasmängu; UAK4 saab tõenduse kombineerides Common~Voice~ET kõrvalejäetud korpuse, kasutajatesti taasmängu ja 48 h argitausta.

### Etapp 3 --- Analüüs ja järeldused (15.--17.05.2026, 3 päeva)

1. **Andmete koondamine.**
   - \texttt{kratt summarize-user-test} jooksub kõikide sessioonide ja kõikide varimudelite peal $\rightarrow$ tabel \enquote{tuvastamismäär $\pm$ Wilsoni 95\%; FPR sihtsarnastel $\pm$ Wilson; FAPH kasutajatesti taasmängul $\pm$ Poisson-Garwood; FAPH 48 h argitaustal $\pm$ Poisson-Garwood}.
   - Eraldi tabel: \texttt{v16c} ühemudelina vs.\ ekspertkonsensus --- selgelt välja toodud, et konsensus on diagnostiline, mitte juurutuses kasutatav, kui kasutajatest seda ei kinnita.

2. **Lõppjärelduste sõnastus.**
   - Iga tabeli järel üks lõik, mis sõnastab Mary Shaw' \enquote{What does it persuade us of?} -- näiteks: \enquote{kasutajatesti taasmäng kinnitab/lükkab ümber esialgset ekspertkonsensuse FAPH$=$0{,}79 numbrit, mis oli punkthinnang ühe korpuse peal}.
   - Ausus: kui kasutajatesti saagis langeb alla 0{,}90, tuleb seda otse väita ja siduda jääkpiiranguks (kooskõlas teise peatüki §-ga \texttt{user-test-methodology}).

3. **Kvalitatiivne analüüs.**
   - Avatud küsimuse vastustest temaatiline kodeerimine (lühike, kaks koodirühma: häirivad mustrid + üllatavad mustrid).
   - Diagnostilised Likert-väärtused esitatakse mediaaniga ja IQR-iga, ei keskmistata, kuna $n$ on väike.

4. **Tagasiside metoodikasse.**
   - Kui kasutajatest paljastab \enquote{neljanda valideerimiskihi} efekti (nt aktsentide variatsioon), siis kolmanda peatüki §\texttt{fourth-round} saab uue konkreetse näite, mitte oletuse.
   - Kui kasutajatest kinnitab kontrollpunkti audit kompromissi (FAPH vs.\ saagis), siis kompositsioonkriteerium saab empiirilise toetuse.

5. **Reprodutseeritavuspakett.**
   - Ühes \texttt{git tag}-is: külmutatud mudelite hashid, taasmänguskript, sessioonide skeema (\texttt{trials.jsonl} + küsimustiku CSV), eetikakomitee numbri viide, anonüümitud osalejate kihistustabel.
   - Eraldi failina: \texttt{LIMITS.md}, mis dokumenteerib valimi piirangud (mugavusvalim, $n=24$, ühe ruumi mikrofoniseaded), nii nagu Shaw' \enquote{Threats to validity} eeldab.

**Vastendus uurimisalamküsimustega:** etapp 3 kinnitab UAK4 numbrid ja seob need usaldusvahemikega; UAK1--UAK3 kohta lisanduvad kasutajatesti tõendid kui täiendav, mitte asendav kiht.

---

## 3. Põhjendus

**Miks see plaan on parem kui praegu sõnastatud variant.**

1. *Eksplitsiitne metoodikaraamistus.* Plaan nimetab strateegia FEDS-i terminites (*Human Risk \& Effectiveness* + *Technical Risk* täiend) ja Shaw' kategoorias (*Analysis* + *Evaluation* + algav *Experience*). Komisjoni küsimusele \enquote{millise meetodi järgi te valideerite?} on üheainsa lausega vastus.

2. *Statistiline kaitse.* Wilsoni vahemiku laius ja Poissoni-Garwoodi ülempiir on \emph{a priori} arvutatud, mitte tagantjärele põhjendatud. See vastab \emph{cum laude}-tasemel oodatavale rangusele ning lubab autoril komisjonile öelda \enquote{me ei deklareeri saagise punkthinnangu tugevust ilma vahemikuta}.

3. *Kihistatud valim adresseerib teadaolevat treeningujaotuse kallutatust.* \enquote{Kule}-vs-\enquote{Kuule}-jaotus on käesoleva töö dokumenteeritud nõrkus; plaan muudab selle eksperimendi sõltumatuks muutujaks, mitte segavaks faktoriks.

4. *Kahe kõrgust mikrofoni manipulatsioon* annab miinimummahus akustilise üldistuse tõenduse, ilma et kogumismaht plahvataks --- vajalik kompromiss üksikautori 10 päeva juures.

5. *Pikaajaline argitausta täiend* eemaldab nõrkuse, et FAPH-tõend toetub ainult kasutajatesti 4-tunnisele kogumahule. 48 h annab Poissoni vahemikule sisuliselt parema lävimanööverdusvälja ning lubab väiteid kõrvutada Common~Voice~ET hold-out punkthinnanguga.

6. *Teostatav (Feasible).* Etapid mahuvad 10 päeva eelarvesse, kasutavad olemasolevaid tööriistu (\texttt{kratt user-test}, \texttt{validate}, \texttt{replay}, \texttt{summarize}) ning eeldavad ainult ühte uut riistvaratarkvaravalmidust (48 h argitausta seadmel käitatud satelliit, mis on niikuinii deployment-väite osa).

7. *Veenev (Rigorous).* Iga etapi väljund vastab konkreetsele alamküsimusele ja konkreetsele Shaw' / FEDS-i nõudele; iga arv tuleb usaldusvahemikuga; jääkpiirangud on \texttt{LIMITS.md}-s, mitte kaudselt sissejuhatuses; reprodutseeritavuspakett ühes \texttt{git tag}-is.

**Mis võib endiselt jääda kaitsmisel haavatavaks.** Üksikautori valim, ühe ruumi akustika, sünteetiliste positiivsete näidete osakaal treeningus ja audio-opt-in määra ennustamatus on kõik teadlikud bakalaureusetöö piirangud, mida plaan ei kõrvalda, vaid eksplitsiitselt dokumenteerib --- see on \emph{cum laude}-tasemel kaitstavam strateegia kui jätta need lugeja avastamiseks.
