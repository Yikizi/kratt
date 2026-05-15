---
source_prompt: /Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/04_Kontrollimine/Konkreetsed_vead/Vorm/Viitamine.txt
prompt_type: evaluative
generated: 2026-05-07
---

# Viitamise audit

Auditi ulatus: lõputöö LaTeX-fail \texttt{thesis-tex-estonian/} (sissejuhatus, peatükid 1--3, kokkuvõte, eesti- ja ingliskeelne abstrakt, ülesandepüstitus). Kolmandat peatükki (\texttt{third\_chapter.tex}) loeti automaatselt; \texttt{second\_chapter.tex} mahust loeti esimene ${\sim}450$ rida ja viidete sample mujalt. Bibliograafia: \texttt{references.bib} (77 BibTeX-kirjet).

### 1. Tabelid ja joonised

*   Auditeeritud failidest ei ilmnenud viidete asukoha rikkumisi (\enquote{vt joonis}, mis viitab numbrita objektile, või \enquote{(Tabel)} ilma numbrita). Tabeli- ja joonise-vormistust (pealkirja/allkirja punkt, pealkirja/allkirja paigutus) ei ole võimalik LaTeX-allikast üheselt tuvastada ilma kompileeritud PDF-i sisuvaateta, kuna \texttt{\textbackslash caption}-i sisu on esitatud paljude valemite ja \texttt{\textbackslash cite}-de sees. Käesolev jaotis ei loetle seetõttu rikkumisi, kuid kompileeritud PDF-i visuaalne kontroll on rangelt soovitatav, eriti tabeli \ref{tab:fair-comparison-holdout}, \ref{tab:expert-consensus} ja \ref{tab:specaug-ablation} pealkirjade lõpu-punktide ning kõikide \texttt{figures/} alt sisestatud jooniste allkirjade lõpu-punktide osas.

### 2. Viitamine ja allikad

*   **Kasutamata allikad bibliograafias (25 kirjet 77-st, ${\sim}32{,}5\%$).** Järgmistele \texttt{references.bib} kirjetele ei viidata üheski peatüki-, sissejuhatus-, abstrakti- ega kokkuvõtte\-failis ja need rikuvad reeglit \enquote{Iga \enquote{Kasutatud materjalides} olev allikas peab olema tekstis viidatud vähemalt korra}: \texttt{ahmed2022robustkws}, \texttt{amazon-twostage2020}, \texttt{apple\_personalized\_hey\_siri\_2018}, \texttt{asu2009estonian}, \texttt{example-reference}, \texttt{felzenszwalb2010dpm}, \texttt{fishs2pro2025}, \texttt{fleurs2023}, \texttt{garai2025sfkws}, \texttt{gdpr2016}, \texttt{google-speech-embedding2020}, \texttt{hou2020mining}, \texttt{iks2019}, \texttt{kim2024ttskws}, \texttt{liu2025noisekws}, \texttt{mazumder2021fewshot}, \texttt{neurokone2025}, \texttt{piits2007corpus}, \texttt{sindhwani2015structured}, \texttt{spectre}, \texttt{tang2020howl}, \texttt{voxpopuli2021}, \texttt{xiao2025adakws}, \texttt{xiao2025imkws}, \texttt{xttsv2est2025}. Kuna \texttt{biblatex} \texttt{\textbackslash printbibliography} formateerib vaikimisi ainult viidatud kirjeid, ei pruugi need PDF-i lõppu jõudagi --- siis pole tegemist vormingu, vaid hoolduse veaga: bibliograafias hoitakse kasutuks muutunud kirjeid. Soovitus: vaadata kompileeritud \texttt{Kasutatud kirjandus}-loend üle ja eemaldada viitamata kirjed \texttt{references.bib}-ist (või lisada vastavad \texttt{\textbackslash cite}-d teksti).

