---
source_prompt: /Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/04_Kontrollimine/Üldisem_tagasiside/Retsensent_karm.txt
prompt_type: evaluative
generated: 2026-05-07
---

# Retsensent (karm) -- bakalaureusetöö hinnang

Roll: kogenud, nõudlik retsensent. Töö: "Kuule Kratt" -- eestikeelne äratussõna mikrokontrolleril. Hindamine on teadlikult kriitiline, kohati kiuslik; see ei tähenda, et töö oleks halb -- lihtsalt et iga kategooria juures tuuakse esile ka see, mis _veel_ vajab parandamist.

------------------------------------------------------------

1.1 Probleemi aktuaalsus ja põhjendus
Punktid: 4/5
Kommentaar + soovitus: Probleem on selgelt sõnastatud (eesti keelt ei toeta openWakeWord ega Picovoice; eesti KKT on serveripoolne; mikrokontrolleril äratussõna on katmata) ja viidatud on konkreetsetele raamistikele ning korpustele. Aktuaalsus tugineb siiski peamiselt _saadavusele_ ("eesti keel puudub toetatud nimekirjast"), mitte mõõdetud kasutajavajadusele. › Soovitus: lisada sissejuhatusse 1--2 lauset selle kohta, kui suur on eesti nutikodu kasutajaskond ja millised on alternatiivid (pilvepõhised assistendid privaatsuse vaatest), et "miks see on probleem _just praegu_" oleks empiiriliselt kinnitatud, mitte ainult tehniliselt põhjendatud. Praegu jätab see kohati mulje, et probleemi tähtsust eeldatakse, mitte ei näidata.

------------------------------------------------------------

1.2 Seos õppekavaga ning töö liigi (uurimus / projekt / kombinatsioon) selgus
Punktid: 3/5
Kommentaar + soovitus: Töö liik on hübriidne -- osaliselt projekt (mudel + integratsioon ESPHome/HA), osaliselt uurimus (hindamisprotokoll, kolm valideerimisringi). Praeguses tekstis ei ole seda eksplitsiitselt välja öeldud; ülesandepüstitus räägib "lahendusest", peatükid 2--3 räägivad "metoodilisest panusest". Lugeja peab ise välja noppima, kumb on töö raskuskese. › Soovitus: lisada sissejuhatusse üks lause: "Käesolev töö on projekti- ja uurimustöö kombinatsioon, kus tehniline panus on äratussõna mudel ja selle integratsioon, uurimuslik panus aga väikese ressursiga keele hindamisprotokoll." Sama märkus võiks kajastuda kokkuvõttes. Ka õppekava (TalTech informaatika BSc) seos pole eksplitsiitselt mainitud -- selle võiks lisada vähemalt ülesandepüstitusse.

------------------------------------------------------------

1.3 Eesmärkide ja ülesannete täpsus
Punktid: 4/5
Kommentaar + soovitus: Eesmärk ("uurida, kuidas ehitada ja hinnata") on sõnastatud ja jagatud nelja alamküsimuseks. Operatsionaalsed sihid (FAPH < 1 ja recall ≥ 0,95) on selgelt väljas ning eraldatud universaalsetest standarditest -- see on tugevus. Karmi pilguga: alamküsimused on ebaühtlase tasemega -- esimesed kolm on metoodilised ("kuidas valideerida", "millist rolli mängivad", "kuidas eristada"), neljas on kvantitatiivne tulemustsiht. Selline asümmeetria ei luba neid lugeda kontrollnimekirjana. › Soovitus: kas ühtlustada (kõik alamküsimused metoodilised või kõik kvantitatiivsed) või ühe lausega selgitada, et alamküsimused jagunevad protsessi- ja tulemussihiks. Lisaks pole kuskil eksplitsiitselt loetletud mõõdetavat _ebaõnnestumiskriteeriumi_ ("kui FAPH > 5 või recall < 0,80, loeb töö selle juurutuskandidaadi tagasilükatuks") -- karm retsensent paneks seda tähele.

------------------------------------------------------------

