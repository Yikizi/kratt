---
source_prompt: "/Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/07_Teadusartikkel/Retsensiooni_alusel_paranduste_soovitamine.txt"
prompt_type: "retsensiooni_alusel_paranduste_soovitamine"
generated: 2026-05-07
---

# Retsensiooni alusel paranduste soovitamine: kohaldatavuse märkus ja tegevusplaan

## Kohaldatavuse piirang

Algne viip eeldab kolme sisendit, mida siin ei ole antud: tegelikud retsensioonid, sihtväljaanne või -konverents ning praktilised piirangud, nagu tähtaeg ja mahupiirang. Seetõttu ei ole võimalik koostada kommentaaripõhist vastust kujul "Retsensent X, kommentaar Y" ega hinnata, millised parandused on konkreetse väljaande nõuete suhtes vältimatud. Samuti ei ole lubatud välja mõelda saadud retsensiooni.

Allolev plaan on seega **mitte vastus tegelikule retsensioonile**, vaid parim pingutus bakalaureusetöö praeguse teksti põhjal: tõenäolised akadeemilise lugeja või kaitsmiskomisjoni kriitikad, nende prioriteet ning kopeerimisvalmis eestikeelsed tekstilõigud, millega töö väiteid täpsustada.

## 1. Parandust vajavad punktid

### 1.1. Ühtlusta töö põhiväide: prototüüp ja hindamisprotokoll, mitte valmis juurutatav äratussõna

* **Seotud märkus:** tõenäoline kriitika, mitte saadud retsensioon: töö sissejuhatuses ja eesmärgipüstituses kõlab kohati lubadus luua kasutuskõlblik mudel, kuid tulemused ja kokkuvõte näitavad, et ükski praegune mudel ei täida korraga kõiki kriteeriume.
* **Prioriteet:** 10/10
* **Põhjendus ja strateegia:** See on kõige olulisem kaitstavuse küsimus. Kui töö väidab lõplikku lahendust, ründab lugeja kohe kasutajatesti puudumist, prefiksi-FPR-i ja tuvastamismäära/FAPH kompromissi. Kui töö väidab reprodutseeritavat hindamisprotokolli ja prototüüpi, muutuvad samad tulemused töö tugevuseks.
* **Juhis autorile:** Täpsusta sissejuhatuse panuse lõiku, abstrakte ja kokkuvõtet sama sõnastusega: töö ei tõenda valmis tootmiskvaliteediga mudelit, vaid esitab metoodika ja empiirilise kompromisside kaardi. Väldi väljendeid, mis jätavad mulje lõplikust kasutusvalmidusest.
* **Uus tekstilõik:**
  > Käesoleva töö tulemusi tuleb tõlgendada prototüübi ja hindamisprotokolli, mitte lõpliku tootmiskvaliteediga äratussõna lahendusena. Eksperimendid näitavad, et eestikeelse fraasi \enquote{Kuule Kratt} lokaalne tuvastamine ESP32-S3 klassi seadmele suunatud mudeliga on tehniliselt teostatav, kuid ükski praegu hinnatud üksikmudel ega mudelikombinatsioon ei täida samaaegselt kõiki operatsionaalseid kriteeriume: kõrget tuvastamismäära eri kõnelejatel, madalat FAPH-i pidevas helivoos ning piisavat eristust prefiksi-, pööratud järjekorra ja sihtfraasiga sarnaste negatiivnäidete suhtes. Seetõttu on töö peamine panus metoodiliselt kontrollitud treeningu- ja hindamistoru ning riskirežiimide empiiriline kaardistus.

### 1.2. Vasta uurimisküsimustele selgelt ja eraldi

