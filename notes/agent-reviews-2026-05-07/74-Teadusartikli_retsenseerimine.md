---
source_prompt: "/Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/07_Teadusartikkel/Teadusartikli_retsenseerimine.txt"
prompt_type: "Teadusartikli retsenseerimine"
generated: 2026-05-07
---

Retsensiooni raam: hindan esitatud materjali Q1-taseme teadusartikli käsikirja kriteeriumidel, kuigi artefakt on sisuliselt bakalaureusetöö, mitte valmis artiklimanuskript. See mõjutab hinnangut: lõputööna on protsessi dokumenteeriv ja enesekriitiline käsitlus väärtuslik, kuid teadusartiklina on tekst liiga pikk, iteratiivne, ebapiisavalt fokuseeritud ja lõpptõendus jääb mitmes keskpunktis lõpetamata.

1.1 Probleemi teaduslik olulisus ja aktuaalsus (kas on "hot topic"?)  
Punktid: 3/5  
Kommentaar + soovitus: Eesti keele lokaalne äratussõna tuvastus mikrokontrolleril on praktiliselt oluline ja väikese keeleruumi kontekstis asjakohane probleem. Käsikiri seob selle nutikodu, servaseadmete, Home Assistanti ja FAPH-põhise kasutatavusega. Q1 artikli jaoks jääb aga teaduslik olulisus osaliselt nišipõhiseks: ei ole piisavalt näidatud, miks just see juhtum muudab üldist teadmist äratussõnade, väikese ressursiga keelte või serva-AI kohta. Soovitus: sõnastada probleem mitte ainult eestikeelse prototüübi puudusena, vaid üldistatava uurimisprobleemina: kuidas hinnata väikese keele äratussõna olukorras, kus positiivseid kõnelejaid ja domeenispetsiifilisi negatiive napib.

1.2 Teaduslik uudsus (kas pakub uut teadmist/meetodit või ainult kordab vana?)  
Punktid: 2/5  
Kommentaar + soovitus: Töö tegelik tugevus on hindamisprotokolli iteratiivne täpsustamine: andmeleke, positiivsete reostus, prefiksi-vallandumised ja FAPH-optimeeritud kontrollpunkti lõks on hästi dokumenteeritud. Samas kasutatud meetodid ise — microWakeWord, SpecAugment, residuaalühendused, konsensus/kaskaad, FAPH — on teadaolevad lahendused ning käsikiri ei tõesta piisavalt, et pakutud protokoll on metoodiliselt uus võrreldes tööstusliku või akadeemilise KWS-praktikaga. Soovitus: eraldada uudsus selgelt tehnilisest ehitusest; esitada kompaktne väide, milline valideerimisprotokolli osa on madala ressursiga keele kontekstis uus, ning toetada seda süstemaatilise võrdlusega varasemate KWS hindamisprotokollidega.

1.3 Uurimislünga (research gap) selge määratlemine ja põhjendamine  
Punktid: 2/5  
Kommentaar + soovitus: Uurimislünk on sissejuhatuses tuvastatav: eesti ASR-ressursid on olemas, kuid eestikeelne avatud mikrokontrolleri-klassi äratussõna tugi on katmata. Probleem on selles, et lünga tõendus jääb narratiivseks. Käsikiri viitab kontrollitud otsingule TalTechNLP, ETIS-e ja Common Voice’i järgtööde lõikes, kuid artiklitasemel puudub reprodutseeritav otsingustrateegia, kaasamis-/välistamiskriteeriumid ja tabel, mis näitaks, mida täpselt ei leitud. Soovitus: lisada lühike süstemaatiline state-of-the-art otsinguprotokoll ja eristada kolm lünka: eesti äratussõna mudel, mikrokontrolleri juurutus ning väikese keele mitmemõõtmeline valideerimine.

2.1 Tiitli, abstrakti ja sisu vastavus (kas abstrakt peegeldab tegelikke tulemusi?)  
Punktid: 3/5  
Kommentaar + soovitus: Eesti- ja ingliskeelne abstrakt peegeldavad käsikirja viimast, ettevaatlikumat järeldust: ükski praegune mudel ei täida kõiki eesmärke ning peamine panus on hindamisprotokoll. See on ausam kui mõni tulemuste peatüki vahepealne tugevam väide sub-1 FAPH saavutamise kohta. Samas jääb abstrakt artikli mõttes liiga üldiseks: selles puuduvad põhinumbrite komplekt, valimite suurused, kõige olulisemad negatiivsed tulemused ja selge lõppotsus, kas süsteem on deploy-kõlblik. Soovitus: kirjutada abstrakt struktureeritult — probleem, meetod, andmed, võtmetulemused koos N ja FAPH väärtustega, peamine piirang ning järeldus, et tegemist on prototüübi/hindamismetoodikaga, mitte valideeritud lõppseadmega.

