---
source_prompt: 03_Lõputöö_alamosad/Seotud_tarkvara.txt
prompt_type: generative
generated: 2026-05-07
---

# Seotud tarkvara: turu-uuring ja konkurentsianalüüs

Käesolev dokument on lõputöö lisamaterjalina koostatud konkurentsianalüüs, mille aluseks on kavandatava tarkvara kirjeldus tööst (peamiselt sissejuhatus, esimene peatükk \emph{Metoodika}, teine peatükk \emph{Tulemused ja arutelu} ning ülesandepüstitus). Loodava lahenduse all peetakse silmas eestikeelse äratussõna \enquote{Kuule Kratt} mudelit ja selle juurde kuuluvat treenimis-, hindamis- ja juurutamistoru, mis lõimitakse Home Assistanti hääljuhtimise ahelasse ESPHome \texttt{voice\_assistant} liidese kaudu ESP32-S3 klassi seadmel.

## 1. Konkurentide ja sarnaste lahenduste analüüs

### 1.1 microWakeWord (Kevin Ahrendt, avatud lähtekoodiga)

**Nimi ja lühikirjeldus.** Avatud lähtekoodiga TensorFlow-põhine raamistik äratussõna mudelite treenimiseks ja juurutamiseks mikrokontrolleritele. Toodab täisarvulises (INT8) vormingus TFLite-mudeleid, mis on otse käivitatavad ESP32-S3 klassi seadmel ESPHome'i kaudu.

**Kattuvus.** See on käesoleva töö praktiline alustehnoloogia, mitte konkurent eristuse mõttes. microWakeWord katab täpselt sama kasutusjuhtu --- alati-aktiivne madala mälumahuga äratussõna detektor mikrokontrolleril --- ja lähtub samast disainikompromissist (väike parameetrite arv, voogedastusrežiim, INT8-kvantiseerimine).

**Erinevused ja puudused.** microWakeWord on raamistik, mitte valmis eestikeelne mudel: see ei paku jaotatud (\emph{distributed}) eestikeelseid kontrollpunkte ega kohanduvat hindamistoru väikese keele tingimustes. Raamistiku enda dokumenteeritud hindamine põhineb peamiselt klipi-tasemel mõõdikutel ja paaril vaikimisi taustaheli korpusel, mis ei kata käesoleva töö teises peatükis kirjeldatud kolme valideerimisringi (sõltumatu kõrvalejäetud komplekt, positiivse andmestiku reostuse audit, mitmemõõtmeline kontrollpunkti valik). Samuti puudub raamistikus sisseehitatud foneetiliselt sarnaste negatiivnäidete \emph{(hard negative)} käsitlus, mis eestikeelse \enquote{Kuule Kratt} eristamiseks fraasidest \enquote{kuule rott} või \enquote{kuule kraam} on kriitilise tähtsusega.

### 1.2 openWakeWord (David Scripka, avatud lähtekoodiga)

**Nimi ja lühikirjeldus.** Avatud lähtekoodiga ONNX-põhine äratussõna raamistik, mis on suunatud Raspberry Pi klassi hostile ja kasutab eeltreenitud kõnetuvastusmudelite tunnusvektoreid (\emph{embedding}) sisendiks. Tihedalt põimitud Home Assistanti ökosüsteemiga.

**Kattuvus.** Lahendab sama probleemi --- lokaalne äratussõna tuvastus ilma pilveta, lõimitav Home Assistanti hääljuhtimise ahelaga --- ning toetab mudelite treenimist sünteetilisel andmestikul, mis on käesoleva töö üks võtmevõtteid.

**Erinevused ja puudused.** openWakeWord ei kuulu \texttt{ESP32-S3} sihtklassi: ONNX-runtime ja eeltreenitud tunnusvektorite ekstraheerija nõuavad Raspberry Pi taseme arvutusvõimsust, mistõttu lahendus ei mahu mikrokontrolleri tensor-arenasse. Eesti keel ei kuulu jaotatud eelmudelite hulka. Lisaks raporteerib raamistiku enda dokumentatsioon FAPH-i ühe sihtväärtusena ($<\!0{,}5$ FA/h), kuid loendusreegel ja taustaheli korpus on vaikimisi ingliskeelsed; käesoleva töö \S\ref{subsec:faph-variants} näitab, et FAPH-loendusreeglid on omavahel ebavõrreldavad ning sama mudeli FAPH võib varieeruda kahe suurusjärgu jagu sõltuvalt kasutatud režiimist.

### 1.3 Picovoice Porcupine (suletud lähtekoodiga, kommertslitsents)

