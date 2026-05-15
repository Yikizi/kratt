---
source_prompt: AS_IS_TO_BE_plaan.txt
prompt_type: inapplicable (generative — best-effort adaptation)
generated: 2026-05-07
---

# AS-IS / TO-BE tegevuskava — kohaldatavuse hinnang ja parim võimalik adaptsioon

## 1. Kohaldatavuse hinnang (lühi)

Etteantud viip eeldab klassikalist **äriprotsesside ümberkujundamise (BPR/BPM) ja kasutajakeskse UI/UX disaini** lõputööd, mille väljundiks on:

* organisatsiooni **AS-IS protsesside** kaardistus (BPMN, juurpõhjuste analüüs);
* **TO-BE protsesside** ümberkujundamine (väärtust mitteloovate sammude eemaldamine, pudelikaelade kõrvaldamine);
* protsessi toetava **interaktiivse kasutajaliidese prototüübi** disain ja valideerimine (ISO 9241-210 / Design Thinking).

Käesolev bakalaureusetöö \enquote{Eestikeelse äratussõna tuvastus piiratud ressursiga nutikodu mikrokontrolleril} **ei ole sellist tüüpi töö**. See on **rakendusliku masinõppe ja sardsüsteemide insenertöö**, mille uurimisobjektid on:

1. mudeliarhitektuur ja treeningutoru (microWakeWord / TensorFlow Lite, MixedNet/SVDF);
2. andmestiku koostamine ja audit (positiivsed, negatiivsed, taustaheli);
3. voogedastushindamise metoodika (FAPH, FRR, Wilsoni / Poissoni-Garwoodi usaldusvahemikud);
4. ESP32-S3 + ESPHome + Home Assistanti integratsioon;
5. piiratud kasutajatest (20--30 osalejat) mudeli valideerimiseks, mitte UI valideerimiseks.

Töös puudub:

* **organisatsioon** ja selle töötajad, kelle tööprotsessi kaardistada;
* **pärandsüsteem (legacy UI)**, mida ümber kujundada;
* **äriprotsess** BPMN-mõttes (osalejad, tegevused, otsuspunktid, andmevood);
* **väärtust mitteloovate tegevuste** (BPR) elimineerimise küsimus;
* **interaktiivse UI prototüübi** (Figma, wireframe, klikkprototüüp) disain ja kasutatavustestimine.

Seetõttu ei ole võimalik viipa **otse** rakendada — BPMN-skeemi joonistamine, juurpõhjuste analüüs töövoogude pudelikaeladest või SUS/UEQ-põhine UI valideerimine annaks kunstlikke artefakte, mis ei kajastaks töö tegelikku metoodikat ega lisaks lõputööle väärtust.

## 2. Mida viip siiski kasulikku pakub

Hoolimata kohaldamatusest sisaldab viip kahte ülekantavat printsiipi, mille saab töö metoodikaga sünteesida:

1. **AS-IS / TO-BE eristus** — fikseeritud lähtepunkti ja sihtseisundi nimetatud kontrastimine, mille vahel toimub dokumenteeritud üleminek. See on töös juba varjatult olemas (ptk 3, §\ref{sec:eval-evolution} \enquote{Kolm valideerimiskihti}: iga ring kirjeldab AS-IS-mõõdiku puudust ja TO-BE-mõõdiku laiendust).
2. **Faasiline tegevuskava nõuetele tuletamise sammuga** — \enquote{kuidas tõlgitakse protsessisamm tarkvara funktsionaalseks nõudeks}. Töös vastab sellele \enquote{kuidas tõlgitakse hindamismetoodika risk treeningutoru / koodibaasi muudatuseks}.

Allpool on **best-effort adaptsioon**: ei ole BPM-tegevuskava, vaid **rakendusliku ML-projekti hindamismetoodika ja juurutustoru AS-IS / TO-BE üleminekuplaan**, mis säilitab viipa palutud struktuuri (faasid 1--4, samm-tegevus-meetod-väljund), aga asendab äriprotsessid hindamis- ja juurutusprotsessidega ning UI prototüübi seadme + Home Assistanti integratsioonimustri prototüübiga.

---

## 3. Best-effort adaptsioon: tegevuskava

### Faas 1: Olemasoleva olukorra analüüs (AS-IS)

**Samm 1.1. Olemasoleva treeningu- ja hindamistoru kaardistus**
* **Tegevus:** dokumenteerida senine \texttt{microWakeWord}-põhine treeningutoru ja klipi-tasemel hindamine (v1--v6 baasjoon), sh andmevoog avalikest korpustest (Speech Commands, MUSAN, VOiCES, Common Voice) treeningu mmap-vormingusse ning sealt TFLite ekspordini.
* **Meetod/Tööriist:** komponentdiagramm ja andmevoo-skeem (analoog BPMN-le, kuid ML-toru kontekstis); tehniline audit (skriptide ja konfiguratsioonifailide läbivaatus); Dumas et al.\ BPM-elutsükli \emph{Process Discovery} faasi mõtteviis kohandatuna ML-torule.
* **Väljund:** ptk 2 (Metoodika) §3.1--§3.5 — torukomponentide ja andmeliikide eristuse kirjeldus.

