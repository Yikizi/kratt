# Negatiivse/kaitsva raamingu lint — 2026-05-16

Eesmärk: tuvastada lõputöö tekstis kohad, kus narratiiv kulutab energiat sellele, mida töö **ei** tee, **ei** tõenda, **ei** kata või kus lõik on raamistatud piirangu/kaitseklauslina. Uus reegel: sissejuhatus, kokkuvõte ja muud kõrge nähtavusega kohad peavad esiplaanile tooma töö panuse, meetodi, tulemuse ja järgmise valideerimissammu; piirangud tuleb sõnastada positiivse ulatuse või jätkusuunana.

Prioriteedid:
- **P0** — sissejuhatus/kokkuvõte/annotatsioon: parandada enne lõppversiooni.
- **P1** — pealkirjad ja lõikude avasõnastus: muuta tooni, sest lugeja skaneerib neid.
- **P2** — tulemuste/arutelu sees olevad kaitseklauslid: vajadusel ümber pöörata, aga osa võib jääda ranguse huvides.
- **OK** — tehniline negatsioon, mis defineerib andmeid või mõõdikut, mitte töö ulatust.

## P0 — kõrge nähtavusega kohad

| Asukoht | Praegune raaming | Probleem | Soovitus |
|---|---|---|---|
| `chapters/introduction.tex:1` | „ei kata eesti keelt ...” | Gap algab negatiivse väitena. Kaitstav, aga toon on puudujäägi-keskne. | Pöörata: „eestikeelse mikrokontrolleri-äratussõna jaoks on vaja kohalikku treeningu- ja hindamisahelat”. |
| `chapters/introduction.tex:3` | „Süsteemitaseme kasutusvalmidust ... käesolev töö ei tõenda ...” | Väga selge kaitseklausel kohe eesmärgi järel; lõhub sissejuhatuse tooni. | Eemaldada sissejuhatusest või pöörata: „Empiiriline fookus on kontrollitud mudeli- ja hindamisprotokollil; süsteemipiloot on järgmine valideerimiskiht.” |
| `chapters/introduction.tex:5` | „ei piisa ainult mudeli treenimisest” | Mõte on õige, aga algab puudujäägist. | Pöörata: „väikese keele äratussõna projekt ühendab mudelitreeningu, andmekontrolli ja pidevvoo hindamise”. |
| `chapters/introduction.tex:11` | „probleeme ... piirangutest” | Alamküsimus kõlab vigade inventuurina. | „kuidas lahutada andmestiku mõju tööahela mõjust” / „kuidas määrata eri tegurite roll”. |
| `chapters/introduction.tex:13` | „peamised piirangud” | Alamküsimus lõpeb negatiivse tooniga. | „millised tegurid määravad lähikõne tuvastamismäära”. |
| `chapters/introduction.tex:17–21` | H1/H2 eraldi plokk | Sissejuhatus paisub ja läheb kaitse-/metoodikakeelseks. | Viia metoodika või tulemuste algusesse; intros piisab uurimisküsimusest ja panusest. |
| `chapters/introduction.tex:23` | „Töö ei kata täielikku STT/TTS toru...” | Klassikaline „mida töö ei tee” lause. | Eemaldada või pöörata: „Töö keskendub äratussõna komponendile ja selle sidumisele Home Assistanti häälvoogu.” |
| `chapters/introduction.tex:25–26` | `Empiirilise ulatuse piirang`; „mitte kui empiirilist hinnangut ...”; „ei moodustatud ...” | Suurim tooniprobleem. Sissejuhatus muutub vabanduseks. | Tõsta arutelu/jätkusuundadesse või kirjutada positiivselt: „Empiiriline osa koosneb kõrvalejäetud klipikomplektidest, pidevvoo taasmängust ja kolmest reaalse kõneleja kontrollist.” |
| `chapters/introduction.tex:28` | „praktiliste riskide, piirangute...” | Struktuurikirjeldus lõpetab intro piirangutega. | „praktiliste mõjude, valideerimisvajaduste ja lõppjäreldustega”. |
| `chapters/summary.tex:1` | „Sõltumatu STT/TTS-ahela kvaliteet ... ei ole ... tulemusväide.” | Kokkuvõtte esimene lõik kulutab ruumi disclaimimisele. | Pöörata: „Tulemusväited keskenduvad äratussõna mudelile, hindamisahelale ja mikrokontrolleri juurutuskihile.” |
| `chapters/summary.tex:1` | „experimental ... mitte ootusena, et see töötab enamuse ajast hästi” | Väga nõrk lõputoon; mõjub iseenda töö mahategemisena. | „Lisamoodul avaldati katsetava arendusartefaktina, mille eesmärk on toetada edasist parameetriseadistust ja välikatseid.” |
| `chapters/summary.tex:7` | „piirangud eristati...” | Vastus algab piirangutest. | „kolm riskiallikat eraldati ...” või „tööahel muutus kontrollitavaks kolme mehhanismiga ...”. |
| `chapters/summary.tex:8` | „ainult ...”; „ükski hinnatud seadistus ei taganud” | Õige tulemus, aga sõnastatud kaotusena. | „Madala FAPH-i saavutas konsensus; kõrge tuvastuse ja fraasiselektiivsuse hoidmine jäi eraldi optimeerimisülesandeks.” |
| `chapters/summary.tex:9` | „kuid ei kandnud edasi...” | Negatiivne jätk sihile. | „Sama mõõdik näitas selgelt kompromissi madala FAPH-i seadistustega ja tõi esile `Kule`-variandi valideerimisvajaduse.” |
| `chapters/summary.tex:12` | „Töö kõige olulisem tulemus ei olnud ..., vaid ...” | Retooriliselt kaitsev. | „Töö kõige olulisem tulemus on hindamismetoodika täpsustamine koos uue mudeliversiooni ja tööahelaga.” |
| `chapters/summary.tex:18–20` | „Töö peamised piirangud ...”; „Need piirangud määravad ...” | Kokkuvõtte lõpp raamib töö piirangute kaudu. | Pealkirjata ümber pöörata: „Järgmised valideerimissammud on ...”; piirangute sisu esitada tegevusplaanina. |
| `chapters/summary.tex:22` | „kuid mitte juurutuskõlblikuks kuulutatud”; „piiranguna, mitte tulemusena” | Väga kaitsev lõpulause. | „v16c on tehniliselt hinnatud kandidaat, mille järgmine kontroll on külmutatud lävedega kasutajapiloot reaalses Korvo-2 seadmes.” |