2.1 Kohustuslikud osad (tiitelleht, sisukord, annotatsioonid, deklaratsioon, lisad) olemas ja korrektsed
Punktid: N/A
Kommentaar + soovitus: Hinnatav osa ei sisalda tiitellehe, sisukorra ega deklaratsiooni faili allikkoodi -- antud kontekstis on saadetud ainult sissejuhatus, kolm peatükki, kokkuvõte, kaks annotatsiooni ja ülesandepüstitus. Annotatsioonid (eesti ja inglise) on olemas ja eraldi failidena, ülesandepüstitus on korralikult vormistatud. Tiitellehte, deklaratsiooni ja lisade tegelikku korrektsust ei saa hinnata ilma neid nägemata. › Soovitus: enne esitamist veenduda, et TalTechi šabloon-vormistus (TUTthesis stiil) on järgitud, deklaratsioon plagiaadivabaduse kohta on lisatud ja lisad (kasutatud andmestiku üksikasjad, küsimustik, eetikakomitee dokumendid) on viidatud peatekstist.

------------------------------------------------------------

2.2 Peatükkide loogiline järgnevus ning tasakaal (teooria <-> praktika <-> tulemused)
Punktid: 3/5
Kommentaar + soovitus: Loogiline kaar on jälgitav: sissejuhatus › metoodika › tulemused (vaheülevaade) › arutelu › kokkuvõte. Ent tasakaal on tugevalt arutelu poole kaldu -- kolmas peatükk (arutelu) on tihe ja sisukas (kolme valideerimisringi muster, agentpõhise arenduse arutelu, lühitee-printsiip), samal ajal kui teine peatükk avaneb sõnadega "tegemist on teadlikult vahekokkuvõttega". Karmi pilguga: bakalaureusetöö, mille tulemuste peatükk on "vahekokkuvõte", näitab esitamiseks ebaküpset tulemustebaasi. › Soovitus: enne kaitsmist tuleb teine peatükk lõpuni viia ja sõnastus "vahekokkuvõte" välja võtta või seda väga selgelt põhjendada (nt "kasutajatesti tulemused on lisas X, kuna kogumine lõppes pärast töö esitamise tähtaega"). Lisaks on metoodika (1. ptk) ja arutelu (3. ptk) vahel sisuline kordus -- mitmemõõtmeline hindamisprotokoll on kirjeldatud kahes kohas. Kord väiksemalt metoodikas, kord pikalt arutelus on aktsepteeritav, kuid praegu jääb mulje, nagu töö raskuskese oleks "kuidas hinnata" pigem kui "kuidas teha".

------------------------------------------------------------

2.3 Peatükkide sisse- / väljajuhatuste ühtsus
Punktid: 3/5
Kommentaar + soovitus: Sissejuhatuses on selgelt esitatud töö struktuur ("metoodika peatükk kirjeldab ...; tulemuste peatükk võtab kokku ...; arutelu ja järelduste peatükk seob ...; kokkuvõte"). Iga peatükk algab lõiguga, mis viitab eelmise peatüki tulemustele -- see on tugevus. Karmi pilguga: peatükkide _lõpus_ pole sümmeetrilist kokkuvõtet ega üleminekut järgmise peatüki teemasse, ainult sissejuhatav lõik. Mõned alajaotused (3.1, 3.2) lõpevad järsku, ilma et oleks selgitatud, kuidas need järgmise alajaotusega seostuvad. › Soovitus: lisada iga peatüki lõppu üks lühike lõik ("käesolev peatükk näitas X-i; järgmine peatükk käsitleb Y-d, mis tugineb sellele"). Eriti vajalik 1. ja 2. peatüki vahel, kus üleminek metoodikalt vahepeal-tulemustele on mehaaniline.

------------------------------------------------------------