*   **Sõna \enquote{peatükk} ekslik kasutus alajaotuste viitamisel.}** Kontrollnimekirja reegel \enquote{Hierarhia nimetused: Peatükk = 1. taseme pealkiri; Jaotis/Alamjaotis = madalamad tasemed} on rikutud järgmistes kohtades, kus \texttt{ptk\textasciitilde\textbackslash ref\{...\}} osutab tegelikult mitte peatüki numbrile, vaid alajaotuse anchor'ile, \emph{aga} sihtmärk on \texttt{\textbackslash label\{chapter:results\}} ehk peatüki tase --- siin on valikud korrektsed (\texttt{ptk}/\texttt{peatükk} viitab peatükile). Kontrollitud read:
    *   \texttt{third\_chapter.tex:38, 101, 141, 143}: \enquote{vt ptk~\textbackslash ref\{chapter:results\}, tabel...} --- \texttt{chapter:results} on tõepoolest peatükk, viide on korrektne.
    *   \texttt{third\_chapter.tex:103}: \enquote{Audit (ptk~\textbackslash ref\{chapter:results\}, §\textbackslash ref\{sec:positive-audit\}) näitas...} --- korrektne.
    *   \texttt{second\_chapter.tex:575, 677}: \enquote{käsitletud peatükis~\textbackslash ref\{chapter:discussion\}} --- korrektne (peatüki tase).
    Reaalseid \enquote{peatükile 3.4} stiilis vigu ei tuvastatud --- alajaotustele viidatakse järjepidevalt \texttt{§\textbackslash ref\{...\}} või \texttt{alapeatükis} kaudu.

*   **Viite ees puuduv tühik.** Auditeeritud failides ei tuvastatud ühtegi mustrit \texttt{[a-zA-Z0-9)]\textbackslash cite\{...\}} (st sõna lõpp + \texttt{\textbackslash cite} ilma tühikuta). Lauselõpu viited järgivad järjekindlalt mustrit \texttt{...tekst \textbackslash cite\{X\}.} (viide enne punkti, tühik ees) --- vastab IEEE reeglile.

*   **Viide pärast lauselõppu.** Mustrit \texttt{.~\textbackslash cite\{...\}} (punkt enne viidet) auditeeritud failides ei tuvastatud. Kõik viited on lause sees enne punkti.

*   **Tühjad viited.} Mustrit \texttt{\textbackslash cite\{\}} või \texttt{[]} / \texttt{[ ]} auditeeritud failides ei tuvastatud.

*   **Annotatsiooni ja Abstracti viidete kontroll: \emph{korrektne}.** \texttt{misc/abstract-estonian.tex}, \texttt{misc/abstract-english.tex} ja \texttt{chapters/summary.tex} ei sisalda ühtegi \texttt{\textbackslash cite}-käsku. See vastab reeglile \enquote{Annotatsioonis ja Abstractis ei tohi olla viiteid}.

*   **Korduvad allikad (duplikaadid).** \texttt{references.bib} võtmete unikaalsuse audit (77 kirjet, 77 unikaalset võtit) ei tuvastanud BibTeX-võtme tasandil duplikaate. Sisulist samale teosele kahe võtme alla kirjeldatud duplikatsiooni ei kontrollitud automaatselt --- soovitus käsitsi üle vaadata, eriti Picovoice (\texttt{picovoice-benchmark2026} vs \texttt{picovoice-guide2026}) ja openWakeWord (\texttt{openwakeword2026} vs \texttt{openwakeword-features2024}) paarid, et veenduda, kas tegemist on tõepoolest eri allikatega.

*   **Allikate kvaliteet.} Bibliograafia sisaldab arvestatava hulga vastastikku eelretsenseeritud teadusartikleid ja konverentsiettekandeid (Park~et~al.\ 2019, He~et~al.\ 2016, Choi~et~al.\ 2021, Wilson 1927, Brown~et~al.\ 2001, Garwood 1936, Park~et~al.\ 2024, Schönherr~et~al.\ 2022, Kundu~et~al.\ 2023, Chen~et~al.\ 2014/2022, Sainath~et~al.\ 2015, Alvarez~et~al.\ 2019, Jacob~et~al.\ 2018, Lewis 2013 jm). Reegel \enquote{teadusartikleid/raamatuid peab olema} on \emph{täidetud}.

