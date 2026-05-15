---
source_prompt: 04_Kontrollimine/Konkreetsed_vead/Sisu/Kontrolli_uurimisküsimuste_vastuseid.txt
prompt_type: evaluative
generated: 2026-05-07
---

# Uurimisküsimuste ja nende vastuste sidususe analüüs

## Sissekäik

Käesolev analüüs hindab töös sissejuhatuses sõnastatud põhiküsimuse ja nelja alamküsimuse ning töö sisus (eeskätt arutelu peatükk ja kokkuvõte) antud vastuste vastavust. Hinnatakse kuut paari: üks põhiküsimus ja viis alamküsimust (sissejuhatuse loend §9–§14 sisaldab nelja punkti, kuid need vastavad sisu peatükkide hindamisühikutele). Hindamise alus on otsene vastavus, tõenduspõhisus, ammendavus, sisemine kooskõla ja akadeemiline kvaliteet.

Hindamiseks kasutatakse järgmisi töö lõike: sissejuhatus (`introduction.tex` §9–§17), metoodika (`first_chapter.tex` §3–§7), arutelu (`third_chapter.tex` §3–§152) ja kokkuvõte (`summary.tex` §1–§11). Tulemuste peatüki konkreetset teksti käesolevas hindamises eraldi ei loetud, kuid arutelu ja kokkuvõte viitavad selle tabelitele (`tab:full-comparison`, `tab:expert-consensus`, `tab:checkpoint-headline`, `tab:fair-comparison-holdout`); seega on tulemuste peatükile tuginev tõendus käesolevas hindamises kaudne.

---

### Uurimisküsimus 1 (põhiküsimus): „Kuidas luua ja hinnata eestikeelset äratussõna tuvastust nii, et see oleks usaldusväärne nutikodu mikrokontrolleri piiratud ressursi tingimustes?"

**Autori vastus (kokkuvõte mitmest peatükist):** Töö pakub vastuseks (a) reprodutseeritava `microWakeWord` põhise treeningu- ja hindamistoru, mis on valideeritud avalikul `Speech Commands` kontrollkatsel (`marvin`); (b) FAPH-keskse pidevvoo hindamise koos sõltumatute kõrvalejäetud komplektide, fraasistruktuuri kontrollivate testide ja kolmes ringis arendatud kontrollpunkti valikukriteeriumiga (vt arutelu §`sec:eval-evolution`); (c) ESP32-S3 + ESPHome + Home Assistant integratsioonimustri ning piloodi aktiivse kandidaadi `v16c` (148 KB TFLite, ~107 KB tensor\_arena). „Usaldusväärne" on operatsionaalselt määratletud sihiks FAPH < 1 ja lähikõne tuvastamismäär ≥ 0,95.

**Hinne:** 7/10

**1. Analüüs**

* **Vastavus:** Osaliselt jah. Vastus käsitleb mõlemat verbi „luua" (toru, mudel, integratsioon) ja „hinnata" (FAPH, kõrvalejäetud komplekt, fraasistruktuur). „Usaldusväärne" on selgelt operatsionaliseeritud kahe kvantitatiivse sihi kaudu (FAPH < 1, recall ≥ 0,95). Küsimuse sõnastus „kuidas" eeldab protsessi/viisi kirjeldust, ja töö annab selle kolmeosalise panusena ning kolme valideerimisringi struktuurina. Üks kitsaskoht: küsimus seab sihiks „usaldusväärsuse mikrokontrolleri piiratud ressursi tingimustes", kuid ressursipiirangute (mälu, latentsus, vooluvool) kvantitatiivne sidumine tuvastuse kvaliteediga jääb vastuses õhukeseks — tensor\_arena ja mudeli maht on raporteeritud, kuid lõpliku compile/flash kontrolli pole tehtud (vt `subsec:quantization` lõpp ja kokkuvõtte §11).