## P1 — pealkirjad ja lõikude avaraam

| Asukoht | Praegune raaming | Soovitus |
|---|---|---|
| `chapters/second_chapter.tex:478` | `\section{FAPH-optimeeritud kontrollpunkti valiku piirangud}` | `FAPH-optimeeritud kontrollpunkti valiku mõju` / `Kontrollpunkti-FAPH kompromiss` |
| `chapters/second_chapter.tex:578` | `\section{Kasutajatesti tulemuste piirangud}` | `Kasutajatesti staatus ja järgmine valideerimiskiht` / `Reaalsete kõnelejate valideerimissamm` |
| `chapters/third_chapter.tex:15` | `\subsection{Andmestiku põhipiirangud}` | `Andmestiku katvus ja domeeninihe` |
| `chapters/third_chapter.tex:27` | `\section{Standardsete võrdlusaluste ebapiisavus reaalse kasutuse ennustamisel}` | `Standardsete võrdlusaluste ja kasutusolukorra lõhe` |
| `chapters/third_chapter.tex:38` | „mitte kinnitatud mustriga ... jääb vajalikuks” | „laiema valimiga kasutajatest kontrollib sama suunaerinevust järgmises valideerimiskihis.” |
| `chapters/third_chapter.tex:75` | „Mõju ei tohi siiski üle tõlgendada...” | `Agentpõhise arenduse mõju ja tõendusmaterjali eraldi roll` tüüpi positiivne avaus. |

## P2 — metoodika peatüki kaitsvad laused