* **Seotud märkus:** tõenäoline kriitika: tekstis on palju katseid ja versioone, kuid lugeja peab ise tuletama, milline on vastus algsele uurimisküsimusele ja alamküsimustele.
* **Prioriteet:** 10/10
* **Põhjendus ja strateegia:** Kaitsmisel või retsenseerimisel on otsene küsimus: kas eesmärk saavutati? Praegune tekst sisaldab vastuse osi, kuid need on jaotunud mitmesse peatükki.
* **Juhis autorile:** Lisa tulemuste või arutelu peatüki lõppu lühike tabel või alapeatükk, mis seob iga sissejuhatuses nimetatud alamküsimuse konkreetse tulemusega. Eriti oluline on vastata FAPH < 1 ja tuvastamismäära \(\geq\) 0,95 sihile eitavalt või tingimuslikult.
* **Uus tekstilõik:**
  > Sissejuhatuses seatud operatsionaalsele sihile saab vastata tingimuslikult. Treeningu-, ekspordi- ja hindamistoru valideeriti ning sõltumatud kõrvalejäetud komplektid muutsid tulemused varasemast usaldusväärsemaks. Samas ei saavutatud praeguste mudelitega konfiguratsiooni, mis täidaks korraga FAPH < 1, vähemalt 0,95 tuvastamismäära eri kõnelejatel ja madala prefiksi- ning segiajamis-FPR-i. Alla ühe valeaktiveeringu tunnis jõudnud konsensusmudelid tegid seda tuvastamismäära arvelt; kõrge tuvastamismääraga mudelid jäid omakorda liiga tundlikuks prefiksi- või segiajamisjuhtumitele. Seega on töö vastus põhiküsimusele: lokaalne eestikeelne äratussõna on selles raamistikus ehitatav ja hinnatav, kuid praegune tõendus ei kinnita veel üldkasutuseks sobivat lõppmudelit.

### 1.3. Too kasutajatesti puudumine varem ja selgemalt piiranguna välja

* **Seotud märkus:** tõenäoline kriitika: ülesandepüstitus lubab kasutajapõhist valideerimist, kuid tulemuste peatükis öeldakse, et 20--30 osalejaga kasutajatesti lõppandmestik puudub.
* **Prioriteet:** 9/10
* **Põhjendus ja strateegia:** See on suur väline valiidsuse risk. Parim strateegia ei ole puudust varjata, vaid vähendada töö nõuet: kasutajatest on järgmine samm, mitte juba täidetud tõend.
* **Juhis autorile:** Lisa sissejuhatusse või metoodika lõppu märkus, et töö praeguses versioonis on kasutajatest planeeritud, mitte põhitõend. Kokkuvõttes ära esita kasutuskõlblikkust laia kasutajaskonna suhtes.
* **Uus tekstilõik:**
  > Planeeritud kasutajatest on käesolevas versioonis töö järgmine valideerimiskiht, mitte lõplike väidete alus. Seetõttu ei üldistata tulemusi kogu kasutajaskonnale ega väideta, et mudel toimib usaldusväärselt eri vanuse, häälduse, aktsendi ja koduse helikeskkonnaga kasutajatel. Reaalsete kõnelejate kohta tehtavad järeldused piirduvad olemasolevate kõrvalejäetud komplektidega ning nende eesmärk on eeskätt näidata hindamisprotokolli toimimist.

### 1.4. Paranda sissejuhatuse struktuurikirjeldus ja panuse loetelu, et need vastaksid tegelikule tööle

* **Seotud märkus:** tõenäoline kriitika: sissejuhatuse lõpus kirjeldatakse tulemuste peatükki peamiselt `marvin` kontrollkatsena, kuid tegelik tulemuste peatükk käsitleb v1--v18 mudeleid, andmeleket, positiivsete andmete reostust, prefiksi-FPR-i ja kontrollpunkti valikut.
* **Prioriteet:** 9/10
* **Põhjendus ja strateegia:** Kui sissejuhatus lubab üht tööd ja peatükid teevad teist, jääb tekst lõpetamata muljega. Parandus on puhtalt tekstiline ja kõrge mõjuga.
* **Juhis autorile:** Asenda sissejuhatuse viimane lõik peatükkide kirjeldusega, mis vastab praegusele sisule. Täpsusta ka panust: mudel on prototüüp või kandidaat, metoodika on põhipanus.
* **Uus tekstilõik:**
  > Töö on üles ehitatud järgmiselt. Metoodika peatükk kirjeldab kasutatud raamistikke, andmeliike, mudeliarhitektuuri, FAPH-põhist voogedastushindamist ning kasutajatesti kavandatud protokolli. Tulemuste peatükk esitab treeningu- ja hindamistoru valideerimise, eestikeelsete mudeliversioonide võrdluse, andmelekke ja positiivsete andmete kvaliteediprobleemide auditid ning mitme mõõdikuga kontrollpunkti- ja konsensuskatsed. Arutelu peatükk tõlgendab neid tulemusi väikese ressursiga keele äratussõna arenduse vaatenurgast ning sõnastab, miks töö põhipanus on mitmemõõtmeline hindamisprotokoll, mitte lõpliku mudeli kasutusvalmidus.

### 1.5. Lisa mõõdikute ja lävede register