**Samm 1.2. AS-IS hindamismetoodika nõrkuste tuvastamine (juurpõhjuste analüüs)**
* **Tegevus:** tuvastada, miks senine klipi-tasemel FPR ei ennustanud reaalse seadme käitumist — MacBook Pro 40-min testil v6 mudel ${\sim}$50 FAPH, kuigi klipi-FPR oli 0,4\%.
* **Meetod/Tööriist:** \emph{5 Whys} / Ishikawa diagramm, kohandatuna ML-toru pudelikaeladele; andmeleke-audit (treening- ja testikomplektide kattuvuse kontroll, ptk 3 §\ref{sec:data-leakage}); positiivse klassi sildiaudit (ptk 3 §\ref{sec:positive-audit}).
* **Väljund:** ptk 3 §\ref{sec:benchmark-gap} \enquote{Standardsete võrdlusaluste ebapiisavus} — neli põhjust (klipi-recall ei kajasta reaalset kõnelejat, FAPH tihedal kõnel ei ennusta keskkonda, klipi-tasemel rasked negatiivid ei kajasta voogedastust, mittekõneliste helide puudumine).

**Samm 1.3. Riistvaralise lähtepunkti AS-IS auditi (sihtplatvormi piirangud)**
* **Tegevus:** dokumenteerida ESP32-S3 mälupiirangud (flash, tensor\_arena), ESPHome \texttt{voice\_assistant} liidese praegune käitumine, Korvo-2 mikrofoni profiil ja varasem MacBook Pro mikrofoniga mõõdetud domeeninihke risk.
* **Meetod/Tööriist:** spetsifikatsiooni-audit, mälu- ja latentsuse-mõõtmised reaalsel seadmel.
* **Väljund:** ptk 2 §\ref{subsec:quantization} (148\,KB TFLite + 45--50\,KB tensor\_arena); ptk 3 §\ref{sec:cross-mic-asymmetry} (mikrofoni asümmeetria).

**AS-IS faasi koondkokkuvõte:** dokumenteeritud lähtepunkt, kus klipi-tasemel mõõdikud andsid eksitavalt optimistliku pildi (FPR 0,4\%) ning toru ei eristanud andmestiku-, hindamis- ega juurutusriske. See on töö \enquote{esimese ringi} dokumenteeritud AS-IS.

---

### Faas 2: Protsesside ümberkujundamine (TO-BE)

**Samm 2.1. Hindamisprotokolli ümberkujundamine — voogedastus + sõltumatud kõrvalejäetud komplektid**
* **Tegevus:** asendada üksik klipi-FPR komposiitsete mõõdikutega (taustaheli FAPH, päriskõnelejate tuvastamismäär, sarnaste negatiivnäidete FPR, fraasistruktuuri testid: prefiks / üksiksõna / pööratud järjekord / kuule-vs-kule).
* **Meetod/Tööriist:** BPR-printsiip \enquote{eemalda väärtust mitteloovad sammud} → eemaldada mõõdikud, mis ei eralda \enquote{õpitud äratussõna} mudelit \enquote{õpitud akustilise lühitee} mudelist; lisada FAPH 4 varianti (raamistiku, skriptitud taasmängu, välitingimuste, kasutajatesti taasmängu) selge loendusreegliga (ptk 2 §\ref{subsec:faph-variants}).
* **Väljund:** ptk 3 §\ref{sec:eval-evolution} \enquote{Kolm valideerimiskihti} — TO-BE mitmemõõtmeline hindamisprotokoll, mis on töö metoodiline põhipanus.

**Samm 2.2. Treeningutoru ümberkujundamine — andmelekke kontroll ja positiivse klassi sildi-audit**
* **Tegevus:** lisada treeningutorule automaatne treeningu- ja hindamiskomplektide disjointsuskontroll; rangem positiivsete näidete poliitika (terve fraasi nõue, prefiksi-tüüpi heli kõrvaldamine).
* **Meetod/Tööriist:** kontrollskriptid CI-stiilis valideerimisena enne iga treeningujooksu; komposiitne kontrollpunkti valikukriteerium (mitte ainult FAPH miinimum, vaid samaaegne FAPH + päriskõneleja recall + sarnasuse-FPR).
* **Väljund:** ptk 3 §\ref{sec:three-rounds} kolmanda ringi parandus — komposiitne kontrollpunkti valikukriteerium.