3.1 Tausta- ja kirjanduse ülevaate põhjalikkus
Punktid: 3/5
Kommentaar + soovitus: Kirjandus on kohal asjakohaselt: Chen 2014 (small-footprint KWS), Lopez-Espejo 2021 (deep KWS ülevaade), Park 2019 (SpecAugment), Choi 2021 (BC-ResNet), He 2016 (residual), Alvarez 2019 (SVDF), Park 2024 (TTS adversarial), Dubois 2020 (TV triggers), Schönherr 2022 (accidental wake), Apple 2017 (Hey Siri), Shrivastava 2021 (DNN-HMM optimisation). See on respektaabel valim. Karmi pilguga: töös puudub eraldi taustpeatükk -- kirjandus on hajutatud sissejuhatusse ja arutellu, mis raskendab hindamist. Eraldi probleem: viited hilisematele Apple/Google/Amazon süsteemidele on enamasti ühe viite sügavused, ilma et oleks tehtud süstemaatilist võrdlust selle töö lähenemisega. Eesti keele KKT-kirjandus on kohal vaid kahe viitega (Alumäe & TalTech ASR, Riigikogu stenogrammid) -- karm retsensent paluks lisaks vähemalt ühte eesti foneetika või akustika allikat (Eek, Asu, Lippus jt), mis põhjendaks äratussõna foneetilist disaini eesti keele kontekstis. › Soovitus: lisada üks alapeatükk "Taust ja seotud tööd" sissejuhatuse järele või laiendada sissejuhatust 1--2 lehekülje võrra, kus eesti keele foneetika, mikrokontrolleri-klassi KWS ja kaskaadarhitektuurid on loetletud süstemaatiliselt, mitte hajutatult.

------------------------------------------------------------

3.2 Allikate hulk, autoriteetsus, ajakohasus
Punktid: 4/5
Kommentaar + soovitus: Allikad on valdavalt autoriteetsed (Interspeech, Tensorflow whitepaper, ICASSP, JASA-tasemel statistikaviited Wilson 1927 ja Garwood 1936) ning enamus on viimase 5 aasta seest. Picovoice'i ja openWakeWord'i dokumentatsiooniviited on praktiliselt vajalikud, kuigi need on ettevõttepoolsed allikad. Karm pilk: mõned viited on ebaühtlase kvaliteediga ("sensory2024realworld" on tõenäoliselt blogipostitus -- see ei tohiks akadeemilise viitena seista samaväärse Park 2024 või Dubois 2020 kõrval). Lisaks on osa viiteid (esphome2026, homeassistant2026, openwakeword2026, picovoice-benchmark2026) dateeritud tulevikukuupäevaga -- kui need on veebiallikad, peab olema ka "viimati vaadatud" kuupäev kirjas. › Soovitus: viidete loetelus eraldada selgelt akadeemilised viited (Interspeech, ICASSP, JASA jt) ja tehnilised dokumentatsiooni-viited; kõikidel veebiviidetel peab olema "Viimati vaadatud: KK.PP.AAAA". Sensory blogile lisada kontekst (nt "kommertsfirma sisemise hindamise raport, mitte vastastikku eelretsenseeritud allikas").

------------------------------------------------------------

3.3 Analüüsi sügavus ja viitamistäpsus (eetika, plagiaadivabadus)
Punktid: 4/5
Kommentaar + soovitus: Analüüsi sügavus on selle töö üks tugevamaid külgi -- arutelu peatükk eraldab nelja erinevasse kategooriasse põhjused, miks standardsed võrdlusalused ei ennusta reaalset kasutust, ning seob need konkreetse kirjandusega (Park 2024, Dubois 2020, Schönherr 2022, MISP). Lühitee-printsiip on hästi formuleeritud ja tugineb nii enda katsetele kui ka kirjandusele. Karm pilk: viidatud kirjandus on mõnel pool _illustratiivne_, mitte rangelt põhjendav -- nt "Park et al. on näidanud, et TTS-andmetega treenitud mudelid kipuvad sünteesitud kõne peal näitama ülehinnatud tuvastamismäära" on kindel väide ühe viite peale, kuigi seda on näidatud pigem teatud arhitektuuride ja andmehulkade peal. Eetika-aspekti (kasutajatesti GDPR/eetikakomitee, kaheastmeline nõusolek) on käsitletud, aga peamiselt metoodikapeatükis. Plagiaadivabaduse deklaratsiooni hinnata ei saa, kuna seda materjali ei esitatud. › Soovitus: lisada eetika ja andmekasutuse kohta eraldi paragraaf (kas TalTechi eetikakomitee on andnud loa? kas sünteetiliste TTS-häälte kasutamine vastab Neurokõne litsentsile? mida tehakse kasutajatesti audioga pärast töö lõppu?). Kõikidesse võimalikku üldistusse hoiavad väited muuta tagasihoidlikumaks ("nagu on näidatud teatud arhitektuuride puhul" jne).

