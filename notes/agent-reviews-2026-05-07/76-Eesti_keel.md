---
source_prompt: "/Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/08_Keeletoimetaja/Eesti_keel.txt"
prompt_type: "keeletoimetus / akadeemiline eesti keel"
generated: 2026-05-07
---

# Eesti keele toimetaja aruanne

## Ulatus ja tööviis

Lugesin läbi määratud peatükid, eestikeelse kokkuvõtte, eestikeelse lühikokkuvõtte ja ülesandepüstituse. Allpool on toimetaja märkused ja konkreetsed paranduskohad; lõputöö faile ei ole muudetud. Viiteid, URL-e, LaTeX-i käske ja `\texttt{...}`-kujulisi koodiidentifikaatoreid tuleks parandamisel säilitada.

## 1. Toimetaja kommentaarid korduvate keeleprobleemide kohta

1. **Inglise toorlaenud ja estonglish on tekstis läbivad.** Akadeemilises põhitekstis esinevad kujul „from-scratch kontrollkatse“, „baseline“, „public taustaheli“, „deploy-kandidaat“, „runtime-loogika“, „failure-režiim“, „benchmark“, „score-jaotused“. Soovitus: kasutada eestikeelseid vasteid ja jätta ingliskeelne termin vaid esmamainimisel sulgudesse, kui see on metoodiliselt vajalik. Näited: „baseline“ → „baasjoon“, „deploy-kandidaat“ → „juurutuskandidaat“, „runtime-loogika“ → „käitusloogika“, „failure-režiim“ → „tõrkerežiim“.

2. **Ülekasutatud postpositsioon „peal“ muudab stiili kõnekeelseks.** See kordub konstruktsioonides „andmestiku peal“, „klippide peal“, „seadme peal“, „kõneleja peal“, „mikrofoni peal“. Enamasti on täpsem „põhjal“, „korral“, „abil“, „kaudu“, „andmetel“ või kohakääne. Näited: „testklippide peal saadud head skoorid“ → „testklippide põhjal saadud head tulemused“; „MacBook~Pro mikrofoni peal“ → „MacBook~Pro mikrofoni abil“.

3. **Kokku-lahkukirjutus ja võõrnimede käänamine vajavad ühtlustamist.** Korduvad vormid „ESP32-S3 põhine“, „\texttt{microWakeWord} põhine“, „\texttt{voice\_assistant} liidese“, „MixedNet arhitektuur“, „testi-komplekt“, „kahe-sõnaline“. Soovitus: „ESP32-S3-põhine“, „\texttt{microWakeWord}il põhinev“ või „\texttt{microWakeWord}i raamistik“, „\texttt{voice\_assistant}-liides“, „MixedNeti arhitektuur“, „testikomplekt“, „kahesõnaline“.

4. **Mitmes lõigus on liiga pikad laused ja nominaalstiil.** Eriti sissejuhatuses ja tulemuste peatükis kuhjuvad ühte lausesse metoodika, näide, viide ja järeldus. Näiteks `introduction.tex` rida 7 võiks jagada 3–4 lauseks. See ei muudaks sisu, kuid vähendaks lugeja koormust ja aitaks rõhutada töö põhiväidet.

5. **Terminoloogia kõigub.** Sama nähtust nimetatakse „valevallandumiseks“, „valeaktiveeringuks“, „valekäivituseks“, „vääraktiveerimiseks“ ja „valehäireks“; `recall` on kord „tuvastamismäär“, kord „saagis“. Soovitus: valida põhitekstis läbivalt „valevallandumine“ ja „tuvastamismäär“, vajaduse korral lisada mõõdikutähis sulgudes.

## 2. Prioriseeritud parandustabel