2.2 Artikli ülesehituse loogika (IMRaD või muu standardne struktuur)  
Punktid: 2/5  
Kommentaar + soovitus: Bakalaureusetööna on peatükid arusaadavad: sissejuhatus, metoodika, tulemused, arutelu ja kokkuvõte. Artiklimanuskriptina on struktuur aga liiga protsessipäevikuline. Tulemuste peatükk sisaldab pikki versioonilugusid v1–v18, auditiringe, sisemisi failiteid ja katsete ajalugu, mis hajutab keskse teadusliku argumendi. Soovitus: artikli jaoks ümber struktureerida tekst klassikalise IMRaD-kuju järgi: üks meetodite peatükk andmete/protokolli kohta, üks tulemuste peatükk 3–5 eeldefineeritud uurimisküsimusega, üks arutelu üldistatava panuse kohta ning kogu versioonilugu viia lisamaterjali.

2.3 Sissejuhatuse fookus ja järelduste konkreetsus  
Punktid: 3/5  
Kommentaar + soovitus: Sissejuhatus määratleb fookuse üsna selgelt: “Kuule Kratt”, ESP32-S3, lokaalsus, FAPH ja lähikõne recall. Järeldused on kiiduväärselt ettevaatlikud ning tunnistavad, et kasutajatesti ei ole veel tehtud ja v16c ei ole tootmiskõlblikkuse tõend. Puudus on selles, et eesmärgid ja lõppseis ei sulgu puhtalt: alguses seatud FAPH < 1 ja recall ≥ 0,95 siht ei saa lõpuks ühes mudelis täidetud, kuid seda ei formuleerita piisavalt terava “primary endpoint failed” järeldusena. Soovitus: lisada artikli lõppu ühemõtteline vastus igale uurimisküsimusele koos staatusega: täidetud, osaliselt täidetud või täitmata.

3.1 Tehnika taseme (State of the Art) ülevaate põhjalikkus ja kriitilisus  
Punktid: 2/5  
Kommentaar + soovitus: Käsikiri nimetab asjakohaseid tööriistu ja allikaid: microWakeWord, openWakeWord, Picovoice, Speech Commands, KWS/FAPH kirjandus, Apple’i kaskaadid ja mõned uuemad uuringud. Siiski on ülevaade pigem töö käigus vajalike komponentide kirjeldus kui kriitiline state-of-the-art süntees. Puudub süstemaatiline võrdlustabel, mis eristaks arhitektuure, andmemahtusid, sihtplatvorme, mõõdikuid ja loendusreegleid. Soovitus: lisada koondtabel varasematest wake-word/KWS süsteemidest ning eraldi kriitiline lõik, millised varasemad hindamised on käesoleva töö väitel ebapiisavad ja miks.

3.2 Viidete asjakohasus, kvaliteet ja kaetus (kas olulised konkureerivad tööd on mainitud?)  
Punktid: 2/5  
Kommentaar + soovitus: Viited on üldjoontes asjakohased, kuid nende kvaliteet on ebaühtlane: eelretsenseeritud artiklid, dokumentatsioon, GitHubi projektid ja vendor-benchmark’id on tekstis läbisegi. See on bakalaureusetöö praktilises kontekstis mõistetav, kuid Q1 artiklis ei saa dokumentatsiooniviiteid käsitleda samal tõendusastmel kui eelretsenseeritud uuringuid. Samuti ei ole esitatud piisavat tõendit, et kõik olulised väikese ressursiga KWS, personaliseeritud wake-word ja phrase-spotting tööd on kaetud. Soovitus: jagada allikad kategooriatesse — eelretsenseeritud teadus, avatud lähtekoodiga raamistikud, kommertsdokumentatsioon — ja teha nähtavaks, millised väited toetuvad millisele tõendusklassile.

3.3 Seosed varasemate uuringutega (kas on selge, mille poolest see töö erineb?)  
Punktid: 2/5  
Kommentaar + soovitus: Töö seob oma tähelepanekud mõistlikult varasemate nähtustega: degradatsiooni org, TTS-i üleoptimism, kaskaadid, FAPH-i loendusreegli probleemid ja partial-keyword negatiivid. Siiski jääb seos sageli illustratiivseks, mitte analüütiliseks. Näiteks öeldakse, et tulemused on kooskõlas Apple’i või Park et al. tähelepanekutega, kuid ei näidata rangelt, milline uus empiiriline panus lisandub. Soovitus: iga suurema tulemuse juures lisada “mida varasem töö ütles / mida meie kinnitame / mis on uus väikese keele mikrokontrolleri kontekstis” raamistik.