| Asukoht | Praegune raaming | Soovitus |
|---|---|---|
| `chapters/first_chapter.tex:6` | „Demoulatus ... piiratud”; „ei ole tulemusväite tõestusbaasis” | „Demo kontrollib ühe nutipirni otsast-lõpuni stsenaariumi; mudeli tulemusväited põhinevad eraldi hindamiskomplektidel.” |
| `chapters/first_chapter.tex:9` | „Picovoice ... jäetakse võrdlusest välja, sest ... ei toeta...” | „Picovoice on kommertslik taustavõrdlus; empiiriline raamistikuvõrdlus keskendub avatud ja kohalikult treenitavatele lahendustele.” |
| `chapters/first_chapter.tex:20` | „ei piisa ainult tavalisest ...” | „mudeli hindamiseks eristab töö kolme andmeliiki...” |
| `chapters/first_chapter.tex:46` | „ei saa toetuda ainult lühikestele negatiivsetele klippidele” | „voogedastushindamine vajab lisaks pikki taustaheli lõike...” |
| `chapters/first_chapter.tex:77` | „ablatsiooni käesolevas töös ei tehtud” | „uurimisressurss suunati andmestiku ja hindamisahela parandustele; arhitektuuri vaikeseadistus fikseeriti.” |
| `chapters/first_chapter.tex:106` | „akna pikendamist ei testitud ... mitte empiiriliseks tõestuseks” | „1500 ms aken on selles töös fikseeritud vaikeseadistus; selle mõju hinnatakse teiste mõõdikute taustal.” |
| `chapters/first_chapter.tex:118` | „ei eraldata float32-ja-INT8 täpsuskaotust” | „kõik raporteeritud tulemused mõõdavad lõpliku INT8-mudeli käitumist, mis hõlmab kvantiseerimise mõju.” |
| `chapters/first_chapter.tex:124` | „Piloot ei ole mõeldud asendama...” | „Piloot lisab tehnilistele mõõdikutele reaalsete kõnelejate ja kasutusolukorra kihi.” |
| `chapters/first_chapter.tex:126` | „ei käsitleta statistilise jõuga ...” | „pilooti tõlgendatakse suunatud eristusvõime kontrollina laiade Wilsoni vahemikega.” |
| `chapters/first_chapter.tex:130` | „ei kasutata neid klippe ... treenimiseks” | „kasutajatesti heli kuulub esmalt hindamisandmestikku; treening toimub eraldatud andmestikel.” |

## P2 — tulemuste peatüki kaitsvad/negatiivsed raamingud

