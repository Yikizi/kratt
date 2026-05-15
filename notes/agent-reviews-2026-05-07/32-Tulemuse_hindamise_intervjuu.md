---
source_prompt: Tulemuse_hindamise_intervjuu.txt
prompt_type: generative
generated: 2026-05-07
---

# Valideerimisintervjuu kava: eestikeelse äratussõna mudel \enquote{Kuule Kratt}

## Analüüs ja kontekst

**Valideerimisobjekt.** Lõputöö tulemus on kolmeosaline ja sisaldab nii tehnilist artefakti kui ka metoodilist panust:

1. eestikeelne äratussõna mudel \enquote{Kuule Kratt} (microWakeWord-põhine MixedNet, sihtkandidaat \texttt{v16c}, kvantiseeritud TFLite, ${\sim}148$\,KB, ESP32-S3 sihtplatvorm);
2. mitmemõõtmeline hindamisprotokoll (sõltumatu kõrvalejäetud komplekti FAPH, päriskõnelejate tuvastamismäär, sarnaste negatiivnäidete FPR, prefiksi- ja segiajamiskontrolli mõõdikud) koos reprodutseeritava treeningu- ja hindamistoruga;
3. ESP32-S3 + ESPHome + Home Assistant lokaalne integratsioonimuster.

**Sihtgrupp.** Intervjuu kava on koostatud nii, et see oleks rakendatav kahele üksteist täiendavale rühmale. Kuna lõputöö panus on tehniliselt ja metoodiliselt tihe, on valideerimine usaldusväärne ainult juhul, kui mõlemad vaatenurgad on kaetud:

- **Tehniline ekspert** (kõnetehnoloogia, masinõppe või manussüsteemide arendaja, kellel on varasem kogemus äratussõna või KWS-mudelite, ESPHome'i, Home Assistanti või väikese keele kõnetehnoloogiaga). Hindab metoodikat, FAPH-protokolli ja tehnilist teostust.
- **Lõppkasutaja-ekspert** (Home Assistanti aktiivkasutaja või eestikeelse häälassistendi vajadusega kodukasutaja). Hindab kasutuskogemust 10-minutilise demoseansi järel.

Käesolev kava on **tehnilise eksperdi versioon**, kuna lõputöö metoodiline panus (mitmemõõtmeline hindamisprotokoll) on töö kõige kindlamini kaitstav osa ning vajab eksperdi-tasandi valideerimist. Lõpus on lühike juhis, kuidas sama struktuuri saab kohandada lõppkasutaja-intervjuuks (lisa A).

**Maht.** Kokku 11 põhiküsimust, mis mahuvad 45–60 minuti sisse, kui igale küsimusele kulub 3–5 minutit.

---

## Osa 1: Intervjueeritava taust ja profiil

### Küsimus 1.1
**Küsimus:** Palun kirjeldage lühidalt oma erialast tausta ja varasemat kokkupuudet kõnetehnoloogia, äratussõna tuvastuse või manussüsteemidel käitatavate mudelitega. Mitu aastat olete vastavate süsteemidega töötanud ning millises rollis?

- **Eesmärk:** Kalibreerida hilisemate hinnangute kaalu --- kas vastaja räägib KWS-süsteemide arendaja, kõnetuvastuse uurija või rakendusarendaja vaatenurgast. Eristada hinnangud, mis tulevad otsesest töökogemusest, nendest, mis tulenevad üldisest masinõppe taustast.

### Küsimus 1.2
**Küsimus:** Milliseid äratussõna või võtmesõna tuvastuse raamistikke (näiteks microWakeWord, openWakeWord, Picovoice Porcupine, Snowboy, Sensory) olete praktikas kasutanud, ja milliste kompromissidega olete nende valikul kokku puutunud?

- **Eesmärk:** Kontrollida, kas vastaja oskab paigutada käesoleva töö raamistikuvaliku (microWakeWord vs.\ openWakeWord) laiemasse maastikku ning kas tema hilisemad kommentaarid integreeritavuse ja laiendatavuse kohta tuginevad võrdlevale kogemusele.

### Küsimus 1.3
**Küsimus:** Kui suur on Teie varasem kokkupuude väikese ressursiga keelte kõnetehnoloogia projektidega või sünteetilise kõne kasutamisega treeningandmestikus?

- **Eesmärk:** Tuvastada, kas vastaja on tundlik just nende riskide suhtes, mida käesolev töö dokumenteerib (TTS-andmete üleoptimism, andmeleke, fraasistruktuuri lühiteed). Tasakaalustada hilisemate vastuste tõlgendust.

---

## Osa 2: Hinnangulised küsimused (skaala + põhjendus)

Kõikide skaalaküsimuste järel palutakse intervjueeritaval lühidalt põhjendada, miks ta just sellise hinde andis. Skaala äärmused defineeritakse iga küsimuse alguses uuesti, et vältida ankurdumist eelmise küsimuse kontekstile.

### Küsimus 2.1 --- mitmemõõtmelise hindamisprotokolli tugevus
**Küsimus:** Kuivõrd nõustute, et töös pakutud hindamisprotokoll --- sõltumatu kõrvalejäetud taustaheli FAPH, päriskõnelejate tuvastamismäär, TTS-allikate tuvastamismäär, sarnaste negatiivnäidete FPR ning fraasistruktuuri kontrollivad mõõdikud (prefiks, üksik sõna, pööratud järjekord, kuule/kule segiajamine) --- katab adekvaatselt äratussõna mudeli juurutatavuse riskid väikese ressursiga keele kontekstis?

- **Skaala:** 1–5, kus 1 = \enquote{ei nõustu üldse, protokollis on olulisi riske katmata}, 5 = \enquote{nõustun täielikult, protokoll katab praktiliselt olulised riskid}.
- **Eesmärk:** Hinnata töö kõige kindlamini kaitstavat panust --- mitmemõõtmelist hindamisprotokolli (vt §\ref{sec:eval-evolution}). Kontrollida, kas eksperdi vaates jääb mõni riskiklass kriitiliselt katmata.
- **Täpsustav lisaküsimus:** \enquote{Palun selgitage lühidalt, miks andsite just sellise hinde. Kas Teie hinnangul on mõni oluline riskiklass, mida see protokoll ei kata?}

### Küsimus 2.2 --- FAPH kui keskne mõõdik
**Küsimus:** Kuidas hindate otsust kasutada keskse vääraktiveerimiste mõõdikuna voogedastusrežiimi FAPH-i (false accepts per hour) eraldi taustaheli korpusel, eristades samas töös nelja FAPH-i varianti (raamistiku, skriptitud taasmängu, välitingimuste, kasutajatesti taasmängu)?

- **Skaala:** 1–5, kus 1 = \enquote{ebasobiv valik, klipi-tasemel mõõdikud oleksid piisavad}, 5 = \enquote{põhjendatud valik, FAPH-i variantide eristamine on metoodiliselt vajalik}.
- **Eesmärk:** Kontrollida, kas FAPH-i loendusreegli sõnastamine ja variantide eristamine (vt §\ref{subsec:faph-variants}) on eksperdi silmis metoodiliselt korrektne.
- **Täpsustav lisaküsimus:** \enquote{Palun selgitage lühidalt, miks andsite just sellise hinde. Kas FAPH-i variantide eristus on Teie hinnangul piisavalt selge, et töö tulemused oleksid teiste uurijate poolt korratavad?}

### Küsimus 2.3 --- raamistikuvalik (microWakeWord ESP32-S3-le)
**Küsimus:** Kuivõrd põhjendatud on Teie hinnangul töö disainivalik kasutada microWakeWord raamistikku peamise sihtraamistikuna ja openWakeWord võrdlusraamistikuna, ESP32-S3 mikrokontrolleri sihtplatvormil ${\sim}57$--$148$\,KB mudelisuurusega?

- **Skaala:** 1–5, kus 1 = \enquote{ebasobiv valik, teine raamistik oleks olnud parem}, 5 = \enquote{põhjendatud ja sihtplatvormiga kooskõlas valik}.
- **Eesmärk:** Hinnata töö tehnoloogiavaliku kaitstavust eksperdi vaates ning saada eraldi kommentaar selle kohta, kas openWakeWord oleks olnud paremaks vaikevalikuks Pi-klassi sihtseadmel.
- **Täpsustav lisaküsimus:** \enquote{Palun selgitage lühidalt, miks andsite just sellise hinde. Kui sihtplatvorm oleks olnud Raspberry Pi 5, kas valik oleks pidanud olema teistsugune?}

### Küsimus 2.4 --- protokolli ülekantavus teistele väikestele keeltele
**Küsimus:** Kuivõrd hindate, et selles töös dokumenteeritud kolmekihiline valideerimisprotokoll --- (a) sõltumatu kõrvalejäetud komplekti kontroll, (b) positiivse andmestiku sisuline audit, (c) mitmekriteeriumiline kontrollpunkti valik --- on otseselt kohaldatav teistele madala ressursiga keelte äratussõna projektidele?

- **Skaala:** 1–5, kus 1 = \enquote{tugevalt eestikeele- või Krati-spetsiifiline}, 5 = \enquote{üldine ja otseselt ülekantav teistele väikestele keeltele}.
- **Eesmärk:** Valideerida töö üldistuse ulatust (vt §\ref{sec:contribution-transferability}) --- kas eksperdi hinnangul väide \enquote{väikese ressursiga keele kohaliku äratussõna mitmemõõtmelise valideerimise protokoll} kannab ka teistele kontekstidele.
- **Täpsustav lisaküsimus:** \enquote{Palun selgitage lühidalt, miks andsite just sellise hinde. Millised protokolli osad oleksid teie hinnangul kõige paremini ülekantavad ja millised vajaksid kohandamist?}

### Küsimus 2.5 --- juurutuskandidaadi praktiline valmidus
**Küsimus:** Käesoleva töö praktiline aktiivne kandidaat on \texttt{v16c}, mille konsensushindamine \texttt{expert-a + expert-b2} saavutas Common~Voice ET kõrvalejäetud komplektil FAPH $= 0{,}79$, kuid jääkpiiranguna jääb tuvastamismäär reaalsetel \enquote{Kule}-hääldustel juurutuslävel madalamaks kui TTS-positiivsetel klippidel. Kuivõrd hindate selle kandidaadi sobivust kodukasutuse pilootkasutuseks (mitte tootmistasemel kasutuseks)?

- **Skaala:** 1–5, kus 1 = \enquote{ei sobi pilootkasutuseks}, 5 = \enquote{sobib pilootkasutuseks ja annab usaldusväärse aluse järgmistele sammudele}.
- **Eesmärk:** Kontrollida, kas eksperdi hinnangul on töö praeguste tulemuste valguses õigustatud kasutajatestid päris osalejatega.
- **Täpsustav lisaküsimus:** \enquote{Palun selgitage lühidalt, miks andsite just sellise hinde. Kas Te muudaksite enne 20--30 osalejaga kasutajatesti veel midagi mudelis, hindamiskorras või sihtkonfiguratsioonis?}

### Küsimus 2.6 --- agentpõhise arenduse käsitluse aususe hinnang
**Küsimus:** Töö arutelu peatükis on eraldi käsitletud agentpõhise tarkvaraarenduse rolli ning autori järeldust, et tehisagendid nihutavad pudelikaela teostuselt tõendusmaterjalile, kuid ei vähenda tõendusmaterjali hankimise kulu. Kuivõrd nõustute selle järelduse aususe ja teadusliku rangusega?

- **Skaala:** 1–5, kus 1 = \enquote{järeldus on alahinnatud või liiga ettevaatlik}, 5 = \enquote{järeldus on kalibreeritud ja teaduslikult korrektne}; kui leiate, et järeldus on \emph{ülehinnatud} (tehisagentide rolli on liialdatud), märkige see eraldi täpsustavas vastuses.
- **Eesmärk:** Hinnata töö metoodilise reflekteerimise kvaliteeti --- üks hindamiskomisjoni jaoks tundlik teema, sest agentpõhise arenduse roll on bakalaureusetöö hindamise mõttes uudne küsimus.
- **Täpsustav lisaküsimus:** \enquote{Palun selgitage lühidalt, miks andsite just sellise hinde. Kas käsitlus oleks Teie hinnangul pidanud olema kriitilisem või usaldavam?}

---

## Osa 3: Avatud arutelu ja parendusettepanekud

### Küsimus 3.1 --- benchmark-päriskasutuse lõhe
**Küsimus:** Töö üks kesksemaid empiirilisi leide on süstemaatiline lahknevus standardsete KWS-võrdlusaluste tulemuste ja päris kõnelejate käitumise vahel (vt §\ref{sec:benchmark-gap}). Töö loetleb neli põhjust: klipi-tasemel tuvastamismäär TTS-häälel, FAPH tihedal kõnel vs.\ kodukeskkonnas, klipipõhine raskete negatiivnäidete test ja mittekõneliste helide puudumine. Kuidas Teie selle nelja-osalise põhjenduse tähtsust hindaksite ja kas Teie kogemuses jääb mõni viies põhjus käsitlemata?

- **Eesmärk:** Saada eksperdi süvavaatlus töö praktiliselt olulisima leiu kohta. Kontrollida, kas töö põhjuste loend on täielik või jätab katmata mõne tähtsa mehhanismi (näiteks domeeninihke spetsiifiline alaliik, mida autor pole märganud).
- **Tegevusjuhis (kui asjakohane):** Palu eksperdil enne vastamist üle vaadata §\ref{sec:benchmark-gap} (lk-d ${\sim}3$ teises peatükis); küsimus eeldab, et ekspert on jaotised \emph{Põhjus 1--4} eelnevalt lugenud või talle on need kokkuvõtlikult ette esitatud.

### Küsimus 3.2 --- teise ringi sildistusprobleem ja fraasistruktuuri testid
**Küsimus:** Töö dokumenteerib teise valideerimisringi käigus avastatud \emph{teist järku sildistusprobleemi}, kus osa positiivseid näiteid ei kandnud sisuliselt tervet fraasi \enquote{Kuule Kratt}, ning seejärel kasutusele võetud fraasistruktuuri testid (prefiks, üksik sõna, pööratud järjekord, kuule/kule segiajamine). Kuidas hindate selle riskiklassi käsitlust ning milliseid täiendavaid teste või andmestiku-puhastuse samme oleksite oma kogemusel sarnases olukorras kasutanud?

- **Eesmärk:** Saada konkreetseid soovitusi positiivse klassi auditi tugevdamiseks. See on töö üks otsesemalt parandatavaid kohti enne lõpuredaktsiooni.
- **Tegevusjuhis:** Palu eksperdil keskenduda just \emph{sildistuse} kvaliteedile, mitte mudeli arhitektuurile.

### Küsimus 3.3 --- konsensus ja kaskaadarhitektuur
**Küsimus:** Töös pakutakse edasiseks suunaks kaskaadarhitektuuri, kus väike alati-aktiivne detektor annab esialgse kandidaadi ja teine aste kontrollib seda põhjalikumalt (vt §\ref{sec:future-cascade}). Kuidas hindate selle suuna teostatavust ESP32-S3 + Home Assistant + Raspberry Pi 5 arhitektuuris, ja milliseid konkreetseid riske näete teise astme realiseerimisel?

- **Eesmärk:** Saada tehnilist tagasisidet edasise arenduse pudelikaelte kohta. Kasulik töö \enquote{edasised suunad} osa täpsustamiseks.

### Küsimus 3.4 --- 10-minutilise kasutajatesti protokolli kriitika
**Küsimus:** Töö järgmine kriitiline samm on 20--30 osalejaga 10-minutiline kasutajatest, mille protokolli sisuline ülesehitus on järgmine: 5 puhast äratussõna ütlust, 5 sarnast negatiivfraasi, 6 skriptitud pirnikäsku, 1 vabas vormis valgusülesanne ning lukustatud lühiküsimustik (UMUX-Lite, SEQ ja neli Krati-spetsiifilist diagnostilist hinnangut). Kus näete selle protokolli olulisemaid metodoloogilisi nõrkusi või konkreetset võimalust, kuidas sama 10-minutilise eelarvega saaksite usaldusväärsemat tõendusmaterjali?

- **Eesmärk:** Tuua välja, kas 10-minutilise lukustatud testi sisuline ehitus on eksperdi hinnangul tasakaalus kontrollitud äratussõna mõõtmise ja kasutuskogemuse mõõtmise vahel. Konkreetsed parandussoovitused enne täismahus kogumist.
- **Tegevusjuhis:** Anna eksperdile dokumendi \texttt{ten-minute-shadow-demo-protocol.md} ja \texttt{mini-questionnaire-form-v1.md} sisu kokkuvõte enne küsimust.

### Küsimus 3.5 --- aus piir ja võimalik neljas valideerimisring
**Küsimus:** Töö §\ref{sec:fourth-round} möönab, et neljanda valideerimiskihi olemasolu ei saa välistada ning et see peab tulema kasutuskogemustest, mida käesolev töö pole veel teostanud (näiteks häälduse vahevormid, aktsendid, lapse kõne). Milliseid konkreetseid kasutuskogemusi või äärejuhte (\emph{edge cases}) Te oma kogemusest soovitaksite teadlikult sisse kavandada järgmisesse valideerimisringi, et neljas kiht oleks tõendipõhiselt kaetud?

- **Eesmärk:** Saada eksperdilt ettepanekuid, mis aitaksid suunata projekti edasist tööd kõige väärtuslikumate äärejuhtude poole. Töö läbipaistvus selles küsimuses on metoodiliselt oluline tugevus, mida tasub eksperdi panusega täpsustada.

---

## Lisa A: Lõppkasutaja-intervjuu kohandused (lühijuhis)

Kui sama struktuuri kasutatakse kodukasutaja-eksperdi (mitte kõnetehnoloogia eksperdi) jaoks pärast 10-minutilist demoseanssi, siis:

- **Osa 1:** asenda küsimused 1.2 ja 1.3 küsimustega varasema häälassistendi (Alexa, Google, Siri, Yandex Alice) kasutuskogemuse ja eestikeelse häälsisendi vajaduse kohta;
- **Osa 2:** asenda metoodilised hinnangud (2.1, 2.2, 2.4, 2.6) küsimustikus juba olemasolevate UMUX-Lite ja SEQ skaaladega; alusta 2.3 (raamistikuvalik) asemel küsimusega \enquote{kuivõrd usaldusväärselt reageeris süsteem demoseansi jooksul Teie häälele}; säilita 2.5 (pilootkasutuse sobivus) sama sõnastusega;
- **Osa 3:** asenda tehnilised arutelud (3.1--3.3) küsimustega kasutuskeskkonna (kodu, ruumi suurus, taustamüra), kõnelejate ringi (lapsed, eakad, mitmekeelsus) ja konkreetsete soovitavate käskude kohta. Säilita 3.4 ja 3.5 sisu, kuid kohanda sõnastust mittetehnilisele auditooriumile.

---

## Märkused intervjueerijale

- **Suunavate küsimuste vältimine:** kõik skaalaküsimused on sõnastatud nii, et hinnangu äärmused on tasakaalus; intervjueerija ei tohi vastust enne hinnet kommenteerida.
- **Põhjenduste salvestamine:** iga skaalaküsimuse järel salvestatakse hinde kõrvale lühike (1--3 lauset) põhjendus; täisvastused arutelu osas salvestatakse helisalvestisena või täismahus märkmena, eraldi nõusoleku alusel.
- **Ajajaotus:** osa 1 ${\sim}5$ min, osa 2 ${\sim}20$ min ($6 \times 3{-}4$ min), osa 3 ${\sim}25$ min ($5 \times 5$ min). Kogumaht 50 min, varuga 10 min.
- **Eelmaterjal:** intervjueeritavale saadetakse vähemalt 24 tundi enne intervjuud lühikokkuvõte (sissejuhatus + abstraktne, ${\sim}2$ lk) ning viited §\ref{sec:benchmark-gap} ja §\ref{sec:eval-evolution} osadele. Tervet lõputööd ei eeldata.
- **Andmekaitse:** intervjuusid käsitletakse pseudonüümselt; salvestamiseks ja säilitamiseks kogutakse eraldi nõusolek, sarnaselt 10-minutilise kasutajatesti kaheastmelise nõusolekumudeliga.
