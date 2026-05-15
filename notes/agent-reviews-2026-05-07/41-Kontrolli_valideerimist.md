---
source_prompt: 04_Kontrollimine/Konkreetsed_vead/Sisu/Kontrolli_valideerimist.txt
prompt_type: evaluative
generated: 2026-05-07
---

# Tulemuste valideerimise audit

## 1. Hinnang

**Hinne:** 6{,}5/10

*(Skaala: 0 = valideerimine puudub; 5 = tehtud on vaid \enquote{demo}; 10 = põhjalik, mitmekülgne ja veenev tõestus.)*

Põhjendus: töös on selgelt eraldi valideerimispeatükk ja korralik metoodika, läbi viidud on mitmekihiline tehniline valideerimine (avalik kontrollkatse, kõrvalejäetud komplektid, taustaheli FAPH, raskete negatiivnäidete test, ekspertkonsensus, ${\sim}99$~h Android-välikatse, mitu ablatsiooni). Sellest punktid üle keskmise. Hindelangetajad: peamine \emph{kasutuspõhine} valideerimine --- 20--30 osalejaga sõltumatu kasutajatest --- on ülesandepüstituses lubatud, kuid esitamise hetkel veel teostamata; kasutajauuringut peale autori on kasutatud ainult kahe-kolme autori-lähedase kõneleja (autor, Kõneleja B, ühe \texttt{pos\_speaker\_d} komplekti $N=145$) tasemel. Bakalaureuseprofiilil on see veel piiri peal, ent ei ulatu \enquote{põhjaliku ja veenva tõestuse} tasemeni.

## 2. Analüüs

### Hetkeseis

Autor on valideerinud lahendust mitmel teljel:

- **Toru valideerimine** avaliku \texttt{Speech Commands}/\texttt{marvin} kontrollkatsega enne eestikeelse mudeli juurde liikumist.
- **Andmelekke audit** (§\ref{sec:data-leakage}) ja sõltumatud kõrvalejäetud testikomplektid; treening- ja testandmete disjointsuskontroll.
- **Voogedastushindamine FAPH-iga** Common~Voice ET kõrvalejäetud korpusel (üksikmudelite tabelid \texttt{tab:fair-comparison-holdout}, \texttt{tab:expert-individual}); FAPH-i nelja varianti eristatakse selgelt (§\ref{subsec:faph-variants}).
- **Statistilised intervallid:** Wilsoni skoor proportsioonidele ja Poissoni--Garwoodi vahemik FAPH-ile; \enquote{kolme reegel} nullsündmuste juures.
- **Ekspertmudelite konsensus} (Common~Voice ET FAPH = 0{,}79; tabel~\ref{tab:expert-consensus}).
- **Risti-mikrofoni ja keele-üleste tingimuste kontroll** (§\ref{sec:cross-mic-asymmetry}, \texttt{tab:cross-language-faph}).
- **Ablatsioonid:} residuaalühendused (\texttt{tab:residual-ablation}), SpecAugment (\texttt{tab:specaug-ablation}), v13a/v13b kontroll-ablatsioon.
- **Fraasi-täielikkuse protokoll} (teine auditiring, §\ref{sec:second-audit}): prefiksi-, üksiku sõna, pööratud järjekorra ja \enquote{kuule}/\enquote{kule} segiajamise mõõdikud.
- **Kontrollpunktivaliku audit} (kolmas auditiring, §\ref{sec:third-audit}; \texttt{tab:checkpoint-headline}, \texttt{tab:checkpoint-consensus}).
- **Välikatse:} ${\sim}99$~h Android-logija jälgimisseanss (FAPH 0{,}58 \texttt{v6-residual} ja 2{,}79 \texttt{expert-a} kohta).
- **Kirjandusega võrdlus:} arutelupeatükk seob leiud Park~\cite{park2024adversarial}, Dubois~\cite{dubois2020triggers}, Sch{\"o}nherr~\cite{schoenherr2022accidental}, Apple~\cite{shrivastava2021optimize}, MISP~\cite{chen2022misp} jt allikatega.

### Tugevused

- **Eraldi struktuurselt eristatud valideerimine:** sissejuhatuses sõnastatud sihid (FAPH$<$1, recall$\geq$0{,}95) on tulemustepeatükis numbriliselt vastatud (FAPH = 0{,}79 saavutatud; recall avatud).
- **Sidusus uurimisküsimustega:** sissejuhatuse alaküsimused (\enquote{kuidas valideerida toru enne EE andmestikku}; \enquote{kuidas eristada andmestiku probleeme tehnilistest piirangutest}) on otseselt lahti kirjutatud kolme auditiringi loogikana.
- **Triangulatsioon:} klipipõhine FPR + voogedastus-FAPH + välikatse FAPH + kontrollkatse + ekspertkonsensus + fraasi-struktuuri testid; ühe mõõdiku tugevdamine ei kompenseeri teisi.
- **Sügavus:** valideerimine ei piirdu funktsionaalse \enquote{töötab/ei tööta} testimisega: ülal-paisutusvaadeldud (Wilsoni/Poissoni intervallid), ülesobitusriskid (lävi ainult valideerimiskomplektil), domeeninihke ja mikrofoniefektide eraldi käsitlus.
- **Aus piiride käsitlus:} §\ref{sec:fourth-round} (\enquote{neljas ring}) ja \enquote{Mida saab juba praegu väita} loetelu rõhutavad, et kasutuspõhine valideerimine ei ole veel teostatud --- see on metoodiliselt korrektne distsipliin.
- **Kirjandusega võrdlus on substantiivne:} Dubois 0{,}95 FA/h tulemused, Sensory tunnistus, MISP Challenge põhimõtted on töö numbriga seotud, mitte ainult viidatud.