*   **Vikipeedia osakaal.} \texttt{references.bib} ei sisalda ühtegi Wikipedia-allikat (\texttt{grep -i wikipedia} = 0). Reegel täidetud.

### 3. Struktuur ja muu

*   **Lisa 2 ja Lisa 3 viitamata.} \texttt{appendices/appendices\_main.tex} sisaldab kaks lisa: \texttt{\textbackslash label\{chapter:appendix-something\}} (\enquote{Lisa 2 -- Something}) ja \texttt{\textbackslash label\{chapter:appendix-something-else\}} (\enquote{Lisa 3 -- Something Else}). Auditeeritud peatüki-, abstrakti- ega kokkuvõtte\-failides ei viidata kummalegi (\texttt{grep -i "lisa\textbackslash s*[23]"} = 0; \texttt{grep "chapter:appendix-something"} = 0). Reegli \enquote{igale lisale peab tekstis viitama vähemalt korra (erand: Lisa 1 = litsents)} kohaselt on tegemist \textbf{kahe rikkumisega}. Lisaks on lisade pealkirjad endiselt mall-väärtused (\enquote{Something}, \enquote{Something Else}) --- need tuleb kas täita sisuga ja teksti siduda või kogu \texttt{appendices\_main.tex} import \texttt{main.tex}-ist eemaldada, kui lisasid 2--3 ei plaanita esitada.

*   **Koodi avalikustamise viide --- ei kontrollitud (puudulik tõendus).} Reegel \enquote{Kui töös mainitakse koodi avalikustamist, peab link/viide sellele olema kõigis: Annotatsioon, Abstract, Kokkuvõte ja Töö põhiosa}. Auditeeritud osades ei leitud ühtegi koodi avalikustamise mainimist (\texttt{github.com}, \texttt{gitlab}, \texttt{repo}, \enquote{lähtekood}); ka peatükkide teksti hetke\-versioon räägib koodist (\texttt{compare\_models.py}, \texttt{kratt user-test} jne) tööriistana, kuid ei luba seda avalikult välja anda. Kui lõputöös on plaanis koodi avalikustamine deklareerida (mh ülesande\-püstituses 4.\ punktis on viide \enquote{avatud lähtekoodiga treenitud mudelit}), tuleb vastav URL/repo lisada \emph{kõigisse} neljasse kohta. Kui mitte, siis ülesande\-püstituse \texttt{ylesandepystitus.tex} rida 96 sõnastust tuleb täpsustada.

*   **Ülesandepüstituse allikate stiil ja seos põhi-bibliograafiaga.} \texttt{ylesandepystitus.tex} ridadel 102--107 on \enquote{Esialgsed allikad} esitatud nummerdatud loendina (\texttt{[1]}--\texttt{[4]}) käsitsi sisseöeldud URL-idega, kasutamata töö \texttt{biblatex}/\texttt{references.bib} taristut. See ei ole otseselt kontrollnimekirja rikkumine (ülesande\-püstitus on eraldi dokument), kuid soovituslik märkus: \texttt{[1]} viitab Kiirkirjutajale, mis põhi-töö bibliograafias täiesti puudub --- juhul kui Kiirkirjutaja STT-d on ka lõputöös vaja viidata, tuleks vastav kirje \texttt{references.bib}-i lisada.

*   **Bibliograafias \enquote{example-reference} platshoidri-kirje.} \texttt{references.bib} sisaldab kirjet \texttt{@misc\{example-reference, ...\}}, mis on tõenäoliselt mall-fail-i järgi sisse jäänud platshoidri-kirje. Olenemata sellest, kas \texttt{biblatex} selle välja kirjutab või ei (kuna seda ei tsiteerita), on tegemist hooldus-puudusega. Soovitus eemaldada.