* **Seotud märkus:** tõenäoline kriitika: FAPH-i, FPR-i, tuvastamismäära ja lävede väärtused esinevad eri kohtades eri operatsioonipunktidel, mistõttu lugejal on raske aru saada, millised arvud on omavahel võrreldavad.
* **Prioriteet:** 8/10
* **Põhjendus ja strateegia:** Töö tugevus on mõõtmine, kuid mõõtmiste rohkus võib muutuda nõrkuseks. Üks kokkuvõttev register vähendab segadust ilma eksperimente muutmata.
* **Juhis autorile:** Lisa metoodika lõppu või tulemuste algusse tabel, mis defineerib iga kasutatud mõõdiku, andmestiku, läve, FAPH-i variandi ja võrdluse eesmärgi. Eraldi märgi, et 0,97, 0,995 ja 0,997 operatsioonipunktid ei ole otse võrreldavad.
* **Uus tekstilõik:**
  > Kõik järgnevad tulemused on võrreldavad ainult sama hindamiskomplekti, sama läve ja sama FAPH-i loendusreegli korral. Seetõttu eristatakse töös klipi-tasemel tuvastamismäära, sihtfraasiga sarnaste negatiivnäidete FPR-i, prefiksi- ja segiajamis-FPR-i ning skriptitud taasmängu FAPH-i. Läved 0,97, 0,995 ja 0,997 tähistavad eri operatsioonipunkte; ühe läve juures saadud paremusjärjestust ei tõlgendata automaatselt teise läve juures kehtivana. Kui tabelites võrreldakse mudeleid, tuleb võrdlust lugeda üksnes vastava tabeli läve ja andmestiku kontekstis.

### 1.6. Koonda tulemuste peatükk uurimisloogika järgi, mitte ainult kronoloogiliseks mudelipäevikuks

* **Seotud märkus:** tõenäoline kriitika: mudeliversioonide pikk kronoloogia võib varjutada töö põhijärelduse ja teha teksti raskesti hinnatavaks.
* **Prioriteet:** 8/10
* **Põhjendus ja strateegia:** Praegune versioon sisaldab palju väärtuslikku infot, kuid lugejal võib kaduda põhiliin. Tugev akadeemiline struktuur eristab põhiteksti, diagnostikat ja lisaandmeid.
* **Juhis autorile:** Hoia põhitekstis kolm auditiringi ja nende järeldused; liiguta liigne versiooniloend, tööjada numbrid, sisemised failiteed ja üksikasjalikud vahetulemused lisasse või lühenda neid. Iga alapeatüki alguses sõnasta üks küsimus ja lõpus üks vastus.
* **Uus tekstilõik:**
  > Tulemuste peatüki lugemiseks on kasulik eristada kolme valideerimisringi. Esimene ring näitas, et klipi-tasemel FPR ei olnud usaldusväärne, kui testandmed kattusid treeningandmetega. Teine ring näitas, et isegi sõltumatu FAPH ja sarnaste negatiivnäidete FPR ei kata prefiksi- ja fraasitäielikkuse vigu. Kolmas ring näitas, et ühe mõõdiku, näiteks taustaheli FAPH-i, järgi valitud kontrollpunkt võib saavutada hea numbri, kaotades samal ajal äratusfraasi tuvastamismäära. Need kolm ringi moodustavad töö keskse tulemuse: hindamisprotokolli tuleb laiendada iga kord, kui reaalajas käitumine paljastab uue mõõtmata riskirežiimi.

### 1.7. Asenda või põhjenda sisemised artefaktiviited

* **Seotud märkus:** tõenäoline kriitika: tekst viitab sisemistele failidele ja tööjada numbritele, mida lõputöö lugeja ei saa kontrollida.
* **Prioriteet:** 7/10
* **Põhjendus ja strateegia:** Sisemised artefaktid on kasulikud reprodutseeritavuse jaoks, kuid akadeemilises tekstis peavad nad olema kas lisas, avalikus repositooriumis või lühidalt kirjeldatud meetodina.
* **Juhis autorile:** Jäta põhiteksti alles ainult need failinimed, mis on vajalikud meetodi mõistmiseks. Kui artefaktid pole avalikult kättesaadavad, sõnasta need kui autori töölogi, mitte kontrollitav allikas. Kui need on lisas, viita lisale.
* **Uus tekstilõik:**
  > Auditi detailid põhinevad projekti töölogidel ja skriptide väljunditel, mida kasutati andmestiku seisundi rekonstrueerimiseks. Põhitekstis esitatakse neist ainult metoodiliselt olulised järeldused: milline andmeallikas oli probleemne, kuidas probleem mudeli käitumist mõjutas ja milline kontroll lisati kordumise vältimiseks. Failiteede ja üksikute tööjooksude täielik loetelu kuulub reprodutseeritavuse lisasse, mitte põhiargumendi tõendusena põhiteksti.