4.1 Uurimismeetodi sobivus ja teaduslik rangus (rigor)  
Punktid: 2/5  
Kommentaar + soovitus: Meetod on praktilise prototüübi jaoks sobiv ja sisaldab mitut head ranguse elementi: avalik kontrollkatse, disjointsuskontroll, FAPH, Wilsoni ja Poissoni usaldusvahemikud ning kontrollitud ablatsioonid residuaalühenduste ja SpecAugment’i kohta. Q1 artikli tasemel rikuvad rangust aga iteratiivsed, tagantjärele ümberdefineeritud katseperede, muutuvate lävede, väikeste valimite ja mitme samaaegselt muudetud teguri rohkus. Täismahus kasutajatesti pole. Soovitus: fikseerida üks lõplik protokoll enne mudelivalikut, defineerida primaarsed ja sekundaarsed mõõdikud ning käsitleda v1–v18 arengut eksploratiivse eelkatsetusena, mitte peamise kinnitava tõendusena.

4.2 Andmete ja protsessi kirjeldus (kas katset on võimalik kirjelduse põhjal korrata?)  
Punktid: 3/5  
Kommentaar + soovitus: Protsessi kirjeldus on ebatavaliselt detailne: nimetatakse skripte, andmekogumeid, lävesid, mudeliversioone, usaldusvahemike meetodeid, loendusreegleid ja mitmeid failiartefakte. See toetab reprodutseeritavust. Puuduseks on, et lugeja ei saa esitatud käsikirja põhjal täielikult taastada andmestiku täpseid manifeste, kõiki train/validation/test jaotusi, mudelifailide versioone ega kasutatud helikorpuste lõplikke filtreid. Soovitus: lisada artiklile reprodutseeritavuse lisa: andmestiku manifestide skeem, splitide kontrollsummad, lõplikud käsuread, Docker/conda keskkond ning selge märkus, milliseid privaatseid helisid ei saa avaldada ja kuidas neid asendada.

4.3 Valimi representatiivsus ja/või andmete kvaliteedikontroll  
Punktid: 1/5  
Kommentaar + soovitus: See on käsikirja üks põhinõrkusi. Töö ise tunnistab, et positiivsed näited pärinesid algselt kitsalt kõnelejate ringilt, suur osa laiendusest on TTS, kasutajatesti lõppandmestik puudub ning üldistused reaalsetele kõnelejatele põhinevad autoril, Kõneleja B-l ja ühel Kõneleja D komplektil. Positiivsete reostuse audit on tugev, kuid see tõendab ühtlasi, et varasem andmekvaliteet oli ebapiisav. Soovitus: enne artiklitasemel väiteid koguda sõltumatu, eelnevalt fikseeritud kõnelejavalim eri soo, vanuse, häälduse, kauguse ja müratingimustega ning raporteerida tulemused ilma treeningusse tagasisöötmiseta.

5.1 Tulemuste usaldusväärsus ja tõenduspõhisus (kas väited on andmetega kaetud?)  
Punktid: 2/5  
Kommentaar + soovitus: Tulemused on arvuliselt rikkalikud ja mitmes kohas ausalt ebakindlust näitavad, kuid peamine järeldus on negatiivne: ükski praegune mudel või kombinatsioon ei täida korraga recall’i, FAPH-i, sarnaste negatiivide, prefiksi- ja segiajamisjuhtumite nõudeid. Mõned tugevad väited, näiteks sub-1 FAPH saavutamine, on õiged ainult ühe korpuse, ühe operatsioonipunkti ja sageli madala recall’i hinnaga. Soovitus: teha tulemuste peatüki alguses “primary outcome table”, kus iga lõplik kandidaat hinnatakse sama külmutatud mõõdikukomplekti vastu; kõik varasemad iteratsioonid paigutada diagnostikaks.

5.2 Võrdlus olemasolevate lahendustega (benchmarking/comparison)  
Punktid: 2/5  
Kommentaar + soovitus: Sisemine võrdlus mudeliversioonide vahel on ulatuslik, kuid väline benchmarking jääb nõrgaks. Autor õigesti märgib, et microWakeWord, openWakeWord ja Picovoice tulemused ei ole eri korpuste, loendusreeglite ja andmemahtude tõttu otseselt võrreldavad. See ettevaatus on hea, kuid tulemuseks on, et käsikiri ei näita veenvalt, kus süsteem rahvusvahelise taseme suhtes paikneb. Soovitus: valida vähemalt üks avalik standardne hindamiskorpus ja üks täpselt kirjeldatud loendusreegel, millel hinnata nii enda mudelit kui võimaluse korral avatud baseline’i samas taasesitusraamis.