**Nimi ja lühikirjeldus.** Tööstuses laialt kasutusel olev kommertsiaalne äratussõna mootor, millel on eraldi mikrokontrolleri-, hosti- ja brauseri-SDK. Pakub avalikku võrdlusalust (\emph{benchmark}) ja kasutab kasutajaspetsiifilist mudeligeneraatori teenust.

**Kattuvus.** Sama kasutusjuht (alati-aktiivne kohalik äratussõna), sama riistvaraklass (sealhulgas ESP32) ja sarnane FAPH-keskne raporteerimine.

**Erinevused ja puudused.** Suletud lähtekood ja litsentsipõhine ärimudel ei luba kasutajal endal kohalikult uut äratussõna mudelit treenida ega sünteetilist andmestikku otse mootori sisse viia. Eesti keel ei kuulu toetatud keelte hulka. Mudeli sisemine arhitektuur, lävi (\emph{threshold}) ja loendusreegel on lukustatud, mis muudab teadusliku korratavuse võimatuks ja välistab Porcupine'i käesoleva töö tegelikust nelja-teljelisest võrdlusest --- nagu ka \S\nobreak\,\enquote{Võrdlusraamistik} esimeses peatükis on selgelt välja öeldud.

### 1.4 Apple Siri / Google \enquote{Hey Google} / Amazon Alexa (kommertsiaalsed pilvepõhised äratussõna süsteemid)

**Nimi ja lühikirjeldus.** Suurte tehnoloogiaettevõtete hääljuhtimise ahelad, mille esimene aste (kohalik DNN-HMM või sarnane väike detektor) töötab seadmel, kuid kontrollv\-erifikatsioon ja edasine kõnetuvastus toimuvad pilves. Apple ja Google on avaldanud tehnilisi artikleid oma kaskaadarhitektuuri kohta \cite{apple-heysiri2017,gruenstein2017cascade}.

**Kattuvus.** Sama põhiline kontseptsioon --- alati-aktiivne väike detektor + täpsem teine aste --- mille käesolev töö pakub välja edasiste sammude all (vt \S\ref{sec:future-cascade}). Suured süsteemid kasutavad ka mitme-mõõdikulist hindamist (valekäivitused, tegelike äratuste kaotus, kõneleja eripära, akustilised keskkonnad), mis sarnaneb käesoleva töö \emph{kolme valideerimiskihiga}.

**Erinevused ja puudused.** Kogu sõltuvus pilvest ja toodete suletud iseloom muudavad need GDPR-tundliku nutikodu lokaalse kasutuse jaoks põhimõtteliselt sobimatuks. Eesti keele tugi on osaline (Siri toetab teatud määral, Alexa praktiliselt mitte) ning vahepealsete pakkujate roll andmete töötluses jääb läbipaistmatuks. Lisaks ei ole nende süsteemide äratussõna kohandamine kasutaja valitud sõnale (\enquote{Kratt}) reeglina võimalik.

### 1.5 Snowboy (KITT.AI, vananenud) ja Mycroft Precise (Mycroft AI, hooldus lõpetatud)

**Nimi ja lühikirjeldus.** Kaks varasemat avatud lähtekoodiga äratussõna lahendust, mis olid 2017--2021 sageli viidatud privaatsuskeskses nutikodu kogukonnas. Snowboy põhines GMM/DNN hübriidil, Precise rekursiivsetel närvivõrkudel.

**Kattuvus.** Sarnane filosoofia --- lokaalne, avatud lähtekoodiga, kasutaja kohandatav äratussõna --- mis on käesoleva töö üks ajendiga seotud eeskuju.

**Erinevused ja puudused.** Mõlemad projektid ei ole enam aktiivselt hooldatud (Snowboy lõpetas tegevuse 2020, Mycroft AI tegevuse 2023). Kumbki ei toeta tänapäevast voogedastushindamist, INT8-kvantiseeritud mikrokontrolleri-juurutust ega Home Assistanti \texttt{voice\_assistant} liidest. Hooldamatuse tõttu pole need ka teadusliku võrdluse seisukohalt ausad sihid: nende vaikimisi konfiguratsioonis saadud nõrk tulemus räägiks rohkem ökosüsteemi seisukorrast kui mudeli arhitektuurist. Mainin neid siiski, et anda lugejale tervikpilt äratussõna avatud lähtekoodiga ajaloost ning näidata, et avatud nišš on ka korduvalt hangunud.

## 2. Loodava tarkvara konkurentsieelis ja parendusettepanekud

### 2.1 Tuvastatud eelised (dokumentide põhjal)