### 1.8. Lisa andmehalduse ja privaatsuse alapeatükk

* **Seotud märkus:** tõenäoline kriitika: töö kasutab autori ja teiste kõnelejate häälenäiteid, sünteetilisi kloone ning võimalikku kasutajatesti, kuid privaatsuse ja nõusoleku käsitlus võiks olla ühes kohas selgem.
* **Prioriteet:** 7/10
* **Põhjendus ja strateegia:** Hääleandmed on tundlikud. Selge andmehaldus vähendab eetilist riski ja toetab töö praktilist usaldusväärsust.
* **Juhis autorile:** Lisa metoodikasse lühike alapeatükk andmete pseudonüümimise, heli säilitamise, toorsalvestuste avaldamata jätmise, nõusoleku ja sünteetiliste andmete kasutamise kohta. Ära lisa uusi fakte; kasuta ainult seda, mis töö tekstis juba olemas või mida autor saab tõendada.
* **Uus tekstilõik:**
  > Kõneandmete kasutamisel järgiti põhimõtet, et avalikus töös ei seostata heliklippe tuvastatavate isikutega. Eraandmetega kõnelejad on tekstis pseudonüümitud ning toorsalvestuste avaldamist ei käsitleta töö vältimatu osana. Kasutajatesti kavandatud nõusolekumudel eristab tehniliste tulemuste kasutamist ja heliklippide säilitamist: minimaalne nõusolek võimaldab pseudonüümseid mõõtetulemusi, eraldi helinõusolek aga lühikeste märgendatud WAV-klippide analüüsi. Selline eristus on vajalik, sest äratussõna arenduses on heli korraga tehniline mõõtmisandmestik ja isiku hääle biometriline jälg.

### 1.9. Pehmenda uudsuse ja tööstusvõrdluse väiteid

* **Seotud märkus:** tõenäoline kriitika: väited esimese eestikeelse äratussõna või tööstuslike süsteemidega samasse suurusjärku jõudmise kohta võivad tunduda liiga tugevad, kui otsing ja võrdluskorpused on piiratud.
* **Prioriteet:** 7/10
* **Põhjendus ja strateegia:** Töö ei pea oma väärtuse näitamiseks esitama absoluutset esmasusväidet. Piisab ettevaatlikust väitest, et autorile teadaolevalt puudub otsene võrreldav avaldatud süsteem ja töö annab kohaliku protokolli.
* **Juhis autorile:** Lisa iga absoluutse väite juurde piirang: otsinguruum, korpuste mitte-võrreldavus ja see, et tööstuslikud näitajad on kontekst, mitte otsene võrdlus.
* **Uus tekstilõik:**
  > Autorile teadaolevalt ei ole avaldatud otseselt võrreldavat eestikeelset mikrokontrolleri-klassi äratussõna uuringut, kuid seda ei käsitleta absoluutse esmasusväitena. Võrdlus ingliskeelsete ja tööstuslike süsteemidega annab ainult suurusjärgulise konteksti, sest korpused, loendusreeglid, treeningandmete maht ja sihtfraaside foneetiline eristuvus erinevad. Seetõttu ei väida töö, et esitatud mudel on nendega otseselt samaväärne; väide piirdub sellega, et sarnaseid mõõdikuid saab rakendada ka väikese ressursiga eesti keele kontekstis.

### 1.10. Täpsusta ESP32-S3 ja Home Assistanti lõimimise tõendatuse astet