* **Loogika ja tõendatus:** Vastus on loogiliselt põhjendatud ja seotud andmetega: FAPH = 0,79 (Common Voice ET hold-out, ekspertkonsensus), kontrollpunkti valiku ablatsioon, andmelekke audit. Loogikaahela kõige nõrgem lüli on selle, kas töö suudab põhiküsimuse juurde naasta ja vastata: „jah, sellised on tingimused, kus mudel on usaldusväärne". Praegu kõlab vastus pigem nii: „usaldusväärsuse hindamiseks on vaja kolmest ringist mitmemõõtmelist protokolli, ja meie töö dokumenteerib selle protokolli". See on metodoloogiline vastus, mitte juurutusotsus. Töö ise teadvustab seda lünka (vt `summary.tex` §11: „v16c jääb eraldi kandidaatiks, mitte tootmisse rakendatavaks tõendiks").

* **Kriitilised puudused:** (1) Põhiküsimuse formuleering sisaldab kahte verbi („luua" + „hinnata"), kuid vastus on tugevasti kaldu hindamise poole; loomise (mudeli enda) lõplik kvalitatiivne väide jääb tingimuslikuks. (2) „Mikrokontrolleri piiratud ressursi tingimustes" tõendus on eraldi alapeatükina (nt eraldi ressursimõõtmiste tabel — latentsus, RAM-i tippkasutus reaalsel seadmel, vooluvool) puudu või ei ole sissejuhatuses ega arutelus selgelt tagasi viidatud. (3) Põhiküsimuse vastus tuleks selgemalt sõnastada üheks lühikeseks lõpu-lõiguks, mis ütleb otse: „põhiküsimusele vastame järgmiselt: …". Praegu peab lugeja vastuse rekonstrueerima `summary.tex` ja `third_chapter.tex` mitmest osast.

**2. Soovitused parendamiseks**

* Lisa kokkuvõtte algusesse või arutelu lõpu lähedale eraldi lõik pealkirjaga „Vastus põhiküsimusele", mis koondab ühte 4–6 lause lõiku: (i) loomise viis (toru + mudel + integratsioon), (ii) hindamise viis (kolm ringi, FAPH, fraasistruktuur), (iii) saavutatud usaldusväärsuse tase võrreldes operatsionaalse sihiga (FAPH < 1, recall ≥ 0,95) ja (iv) kus see siht jääb täitmata (Kule-hääldus, kasutajatest pooleli).
* Sõnasta selgelt, kas töö väidab, et põhiküsimusele on vastatud konstruktiivselt („nõnda saab luua ja hinnata") või tingimuslikult („nõnda tuleks luua ja hinnata, kuid lõplik usaldusväärsuse tõendus ootab kasutajatesti"). Praegune sõnastus on kaldu teise tõlgenduse poole, kuid see pole eksplitsiitne.
* Tugevda mikrokontrolleri-tahku: viita selgelt §`subsec:quantization` arvudele (148 KB, ~107 KB tensor\_arena) põhiküsimuse vastuses ja maini, et lõpliku compile/flash valideerimise puudumine on teadvustatud piirang.

---

### Uurimisküsimus 2 (alamküsimus): „Kuidas valideerida treeningu- ja hindamistoru enne eestikeelse andmestiku juurde liikumist?"

**Autori vastus (kokkuvõte):** Toru valideeriti avaliku `Speech Commands` korpuse ja sihtsõna `marvin` peal otsast lõpuni kontrollkatsega (sissejuhatus §17; metoodika §`Avalikud andmekorpused`; arutelu `third_chapter.tex` §3–§6 „Miks avalik kontrollkatse oli vajalik"). Kontrollkatse kinnitas, et treening, eksport ja evaluatsioon töötavad terviklikult, ja eraldas treeningutoru tehnilised piirangud andmestikust või seadme mikrofonist tulenevatest probleemidest.

**Hinne:** 8/10

**1. Analüüs**

* **Vastavus:** Jah. Küsimus „kuidas" on saanud konkreetse protseduurilise vastuse: avaliku korpuse valik, kindla sihtsõna fikseerimine (`marvin`), otsast-lõpuni läbimäng (treening → eksport → evaluatsioon), seejärel ülejooks eestikeelsele andmestikule. Vastus on otseselt seotud küsimusega ja vastus on protseduuriline, mitte hinnanguline.

* **Loogika ja tõendatus:** Loogika on tugev: ilma kontrollkatseta oleks iga hilisem nõrk eestikeelne tulemus võinud näida andmestiku või mikrofoni probleemina (vt `third_chapter.tex` §4). Tõendus on sissejuhatuses ja arutelus seotud, kuid täpne tulemus (millised mõõdikud `marvin` peal saavutati) viitab tabelile `tab:full-comparison` ja `tab:fair-comparison-holdout` — tabelite konkreetset sisu ma käesolevas hindamises ei lugenud, mistõttu ei saa veenduda, kas need tabelid sisaldavad eraldi `marvin`-ridu. Kui sisaldavad, on tõendus täielik.

* **Kriitilised puudused:** (1) Vastus ütleb, mida tehti, aga mitte täpselt, millised olid valideerimise vastuvõtukriteeriumid (nt „torukvaliteet on aktsepteeritav, kui `marvin` saavutab FAPH < X taustaheli komplektil ja recall > Y"). (2) Kontrollkatse rolli on mõnevõrra tagant kohandatud: arutelu §6 ütleb, et kontrollkatse „muutis järgmises alampeatükis esitatud kahe raamistiku võrdluse tõeliseks samaväärsuse-testiks", mis on tagantjärele kontekstualiseering, mitte etteseatud kriteerium. See ei ole faktiviga, kuid akadeemiliselt veenvam oleks teine järjekord: enne kontrollkatset oleks pidanud sõnastama, mis tulemus loetakse „tõendiks, et toru on usaldusväärne".

**2. Soovitused parendamiseks**

* Lisa metoodikasse või arutelusse 2–3 lauset selle kohta, milline `marvin`-tulemus oleks loetud ebapiisavaks, st millise stsenaariumi korral oleks kontrollkatse näidanud, et toru ise on katki. See teeb valideerimisest tagantjärele-kinnituse asemel etteseatud testi.
* Vastust tugevdaks lühike eraldi tabel või lõik „kontrollkatse tulemused": `marvin` recall, FAPH, andmelekke kontroll. Kui see on juba tulemuste peatükis, viita siinkohal otseselt konkreetsele reale (mitte üldisele tabelile).

---

### Uurimisküsimus 3 (alamküsimus): „Millist rolli mängivad positiivsed, negatiivsed ja taustaheli-andmed äratussõna mudeli kvaliteedi hindamisel?"

**Autori vastus (kokkuvõte):** Metoodika peatükis (§`Andmeliikide eristamine`) on rollid eraldi sõnastatud: positiivsed klipid õpetavad sihtsõna akustilist kuju; negatiivsed klipid õpetavad, mida mitte pidada äratussõnaks; taustaheli salvestused võimaldavad hinnata FAPH pidevas helivoos. Arutelu peatükis on iga andmeliigi roll ka tõenduspõhiselt seotud eraldi riskiga: positiivsete klippide andmelekke ja prefiksi-õppimise audit (`sec:positive-audit`), negatiivsete klippide sarnaste fraaside risk (`sec:benchmark-gap` põhjus 3), taustaheli sõltumatu kõrvalejäetud komplekti audit (`sec:data-leakage`). Lisaks eristab töö nelja FAPH-i varianti, mis tugineb taustaheli rolli erinevatele tõlgendustele (raamistiku, scripted-replay, field, user-study replay).

**Hinne:** 9/10

**1. Analüüs**

* **Vastavus:** Jah, väga otse. Küsimus küsib „millist rolli", ja vastus annab kolmele andmeliigile selgelt erineva rolli, mis on seotud erinevate hindamismõõdikutega (recall vs. FPR/raskete negatiivide eristus vs. FAPH).

* **Loogika ja tõendatus:** Loogika on tugev ja kihiline. Esmane vastus (metoodika) seab põhimõtte, arutelu (kolm valideerimisringi, `sec:three-rounds`) näitab empiiriliselt, mida juhtub iga rolli vääriti hindamise korral: andmelekke korral mõõdab klipi-tasemel FPR mälu, mitte üldistust; positiivse klassi sildistusprobleem viib prefiksi õppimisele; taustaheli FAPH miinimumi sihtimine viib „lühitee"-mudelini, mis on vaikne ka päris kõnelejate suhtes. See on harukordselt tõenduspõhine vastus „millist rolli" küsimusele.

* **Kriitilised puudused:** (1) Üks väiksem lünk: vastus on rikkalik andmeliikide *negatiivsete* rollide poolelt (mida juhtub, kui rolli vääriti tõlgendada), kuid positiivse-rolli sõnastus on suhteliselt lihtne („õpetavad sihtsõna akustilist kuju"). Sümmeetria mõttes võiks öelda ka, et positiivsete klippide hindamisroll on hinnata recall'i (sh kõnelejate mitmekesisust ja TTS vs päris-kõneleja varieerumist) ning et see roll oli `v6` mudeli puhul ülehinnatud just sünteetilise testi tõttu. (2) Sõnastus „taustaheli-andmed" on sissejuhatuses mainitud üksuse kujul, kuid metoodika eristab nelja FAPH-varianti — alamküsimuse vastus võiks otseselt viidata sellele eristusele.

**2. Soovitused parendamiseks**

* Sõnastusta positiivsete andmete hindamisroll selgemalt: lisaks „õpetab" ka „võimaldab hinnata recalli reaalsetel ja sünteetilistel kõnelejatel ning eristada, kas mudel on saavutanud üldistuse või õppinud salvestusseadme allkirja".
* Sissejuhatuses võiks alamküsimuse vastusele viitavalt mainida, et taustaheli-andmete roll on lisaks FAPH mõõtmisele ka pidevvoo režiimi *eristamise* roll võrreldes klipi-tasandiga; see seob alamküsimuse 3 ja alamküsimuse 4 tihedamalt.

---

### Uurimisküsimus 4 (alamküsimus): „Kuidas eristada andmestikust tulenevaid probleeme toru tehnilistest piirangutest?"

**Autori vastus (kokkuvõte):** Eristus saavutatakse kolme mehhanismi kaudu: (a) avalik `marvin`-kontrollkatse fikseerib toru tehnilise korrektsuse enne eestikeelse andmestiku juurde liikumist (`third_chapter.tex` §3–§6); (b) sõltumatud kõrvalejäetud komplektid ja treeningandmete disjointsuskontroll eristavad andmelekke (toru kõrvalprobleem) tegelikust üldistusprobleemist (andmestik); (c) kolm valideerimisringi (`sec:three-rounds`) eristavad sammhaaval erinevat tüüpi probleeme — ring 1: andmeleke (toru); ring 2: positiivse klassi sildistusprobleem (andmestik); ring 3: kontrollpunkti valikukriteerium (treeningu/objektiivi-tasandi probleem).

**Hinne:** 8/10

**1. Analüüs**

* **Vastavus:** Jah. Küsimus küsib „kuidas", ja vastus annab kolm konkreetset tehnikat. Eristus „andmestikust tulenev" vs „toru tehniline" on töö üks kandvaid metodoloogilisi naelteljeid (vt `first_chapter.tex` §1).

* **Loogika ja tõendatus:** Loogika on rangelt järjestikune: ilma kontrollkatseta poleks andmelekke leidu olnud võimalik selgelt omistada andmestikule; ilma kõrvalejäetud komplektideta poleks olnud võimalik eraldada mälu üldistusest. Tõendus on tugev: konkreetne näide v6 MacBook Pro 50 FAPH vs Common Voice ET FPR 0,4% on toodud sissejuhatuses ja tulemuste peatüki tabelite kaudu.

* **Kriitilised puudused:** (1) Vastus ei ütle eksplitsiitselt, et osa probleeme on *segapärased* — nt residuaalühenduste mõju (`v6-residual` 25,4 → 14,4 FAPH) on samaaegselt arhitektuuri ja andmestiku-vastandlike interaktsioonide ilming. Praktiliselt ei saa alati öelda „see on andmestik" või „see on toru" — vahel on probleem nende ristumises. Vastus võiks seda piiri tunnistada. (2) Kolmas valideerimisring (kontrollpunkti valikukriteerium) ei ole otseselt „andmestik vs toru" eristus, vaid pigem „treeningu objektiiv vs hindamise lai katvus" eristus. Vastuse loogiline raam võib muutuda hägusemaks, kui ringi 3 kategoriseerida sama eristuse alla.

**2. Soovitused parendamiseks**

* Lisa arutelusse või kokkuvõttesse 1–2 lauset, mis tunnistavad, et kõik probleemid pole puhtalt eraldatavad: nt residuaalühendus-tulemus näitab, et arhitektuuri muutus mõjutab seda, kuidas andmestiku piirangud avalduvad. See teeb metoodilise väite ausamaks.
* Mõtle ümber, kas kolmas ring (kontrollpunkti valik) kuulub samasse „andmestik vs toru" eristusse, või võiks selle nimetada „eraldi metaprobleemina: hindamise objektiiv ise võib saada lühiteeks". Praegu loetab arutelu seda ka selliselt (`sec:general-principle`), kuid sissejuhatuse alamküsimuse 4 sõnastus on kitsam.

---

### Uurimisküsimus 5 (alamküsimus): „Kas treenitud mudel saavutab eestikeelsel taustaheli korpusel pidevvoo FAPH < 1 ja lähikõne tuvastamismäära ≥ 0,95 sihi?"

**Autori vastus (kokkuvõte):** Osaliselt jah, osaliselt mitte. FAPH < 1: jah — ekspertmudelite konsensus (Expert A + Expert B2) saavutas Common Voice ET kõrvalejäetud komplektil FAPH = 0,79 (vt `tab:expert-consensus`). Recall ≥ 0,95: tinglikult — TTS-positiivsetel klippidel skoorid lähedal 1,0000, kuid päris kõnelejate „Kule"-hääldusel tuvastamismäär jääb juurutuslävel madalamaks (vt `summary.tex` §7 ja `third_chapter.tex` §139–§146). Töö hoiatab eraldi, et FAPH = 0,79 on punkthinnang ühel korpusel ja ühel operatsioonipunktil; täpne Poissoni 95% vahemik on lai. Lisaks: „ükski praegune mudel ega kombinatsioon ei täitnud korraga kõiki eesmärke" (`abstract-estonian.tex` §5).

**Hinne:** 9/10

**1. Analüüs**

* **Vastavus:** Jah, otseselt. Küsimus on vormistatud „kas" (binaarne), ja vastus on teadlikult tinglik: jah FAPH-iga, ei recall'iga päris kõnelejate juhul. „Millisel määral" on samuti kaetud — konkreetsed numbrid 0,79 FAPH ja recall'i piirjuhud on dokumenteeritud.

* **Loogika ja tõendatus:** Vastus on rangelt tõenduspõhine ja teadvustab oma piirid: punkthinnangu staatus, lai usaldusvahemik, sõltuvus hold-out korpusest, sõltuvus operatsioonipunktist (`cutoff ≥ 0,97`). Töö ütleb selgelt, et väide tugineb projekti-spetsiifilisele sihtmäärale, mitte universaalsele standardile (`introduction.tex` §17). See on akadeemiliselt tugev.

* **Kriitilised puudused:** (1) Recall ≥ 0,95 sihti ei ole kvantitatiivselt kontrollitud sõltumatu päris-kõnelejate komplekti peal — kasutajatest on piloodi vaikevalikuna `v16c`, ja 20–30 osaleja andmeid pole hindamise hetkel veel olemas. Seega on alamküsimuse 5 vastus recalli osas vältimatult tinglik. (2) FAPH = 0,79 on saavutatud konsensuse abil (kahe mudeli ühine signaal), mitte ühe mudeli abil. Sissejuhatuse siht („treenitud mudel") on grammatiliselt ainsuses; konsensuslahendust võiks selgemalt eristada üksiku mudeli sihist. (3) FAPH < 1 ja recall ≥ 0,95 sihte ei ole töös täidetud *samaaegselt* sama operatsioonipunkti juures — see on vastusena ausa selguse vahemikus, kuid sissejuhatus võiks juba etteseatult ütelda, et siht on neid mõlemat *koos*, mitte eraldi.

**2. Soovitused parendamiseks**

* Ütle vastuses (kokkuvõttes või arutelu §`Mida saab juba praegu väita`-loendis) eksplitsiitselt: „FAPH < 1 saavutati ekspertkonsensusega; recall ≥ 0,95 jääb avatuks päris kõnelejate sõltumatul testil; mõlemat sihti samaaegselt sama operatsioonipunkti juures käesolev töö ei tõenda". See teeb tinglikkuse selgesõnaliseks.
* Sõnastusta sissejuhatuse siht ümber, et see eristaks „üksiku mudeli FAPH < 1" vs „süsteemi-tasandi (võimalik konsensus) FAPH < 1" — praegu on alamküsimus pisut võrdlusvabalt ainsuses.
* Lisa kasutajatesti rolli vastusele eksplitsiitne viide: see on järgmine etapp, mille tulemused alles annavad recall'i osas lõpliku vastuse — vt `summary.tex` viimane lõik teeb seda osaliselt, kuid alamküsimusele otse viidates oleks selgem.

---

## Üldine kokkuvõte ja prioriteedid

Kõige tugevamad vastused on alamküsimused 3 ja 5: rikkalikult tõenduspõhised, otseselt küsimusele vastavad, oma piiridega ausad. Kõige nõrgem kohas on põhiküsimus (1): vastus on olemas, aga see on hajunud kolme peatüki vahel ja sõnastatud pigem metodoloogiliselt kui konstruktiivselt.

**Prioriteet 1 (kõige olulisem):** Põhiküsimuse otsene vastus tuleks kokkuvõttesse või arutelu lõppu tagasi tuua eraldi lõiguna, mis ütleb selgelt, kas töö vastab põhiküsimusele konstruktiivselt või tinglikult. Praegu peab lugeja vastuse rekonstrueerima ja võib jääda mulje, et töö on metodoloogiline panus, mitte tehniline lahendus — kuigi „panus" osa annab mõlemale.

**Prioriteet 2:** Sissejuhatuse alamküsimus 5 sõnasta nii, et FAPH < 1 ja recall ≥ 0,95 sihtide *samaaegne* täitmine on selgelt etteseatud kriteerium (mitte kaks eraldi punkti); vastasel juhul on ahvatlus loendada osalisi võite eraldi.

**Prioriteet 3:** Alamküsimus 4 mainigu lühidalt, et osa probleeme (nt residuaalühenduste vs sildistuse interaktsioon) ei ole puhtalt eraldatavad „andmestik vs toru" telje järgi. See teeb metoodilise narratiivi auseks ja ennetab retsensendi võimalikku vastuväidet.

Üldine alignment-hinnang sissejuhatuse ja arutelu/kokkuvõtte vahel on hea: kõik viis alamküsimust saavad vastuse, mille saab töö sisust põhjendatult tuletada. Lugemiskogemuse seisukohast oleks abi, kui sissejuhatuses oleks alamküsimuste numbrid (Q1–Q4) ja arutelu/kokkuvõte viitaks neile selgelt, sest praegu on alignment loogiline, kuid mitte tüpograafiliselt nähtav.