### Kriitilised puudujäägid

1. **Osapoolte puudus.** Ülesandepüstitus lubab \enquote{kasutuspõhist valideerimist erinevate kõnelejatega} ja kavandatud 20--30 osalejaga test on §\ref{sec:user-test-methodology}-s põhjalikult kirjeldatud, kuid §\ref{sec:user-test-results} tunnistab otse, et täismahus andmestik ei ole esitamise hetkel veel olemas. Praktiliselt sõltub töö \enquote{päris-kasutuse} valideerimine kahest autori-lähedasest kõnelejast pluss \texttt{pos\_speaker\_d} ($N=145$) komplektist. Kaitsmiskomisjonile on see kõige nõrgem koht --- \enquote{Kule}-vormi tuvastamismäär on tunnistatud avatud peamise riskina, aga see ei ole tegelikult sõltumatult mõõdetud.

2. **Recall-sihi (${\geq}\,0{,}95$) saavutamise tõendus on lünklik.** Sissejuhatus seab kaks ühendsihti (FAPH$<$1 \emph{ja} recall$\geq$0{,}95). FAPH-pool on saavutatud (0{,}79), kuid recall on tugev TTS-positiivsetel klippidel ($\sim$1{,}0000) ja madal \enquote{Kule}-hääldusel; seda kompromissi tunnistatakse, kuid sihti ennast ei ole ühtegi kõnelejakogumi peal samaaegselt täidetud. Töö ütleb seda küll otse, ent see jätab \enquote{usaldusväärne} keskse väite formaalselt avatuks.

3. **Subjektiivse rahulolu mõõtmine on planeeritud, mitte teostatud.** UMUX-Lite, sessioonijärgsed Likert-küsimused on kavandatud, kuid puuduvad andmed. See vähendab kasutusmugavuse-telje hindamise sügavust.

4. **Latentsuse mõõtmine on alaesindatud.** Ülesandepüstitus mainib latentsust \enquote{tehnilise valideerimise} all. Mudelite latentsust ESP32-S3 peal seadme-sees mõõdetuna ei ole tabelina raporteeritud (mainitud on tensor\_arena suurusjärk ja teostatavus, kuid mitte konkreetset latentsuse arvu \texttt{ms}-des koos jaotusega).

5. **Mittekõneliste helide süstemaatiline test puudub.} §3.\ref{sec:benchmark-gap} tunnistab seda otsesõnu (\enquote{süstemaatilist aktivatsioonimäära mittekõnelistel stiimulitel käesolevas töös eraldi ei mõõdetud}). See on \emph{teadlik} piir, kuid jätab valideerimise neljanda telje katmata.

6. **Konsensuse FAPH = 0{,}79 statistiline pinge.} Töö tunnistab, et Poissoni 95\% vahemik on \enquote{lai}; kvantitatiivset arvuvahemikku tekstis ei ole välja toodud (kuigi metoodika seda nõuab). See on punkthinnang ühel korpusel ja ühel operatsioonipunktil --- mainitud, aga visualiseerimata.

