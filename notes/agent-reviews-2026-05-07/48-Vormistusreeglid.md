---
source_prompt: 04_Kontrollimine/Konkreetsed_vead/Vorm/Vormistusreeglid.txt
prompt_type: evaluative
generated: 2026-05-07
---

# Vormistusreeglite kontroll TalTech IT-teaduskonna juhendi (2020) järgi

## Kontrolli ulatus ja piirangud

Promptis eeldatakse PDF-formaadis lõputööd ja viidatakse leheküljenumbritele. Käesolev kontroll põhineb LaTeX-allikfailide alamhulgal (sissejuhatus, peatükid 1–3, kokkuvõte, eesti- ja ingliskeelne annotatsioon, ülesandepüstitus). Allikfailides ei ole otseselt kättesaadavad järgmised vormistuselemendid:

- tiitelleht (genereeritakse mallifailist `thesis.cls` / `\maketitle` makrodest, mida käesolevas kontrollis ei loetud);
- autorideklaratsioon (eraldi mallifail);
- lihtlitsentsi lisa;
- sisukord, jooniste ja tabelite loetelud (genereeritakse automaatselt);
- leheküljenumeratsioon, fondid, veerised, reavahed.

Kontrollin AINULT neid reeglirikkumisi, mille saan tuvastada loetud `.tex`-failide tekstist. Kõik täheldatud rikkumised viitan failile ja reale, mitte PDF-i leheküljenumbrile, sest kompileeritud PDF-i ei ole kontrolli käigus genereeritud. Kus reegel on PDF-tasemel kontrollitav (nt tiitellehe leheküljenumeratsiooni nähtavus), märgin selle eraldi kui „mitte kontrollitav allika tasemel".

---

## I. Üldine struktuur ja järjestus

Allikast loetud failidest leitavad osad: sissejuhatus, kolm peatükki, kokkuvõte, eestikeelne annotatsioon, ingliskeelne annotatsioon (Abstract), eraldi ülesandepüstituse fail. Kohustuslikest osadest EI OLE allikast otseselt nähtavad: autorideklaratsioon, lühendite ja mõistete sõnastik, sisukord, jooniste loetelu, tabelite loetelu, kasutatud kirjanduse loetelu (`references.bib` on olemas, kuid loetelu paigutust ei kontrollitud), Lisa 1 (Lihtlitsents). Need on tõenäoliselt mallis, kuid kontroll ei saa kinnitada nende olemasolu ega järjestust.

**Tähelepanek (struktuur):** ülesandepüstitus (`ylesandepystitus.tex`) on koostatud iseseisva dokumendina (`\documentclass[12pt]{report}` koos `\begin{document}`/`\end{document}`-iga). Juhendi kohaselt peab ülesandeleht — kui see on tööle lisatud — paiknema autorideklaratsiooni järel, ENNE annotatsioone, ühe ja sama köitepuu sees. Allikast ei selgu, kas see fail kompileeritakse põhitöö PDF-i sisse või jäetakse eraldiseisvaks. Kui see on eraldi PDF, siis põhitöö PDF-is ülesandelehte tõenäoliselt ei ole — see ei oleks reeglirikkumine, sest ülesandeleht on valikuline. Kui aga eraldi PDF-i tahetakse esitada koos lõputööga, tuleb kontrollida, et selle paigutus vastaks juhendile.

---

## II. Tiitelleht

**Mitte kontrollitav allika tasemel** loetud failide hulgast. Ülesandepüstituse failis on titlepage-keskkond, mis sisaldab:

- `\universityEst` ja `\schoolEst` (peaks vastama „TALLINNA TEHNIKAÜLIKOOL" + „Infotehnoloogia teaduskond");
- autori nimi (`\authorNameEst`) ja üliõpilaskood (`\studentcodeEst`);
- pealkiri (`\thesisTitleEst`);
- töö liik („Bakalaureusetöö ülesandepüstitus");
- juhendaja andmed (`\supervisorNameEst`, `\supervisortitleEst`);
- linn („Tallinn") ja aastaarv (`\Year`).

Need elemendid VASTAVAD juhendi nõuetele, eeldusel et makrod sisaldavad korrektseid väärtusi. Põhitöö tiitellehte ei ole kontrolli ulatuses ja seda tuleb eraldi PDF-is kinnitada.

---

## III. Lehekülgede nummerdamine

**Mitte kontrollitav allika tasemel.** LaTeX-mall vastutab numeratsiooni eest. PDF-is tuleb kontrollida, et:

- tiitellehel ei ole nähtavat numbrit;
- alates teisest lehest on number nähtav lehe allosas keskel;
- numeratsioon on läbiv kuni viimase lisani.

---

## IV. Autorideklaratsioon

**Mitte kontrollitav allika tasemel.** Autorideklaratsiooni faili ei loetud. PDF-is tuleb kontrollida pealkirja, kohustusliku teksti ja kuupäeva formaati `pp.kk.aaaa`.

---

## V. Annotatsioonid

### V.1 Eestikeelne annotatsioon (`abstract-estonian.tex`)

**Vastab nõuetele:**

- lõpulause kasutab korrektset struktuuri ja `\langEst`, `\calculatepages`, `\total{totalchapters}`, `\total{figure}`, `\total{table}` makrosid (read 12–17);
- struktuur „kirjutatud … keeles ning sisaldab teksti … leheküljel, … peatükki, … joonist, … tabelit" on olemas.

**Mitte kontrollitav:** pealkirja vorming („Heading_center", tsentreeritud, nummerduseta, uuelt leheküljelt) sõltub mallist.

### V.2 Ingliskeelne annotatsioon (`abstract-english.tex`)

**Vastab nõuetele:**

- lõpulause järgib struktuuri „The thesis is in [language] and contains [pages] pages of text, [chapters] chapters, [figures] figures, [tables] tables." (read 11–16).

**VÕIMALIK RIKKUMINE — VI/V.4:** juhendi punkt V.4 ütleb: „Kui on võõrkeelne annotatsioon, peab annotatsiooni sisu ja pealkirja vahel olema töö võõrkeelne pealkiri." Loetud failis (`abstract-english.tex`) ON ainult sisu, võõrkeelset pealkirja faili sees EI OLE. Tõenäoliselt sisestab pealkirja mall (`\selectlanguage{english}` + `\begin{abstract}` makro), kuid ALLIKAST ei näe seda kinnitust. **Soovitus:** kontrollida kompileeritud PDF-is, et ingliskeelse annotatsiooni kohal oleks töö ingliskeelne pealkiri eraldi reana enne sisu.

---

## VI. Lühendite ja mõistete sõnastik

**Mitte kontrollitav allika tasemel.** Vastav fail ei kuulunud kontrolli sisendisse. Töö sisus kasutatakse mitut võõrkeelset terminit (nt `wake word`, `streaming inference`, `pipeline`, `false accepts per hour`, `pre-context`, `vanishing gradients`, `redundant`, `kernel size`, `repeat_in_block`, `tensor_arena`, `temporal reduction`, `pointwise convolution`, `depthwise convolution`, `ground truth`, `pseudonüümne` jt), mis on tekstis seletatud sulgudes või kursiivis. Kui töös on jaotis „Lühendite ja mõistete sõnastik", peab see olema kahe veeruga tabel ja sorteeritud tähestiku järjekorras. **Soovitus:** veendu, et FAPH, FRR, FPR, AUC, KWS, MCU, ASR, VAD, INT8, ONNX, TFLite, MFCC, SVDF, MixedNet, BC-ResNet, ESP32-S3 ja teised tekstis ühe korra defineeritud lühendid oleksid sõnastikus tähestikulises järjekorras.

---

## VII. Sisukord, jooniste ja tabelite loetelud

**Mitte kontrollitav allika tasemel.** Genereerib mall.

**Tähelepanek:** kolmandas peatükis viidatakse korduvalt tabelitele (`tab:full-comparison`, `tab:checkpoint-headline`, `tab:expert-consensus`, `tab:fair-comparison-holdout`, `tab:model-versions`) ja sektsioonidele teise peatüki sees (`subsec:quantization`, `sec:cross-mic-asymmetry`). Kui nendes tabelites on tegelik sisu (mida käesolevas kontrollis ei näinud), peab olema **tabelite loetelu** sisukorra järel — see on kohustuslik, kui töös on tabeleid.

---

## VIII. Peatükkide pealkirjad ja numeratsioon

### VIII.1 Numeratsioon

Allikast nähtud peatükkide failid kasutavad `\section{...}` ja `\subsection{...}` makrosid (LaTeX nummerdab need automaatselt). VASTAB nõudele „araabia numbritega".

### VIII.2 Pealkirjale järgneb tekst

**RIKKUMISED — VIII.5:**

Juhend nõuab, et iga peatüki/alapeatüki pealkirjale järgneks vahetult tekst, mitte teine pealkiri.

- **`second_chapter.tex` rida 77–79:** `\section{Mudeli arhitektuur}` (rida 77–78) järgneb tavateksti lõik (rida 80) — see on KORRAS. Aga selle järel `\subsection{MixedConv plokid}` (rida 82) tuleb pärast tavateksti lõiku — KORRAS.
- **`second_chapter.tex` rida 90–91:** `\subsection{Voogedastusrežiim}` (rida 90) järgneb `\label{...}` (rida 91) ja siis tekst (rida 93) — KORRAS.
- **`third_chapter.tex` rida 91–94:** `\section{Mitmemõõtmeline hindamisprotokoll …}` (rida 91), `\label{...}` (rida 92), seejärel `\subsection{Kolm valideerimiskihti: muster}` (rida 96) järgneb pärast tavateksti lõiku (rida 94) — KORRAS.
- **`third_chapter.tex` rida 96–99:** `\subsection{Kolm valideerimiskihti: muster}` (rida 96), `\label{...}` (rida 97), seejärel tavatekst (rida 99) — KORRAS.

**KÕIK loetud peatükid järgivad reeglit VIII.5** — pealkirjale järgneb alati tavatekst enne järgmist alampealkirja.

### VIII.3 Pealkirjade tasemete arv (VIII.6)

Juhend nõuab maksimaalselt kolme taset (peatükk, section, subsection). Loetud failides:

- `\section{...}` ja `\subsection{...}` on kasutusel — **2 taset alampeatükke** (peatükk + 2 alamtaset = kokku 3 taset). VASTAB nõudele.
- `\subsubsection{...}` makrosid loetud failides EI ESINE.

### VIII.4 Alapeatüki sisu (VIII.7)

Juhend ütleb: „Alapeatükk ei tohi sisaldada ainult ühte lõiku teksti."

Kontrollin loetud `\subsection{...}` plokke:

- **`second_chapter.tex` `\subsection{Kvantiseerimine}` (rida 122–127):** sisu on üks lõik (rida 125) ja teine lõik (rida 127). **2 lõiku → KORRAS.**
- **`second_chapter.tex` `\subsection{Kontekstiaken}` (rida 106–113):** kolm lõiku (read 109, 111, 113). KORRAS.
- **`second_chapter.tex` `\subsection{SpecAugment}` (rida 115–120):** kaks lõiku (read 118, 120). KORRAS.
- **`second_chapter.tex` `\subsection{Voogedastusrežiim}` (rida 90–95):** kaks lõiku (read 93, 95). KORRAS.
- **`second_chapter.tex` `\subsection{Residuaalühendused}` (rida 97–104):** kolm lõiku (read 100, 102, 104). KORRAS.
- **`second_chapter.tex` `\subsection{MixedConv plokid}` (rida 82–88):** kolm lõiku (read 84, 86, 88). KORRAS.
- **`second_chapter.tex` `\subsection{FAPH-i variandid ja loendusreegel}` (rida 62–73):** üks lõik järelloeteluga, lõpeb lõiguga (rida 71) ja eraldi lõik (rida 73). KORRAS.
- **`third_chapter.tex` `\subsection{Andmestiku põhipiirangud}` (rida 18–21):** kaks lõiku (read 19, 21). KORRAS.
- **`third_chapter.tex` `\subsection{Hindamise ja juurutuse põhimõtted}` (rida 23–28):** kolm lõiku (read 24, 26, 28). KORRAS.
- **`third_chapter.tex` `\subsection{Empiiriline tõendus lahknevusest}` (rida 36–42):** kolm lõiku. KORRAS.
- **`third_chapter.tex` `\subsection{Põhjus 1: ...}` (rida 44–48):** kaks lõiku. KORRAS.
- **`third_chapter.tex` `\subsection{Põhjus 2: ...}` (rida 50–54):** kaks lõiku. KORRAS.
- **`third_chapter.tex` `\subsection{Põhjus 3: ...}` (rida 56–58):** **AINULT ÜKS LÕIK.** **VÕIMALIK RIKKUMINE VIII.7** — alapeatükk „Põhjus 3: klipitaseme raskete negatiivsete näidete test ei kajasta streaming-konteksti" sisaldab vaid ühe lõigu teksti. **Soovitus:** lisada teine lõik või liita see eelnevasse alapeatükki.
- **`third_chapter.tex` `\subsection{Põhjus 4: mittekõneliste helide puudumine}` (rida 60–62):** **AINULT ÜKS LÕIK.** **VÕIMALIK RIKKUMINE VIII.7** — sama probleem nagu Põhjus 3-s. **Soovitus:** laiendada või liita.
- **`third_chapter.tex` `\subsection{Lahendusena: stsenaariumpõhine testimisvoog}` (rida 64–79):** mitu lõiku ja loend. KORRAS.
- **`third_chapter.tex` `\subsection{Kolm valideerimiskihti: muster}` (rida 96–105):** ülesehitus on üks sissejuhatav lõik (99) ja kolm lõiku „Esimene/Teine/Kolmas ring" (101, 103, 105). KORRAS.
- **`third_chapter.tex` `\subsection{Üldine printsiip: ...}` (rida 107–120):** mitu lõiku ja loend. KORRAS.
- **`third_chapter.tex` `\subsection{Töö-tasemel panus ja selle ülekantavus}` (rida 122–129):** kolm lõiku. KORRAS.
- **`third_chapter.tex` `\subsection{Aus piir: võimalik neljas ring}` (rida 131–136):** kaks lõiku. KORRAS.

### VIII.5 Esimese taseme pealkiri uuelt leheküljelt (VIII.2)

**Mitte kontrollitav allika tasemel** — sõltub mallist `\chapter`-makrost.

---

## IX. Joonised ja tabelid

**Loetud failides EI ESINE** ühtegi `\begin{figure}`, `\includegraphics`, `\begin{table}` ega `\caption{...}` makrot. Kõik viited tabelitele (nt `tab:full-comparison`, `tab:expert-consensus`) ja sektsioonidele toimuvad `\ref{...}`/`\cite{...}` kaudu. See tähendab, et joonised ja tabelid asuvad TEISTES failides (tõenäoliselt tulemuste peatükis, mida ei loetud), ja nende vormistust (allkiri, pealkiri, viide enne joonist/tabelit, paigutus samal leheküljel, võõrkeelne tekst kursiivis) ei ole võimalik kontrollida.

**Soovitus:** veendu eraldi tulemuste peatüki kontrollis, et:

- iga joonisel on allkiri vormingus „Joonis [number]. [Allkiri].";
- iga tabelil on pealkiri vormingus „Tabel [number]. [Pealkiri].";
- igale joonisele/tabelile on tekstis viide ENNE selle esitamist;
- numeratsioon on läbiv;
- võõrkeelne tekst joonistel/tabelites on kursiivis.

---

## X. Programmikood

**Loetud failides EI ESINE** programmikoodi blokke (`\begin{lstlisting}`, `verbatim` jms). Selle reegli rikkumisi ei ole võimalik allikast tuvastada.

---

## XI. Valemid

**Loetud failides EI ESINE** ühtegi `\begin{equation}`, `\[...\]` ega `$$...$$` valemit. Tekstis on inline-matemaatika (`$T$`, `$k=0$`, `$\sim 3/T$`, `${\sim}22\,000$`, `${\sim}107$\,KB`, `${\sim}99$~h`), kuid see EI OLE eraldi nummerdatud valem. Sissejuhatuse failis (rida 7) on inline `cutoff\,$\geq$\,0,97` jms — kõik on lauses sees, viiteta. Reegli XI rikkumisi (nummerdamata viidatud valemid) ALLIKAST EI TUVASTA.

---

## XII. Kasutatud kirjandusele viitamine

### XII.1 Tekstisisesed viited

LaTeX-allikas kasutatakse `\cite{...}`-makrot, mis BibLaTeXi/natbib seadetest sõltuvalt genereerib nurksulgudes numbrilised viited (nt `[5]`). Eeldades, et `thesis.cls` kasutab numbrilist viitestiili (mis on nõutav), VASTAB nõudele.

**Tähelepanek:** mitmes kohas on viited lause LÕPUS enne punkti, mis on KORRAS, näiteks:

- `sissejuhatus.tex` rida 1: „...\cite{taltech-asr-data2024,riigikogu-stenograms2025}." — KORRAS.
- `second_chapter.tex` rida 4: „...\cite{microwakeword2026}, mille all töötab TensorFlow \cite{tensorflow2015}." — KORRAS.

**VÕIMALIK RIKKUMINE — XII.2:** juhend ütleb „viide lause sees, mitte lause alguses ega eraldi lausena". Kontrollin, kas leidub viiteid eraldi lausena või lause alguses:

- **`third_chapter.tex` rida 48:** „Park et al.~\cite{park2024adversarial} on näidanud, et …" — viide lause keskel, KORRAS.
- **`third_chapter.tex` rida 54:** „Dubois et al.~\cite{dubois2020triggers} demonstreerisid …" — KORRAS.
- **`third_chapter.tex` rida 54:** „Sch{\"o}nherr et al.\ \cite{schoenherr2022accidental} kinnitavad …" — KORRAS.
- **`third_chapter.tex` rida 77:** „MISP Challenge~\cite{chen2022misp} loodi spetsiaalselt …" — KORRAS.
- **`third_chapter.tex` rida 103:** „Apple'i otsast-lõpuni DNN-HMM treening lisab partial-keyword … negatiivnäiteid just selleks, et mudel ei vallanduks osafraasidel ega vales järjekorras \cite{shrivastava2021optimize}." — KORRAS.

**Märkus:** `Park et al.\cite{...}` ja `Dubois et al.\cite{...}` stiil on aktsepteeritav, kui juhend ei nõua puhtnumbrilist „[N] on näidanud" stiili. TalTechi 2020 juhend võimaldab autori-nime + numbrilise viite kombineerimist, kuid mõned juhendid eelistavad „autorid [N] on näidanud" stiili. **Soovitus:** kontrolli juhendaja eelistust nimega-tsitaatide osas.

### XII.3 Kirjanduse loetelu pealkiri

**Mitte kontrollitav allika tasemel** — genereeritakse mallist.

---

## XIII. Lisad

**Mitte kontrollitav allika tasemel** — Lisa 1 (Lihtlitsents) ega muud lisad ei kuulunud loetud failide hulka.

**Tähelepanek:** kontrolli PDF-is, et:

- Lisa 1 on Lihtlitsents, esimene lisa;
- nurksulgudes platseholderid (`[Autori ees- ja perenimi]`, `[Lõputöö pealkiri]`, `[Juhendaja ees- ja perenimi]`, `[pp.kk.aaaa]`) on **asendatud konkreetsete väärtustega ilma nurksulgudeta**;
- igale lisale on põhitekstis viide.

---

## XIV. Teksti kasutamine

### XIV.1 Tühikud

Loetud failides ei tuvastanud topelttühikuid LaTeX-allikas (LaTeX kompresseerib niikuinii). KORRAS.

### XIV.2 Mõttekriips vs sidekriips

Juhend nõuab pikka mõttekriipsu (—, en-dash või em-dash) vahemike ja seletuste puhul.

**Tähelepanek:** loetud failides kasutatakse järjekindlalt **`---` (em-dash, kolm sidekriipsu)** seletuste sees:

- `sissejuhatus.tex` rida 1: „...rahvusvaheline kirjandus põhjalikult \cite{...}, ei kuulu …";
- `second_chapter.tex` rida 21: „...mälupiirangute vastu otseselt võrreldavad --- see asümmeetria on integreeritavuse telje tulemus, mitte selle puudus.";
- `third_chapter.tex` rida 4: „...peituda hoopis treeningutoru tehnilises piirangus --- täpsemalt samas voogedastushindamise...";
- `third_chapter.tex` rida 34: „...ei ole pelgalt metoodika ebaküpsuse artefakt --- tegemist on...";
- `third_chapter.tex` rida 79: „... ühe keele üks sõna ---\,...";
- `summary.tex` rida 7: „...vähendas vääraktiveerimisi märgatavalt ja saavutas Common Voice eesti keele hold-out kõnel FAPH~$=$~0{,}79, kuid tegi seda saagise arvelt." — siin EI OLE mõttekriipsu, tavaline tekst. KORRAS.

`---` on em-dash, mis on aktsepteeritav. Eesti keeles eelistatakse tihtipeale en-dash'i (`--`) seletuste puhul, kuid TalTechi juhend lubab mõlemat. **KORRAS, aga jälgi järjepidevust** — kogu tööd peab kasutama sama stiili (em-dash või en-dash).

**Vahemikud:** kontrollin numbrilisi vahemikke:

- `sissejuhatus.tex` rida 7: „lähikõne tuvastamismäära~$\geq$~0{,}95" — kasutab matemaatilist sümbolit, KORRAS.
- `second_chapter.tex` rida 41: „kuni 2 sagedusmaski laiusega kuni 3 riba" — kasutab sõna „kuni", KORRAS.
- `second_chapter.tex` rida 109: „194 ajakaadrit, 40 mel-sagedusribal" — KORRAS.
- `second_chapter.tex` rida 111: „0{,}8--1{,}2\,s" — kasutab `--` (en-dash) vahemikus. KORRAS.
- `second_chapter.tex` rida 111: „300--700\,ms" — KORRAS.
- `second_chapter.tex` rida 41 ja `third_chapter.tex` rida 134: „v1--v8", „v1--v6", „20--30 osalejat" — kasutab `--` (en-dash). KORRAS.

Vahemikes kasutatakse järjepidevalt `--` (en-dash) ja seletuste puhul `---` (em-dash). VASTAB juhendile.

### XIV.3 Komakohad numbrites

Loetud failides on järjepidevalt kasutatud koma kümnendkohas eesti keele konventsiooni järgi (`0{,}79`, `1{,}5`, `0{,}95`, `0{,}996`, `1{,}0000`, `0{,}4\%`). KORRAS.

**Tähelepanek (segastiil):** ühes kohas:

- `second_chapter.tex` rida 102: „96,9\%" — ilma `{}`-deta. Eesti keeles eelistatakse tühimatust koma ja arvu vahel, mis tagatakse `{,}` kasutamisega.

Üldiselt töö kasutab `{,}`-d, kuid see üksik koht („96,9\%") on otsekoma. **Soovitus:** ühtlustada `96{,}9\%`-ks.

### XIV.4 Kindlad tühikud (~)

Töö kasutab korrektselt `~`-d numbrite ja ühikute vahel (nt `0{,}79`, `5\,KB`, `148\,KB`, `45--50\,KB`, `1500\,ms`, `~h`). KORRAS.

---

## XV. Tabelid/joonised lisas

**Mitte kontrollitav allika tasemel** — lisad ja jooniste/tabelite loetelud ei kuulu loetud failide hulka.

---

## Kokkuvõte: tuvastatud rikkumised ja soovitused

### Tuvastatud potentsiaalsed rikkumised (kontrollitavad allikast)

1. **VIII.7 — alapeatükk ei tohi sisaldada ainult ühte lõiku:**
   - `third_chapter.tex` rida 56–58, alapeatükk „Põhjus 3: klipitaseme raskete negatiivsete näidete test ei kajasta streaming-konteksti" — ainult üks lõik.
   - `third_chapter.tex` rida 60–62, alapeatükk „Põhjus 4: mittekõneliste helide puudumine" — ainult üks lõik.
   - **Soovitus:** laiendada mõlemat alapeatükki teise lõiguga (nt streaming-konteksti puhul lisada konkreetne arvuline näide; mittekõneliste helide puhul lisada lõik tagajärgedest või mõõtmise puudujäägi tähendusest).

2. **XIV.3 (komakoha vorming) — järjepidevus:**
   - `second_chapter.tex` rida 102, „96,9\%" tuleks ühtlustada ülejäänud tööga vormi `96{,}9\%`.

### Tähelepanekud (vajavad PDF-tasemel kontrolli)

3. **V.4 — võõrkeelne pealkiri ingliskeelse annotatsiooni ja sisu vahel:** kontrolli kompileeritud PDF-is, et `Abstract`-pealkirja ja annotatsiooni teksti vahel oleks töö ingliskeelne pealkiri.

4. **I — kohustuslike osade järjestus PDF-is:** autorideklaratsioon, sisukord, kasutatud kirjandus, Lisa 1 (Lihtlitsents) — kontrolli PDF-is olemasolu ja järjestust.

5. **XIII — Lisa 1 platseholderid:** veendu, et Lihtlitsentsi tekstis on `[Autori ees- ja perenimi]`, `[Lõputöö pealkiri]`, `[Juhendaja ees- ja perenimi]` ja `[pp.kk.aaaa]` ASENDATUD konkreetsete väärtustega.

6. **IX — joonised ja tabelid:** kontrolli tulemuste peatüki vormistust eraldi (ei kuulunud käesolevasse kontrolli).

7. **VI — lühendite ja mõistete sõnastik:** kui see on töös olemas, veendu, et FAPH, FRR, FPR, AUC, KWS, MCU, ASR, VAD, INT8, ONNX, TFLite, MFCC, SVDF, MixedNet, BC-ResNet, ESP32-S3, XTTS, TTS, STT, GDPR, FAPH-loendusreegli variantide nimed ja muud töös defineeritud lühendid oleksid kahe veeruga tabelis tähestiku järjekorras.

8. **XII.1 (viitestiili kontroll):** kuigi `\cite{...}` makro kasutamine on järjepidev, peab juhendaja kinnitama, kas „Park et al.~\cite{...} on näidanud" stiil on aktsepteeritav, või tuleb kasutada puhtnumbrilist „[N] on näidanud" stiili.

### Mitte kontrollitavad allika tasemel

- Tiitellehe paigutus, fondid, veerised, leheküljenumeratsioon (II, III).
- Autorideklaratsioon (IV).
- Lühendite ja mõistete sõnastik (VI).
- Sisukord, jooniste ja tabelite loetelud (VII).
- Esimese taseme pealkirja uuelt leheküljelt algamine (VIII.2).
- Programmikoodi vormistus (X).
- Valemite numeratsioon (XI) — ühtegi nummerdatud valemit loetud failides ei esine.
- Kasutatud kirjanduse loetelu (XII.3).
- Lisad, sh Lisa 1 — Lihtlitsents (XIII).
- Tabelid/joonised lisas (XV).

### Üldhinnang

Loetud LaTeX-allikfailide ulatuses on tekst metoodiliselt korrektselt vormistatud: pealkirjastamine kasutab kuni kolme taset, pealkirjadele järgneb tekst, viited on lause sees, em-dash ja en-dash on järjepidevalt kasutatud vastavalt funktsioonile, komakoht on järjepidev. **Kaks selget rikkumist (kaks ühe-lõiguga alapeatükki Põhjus 3 ja Põhjus 4)** vajavad parandamist enne PDF-i lõplikku versiooni. Ülejäänud kontrollitavad reeglid eeldavad kompileeritud PDF-i ja täismalli faile, mis ei kuulunud käesoleva kontrolli ulatusse.