------------------------------------------------------------

4.1 Meetodi sobivus püstitatud eesmärkide saavutamiseks
Punktid: 4/5
Kommentaar + soovitus: Meetod -- microWakeWord raamistik MixedNet arhitektuuriga, kontrollkatse marvin-iga enne eesti keelt, mitmemõõtmeline FAPH-põhine hindamine -- on eesmärkidele sobiv ja teadlikult valitud. Eraldi tugevus on, et openWakeWord on kaasatud võrdlusraamistikuna, mitte ignoreeritud. Karm pilk: meetodi ja eesmärgi vahel on osaline ebakõla -- eesmärk on _juurutuskõlbliku mudeli_ saamine, kuid suur osa metoodikat keskendub _hindamisprotokolli ehitamisele_. Need ei ole vastuolus, aga töö positsioneeris end "esimeseks eesti äratussõna mudeliks", samal ajal kui keskne panus on "väikese keele hindamisprotokoll". Karm retsensent küsiks: kas meetod on disainitud pigem _mudelit treenima_ või _hindamist üles ehitama_? Praegune muster näitab teist. › Soovitus: kas ühtlustada eesmärgi sõnastust (lugeda ülaltoodud kahesust eksplitsiitseks) või valida üks fookus ja teist allutada. Praegu konkureerivad ülesandepüstituses öeldud "töötada välja eestikeelne äratussõna mudel" ja arutelu peatükis öeldud "töö üks peamisi panuseid ei ole esimene eesti äratussõna mudel ... vaid hindamise protokoll" -- need ei ole kokkupandavad ilma ümbersõnastamata.

------------------------------------------------------------

4.2 Valimi / andmekogumise / analüüsi kirjeldus ja põhjendus
Punktid: 3/5
Kommentaar + soovitus: Andmekogumise kirjeldus on tehniliselt põhjalik (1076 positiivset klippi ühelt kõnelejalt, Common~Voice eesti negatiivsed, MUSAN/VOiCES taustaheli, Korvo-2 sama-seadme negatiivsed). FAPH-mõõdiku eri variandid (raamistiku, taasmängu, välitingimuste, kasutajatesti taasmäng) on selgelt eristatud -- see on tugevus. Karm pilk: positiivsete kõneleja_valim on ühene -- _üks_ kõneleja, ülejäänu sünteetiliselt laiendatud. See on töö suurim sisuline piirang ja seda ei tohi peita: "kõnelejate mitmekesisuse probleem" on mainitud, aga selle mõju lõplikule mudelile pole kvantifitseeritud. Kasutajatest 20--30 osalejaga on _planeeritud_, mitte teostatud -- see on bakalaureusetöö esitamise hetkel suur risk. Andmestiku eetiline külg (kuidas saadi nõusolek, kas Korvo-2 negatiivsete salvestamine möödaminejailt on lubatud?) pole selgelt esitatud. › Soovitus: kvantifitseerida kõneleja-piiratuse mõju vähemalt ühe arvuga (nt "ühe kõneleja korral on tuvastusmäära ülempiir 95% intervalliga ± X"); lisada andmestiku eetiline lisa; selgitada, kas kasutajatest jõuab töö lõpliku versiooni sisse või ainult järelduste lisana.

------------------------------------------------------------