7. **Generaliseeruvus väikse kõnelejate baasi tõttu.} \enquote{15+ mudeliversiooni} võrdlus ja ablatsioonid on metoodiliselt rikkad, kuid kõik rajanevad kitsa kõnelejate ringi peal --- klipipõhise hindamise piiride tunnistamine on aus, kuid kompenseerivat välist valideerimist (sõltumatu kasutajatest) selle vastu pole esitada.

## 3. \enquote{Kiirabi} plaan (teostatav 24~h jooksul)

1. **Pilooditesta vähemalt 3--5 mitte-autori-lähedast osalejat olemasoleva \texttt{kratt user-test} tööriistaga ja lisa tulemused §\ref{sec:user-test-results}.} Ka väike $N=3\!-\!5$ ($\sim$25--40 ütlust) annab Wilsoni intervalli ning eemaldab puhta-puuduse-süüdistuse: see on \emph{mingisugune} sõltumatu tõend, mitte tühi tabel. Eraldi raporteeri \enquote{Kuule}- ja \enquote{Kule}-hääldused.

2. **Lisa konkreetne Poissoni 95\% usaldusvahemik FAPH = 0{,}79 ümber} (Garwood; $T=$ tabelis~\ref{tab:expert-consensus} olev hindamisaeg). See annab tekstinumbri, mis muudab \enquote{lai vahemik}-väite kontrollitavaks ja seotud rangelt § \ref{subsec:faph-variants} loendusreegliga.

3. **Mõõda olemasoleva ESPHome \texttt{v16c} seadistuse latentsus} (50/95/99 protsentiili) lihtsa silmukulisemise skripiga (Korvo-2 äratus → wake-event), kasvõi $N=30$ käsiäratust. Lisa üheks tabelina §3.7 lõppu või tulemustepeatükki. See sulgeb ülesandepüstituse \enquote{latentsus} lubaduse.

4. **Tee minimaalne mittekõneliste helide \enquote{audit-batch}} olemasolevatest MUSAN/VOiCES klippidest (nt 30~min muusikat, 30~min koduse keskkonna helisid) ja raporteeri FAPH neil radadel. See ei nõua uut salvestust, kasutab juba laaditud korpust ning lisab Põhjus 4 alajaotusele empiirilise toetuse.

5. **Lisa otsesõnu \enquote{ohutu kasutamise} alajaotus arutelu peatükki}, mis kaardistab konkreetselt: (a) milliseid väiteid saab teha praeguste tõendite najal, (b) milliseid ainult pärast täismahus kasutajatesti, (c) milliste väidete maht on \emph{ülespoole piiratud} kahe autori-lähedase kõneleja andmetega. Sellega muutub puudus kontrollitud piiranguks, mitte varjatud nõrkuseks.

6. **Heuristiline hindamine (kognitiivne läbikäik) ühe kogenud kõrvalseisja poolt} (juhendaja, kursusekaaslane): 15--20 minutit, lihtne SUS- või UMUX-Lite vorm. Üks lisahääl on metoodiliselt parem kui null sõltumatut häält. Raporteeri ausalt $N=1\!-\!2$ ja kasutuselevõtu tagasiside vormingus, mitte üldistavate skooridena.

7. **Sõnasta FAPH$<$1 ja recall$\geq$0{,}95 sihtide saavutamise staatus eraldi tabelina} \enquote{Mida saab juba praegu väita} kõrvale: roheline/kollane/punane skeem mõõdiku, korpuse ja kõneleja-allika kaupa. See aitab komisjonil kiiresti aru saada, kus tõestus seisab ja kus on lünk --- sama info on tekstis olemas, kuid pole ühe pilguga kontrollitav.

8. **Kontrolli järjepidevust:** veendu, et iga numbri (FAPH = 0{,}79; recall; FPR-väärtused; v6 ${\sim}50$ FAPH; v6-residual 0{,}58; expert-a 2{,}79) raporteerimisel on tabelis või joonealuses märgitud (a) korpus, (b) lävi, (c) FAPH-i variant. Suuremas osas tehtud, kuid kontrolli viimane lugemisring tasub teha enne esitamist --- sissejuhatuses olev v6 ${\sim}50$ FAPH tekst peaks olema sõnaselgelt seotud raamistiku/skriptitud variandiga.
