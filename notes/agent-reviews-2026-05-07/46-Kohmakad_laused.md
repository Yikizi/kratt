---
source_prompt: 04_Kontrollimine/Konkreetsed_vead/Vorm/Kohmakad_laused.txt
prompt_type: evaluative + generative (stiilitoimetuse audit)
generated: 2026-05-07
---

# Stiilitoimetuse audit: kohmakad laused ja "kaardistama" kasutus

Põhikeel: eesti keel. Audit hõlmab faile `introduction.tex`, `first_chapter.tex`, `second_chapter.tex`, `third_chapter.tex`, `summary.tex`, `abstract-estonian.tex` ning `ylesandepystitus.tex`. Audit puudutab ainult vormi (lauseehitus, nominaalstiil, kohmakas sõnastus); sisulist väiteid ei muudeta.

---

## 1. Stiilivead ja kohmakad laused (TOP 10)

*(Järjestus raskusastme järgi kahanevalt — kõige "haigem" lause kõige ees.)*

---

**1. Asukoht:** `introduction.tex`, lõik 1 (teine lause, "Ehkki eesti keele jaoks...")

*   **Algne:** "Ehkki eesti keele jaoks on olemas mahukad kõnetuvastuse korpused ja mudelid \cite{...} ning äratussõna tuvastust käsitleb rahvusvaheline kirjandus põhjalikult \cite{...}, ei kuulu eesti keel avatud raamistiku \texttt{openWakeWord} jaotatud mudelite \cite{...} ega lähima suletud lähtekoodiga võrdluspunkti Picovoice Porcupine toetatud keelte hulka \cite{...}."
*   **Probleem:** ülipikk üheahelaline lause kahe vastandusega ("Ehkki ... ning ..., ei kuulu ... ega ..."), neli viidet ühes lauses, lugeja kaotab subjektist sihituseni jõudmisel ülevaate. Klassikaline akadeemiline pikalause, mis ühendab kolm sõltumatut väidet.
*   **Parandus:** "Eesti keele jaoks on olemas mahukad kõnetuvastuse korpused ja mudelid \cite{...} ning äratussõna tuvastust käsitleb rahvusvaheline kirjandus põhjalikult \cite{...}. Sellele vaatamata ei toeta eesti keelt avatud raamistik \texttt{openWakeWord} \cite{...} ega lähim suletud lähtekoodiga võrdluspunkt Picovoice Porcupine \cite{...}."

---

**2. Asukoht:** `introduction.tex`, lõik 4 (lause "Seetõttu tuleb lisaks klassikalistele mõõdikutele...")

*   **Algne:** "Seetõttu tuleb lisaks klassikalistele mõõdikutele hinnata ka valevallandumisi pika taustahelisalvestuse (ingl \emph{ambient audio}) peal, mõõdetuna FAPH-mõõdikuga (ingl \emph{false accepts per hour}, valevallandumiste arv tunnis), mis on pidevas helivoo režiimis äratussõna tuvastuse kirjanduses laialt kasutatav raportimisviis, mille kohta annab ülevaate \cite{lopezespejo2021deepkws}, kuna kodukasutuses on kasutajakogemuse jaoks määrav valevallandumiste tihedus ajaühikus, mitte nende osakaal testklippides; konkreetse näitena andis v6 mudel MacBook~Pro mikrofoni 40-minutilisel tavakõne testil FAPH~$\approx$~50 (vt §\ref{sec:cross-mic-asymmetry})."
*   **Probleem:** üks lause, kuhu on kuhjatud määratlus, viide, põhjendus ja näide; kaks sulgudes võõrkeelset terminit; lause kaotab loetavuse paranduslause "kuna kodukasutuses..." ja semikooloniga lisatud näite tõttu juba enne lõppu.
*   **Parandus:** "Seetõttu tuleb lisaks klassikalistele mõõdikutele hinnata valevallandumisi pikal taustahelisalvestusel (ingl \emph{ambient audio}). Mõõdikuks on FAPH (ingl \emph{false accepts per hour}, valevallandumiste arv tunnis) — pidevas helivoo režiimis laialt kasutatav raportimisviis \cite{lopezespejo2021deepkws}. Põhjus on lihtne: kodukasutuses määrab kasutajakogemuse valevallandumiste tihedus ajaühikus, mitte nende osakaal testklippides. Näiteks andis v6 mudel MacBook~Pro mikrofoni 40-minutilisel tavakõne testil FAPH~$\approx$~50 (vt §\ref{sec:cross-mic-asymmetry})."