4.3 Meetodi rakenduse korrektsus
Punktid: 4/5
Kommentaar + soovitus: Rakendus on kohati _liigagi_ rangelt teostatud -- treening- ja testandmete disjointsuskontroll, andmelekke audit pärast esimese ringi avastust, kõrvalejäetud komplektid, statistilised intervallid (Wilson + Poisson-Garwood) -- see on bakalaureusetöö kohta rikkalik. Karm pilk: rangus ei tähenda _kindlat_ -- on mitmeid kohti, kus muutuvaid parameetreid (nt v6-residual ablatsioon vs. v16c kandidaat) ei kontrollita ühe-muutuja-korraga reegli järgi. Konkreetne näide: v7 oli "teadlikult süsteemitaseme variant, kus muudeti korraga ka sarnaste negatiivnäidete hulka" -- see on aus tunnistus, kuid samas tähendab, et SpecAugment'i ja sarnaste negatiivide eraldi mõju ei eraldata kuni v13a/v13b ablatsioonini. Kontrollpunkti FAPH-objektiivi ablatsioon (kolmas valideerimisring) on hästi dokumenteeritud, aga "FAPH-sihti lõdvendades paranes recall ainult osaliselt" on raporteeritud ilma konkreetsete arvudeta arutelu peatükis (need on tulemustes, aga lugejal on raske neid kokku panna). › Soovitus: lisada arutelu peatüki olulistesse väidetele konkreetne arv (nt "FAPH-sihti 1-lt 5-le lõdvendades kasvas recall A%-lt B%-le" mitte ainult "ainult osaliselt"). Tagada, et iga eksperimendi puhul oleks selgelt mainitud, kas tegemist on ühe-muutujaga ablatsiooniga või süsteemi-variandiga.

------------------------------------------------------------

5.1 Tulemuste piisavus ja selgus (graafikud, tabelid, tekst)
Punktid: 3/5
Kommentaar + soovitus: Tulemustabelid (mudeliversioonide võrdlus, õiglane võrdlus, kontrollpunktid, ekspertide konsensus) on olemas ja viidatud. Konkreetsed arvud (FAPH = 0,79; v6 25,4 › v6-residual 14,4; recall 92,8% jne) on käes. Karm pilk: ROC-kõveraid, score-jaotusi ja ajalisi graafikuid mainitakse tekstis, aga hinnatav materjal ei sisalda selgesti vormistatud joonist. Tabelite paigutus on tihe ja mõned on ainult abstraktselt viidatud (\ref{tab:expert-consensus}, \ref{tab:checkpoint-headline} jt) -- tegelikku tabelisisu ei näe. Üks põhitulemus -- konsensus 0,79 FAPH -- on raporteeritud _punktiväärtusena_, kuigi on tunnistatud, et "Poissoni 95% vahemik on lai". See on aus, kuid jätab esilehe-väite (FAPH < 1 saavutatud) ebakindlasse seisu. › Soovitus: lisada vähemalt üks selge ROC-kõvera joonis ja üks ajaline graafik (FAPH üle aja eri mudelitele); raporteerida iga olulise väite juurde 95% vahemik mitte ainult metoodikas, vaid ka kokkuvõttes ja annotatsioonis. Annotatsioonis on praegu raporteeritud "FAPH = 0,79" ilma vahemikuta -- see on klassikaline retsensendi-vastasus.

------------------------------------------------------------

5.2 Vastavus püstitatud eesmärkidele
Punktid: 3/5
Kommentaar + soovitus: Töö eesmärk oli (a) eestikeelse mudeli väljatöötamine, (b) süsteemi lõimimine ja (c) empiiriline valideerimine. Seisuga, mida hinnatakse: (a) on tehtud (mudelid v1...v16c, ekspertmudelid); (b) on osaliselt tehtud (ESPHome + voice_assistant integratsioon mainitud, kuid "lõplik compile/flash kontroll tehakse kasutajatesti aktiivse konfiguratsiooni peal" -- ehk pole _tõestatud_); (c) on osaliselt tehtud (tehniline mõõtmine valmis, kasutajatest plaanis). Karm pilk: kolmest eesmärgist on üks täielikult, üks osaliselt ja üks kavandatav. Kokkuvõte ja annotatsioon esitavad seda kohati liiga optimistlikult ("töö tulemus on reprodutseeritav toru ja empiiriline kirjeldus kompromissidest" -- see on tõsi, kuid eesmärk öeldi sõnadega "töötada välja ... mudel" mitte "kirjeldada kompromisse"). › Soovitus: kokkuvõttes eksplitsiitselt mainida iga kolme alameesmärgi täitmise staatus ("alameesmärk a -- täidetud; b -- osaliselt täidetud, lõplik integratsioonitestimine pooleli; c -- tehniline tasand täidetud, kasutuspõhine tasand kasutajatesti läbiviimisel"). See ei nõrgesta tööd; see lisab usaldust.