* **Seotud märkus:** tõenäoline kriitika: tekstis on kohati tugev praktilise juurutuse lubadus, kuid kokkuvõttes on öeldud, et v16c jääb kandidaadiks kuni eraldi ESPHome + `voice_assistant` valideerimiseni.
* **Prioriteet:** 6/10
* **Põhjendus ja strateegia:** Riistvaraline teostatavus ja tegelik seadmetest ei ole sama asi. Täpsus kaitseb tööd üleväidete eest.
* **Juhis autorile:** Eralda kolm taset: mudeli maht ja kvantiseerimine; tehniline integreeritavus ESPHome/Home Assistanti kaudu; lõplik seadmel valideeritud kasutus. Kui viimane pole tehtud, ütle seda selgelt.
* **Uus tekstilõik:**
  > ESP32-S3 sihtplatvormi kohta eristatakse käesolevas töös mälumahu põhjal hinnatud teostatavust ja lõplikku seadmel valideeritud kasutust. Kvantiseeritud mudelid mahuvad suurusjärgu poolest ESP32-S3 klassi seadmele ning ESPHome/Home Assistanti liides annab praktilise lõimimisraja. See ei ole siiski samaväärne väitega, et konkreetne lõppkonfiguratsioon on tervikuna seadmel kasutusvalmis. Lõplik juurutusväide eeldab eraldi kontrolli tegeliku mudeli, läve, töömälu, latentsuse ja koduse helikeskkonna kohta.

### 1.11. Paranda terminoloogiat ja vähenda tarbetut inglise-eesti segakeelt

* **Seotud märkus:** tõenäoline kriitika: tekst sisaldab mitmel pool ingliskeelseid toorlaene, kuigi lõputöö on eestikeelne.
* **Prioriteet:** 6/10
* **Põhjendus ja strateegia:** Keeleline täpsus mõjutab töö professionaalset muljet. Tehnilised koodinimed võivad jääda inglise keelde, kuid üldmõisted peaksid olema eestikeelsed.
* **Juhis autorile:** Tee kogu tekstis terminoloogiline otsing ja asendus. Soovituslikud asendused: `pipeline` -> töötlustoru; `benchmark` -> võrdluskatse või võrdlusalus; `baseline` -> lähtevõrdlus või baasjoon; `deploy-kandidaat` -> juurutuskandidaat; `hard negative` -> sihtfraasiga sarnane negatiivnäide; `recall` -> tuvastamismäär või saagis; `threshold/cutoff` -> lävi. Koodiparameetrid jäta muutmata.
* **Uus tekstilõik:**
  > Terminoloogiliselt kasutatakse töös edaspidi läbivalt eestikeelseid üldmõisteid: \enquote{töötlustoru} treeningu ja hindamise sammude kohta, \enquote{võrdluskatse} avaliku kontrollülesande kohta, \enquote{lävi} mudeli otsustuspiiri kohta ning \enquote{juurutuskandidaat} mudeli kohta, mida kaalutakse seadmel kasutamiseks. Ingliskeelsed nimetused säilitatakse ainult raamistikunimedes, andmestike pealkirjades ja koodiparameetrites, kus tõlge halvendaks üheselt mõistetavust.

### 1.12. Lisa koondatud piirangute peatükk enne kokkuvõtet

* **Seotud märkus:** tõenäoline kriitika: piirangud on tekstis olemas, kuid hajutatud; lugeja võib pidada mõnda nõrkust autorile märkamata jäänuks.
* **Prioriteet:** 5/10
* **Põhjendus ja strateegia:** Kui piirangud on koondatud ja ausalt sõnastatud, muutuvad need kontrollitud teaduslikuks raamiks, mitte ootamatuks puuduseks.
* **Juhis autorile:** Lisa arutelu lõppu alapeatükk "Piirangud". Too välja vähemalt kasutajatesti puudumine, kõnelejate vähesus, ühe äratusfraasi piirang, FAPH-korpuste piiratud kestus, TTS-i üleesindatus ja lõpliku seadmetesti piirang.
* **Uus tekstilõik:**
  > Töö piirangud on järgmised. Esiteks ei asenda olemasolevad kõrvalejäetud komplektid sõltumatut 20--30 osalejaga kasutajatesti. Teiseks on positiivne kõnelejate mitmekesisus piiratud ning osa hindamisest tugineb sünteetilisele või kloonitud kõnele. Kolmandaks käsitletakse ainult üht äratusfraasi, mistõttu tulemusi ei saa automaatselt üldistada teistele eestikeelsetele fraasidele. Neljandaks annavad mõnetunnised FAPH-rajad kasuliku, kuid statistiliselt piiratud pildi harvade valeaktiveeringute kohta. Viiendaks ei ole lõplikku juurutusväidet võimalik teha enne, kui valitud mudelikonfiguratsioon on tervikuna kontrollitud sihtseadmel ja tegelikus koduses helikeskkonnas.

## 2. Vastulaused ja punktid, mida ei tohiks üle parandada