| Prioriteet | Fail / rida | Praegune tekstikatke | Soovitatud parandus | Märkus |
|---|---:|---|---|---|
| Kõrge | `chapters/introduction.tex`:5 | „ESP32-S3 põhine seade“ | „ESP32-S3-põhine seade“ | Kokku-lahkukirjutus. |
| Kõrge | `chapters/introduction.tex`:5 | „ESPHome tarkvarakihi kaudu“ | „ESPHome'i tarkvarakihi kaudu“ | Võõrnime omastav kääne. |
| Kõrge | `chapters/introduction.tex`:5 | „\texttt{microWakeWord} raamistikku“ | „\texttt{microWakeWord}i raamistikku“ | Käänata nimi, mitte jätta nimetavasse. |
| Kõrge | `chapters/introduction.tex`:5 | „\texttt{voice\_assistant} liidese“ | „\texttt{voice\_assistant}-liidese“ | Lisand + põhisõna sidekriipsuga. |
| Kõrge | `chapters/introduction.tex`:7 | „testklippide peal häid tulemusi“ | „testklippide põhjal häid tulemusi“ | „Peal“ ei ole siin täpne. |
| Kõrge | `chapters/introduction.tex`:7 | Üks pikk lause alates „Seetõttu tuleb lisaks…“ kuni viiteni | Jagada lauseks: FAPH-i vajadus; mõõdiku definitsioon; kodukasutuse põhjendus; näited. | Loetavus ja akadeemiline selgus. |
| Kõrge | `chapters/first_chapter.tex`:4 | „ESP32-S3 põhine arendusplaat“ | „ESP32-S3-põhine arendusplaat“ | Sama muster kogu töös ühtlustada. |
| Kõrge | `chapters/first_chapter.tex`:6 | „järeldamine jookseb päris mikrokontrolleril“ | „järeldamine toimub mikrokontrolleris“ | Vältida IT-kõnekeelt „jooksma“. |
| Keskmine | `chapters/first_chapter.tex`:13 | „Võrdlus viiakse läbi neljal teljel“ | „Võrreldakse neljal teljel“ | Kantseliitliku „läbi viima“ asendus. |
| Kõrge | `chapters/first_chapter.tex`:39 | „Memory-mapped file lähenemine“ | „Mälukaardistatud faili kasutamine“ | Toorlaen põhitekstis. |
| Keskmine | `chapters/first_chapter.tex`:55–57 | „false rejection rate“, „false accepts per hour“, „threshold'id“ | „valenegatiivsete määr“, „valevallandumiste arv tunnis“, „läved“ | Ingliskeelsed terminid võib jätta sulgudesse esmamainimisel. |
| Keskmine | `chapters/first_chapter.tex`:64–69 | „runtime-loogika“, „scripted offline“, „field“, „user-study replay“ | „käitusloogika“, „skriptitud võrguväline taasesitus“, „välitingimused“, „kasutajatesti taasesitus“ | Tabeli mõisted eestindada; koodinimesid mitte muuta. |
| Kõrge | `chapters/first_chapter.tex`:127 | „flash-mällu“, „ESPHome manifest“, „compile/flash kontroll“ | „välkmällu“, „ESPHome'i manifest“, „kompileerimise ja seadmesse laadimise kontroll“ | Toorlaenud ja võõrnime kääne. |
| Kõrge | `chapters/second_chapter.tex`:14 | „from-scratch kontrollkatse … sihtsõna peal“ | „algusest peale treenitud kontrollkatse … sihtsõna põhjal“ | Toorlaen + „peal“. |
| Kõrge | `chapters/second_chapter.tex`:21 | „cutoff/threshold ja score-jaotustega“ | „lävede ja skoorijaotustega“ | Eesti vaste piisab; vajaduse korral inglise termin sulgudesse. |
| Kõrge | `chapters/second_chapter.tex`:27 | „run'is“, „evaluatsiooniseadistust“ | „katsejooksus“, „hindamisseadistust“ | Toorlaenud. |
| Kõrge | `chapters/second_chapter.tex`:39–40 | „\texttt{marvin} baseline“; „public taustaheli ja speech-negative korpused“ | „\texttt{marvin}-baasjoon“; „avalikud taustaheli- ja kõnepõhiste negatiivnäidete korpused“ | Segakeelne loetelu. |
| Kõrge | `chapters/second_chapter.tex`:158, 167 | „disjoint“, „test set“, „tripwire“ | „mittekattuv“, „testikomplekt“, „kontrolltõke“ | Põhitekstis eestikeelsed vasted; funktsiooninimi jätta muutmata. |
| Keskmine | `chapters/second_chapter.tex`:171 | „Streaming FAPH … moving-average'iga“ | „Voogedastus-FAPH … liugkeskmisega“ | Mõõdikutähis jääb samaks, kirjeldus eestikeelseks. |
| Kõrge | `chapters/second_chapter.tex`:210 | „disjointness checki test setide vs treeningandmete vahel“ | „treening- ja testandmete mittekattuvuse kohustuslikku kontrolli“ | Segakeelne ja ebaeestipärane konstruktsioon. |
| Keskmine | `chapters/second_chapter.tex`:247, 251 | „corpus'tel“, „Corpus“ | „korpustel“, „Korpus“ | Võõrsõna käänamine ja tabelipealkiri. |
| Keskmine | `chapters/second_chapter.tex`:392 | „Sub-1 FAPH on saavutatav“ | „FAPH alla 1 on saavutatav“ | Inglise eesliide pole vajalik. |
| Kõrge | `chapters/second_chapter.tex`:464 | „voice-cloning-iga genereeritud“ | „häälekloonimisega genereeritud“ või „hääleklooni abil genereeritud“ | Selge eestikeelne vaste. |
| Kõrge | `chapters/second_chapter.tex`:504 | „tunnusekäo (\emph{feature cache}) sõrmejälge … fingerpriniti“ | „tunnusevahemälu (\emph{feature cache}) sõrmejälge … sõrmejälje“ | „tunnusekäo“ näib olevat kirjaviga; „fingerprint“ eestindada. |
| Kõrge | `chapters/second_chapter.tex`:521 | „failure-režiimi … deploy-kandidaat … eksplitsiitselt“ | „tõrkerežiimi … juurutuskandidaat … selgesõnaliselt“ | Kolm toorlaenu ühes lauses. |
| Kõrge | `chapters/second_chapter.tex`:556 | „deploy-kõlbmatu“; „praeguses pooltes“ | „juurutuskõlbmatu“; kontrollida ja asendada nt „praeguses andmepoolis“ või „praeguses seadistuses“ | Teine katke näib olevat sisuline/kirjaviga; vajab autori kinnitust. |
| Kõrge | `chapters/second_chapter.tex`:584 | „sisemise validatsiooni tunnetel“ | „sisemise valideerimiskogumi põhjal“ või „sisemise valideerimise andmetel“ | „Tunnetel“ on tõenäoline kirjaviga. |
| Keskmine | `chapters/third_chapter.tex`:1 | „klippide peal saadud head skoorid“ | „klippide põhjal saadud head tulemused“ | „Skoor“ sobib mõõdiku nimena, kuid siin on „tulemus“ loomulikum. |
| Kõrge | `chapters/third_chapter.tex`:46 | „lävel cutoff\,$\geq$\,0,97“ | „lõikelävel $\geq$\,0,97“ või lihtsalt „lävel $\geq$\,0,97“ | Eestikeelne + vältida topeltütlust. |
| Keskmine | `chapters/third_chapter.tex`:56–58 | „streaming-konteksti“, „Streaming-režiimis“ | „voogedastuskonteksti“, „Voogedastusrežiimis“ | Ühtlustada terminiga „voogedastus“. |
| Keskmine | `chapters/third_chapter.tex`:75 | „ajaliste põhitõe märgenditega“ | „ajaliste tõemärgenditega“ või „ajapõhiste põhitõemärgenditega“ | Praegune rektsioon on kohmakas. |
| Kõrge | `chapters/third_chapter.tex`:83 | Väga pikk lause alates „Eelnevalt kirjeldatud…“ | Jagada vähemalt kaheks lauseks: tööriistastiku jõukohasus; agentpõhise arenduse roll. | Loetavus. |
| Keskmine | `chapters/summary.tex`:3 | „\texttt{microWakeWord} põhist“ | „\texttt{microWakeWord}il põhinevat“ | Kokku-lahkukirjutus ja kääne. |
| Kõrge | `chapters/summary.tex`:5 | „disjointsuskontroll“ | „mittekattuvuse kontroll“ | Eesti vaste on selgem. |
| Kõrge | `chapters/summary.tex`:7 | „saagise“, „Common Voice eesti keele hold-out kõnel“ | „tuvastamismäära“, „Common Voice'i eestikeelsel kõrvalejäetud kõnel“ | Terminoloogiline ühtlus + toorlaen. |
| Keskmine | `misc/abstract-estonian.tex`:1 | „mille sihiks on fraasi … tuvastamine ESP32-S3 klassi seadmel lokaalselt“ | „mille siht on tuvastada fraas … lokaalselt ESP32-S3 klassi seadmel“ | Eestipärasem sõnajärg. |
| Keskmine | `misc/abstract-estonian.tex`:3 | „\texttt{microWakeWord} põhine“; „disjointsuskontroll“ | „\texttt{microWakeWord}il põhinev“; „mittekattuvuse kontroll“ | Sama muster nagu kokkuvõttes. |
| Keskmine | `ylesandepystitus.tex`:65 | „ESPHome + \texttt{home\_assistant}/\texttt{voice\_assistant} liidesega“ | „ESPHome'i ja \texttt{home\_assistant}/\texttt{voice\_assistant}-liidese abil“ | Kääne ja sidekriips. |
| Keskmine | `ylesandepystitus.tex`:68 | „fraasile ,,Kuule Kratt''“ | „fraasi \enquote{Kuule Kratt} jaoks“ | Jutumärkide ühtlus üle töö. |
| Keskmine | `ylesandepystitus.tex`:83 | „muuhulgas“; „MixConv kihtidel põhinevat mixednet arhitektuuri“ | „muu hulgas“; „\texttt{MixedConv}-kihtidel põhinevat \texttt{MixedNeti} arhitektuuri“ | Õigekiri + nimekuju ühtlus. |
| Keskmine | `ylesandepystitus.tex`:86 | „\texttt{voice\_assistant} liidese abil“ | „\texttt{voice\_assistant}-liidese abil“ | Lisand + põhisõna. |