**Samm 2.3. Juurutusarhitektuuri ümberkujundamine — kaskaadi/konsensuse kandidaat**
* **Tegevus:** uurida ekspertmudelite konsensust (\texttt{expert-a + expert-b2}, FAPH 0,79 Common~Voice ET kõrvalejäetud kõnel) kui üleminekut üksiku mudeli paradigmast kahekihilisele detektsioonile.
* **Meetod/Tööriist:** kaskaadarhitektuuri kirjandus (Apple, Google KWS \cite{gruenstein2017cascade,apple_voice_trigger_2023,michaely2017googlekws}); konsensuse mõju mõõtmine FAPH ja recall vahekompromissil.
* **Väljund:** ptk 3 §\ref{sec:future-cascade} — TO-BE arhitektuurisuund, mis on töös dokumenteeritud kandidaadina, mitte juurutuslubadusena.

---

### Faas 3: Nõuete tuletamine ja prototüüpimine (analoog UI/UX-le)

> **Märkus kohaldamatusest:** klassikalises BPM/UX-töös oleks see faas Figma-prototüüp + \emph{user stories}. Käesolevas töös vastab sellele **mudeli + ESPHome + Home Assistant integratsioonimustri prototüüp ning kasutajatesti protokoll**. Säilitan viipa nõutud sammu \enquote{kuidas TO-BE protsess tõlgitakse funktsionaalseteks nõueteks}, kohaldades selle ML-/sardsüsteemi konteksti.

**Samm 3.1. TO-BE hindamisprotokolli tõlkimine täidetavateks nõueteks (kasutuslood)**
* **Tegevus:** sõnastada hindamisprotokolli punktid täidetavate nõuetena, nt:
  * \enquote{Kasutajana tahan, et iga raporteeritud FAPH-arv viitaks variandile (raamistiku / skriptitud / välitingimuste / kasutajatesti taasmängu), et tabelid oleksid omavahel võrreldavad.}
  * \enquote{Kasutajana tahan, et treeningutoru keelduks startimast, kui treeningu- ja hindamiskomplekt kattuvad, et vältida andmeleket.}
  * \enquote{Kasutajana tahan, et iga FAPH-arv oleks raporteeritud koos 95\%~Poissoni-Garwoodi vahemikuga.}
* **Meetod/Tööriist:** \emph{user story}-stiilis nõuete tuletamine, kohaldatuna sisemise tööriistaahelale; \texttt{kratt} CLI-käskude (\texttt{kratt user-test}, \texttt{kratt validate-user-test}, \texttt{kratt replay-user-test}, \texttt{kratt summarize-user-test}) liidesedisain.
* **Väljund:** ptk 2 §\ref{sec:user-test-methodology} kirjeldatud tööriistaahel.

**Samm 3.2. Sihtseadme \enquote{prototüübi} valmidus**
* **Tegevus:** valmistada ette külmutatud kasutajatesti seade (\texttt{v16c} ESPHome + \texttt{voice\_assistant}, Korvo-2), millel sessioon viiakse läbi; külmutada lävi enne salvestust, et hilisem mitme mudeli taasmäng oleks identsel sisendil.
* **Meetod/Tööriist:** ISO 9241-210 \emph{Design with users in mind} põhimõte ülekantud — kasutaja näeb ühte stabiilset baasjoont, mitte keelelist ümberlülitamist mudelite vahel; ESPHome'i compile/flash kontroll \texttt{v16c} aktiivsel konfiguratsioonil.
* **Väljund:** kasutajatesti aktiivse seadme dokumenteeritud konfiguratsioon (ptk 2 §\ref{sec:user-test-methodology}).

**Samm 3.3. Subjektiivse rahulolu mõõtmise instrument**
* **Tegevus:** valida valideeritud lühiskaala (UMUX-Lite kaks väidet, ptk 2 §\ref{sec:user-test-methodology}) ja eraldada see uurija koostatud diagnostilistest küsimustest; sõnastada üks avatud küsimus häiriva või üllatava kogemuse kohta.
* **Meetod/Tööriist:** Lewis 2013 UMUX-Lite \cite{lewis2013umuxlite}, Sauro 2009 SEQ \cite{sauro2009seq}; kaheastmeline nõusolekumudel (minimaalne / audio opt-in).
* **Väljund:** kasutajatesti küsimustik (\texttt{docs/user-testing/mini-questionnaire-form-v1.md}).

---

### Faas 4: Valideerimine ja hindamine