Kuna tegelikke retsensioone ei esitatud, ei ole alljärgnevad vastused mõeldud saadud retsensendi märkustele vastamiseks. Need on võimalikud kaitse- või kaaskirjavastused olukordadeks, kus lugeja nõuab midagi, mida praeguse töö ulatus ei kata.

### 2.1. Täismahus kasutajatesti puudumine

* **Seotud märkus:** võimalik kriitika, mitte tegelik retsensioon: töö peaks tõendama toimimist 20--30 sõltumatu kasutajaga.
* **Miks mitte parandada ainult tekstis:** kui andmeid pole kogutud, ei tohi kasutajatesti tulemusi teeselda ega asendada üksikute autori-lähedaste kõnelejatega.
* **Soovituslik vastus:**
  > Nõustun, et sõltumatu kasutajatest on lõpliku kasutusvalmiduse hindamiseks vajalik. Käesolevas versioonis ei käsitleta kasutajatesti tulemusi põhitõendina, sest lõppandmestik ei ole moodustatud. Seetõttu on töö väited piiratud prototüübi, hindamismetoodika ja olemasolevate kõrvalejäetud komplektide tulemustega. Kasutajatest on sõnastatud järgmise valideerimiskihina, mitte juba saavutatud tulemusena.

### 2.2. Porcupine'i või teiste suletud süsteemide otsene eestikeelne võrdlus

* **Seotud märkus:** võimalik kriitika: töö peaks võrdlema mudelit kommertslike äratussõna süsteemidega.
* **Miks mitte parandada ainult tekstis:** lõputöö tekstis toodud info järgi ei toeta lähim suletud lähtekoodiga võrdluspunkt eesti keelt ega võimalda sama äratusfraasi samal viisil treenida. Otsene võrdlus oleks seetõttu eksitav.
* **Soovituslik vastus:**
  > Kommertslike süsteemidega otsene kvantitatiivne võrdlus ei oleks käesolevas töös metoodiliselt samaväärne, sest nende treeningandmed, toetatud keeled, mudelid ja hindamiskorpused ei ole võrreldavad. Seetõttu kasutatakse neid ainult kontekstina, mitte väitena, et esitatud mudel on nendega samadel alustel parem või halvem. Töö keskne võrdlus toimub avatud lähtekoodiga ja reprodutseeritavate töötlustorude piires.

### 2.3. Ainult FAPH-i optimeerimine lõppmudeli valikuks

* **Seotud märkus:** võimalik kriitika: vali lihtsalt madalaima FAPH-iga mudel.
* **Miks mitte parandada:** töö tulemused näitavad, et madal FAPH võib tekkida ülikonservatiivse mudeli tõttu, mis jätab äratusfraasid tuvastamata. Selline parandus halvendaks lõppeesmärki.
* **Soovituslik vastus:**
  > Madalaim FAPH ei ole iseseisvalt piisav valikukriteerium. Kontrollpunkti-FAPH katsed näitasid, et FAPH-i agressiivne vähendamine võib valida mudeli, mis on taustahelil vaikne, kuid kaotab reaalsete kõnelejate tuvastamismäära. Seetõttu tuleb lõppmudelit hinnata komposiitselt: FAPH, tuvastamismäär, sarnaste negatiivnäidete FPR ning prefiksi- ja segiajamisjuhtumid peavad olema korraga nähtavad.

## 3. Kokkuvõttev paranduste järjekord

1. Sõnasta töö põhinõue ümber: hindamisprotokoll ja prototüüp, mitte valmis üldkasutatav mudel.
2. Vasta uurimisküsimustele eksplitsiitselt, sh FAPH < 1 ja tuvastamismäära sihi mittetäielik täitmine.
3. Too kasutajatesti puudumine varakult piiranguna välja.
4. Joonda sissejuhatus, abstraktid, tulemuste peatükk ja kokkuvõte sama väitetasemega.
5. Lisa mõõdikute ja lävede register ning täpsusta, millised tabelid on võrreldavad.
6. Lühenda kronoloogilist mudelipäevikut ja tõsta sisemised artefaktid lisasse.
7. Lisa andmehalduse, privaatsuse ja reprodutseeritavuse alapeatükid.
8. Pehmenda absoluutseid uudsus- ja tööstusvõrdluse väiteid.
9. Täpsusta riistvaralise lõimimise tõendatuse astet.
10. Tee terminoloogiline toimetamine kogu töö ulatuses.