---

**3. Asukoht:** `third_chapter.tex`, §\ref{sec:agent-based} ("Agentpõhine arendus kui töövõimendaja"), esimene lõik

*   **Algne:** "Eelnevalt kirjeldatud stsenaariumipõhine hindamistoru, valevallandumiste logija ja taustaheli korpuse tööriistastik ei oleks üksiku autori jaoks olnud selles mahus jõukohased ilma agentpõhise tarkvaraarenduseta, mistõttu järgnev osa on pigem eelneva metoodikaargumendi tehniline järellugu kui iseseisev kõrvalpõige."
*   **Probleem:** topeltlisandus ja meta-meta-kommentaar ("järgnev osa on pigem ... kui iseseisev kõrvalpõige"). Lause põhiväide upub ettevaatlikkuse-pesasse; nominaalstiil ("hindamistoru ... tööriistastik ei oleks olnud jõukohased").
*   **Parandus:** "Eelnevalt kirjeldatud stsenaariumipõhist hindamistoru, valevallandumiste logijat ja taustaheli korpuse tööriistastikku ei oleks üksik autor selles mahus suutnud ilma agentpõhise tarkvaraarenduseta välja ehitada. Järgnev osa on seetõttu eelneva metoodikaargumendi tehniline järellugu, mitte iseseisev kõrvalpõige."

---

**4. Asukoht:** `first_chapter.tex`, §\ref{subsec:faph-variants} avalause

*   **Algne:** "Käesolevas töös eristatakse nelja FAPH-i mõõdiku varianti, mille loendusreegel ja runtime-loogika erinevad ning mis ei ole otseselt vastastikku võrreldavad \cite{...}."
*   **Probleem:** kolm relatiivlauset ("mille ... ja ... mis"), passiivkonstruktsioon "eristatakse" ühendub keerukate omadustega; kogu pikk lisand muutub raskesti haaratavaks.
*   **Parandus:** "Käesolev töö eristab nelja FAPH-i varianti. Need erinevad loendusreegli ja runtime-loogika poolest ega ole seetõttu otseselt võrreldavad \cite{...}."

---

**5. Asukoht:** `second_chapter.tex`, §\ref{sec:benchmark-gap}, alapunkt "Põhjus 1", lause 4

*   **Algne:** "Reaalsete ütluste silutud skoorid jäid katseprotokolli alusel juurutamislävega võrreldava suurusjärku juurde, mis tähendab, et lävel cutoff\,$\geq$\,0,97 jääb osa ütlusi piirile lähedale või allapoole piiri (täpne ütluse-tasandi skoorijaotus pole eraldi artefaktina fikseeritud)."
*   **Probleem:** "võrreldava suurusjärku juurde" on kohmakas ja sisuliselt vigane vorm ("suurusjärku juurde" → kas "suurusjärku" või "lähedale"); peamine väide kaob eessõnade kuhja ja sulgudes-täpsustuse alla.
*   **Parandus:** "Reaalsete ütluste silutud skoorid jäid katseprotokolli alusel juurutamislävega samasse suurusjärku. See tähendab, et lävel cutoff\,$\geq$\,0{,}97 jääb osa ütlusi piiri lähedale või selle alla. Ütluse-tasandi täpne skoorijaotus pole eraldi artefaktina fikseeritud."

---

**6. Asukoht:** `second_chapter.tex`, §\ref{sec:agent-based}, kolmas lõik (lause "Käesoleva töö üks keskseid järeldusi ongi...")