**Samm 4.1. Tehniline valideerimine fikseeritud varjuskomplekti peal**
* **Tegevus:** käivitada külmutatud läve juures kõikide salvestatud kasutajatesti WAV-klippide taasmäng mitme varimudeli peal (\texttt{v16c}, \texttt{expert-a}, \texttt{expert-b2}, \texttt{v6-residual}, \texttt{v10}, \texttt{v15}, konsensus \texttt{expert-a+expert-b2}); raporteerida tuvastamismäär ja FPR Wilsoni vahemikega.
* **Meetod/Tööriist:** \texttt{kratt replay-user-test}, \texttt{kratt summarize-user-test}; Wilson 1927 / Brown 2001 vahemikud.
* **Väljund:** ptk 3 lõplik kasutajatesti taasmängu FAPH-tabel.

**Samm 4.2. Kasutuspõhine valideerimine (20--30 osalejat)**
* **Tegevus:** läbi viia 10-min ühe-nutipirni stsenaarium 20--30 osalejaga: 5 puhast äratussõna ütlust, 5 sarnast negatiivfraasi, 6 skriptitud pirnikäsku, 1 vabas vormis valgusülesanne.
* **Meetod/Tööriist:** \texttt{kratt user-test} CLI; \texttt{trials.jsonl} + 16~kHz mono WAV-klipid (audio opt-in); UMUX-Lite + diagnostilised küsimused.
* **Väljund:** ptk 3 päriskõnelejate tuvastamismäära ja sarnasuse-FPR mõõtmised; subjektiivse rahulolu lühiraport.

**Samm 4.3. Aus piir ja \enquote{neljanda ringi} dokumenteerimine**
* **Tegevus:** sõnastada selgelt, milliseid režiime (häälduse vahevormid, aktsendid, lapse kõne, vaikne äratus pärast pikka vaikust) praegune valideerimine ei kata.
* **Meetod/Tööriist:** ausus-piir kui metoodiline distsipliin (ptk 3 §\ref{sec:fourth-round}).
* **Väljund:** kokkuvõte (\texttt{summary.tex}) + arutelu lõpp — protokoll on tõendusdistsipliin, mitte tagatud lõppjaam.

---

## 4. Kokkuvõte: viip ↔ töö joondumine

| Viiba element | Töös vastav element | Joondumise kvaliteet |
|---|---|---|
| AS-IS äriprotsessid (BPMN) | Senine treeningu- ja hindamistoru (ptk 2 §3) | adaptsioon, mitte otseseos |
| BPR — väärtust mitteloovate sammude eemaldamine | Andmelekke kõrvaldamine, klipi-FPR asendamine FAPH-iga | hea analoogia |
| Pudelikaelade tuvastamine | \enquote{Lühitee}-mehhanismid hindamises (§\ref{sec:general-principle}) | hea analoogia |
| Protsessisamm → funktsionaalne nõue / user story | Hindamisprotokolli risk → CLI-käsk / valideerimisskript | adaptsioon |
| ISO 9241-210 / Design Thinking | Kasutajatesti protokoll, fikseeritud baasjoon, mitme mudeli taasmäng | osaline |
| Interaktiivne UI prototüüp | **Puudub** — töös ei ole ega ka ei peaks olema graafilist UI prototüüpi | mitteseos |
| SUS / UEQ / kasutatavustestid | UMUX-Lite + uurija küsimused | osaline |

## 5. Soovitus

Viip on **vales metoodikaperekonnas** käesoleva töö jaoks. Lõputöö **ei tohiks** viipa otse järgida — st BPMN-skeemi senise hindamistoru asemele joonistamine, kunstliku \enquote{legacy UI} kirjeldamine või Figma-prototüübi lisamine **lahjendaks** töö metoodilist põhipanust (mitmemõõtmeline hindamisprotokoll), mitte ei tugevdaks seda.

Kui retsensent või juhendaja siiski palub, et töö struktuur kõlaks rohkem AS-IS / TO-BE-na, siis **ainus mõistlik adaptsioon** on käesoleva dokumendi p.~3 raamistiku rakendamine **olemasoleva ptk~3 §\ref{sec:eval-evolution} \enquote{Kolm valideerimiskihti} sees**: iga ring on AS-IS → TO-BE üleminek hindamismetoodikas, mitte äriprotsessis. Töö ei vaja selle vormistuse jaoks ühtegi uut katset ega andmekogumist; vajadusel võib lisada ühe lõigu §\ref{sec:eval-evolution} algusesse, mis sõnastab kolm ringi avalikult AS-IS/TO-BE keeles.

Suurem ümberstruktureerimine (eraldi peatükk \enquote{AS-IS protsessid}, BPMN-joonised, UI prototüüp) ei ole põhjendatud ega anna lugejale uut informatsiooni; see lihtsalt asendaks töö praegused joonised ja terminoloogia teisega, kaotades samal ajal viite mehaanilise õppe ja sardsüsteemide kirjandusele, mille poole töö praegu sõnaselgelt joondub.