## 3. Lühike toimetatud näidis abstrakti/kokkuvõtte stiiliks

Alljärgnev on **näidis**, mitte kogu abstrakti ega kokkuvõtte tervikredaktsioon. Sisu, viited ja tehnilised nimetused on jäetud muutmata.

### Eestikeelse abstrakti alguse näidis

Käesoleva bakalaureusetöö eesmärk on uurida, kuidas luua ja hinnata eestikeelset äratussõna tuvastust piiratud ressursiga nutikodu mikrokontrolleril. Töö keskmes on projekt \enquote{Kratt}, mille siht on tuvastada fraas \enquote{Kuule Kratt} lokaalselt ESP32-S3 klassi seadmel ilma pilveteenust kasutamata. Töö praktiline lähtekoht on väikeste keelte häälassistentide toe puudujääk: eestikeelse kõnetuvastuse jaoks leidub juba sobivaid mudeleid, kuid kohalik äratussõna tuvastus määrab suuresti kogu hääljuhtimise kasutatavuse.

Töös rekonstrueeriti ja täpsustati \texttt{microWakeWord}il põhinev treeningu- ja hindamistoru ning valideeriti seda avaliku \texttt{Speech Commands} andmestiku kontrollkatsega. Esialgne klipitasemel hindamine andis negatiivsete näidete andmelekke tõttu eksitavalt optimistliku pildi. Selle riski maandamiseks koostati sõltumatud kõrvalejäetud testikomplektid, lisati treeningandmete mittekattuvuse kontroll ning võeti keskseks voogedastushindamise mõõdikuks FAPH ehk valevallandumiste arv tunnis.

### Kokkuvõtte probleemse lõigu näidis

Korrigeeritud hindamine näitas, et mudelivalik sõltub tugevalt optimeeritavast omadusest. Mõned mudeliversioonid saavutasid parema tuvastamismäära uue kõneleja või seadme korral, teised madalama FAPH-i või tugevama sarnaste negatiivnäidete eristuse. Üksiku mudeli puhul ei õnnestunud neid eesmärke täielikult ühendada. Seetõttu katsetati töö praktilise laiendusena ka spetsialiseeritud ekspertmudelite konsensust, mis vähendas valevallandumisi märgatavalt ja saavutas Common Voice'i eestikeelsel kõrvalejäetud kõnel FAPH~$=$~0{,}79, kuid tegi seda tuvastamismäära arvelt.