*   **Algne:** "Käesoleva töö üks keskseid järeldusi ongi, et tänapäevane agentpõhine tööviis nihutab peamise pudelikaela teostuselt tõendusmaterjalile: üksi töötav autor võib ehitada lühikese ajaga oluliselt laiema tehnilise süsteemi kui varem, kuid lõppjärelduste tugevus sõltub endiselt sellest, kui hästi on korraldatud pärisandmete kogumine, hindamismetoodika ja esialgsete tulemuste eristamine lõplikest väidetest."
*   **Probleem:** ühe lausesse pakitud topeltkonstruktsioon (koolon + "kuid"); "sellest, kui hästi on korraldatud" on tüüpiline nominaalstiil ja kantseliit; lause venib üle 50 sõna.
*   **Parandus:** "Üks töö keskseid järeldusi ongi, et agentpõhine tööviis nihutab peamise pudelikaela teostuselt tõendusmaterjalile. Üksi töötav autor võib lühikese ajaga ehitada oluliselt laiema tehnilise süsteemi kui varem. Lõppjärelduste tugevus sõltub aga endiselt sellest, kui hoolikalt on kogutud pärisandmed, kavandatud hindamismetoodika ja eristatud esialgsed tulemused lõplikest väidetest."

---

**7. Asukoht:** `first_chapter.tex`, §\ref{sec:user-test-methodology}, esimene lõik (lause "Iga osaleja sessioon sisaldab...")

*   **Algne:** "Iga osaleja sessioon sisaldab viit puhast äratussõna ütlust, viit sihtfraasiga foneetiliselt sarnast negatiivfraasi, kuut skriptitud pirnikäsku ning ühte vabas vormis valgusülesannet."
*   **Probleem:** loend on grammatiliselt korrektne, kuid liige "vabas vormis valgusülesannet" on tähenduslikult häguselt sõnastatud — "valgusülesanne" jääb terminina abstraktseks ja eeldab konteksti, mida lugejal pole. Liiga tihe loend ilma loendipunktideta.
*   **Parandus:** "Iga osaleja sessioon sisaldab viit puhast äratussõna ütlust, viit sihtfraasiga foneetiliselt sarnast negatiivfraasi, kuut skriptitud käsku nutipirnile ning ühe vabas vormis valgustusülesande."

---

**8. Asukoht:** `first_chapter.tex`, §\ref{sec:model-architecture}, esimese lõigu lõpp

*   **Algne:** "Erinevalt tavalisest kahedimensioonilisest konvolutsioonist jagab SVDF-kiht ajalise ja sagedusmõõtme töötluse kaheks eraldiseisvaks operatsiooniks: esmalt rakendatakse aja dimensioonis süvakonvolutsiooni (\emph{depthwise convolution}), seejärel sageduse dimensioonis punktkonvolutsiooni (\emph{pointwise convolution})."
*   **Probleem:** kaks järjestikust passiivkonstruktsiooni ("rakendatakse ... rakendatakse"); "ajalise ja sagedusmõõtme töötluse" on raske nominaaltarind, mille võiks lihtsamalt sõnastada.
*   **Parandus:** "Erinevalt tavalisest kahedimensioonilisest konvolutsioonist eraldab SVDF-kiht aja- ja sagedusmõõtme töötluse: esmalt teeb mudel ajadimensioonis süvakonvolutsiooni (\emph{depthwise convolution}), seejärel sagedusdimensioonis punktkonvolutsiooni (\emph{pointwise convolution})."

---

**9. Asukoht:** `summary.tex`, neljas lõik

*   **Algne:** "Korrigeeritud hindamine näitas, et mudelivalik sõltub tugevalt sellest, millist omadust optimeerida."
*   **Probleem:** "sõltub sellest, millist omadust optimeerida" on tüüpiline kantseliitne nominaalkett ("sõltub sellest"). Lause on üldjoontes loetav, kuid stiililt nõrk just kokkuvõttes, kus mõte peaks olema teritatud.
*   **Parandus:** "Korrigeeritud hindamine näitas, et mudelivalik sõltub tugevalt valitud optimeerimissihist."

---

**10. Asukoht:** `summary.tex`, viies lõik (konsensus-lause)