| Asukoht | Praegune raaming | Soovitus |
|---|---|---|
| `chapters/second_chapter.tex:127` | „mitte üldistust”; „kehtetud”; „mitte lihtsalt korrigeeritava vea hulka” | Säilitada sisuline rangus, aga lõpetada panusega: „andmelekkekontroll muutus tööahela keskseks kvaliteediväravaks.” |
| `chapters/second_chapter.tex:179` | „reaalsete uute kõnelejate kinnitus jääb edasiseks tööks” | „järgmine valideerimiskiht on reaalsete uute kõnelejate komplekt.” |
| `chapters/second_chapter.tex:186` | „ei ole usaldusväärne”; „mudel ei ole kunagi näinud”; „puudumiseni...” | Mõte jääb, aga positiivne järeldus ette: „usaldusväärne üldistushinnang vajab kõrvalejäetud komplekte ja pidevvoo kontrolli.” |
| `chapters/second_chapter.tex:208` | pikk lõpp: „hüpotees, mitte ...; jääb töö ulatusest välja” | Lühendada: „Tulemust käsitletakse hüpoteesina; kontrolli laiendab teine seade ja teine kõneleja.” |
| `chapters/second_chapter.tex:210` | „autor ... ei leidnud” | Kui jääb, muuta joonealuseks/otsingu märkuseks; põhitekstis rõhutada, et töö raporteerib asümmeetria eksplitsiitselt. |
| `chapters/second_chapter.tex:241` | „ei tõenda ühe katsega” | „ühe katse põhjal on see suunav tõend sihtkeelse negatiivmaterjali kasuks.” |
| `chapters/second_chapter.tex:243` | „mida käesolev töö ei tee” | „selle suunise järgmine kontroll on eraldi ablatsioonkatse.” |
| `chapters/second_chapter.tex:247` | „ei ole ... tõestanud”; „ei esita” | „käesolev töö käsitleb mahtu tõenäolise kitsaskohana ja kvantifitseerib mastaabivahe.” |
| `chapters/second_chapter.tex:290` | „ei saa esitada üldise FAPH-sihina” | „tulemus on ühe korpuse ja operatsioonipunkti punkthinnang ning demonstreerib suurusjärgu langust.” |
| `chapters/second_chapter.tex:292` | „ei tõenda tootmisvalmidust...” | „konsensus toimib diagnostilise kontrollina: madal FAPH saavutatakse tuvastamismäära ja fraasiselektiivsuse hinnaga.” |
| `chapters/second_chapter.tex:351` | „et lõputöö ei omistaks...” | „eristus hoiab põhjuslikud järeldused ühe muutujaga võrdluste juures.” |
| `chapters/second_chapter.tex:398` | „eesmärk ei ole ..., vaid ...” | „kaitsed muudavad järgmised tulemused kontrollitavaks ja ennetavad sama sildistusvea kordumist.” |
| `chapters/second_chapter.tex:428` | tabeli NB: „McNemar ... töö skoobist väljas” | Kui tabelis ruumi vaja, eemaldada või viia metoodika/statistika märkusse. |
| `chapters/second_chapter.tex:471` | „ei taga veel ...” | „v18 tulemused näitavad järgmise mõõdikukihi vajadust järjekorratundlikkuse jaoks.” |
| `chapters/second_chapter.tex:476` | „Praegu pole ükski ... vastanud” | „kombineeritud kriteerium eristab järgmise arendusetapi sihi.” |
| `chapters/second_chapter.tex:555` | „Tulemust ei saa ... tõlgendada” | „Tulemus kirjeldab madala-FAPH konsensuse käitumist: madal taustaheli FAPH tuleb koos madala Kõneleja D tuvastusega.” |
| `chapters/second_chapter.tex:560` | „Valim on väike ... mitte statistiline” | „kuulamiskontroll on kvalitatiivne ja näitab peamisi aktiveerumiskontekste.” |
| `chapters/second_chapter.tex:562` | „ei sobi ... jääb edasiseks tööks” | „põhjusliku mehhanismi kontrollimiseks sobib järgmine ablatsioon: ilma autori/MacBooki positiivideta treening või uus mikrofon/ruum.” |
| `chapters/second_chapter.tex:573` | „Käesolev töö seda väidet ... ei kontrolli” | „Hüpoteesi kinnitav järgmine katse on ...” |
| `chapters/second_chapter.tex:581` | „puudumisega ... üldistuspiirangutega”; viitab `scope-and-limitations` | Pöörata: „alaosa koondab, millise tõendusbaasi töö praeguseks annab ja milline kasutajatest selle peale lisandub.” |
| `chapters/second_chapter.tex:583` | „ei moodustatud”; „Tühje tulemusetabeleid siia ei lisata” | „Kasutajatesti protokoll on valmis; tulemused raporteeritakse pärast piisava osalejakogumi kogumist külmutatud lävedel.” |
| `chapters/second_chapter.tex:585` | „ei kata ... jääb tõendusulatusest välja” | „Kõneleja D komplekt katab `Kuule`-vormi; `Kule`-vorm on järgmise kasutajatesti eraldi mõõdetav dimensioon.” |

## P2 — arutelu peatüki kaitsvad/negatiivsed raamingud