Käesoleva töö enda materjali lugemisel ilmnevad järgmised konkreetsed eristumiskohad olemasolevate lahenduste suhtes:

1. **Esimene reprodutseeritavalt dokumenteeritud eestikeelne äratussõna mudel** mikrokontrolleri klassi seadmele. Ei microWakeWord ega openWakeWord ei jaota vaikimisi eestikeelset kontrollpunkti, ja Picovoice Porcupine ei toeta keelt üldse.
2. **Mitmemõõtmeline valideerimisprotokoll** väikese ressursiga keele kontekstis (sõltumatu kõrvalejäetud komplekt, positiivse andmestiku reostuse audit, mitmekriteeriumiline kontrollpunkti valik), mis on töö enda tunnistuse järgi \enquote{kõige kindlamini kaitstav teaduslik panus}.
3. **FAPH-i loendusreeglite ekspliitne taksonoomia** (raamistiku, skriptitud taasmängu, välitingimuste ja kasutajatesti taasmängu FAPH; \S\ref{subsec:faph-variants}). Kirjandus tunnistab loendusreegli auku reprodutseeritavuses, kuid harva kirjeldab see konkreetselt välja.
4. **Konsensus kahe ekspertmudeli vahel** kui empiiriliselt valideeritud kompromiss madalaima taustaheli FAPH-i (0,79 Common Voice ET kõrvalejäetud kõnel) ja kasutuskõlbliku tuvastamismäära vahel.
5. **Avatud lähtekoodiga, GDPR-sõbralik, ainult-lokaalne** (ingl \emph{cloud-free}) lahendus, mis lõimib end olemasoleva Home Assistant + ESPHome ahelaga ilma välise teenuseta.

### 2.2 Soovituslikud lisandväärtused

Allpool on autoripoolsed ettepanekud, kuidas töö lõputulemust olemasolevate lahenduste suhtes selgemini eristada. Neist osa on praktilised, osa teaduslikud, ja kõik on koostatud nii, et need ei nõuaks 2026-05-18 esituseelse perioodi jooksul lisaeksperimente, mis ohustaksid kirjutamise ajakava.

1. **Foneetiliselt sarnaste negatiivnäidete avalik testikomplekt eesti keele jaoks.** Käesolev töö dokumenteerib juba sellist komplekti (kuule rott, kuule kraam, prefiksid, pööratud järjekord, kuule/kule segiajamine). Kui see komplekt avaldatakse koos mudelitega avalikus repositooriumis, saab see iseseisvaks panuseks väikese keele äratussõna kogukonnale, mida ükski olemasolev raamistik ei paku.
2. **Mitme mudeli konsensushääletus kui esmaklassi (\emph{first-class}) juurutusmuster ESPHome'is.** Praegu juurutatakse ESPHome \texttt{micro\_wake\_word} all üks mudel; käesoleva töö konsensus-eksperiment näitab, et kahe spetsialiseeritud ekspertmudeli ühishääletus annab madalama FAPH-i. Kui see lõimitakse vastavasse ESPHome komponenti või avaldatakse eraldi konfiguratsioonimustrina, saab sellest iseseisev avatud lähtekoodiga panus.
3. **Kaskaadarhitektuuri teine aste, mis kontrollib eraldi sõnu \enquote{kuule} ja \enquote{kratt} ning nende järjekorda} (vt \S\ref{sec:future-cascade}). Selline kaskaad lahendaks otseselt töö dokumenteeritud lühitee-probleemi, kus mudel reageerib eesliitele \enquote{kuule} ilma \enquote{kratt}-i lisamata. Suured kommerts\-süsteemid kasutavad sarnast struktuuri, kuid avatud lähtekoodiga ESP32-tasemel pole see laialt levinud.
4. **Stsenaariumipõhine 2-tunnine annoteeritud taustaheli korpus eestikeelses kodukeskkonnas} (\S\ref{sec:benchmark-gap} on selle juba välja pakkunud). See on otseselt ülekantav teistele madala ressursiga keeltele ja täidab kirjanduses tunnistatud lünka standardsete võrdlusaluste ja reaalse kasutuse vahel \cite{dubois2020triggers,sensory2024realworld}.
5. **Ühtne \enquote{kratt} CLI tööriistastik}, mis annab nii arendajale kui ka uurijale otsast lõpuni reprodutseeritava ahela: \texttt{kratt user-test}, \texttt{kratt validate-user-test}, \texttt{kratt replay-user-test}, \texttt{kratt summarize-user-test}. Selline ühtsus puudub microWakeWord ja openWakeWord raamistike vahel, kus iga samm nõuab eraldi skripte.
6. **Kahe-astmeline nõusolekumudel (privaatsuskiht).** Minimaalne nõusolek pseudonüümseteks tehnilisteks tulemusteks, eraldi audio opt-in lühikeste märgendatud klippide säilitamiseks. See on dokumenteeritud käesoleva töö kasutajatesti metoodikas (\S\ref{sec:user-test-methodology}) ja vastab GDPR-i mõttele paremini kui kommertsiaalsete pilvepõhiste süsteemide \enquote{kõik või mitte midagi} loogika.