*   **Algne:** "Seetõttu katsetati töö praktilise laiendusena ka spetsialiseeritud ekspertmudelite konsensust, mis vähendas vääraktiveerimisi märgatavalt ja saavutas Common Voice eesti keele hold-out kõnel FAPH~$=$~0{,}79, kuid tegi seda saagise arvelt."
*   **Probleem:** algab passiiviga "katsetati ... konsensust"; "praktilise laiendusena" on määrustetäide; "tegi seda saagise arvelt" sõltub eelnevast subjektist (konsensus), kuid grammatiliselt on subjekt ebamäärane. Kokkuvõttes liiga venitatud.
*   **Parandus:** "Seetõttu katsetati ka spetsialiseeritud ekspertmudelite konsensust. See vähendas vääraktiveerimisi märgatavalt ja andis Common Voice eesti keele hold-out kõnel FAPH~$=$~0{,}79, kuid saagise arvelt."

---

### Kokkuvõte top-10 mustritest

Sagedasimad mustrid auditeeritud tekstis on:

1.  **ülipikad mitme-vastandusega laused** ("Ehkki ... ning ..., ei ... ega ..."), kuhu pakitakse kolm väidet ja neli viidet — vt #1, #2, #6;
2.  **passiivi ja nominaalstiili kuhjumine** ("eristatakse", "rakendatakse ... rakendatakse", "sõltub sellest, kui hästi on korraldatud") — vt #4, #6, #8, #9;
3.  **meta-kommentaarid lause sees** ("järgnev osa on pigem ... kui iseseisev kõrvalpõige") — vt #3;
4.  **eessõnade kuhi ja vigased vormid** ("võrreldava suurusjärku juurde") — vt #5.

---

## 2. Sõna "kaardistama" audit

Otsisin kõigist auditeeritud failidest sõnu "kaardista*", "kaardistus", "mapping", "kaart". Tähenduses "tutvuma / ülevaadet tegema / kirjeldama / tuvastama" kasutatud lauseid **ei leidunud**.

Lähimad pinnakontaktid ja nende staatus:

*   `second_chapter.tex`, §\ref{sec:contribution-transferability}, esimene lõik: "Käesoleva töö dokumenteeritud protokoll --- (a) sõltumatu kõrvalejäetud komplekti kontroll, (b) positiivse andmestiku sisuline audit ja (c) mitmekriteeriumiline kontrollpunkti valik --- on **kohaldatav** kõigile sarnastele projektidele." — Sõna "kohaldatav" on kasutatud korrektselt sihituse mõttes "rakendatav"; ei ole "kaardistama" tähenduses.
*   `abstract-english.tex`, kokkuvõte: "an empirical **mapping** of the trade-offs between recall, target-similar negative rejection, prefix and confusable false positives, and false activations". — See on inglise keelne abstrakt, kus "mapping" tähistab kompromisside *empiirilist kirjeldust / kompromissiruumi joonistamist*. Eestikeelses abstraktis (`abstract-estonian.tex`) on sama mõte sõnastatud kui "empiiriline **kirjeldus** kompromissidest", mis on stilistiliselt korrektsem ja vastab parandusprintsiibile. Eestikeelne tekst ei vaja seega muudatust; ingliskeelne "mapping" on metafoorses tähenduses, kuid kuna see esineb ainult ingliskeelses abstraktis, jääb see käesoleva eesti keele auditi reguleerimisalast välja.

**Auditi tulemus:** sõna "kaardistama" pole eestikeelses tekstis ülekantud või ebamäärases tähenduses kasutatud. Parandust ei vaja ükski lause.

---

## Kokkuvõtlik soovitus toimetajale

*   Suurim lihvimisvõit on **introduction.tex** esimese ja neljanda lõigu pikalause-lammutus (#1, #2). Need kaks lauset jätavad kogu sissejuhatusele raske mulje; nende lühendamine parandab loetavust märgatavalt.
*   **Summary.tex** sisaldab ainult kahte top-10 lauset (#9, #10), kuid kokkuvõtte stiililine teritamine on lugejakogemuses võimendatud — toimetada esmajärjekorras.
*   **Second_chapter.tex** §\ref{sec:agent-based} esimene lause (#3) sisaldab metakommentaari, mille võiks tervikuna kustutada või eraldi lauseks tõsta — see on kõige selgem nominaalstiili näide tekstis.
*   "Kaardistama"-auditist tulenevaid muudatusi ei ole vaja teha.