| Asukoht | Praegune raaming | Soovitus |
|---|---|---|
| `chapters/third_chapter.tex:1` | „ei taga”; „ei sisaldanud” | Võib jääda, aga avas võiks olla positiivne teesi-lause: „töö keskne leid on mitmemõõtmelise hindamise vajadus.” |
| `chapters/third_chapter.tex:4` | „Ilma selle vahekontrollita...” | Pöörata: „kontrollkatse eraldas treeninguahela tehnilise toimimise keele- ja andmeriskidest.” |
| `chapters/third_chapter.tex:7` | „ei piisa väitest ...”; „mitte üldise võrdlusena” | „raamistikuvalik on projektispetsiifiline kompromiss...” |
| `chapters/third_chapter.tex:15` | „ei kõrvalda”; „ei asenda” | „sihtseadmega kogumine vähendab domeeninihke riski; kõnelejate mitmekesisust lisab järgmine andmekogum.” |
| `chapters/third_chapter.tex:38` | „mitte kinnitatud mustriga” | „suunanäitaja, mida kasutajatest saab kinnitada laiemal valimil.” |
| `chapters/third_chapter.tex:44` | „TTS-kõne ei sisalda...” | Tehniliselt OK, aga lõik võiks lõppeda positiivse panusega: hindamiskomplekti kõneleja-/allikalahusus. |
| `chapters/third_chapter.tex:56` | „ei sisalda ... ei kata” | Pöörata: „koduse keskkonna stiimulid moodustavad eraldi kattekihi, mida stsenaariumpõhine hindamisvoog lisab.” |
| `chapters/third_chapter.tex:65` | „töö ei väida selle leiutamist” | Eemaldada. Öelda: „töö esitab Androidi väliterminali konkreetse privaatsust hoidva teostusena...” |
| `chapters/third_chapter.tex:68` | „ei säilitata, ei ole ... võimalik” | Pöörata kompromissina: „privaatsust hoidev logimine eelistab sündmuste kogumist; reprodutseeritav mudelivõrdlus vajab paralleeljooksu.” |
| `chapters/third_chapter.tex:75` | „ei tohi üle tõlgendada”; „ei loo/asenda/lahenda” | Pöörata: „agentide peamine mõju on süsteemiehituse kiirendamine; tõendusmaterjali kvaliteet jääb andmekogumise ja valideerimise ülesandeks.” |
| `chapters/third_chapter.tex:96` | „praegu pole võimalik eristada...” | Pöörata: „kordusjooksud eraldavad sihtväärtuse mõju jooksu juhuslikkusest.” |
| `chapters/third_chapter.tex:101` | „ei saa neist otse järeldada” | „kasutajapiloot mõõdab latentsust, mikrofonigeomeetriat ja ootuste lõhet reaalses seadmes.” |
| `chapters/third_chapter.tex:103` | „ei ole esitatud”; „ei sobi enam” | „järgmine samm on kvantitatiivne openWakeWordi vastandite võrdlus ja uus true-held-out komplekt.” |

## OK / mitteprobleemsed negatsioonid

Need ei vaja tingimata muutmist, sest defineerivad andmeid, mudelikäitumist või eksperimendi loogikat, mitte ei vabanda töö ulatust:

- `chapters/first_chapter.tex:23` — „äratussõna puudub” negatiivsete klippide definitsioon.
- `chapters/first_chapter.tex:61` — FAPH-variantide „ei ole vastastikku võrreldavad” on tehniline täpsustus.
- `chapters/second_chapter.tex:47` — sarnased negatiivfraasid „ei ole äratussõna” on andmestiku definitsioon.
- `chapters/second_chapter.tex:407` — prefiksi-komplekt „ilma Kratt-iks jätkamata” on mõõdikudefinitsioon.
- `chapters/second_chapter.tex:422` — range positiivne poliitika „ilma ...” on andmefiltri definitsioon.
- `chapters/third_chapter.tex:63` — valeaktiveeringu definitsioon: sihtfraasi ei öeldud.

## Järjekord parandamiseks

1. **Sissejuhatus**: eemaldada `scope-and-limitations` lõik, STT/TTS negatiivne lause ja H1/H2 plokk või viia need metoodikasse/tulemustesse. Pärast seda peaks sissejuhatus taastuma umbes `ce3511e` mahule.
2. **Kokkuvõte**: muuta lõpp mitte piirangute nimekirjaks, vaid „tulemused + järgmised valideerimissammud”.
3. **Pealkirjad**: asendada `piirangud` ja `ebapiisavus` positiivsete „mõju / lõhe / valideerimissamm” pealkirjadega.
4. **Metoodika kasutajatesti osa**: „ei asenda” → „lisab eraldi valideerimiskihi”.
5. **Tulemused/arutelu**: jätta statistiline ausus alles, aga vahetada „ei tõenda / ei saa / ei tee” vormid „tulemus näitab / järgmine kontroll / mõõdetud ulatus” vormideks.