5.3 Tulemuste kriitiline analüüs ja töö piirangute (limitations) aus väljatoomine  
Punktid: 4/5  
Kommentaar + soovitus: See on käsikirja tugevaim osa. Autor dokumenteerib andmelekke, positiivsete reostuse, prefiksi-vallandumise, FAPH-optimeeritud kontrollpunkti lühitee ja kasutajatesti puudumise ebatavaliselt ausalt. Piiranguid ei peideta, vaid neist tehakse metoodiline panus. Punkt ei ole 5/5, sest kriitiline analüüs on laialivalguv ja kohati seguneb uute katsete kirjeldusega; lugejal on raske eristada lõplikke järeldusi tööpäeviku õppetundidest. Soovitus: koondada piirangud eraldi tabelisse “risk — kuidas tuvastati — kas lahendatud — allesjäänud mõju”.

5.4 Visuaalide (joonised, tabelid) informatiivsus ja kvaliteet  
Punktid: 3/5  
Kommentaar + soovitus: Tabelid on informatiivsed ja annavad palju mõõdikuid, sh usaldusvahemikud. Joonised nagu FAPH–recall operatsioonipunktide graafik ja DET-kõverad tunduvad sisuliselt asjakohased. Probleem on koormus: tabelid on väga tihedad, sisaldavad paljusid versioone ja mõõdikuid korraga ning osa võrdlustest on eksploratiivsed. Artikli lugeja vajab vähem, kuid otsustavamaid visuaale. Soovitus: alles jätta 3–4 põhijoonist/tabelit: andmevoog, lõplik mõõdikumaatriks, DET/FAPH–recall kompromiss ja vearežiimide tabel; ülejäänu viia lisasse.

6.1 Terminoloogia täpsus ja ühtsus  
Punktid: 3/5  
Kommentaar + soovitus: Terminoloogia on valdavalt arusaadav ning FAPH, FRR, recall, FPR, hold-out, streaming ja wake word on sisuliselt korrektselt kasutatud. Samas on eesti ja inglise terminid ebaühtlaselt segatud: “deploy”, “checkpoint”, “scripted offline”, “holdout”, “recall” ja “FAPH” esinevad läbisegi eestikeelsete vastetega. See ei ole kriitiline lõputöö prototüübis, kuid artiklis vähendab täpsust. Soovitus: lisada mõistete tabel ning valida iga termini jaoks üks eelistatud eestikeelne vaste ja sulgudes ingliskeelne vaste esmakasutusel.

6.2 Akadeemiline stiil ja loetavus (loogiline sidusus)  
Punktid: 2/5  
Kommentaar + soovitus: Tekst on üldiselt loetav, kuid akadeemilise artiklina liiga narratiivne ja kronoloogiline. Sõnastused nagu “kirjutamise hetkeks”, sisemiste skriptide ja failide pikad nimetused, versioonide ajalugu ning agentpõhise arenduse kõrvalteema annavad tööprotsessi läbipaistvust, kuid nõrgendavad teadusartikli fookust. Soovitus: eemaldada artikli põhitekstist arenduslugu ja sisemised artefaktinimed, säilitades ainult metoodiliselt vajalikud detailid; sõnastada tekst tulemuspõhiselt, mitte ajajoonena.

6.3 Vormistuslik korrektsus (ühikud, valemid, viitamisstiil)  
Punktid: 3/5  
Kommentaar + soovitus: LaTeX-vormistus, tabelid, viited ja mõõdikute ühikud on üldiselt kontrollitud muljega. Positiivne on usaldusvahemike meetodite nimetamine ja FAPH loendusreeglite eristamine. Samas on käsikirjas palju väga pikki tabeleid, makrodega tiitleid/abstraktide vormielemente, segamini koma- ja punktipõhiseid arvuvorminguid ning mitmeid “scripted offline” täpsustusi, mis vajavad ühtset vormistust. Soovitus: standardiseerida arvude esitus, defineerida kõik mõõdikud ühes kohas, kontrollida ristviiteid ning eraldada artikli põhitekstist lõputöö tehnilised vormielemendid.

Kokkuvõttev otsus Q1 teadusartikli käsikirjana: Reject / põhjalik ümberkirjutus enne uut esitamist.  
Kogupunktid: 43/90.  
Põhjendus: töö sisaldab väärtuslikku ja ausat metoodilist õppetundi väikese ressursiga äratussõna hindamisest, kuid artiklina ei ole see veel piisavalt fokuseeritud, lõplikult valideeritud ega sõltumatu valimiga tõendatud. Kõige olulisemad puudused on täismahus kasutajatesti puudumine, kõnelejate ja andmestiku piiratud representatiivsus, lõpliku mudeli ebaõnnestumine kõigi seatud mõõdikute samaaegsel täitmisel ning liiga protsessipõhine esitus. Bakalaureusetööna on materjal siiski sisukas prototüübi- ja hindamismetoodika dokumentatsioon, kui lõplikud väited hoitakse ettevaatlikud.