## 3. Kohustuslik funktsionaalsus (MVP nõuded)

Et loodav lahendus oleks turul olemasolevate äratussõna lahenduste suhtes konkurentsivõimeline ka tehnilises mõttes, peavad olema täidetud järgmised baasnõuded. Need on samaaegselt töö enda jaoks juurutuse minimaalsed kriteeriumid:

1. **INT8-kvantiseeritud TFLite-mudel}, mille maht koos tensor-arenaga mahub ESP32-S3 mälupiirangute (alla 200\,KB) sisse. Ilma selleta ei ole tegemist mikrokontrolleri-klassi lahendusega, vaid Raspberry Pi-klassi konkurendiga.
2. **Voogedastusrežiimi tugi (\emph{streaming inference})}, kus mudel uuendab sisemist olekut iga uue ${\sim}10$\,ms kaadri saabumisel ja annab ühe tõenäosuse väljundi. Klipi-tasemel järeldamine ei ole kasutuskõlblik alati-aktiivse detektori kontekstis.
3. **FAPH-mõõdik koos ekspliitse loendusreegliga}, mis on raporteeritud sõltumatu taustaheli korpuse peal vähemalt mitme tunni mahus, ning seda koos 95\% usaldusvahemikuga (Poissoni-Garwood või kolmereegli ülemine piir, kui $k=0$).
4. **Treening- ja testandmete disjointsuskontroll}, mis välistab klipi-tasemel andmelekke. See on käesoleva töö esimeses valideerimisringis tuvastatud risk, mille vältimine on iga tõsiseltvõetava äratussõna mudeli baasnõue.
5. **Foneetiliselt sarnaste negatiivnäidete eraldi mõõtmine} (raskete negatiivide testikomplekt), mitte ainult üldise valepositiivse määra raporteerimine.
6. **Lokaalne (pilveta) järeldamine} ja avatud integratsiooniliides, käesolevas projektis ESPHome \texttt{voice\_assistant} ja Home Assistanti Wyoming-protokoll. Pilvest sõltuv lahendus ei ole privaatsuskeskses nutikodu turuosas konkurentsivõimeline.
7. **Reprodutseeritav treeningu- ja hindamistoru} koos versioneeritud konfiguratsiooniga (vrdl töö \texttt{microWakeWord} kasutus, \texttt{kratt} CLI ja YAML-konfid). See on miinimum, et töö tulemusi saaks teine uurija või arendaja iseseisvalt kontrollida.
8. **Vähemalt üks reaalsete kõnelejatega (mitte ainult TTS-iga) tehtud hindamisring}, mis annab tuvastamismäära päriskõnelejatel. Käesolevas töös täidab seda käsil olev 20--30 osalejaga kasutajatest. Ainult-TTS-i hindamine on töös eraldi tunnistatud kui eksitav metoodika \cite{park2024adversarial}.
9. **Kasutaja konfigureeritav lävi (\emph{threshold})} ja vähemalt üks dokumenteeritud operatsioonipunkt, mille juures töö tulemused on kalibreeritud. Picovoice'i ja openWakeWord-iga ühilduv miinimum.
10. **Avatud lähtekoodi litsents}, mis lubab kohandamist madala ressursiga keelte jaoks. Picovoice'i tüüpi suletud SDK ei kvalifitseeru iseseisvaks akadeemiliseks panuseks ega kogukonna jaoks taaskasutatavaks komponendiks.

---

## Lühikokkuvõte tööle

Loodava tarkvara konkurentsieelis seisneb vähem mudeli enda absoluutses kvaliteedis (suured kommerts\-süsteemid on selles plaanis vaieldamatult ees) ja rohkem **väikese ressursiga keele jaoks teostatava tõendusprotokolli** kui teadusliku tulemuse saavutamises. See on ka töö enda väljaöeldud peamine kaitstav panus. Kõik selles dokumendis toodud lisandväärtuste ettepanekud on välja pakutud nii, et need säilitavad selle fookuse ega lükka 2026-05-18 esituseelset graafikut kõrvale.