------------------------------------------------------------

5.3 Seos teooriaga, usaldusväärsus, praktiline väärtus
Punktid: 4/5
Kommentaar + soovitus: Seos teooriaga on tugev kohas, kus arutelu seob enda tulemused Park 2024, Dubois 2020 ja Schönherr 2022 leidudega -- see näitab, et töö ei ole tehtud isolatsioonis. Lühitee (shortcut learning) printsiibi sõnastamine on filosoofiliselt tugev ja võiks olla töö ühe peamise panusena selgelt välja toodud. Praktiline väärtus on olemas, aga piiratud: ühe äratussõnaga ühe keele projekt, üks põhikõneleja. Karm pilk: usaldusväärsuse hinnang sõltub kasutajatestist, mida pole tehtud. Praktilist väärtust seostatakse "ülekantavusega teistele väikeste keelte projektidele", aga seda ülekandmist ei ole demonstreeritud (nt teises keeles lühikatset, ühe-õhtusena). › Soovitus: lisada üks lõik konkreetsete _järgmiste sammude_ kohta, mis tõestaksid ülekandmist (nt soome või läti keele kontrollkatse mõne nädala-sammuga). Vähemalt kavandina, kui mitte teostatud kujul.

------------------------------------------------------------

5.4 Tuleviku-uuringute või rakenduse väljavaated
Punktid: 4/5
Kommentaar + soovitus: Edasiste suundade jaoks on eraldi alajaotus (kaskaadarhitektuur, võimalik neljas valideerimisring) ja need on hästi seotud nii enda tulemustega kui ka kirjandusega (Gruenstein 2017, Apple 2023, Sigtia 2020). "Aus piir: võimalik neljas ring" alajaotus on metoodiliselt eeskujulik -- näitab, et autor mõistab oma töö piiranguid. Karm pilk: edasised suunad on _tehnilised_ (kaskaad, kasutajatest, lapse-kõne), kuid pole selget ärilist või rakenduslikku perspektiivi -- nt "kuidas see jõuab Home Assistanti ametlikku jaotusse?", "kas avaldatakse mudel + andmestik avalikult?". Karm retsensent küsiks ka: "milline on plaan, kui kasutajatest näitab, et v16c FAPH > 1 reaalsetes oludes?". › Soovitus: lisada ühe lõigu jagu praktilist tegevuskava ("kui kasutajatest kinnitab, siis X; kui mitte, siis Y").

------------------------------------------------------------

6.1 Vastavus ülikooli vormistus- ja viitamisnõuetele
Punktid: N/A
Kommentaar + soovitus: Vormistuse korrektsust (TalTechi šabloon, leheküljenumeratsioon, sisukord, deklaratsioon) ei saa hinnata, kuna saadetud failid sisaldavad ainult peatükkide allikkoodi ja annotatsioone. LaTeX-allikas viitab \texttt{thesis.cls} stiilile (TUTthesis šabloon) ning kasutab BibTeXi viitamissüsteemi -- need on vormiliselt korrektsed. Viitamisstiil on numbriline ja järjepidev. › Soovitus: enne lõplikku esitamist tellida üks "vormistuskontrolli läbimine" -- TalTechi raamatukogu pakub tihti seda teenust; karm retsensent leiab tüüpiliselt 5--10 väikest vormistusprobleemi (joonise pealkirjade asukoht, tabelite formaat, viidete korduvus, tühje lehti).

------------------------------------------------------------

6.2 Keele korrektsus, terminoloogia täpsus, stiil
Punktid: 4/5
Kommentaar + soovitus: Eesti keel on heal tasemel, terminoloogia on järjepidev (äratussõna, taustaheli, tuvastamismäär, valevallandumine). Inglise terminite \emph{...} sissetoomine on süstemaatiline ja õpiku-laadne. Lauseehitus on kohati raske ja sisaldab mitut alamlauset -- bakalaureusetöö pikkades lõikudes on see vahel hea, aga vahel teeb lugemise pingutavaks. Karm pilk: mõned keeleotsused on ebaühtlased: "äratussõna", "äratusfraasi", "äratuse fraas", "sihtfraasi" -- need eksisteerivad kõrvuti. "Valevallandumine", "vääraktiveerimine", "valeaktiveering", "valekäivitus", "tahtmatu aktiveerimine" -- liiga palju sünonüüme, mis raskendab indekseerimist. Üks lause sissejuhatuses on 6 reaviivisajaline ja sisaldab kahte semikoolonit -- see on stilistiliselt kahtlane. › Soovitus: koostada terminite_glossaarium juba enne lõplikku esitamist (võib lisada lisana) ning käia üks redigeerimisring lihtsalt "lühenda lauseid" eesmärgiga. Inglise abstraktis on "Estonian wake-word detector" hea, aga kogu abstraktiks "the front-end component that determines the usability of the whole voice pipeline" on natuke laius -- see võiks olla teravam.

------------------------------------------------------------

6.3 Tabelite ja jooniste kvaliteet, nummerdus, lisade korrektsus
Punktid: N/A
Kommentaar + soovitus: Tabelite ja jooniste tegelikku visuaalset kvaliteeti ei saa hinnata, kuna LaTeX-iks renderdatud PDF-i pole esitatud. Allikkoodist nähtub, et tabelid kasutavad standardset \texttt{tabular} keskkonda ning numeratsioon on \texttt{label}-itega. Karm pilk: hinnatav allikkood viitab paljudele tabelitele ja joonistele (tab:full-comparison, tab:expert-consensus, tab:checkpoint-headline jt), millest mõned on ainult viidatud, mitte nähtavad. Lisade kohta puudub info -- kas on kavandatud andmekogumise lisa, küsimustiku lisa, kasutajatesti protokolli lisa? › Soovitus: tagada, et iga tabel on järjepideva formaadiga (sama veerge laius, ühilduvad ühikud, sama tüüpi usaldusvahemike esitusviis); lisad nummerdada A, B, C ja viidata neist peatekstist iga olulise andmevoolu juures.

------------------------------------------------------------

KOKKUVÕTLIK HINNANG (mitteformaalne)
Töö on bakalaureuse-tasemel sisukas, korralikult dokumenteeritud ja metoodiliselt teadvustatud. Selle peamine tugevus on hindamisprotokolli ehitamise dokumenteeritud avastusprotsess (kolm valideerimisringi, lühitee-printsiip), peamine nõrkus aga see, et töö "müüb" end ühe asjana (eesti äratussõna mudel), kuid "kohale toob" teise (väikese keele hindamisprotokoll) -- need ei ole vastuolus, aga lugejat juhitakse kahe erineva narratiivi vahel. Karm retsensent küsiks lisaks: kas kasutajatest jõuab töö sisse või jääb järelduse-tasandile, ja kas v16c on tegelikult juurutatud (compile + flash + reaalne kasutus) või ainult teoreetiliselt eelistatud kandidaat. Need kaks vastust määravad lõpuks, kas töö on _projekt + uurimus_ või ainult _uurimus + plaan_.

Mõõdetav koondkategooria-järgne keskmine (välja arvatud N/A): ${\sim}3{,}6 / 5$. See on kindel "väga rahuldav, üksikute väga heade aspektidega" hinne. Selle tõstmine "väga heaks" sõltub eelkõige (a) kasutajatesti tegelikust läbiviimisest, (b) v16c integratsiooni lõpetamisest ja (c) mõõdetava ebakõla kõrvaldamisest sissejuhatuse väite ja arutelu pearõhuvalu vahel.
