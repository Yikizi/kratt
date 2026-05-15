---
source_prompt: 07_Teadusartikkel/Mida_muuta_uude_ajakirja_esitamisel.txt
prompt_type: inapplicable (best-effort + gap explanation)
generated: 2026-05-07
---

# Mida muuta uude ajakirja esitamisel — analüüs

## Sissejuhatav märkus: prompti rakendatavus

Prompt eeldab kahe konkreetse ajakirja nime sisestamist (Ajakiri 1 = algne sihtkoht, Ajakiri 2 = uus sihtkoht), kuid mõlemad väljad on lähtefailis täitmata platsihoidjad (`<Sisesta siia ajakirja nimi, nt Nature>` ja `<Sisesta siia ajakirja nimi, nt PLOS ONE>`). Lisaks on analüüsitav artefakt mitte teadusartikli käsikiri, vaid bakalaureusetöö LaTeX-allikas (`introduction.tex`, `first_chapter.tex`, `second_chapter.tex`, `third_chapter.tex`, `summary.tex`, abstraktid). Töö ei ole praegu sõnastatud teadusartiklina ja ühtegi ajakirja-spetsiifilist vormi (autorijuhend, viitamisstiil, sõnapiirang) pole varem rakendatud.

Seetõttu ei saa täita prompti otseselt sõnastatud kujul (\enquote{võrdle Ajakirja 1 ja Ajakirja 2 nõudeid \textrightarrow{} koosta tegevuskava ülemineku jaoks}), sest:

1. lähtenõuded (Ajakiri 1) on määratlemata — ei ole olemas \enquote{eelmist esitamist}, millest üle minna;
2. sihtnõuded (Ajakiri 2) on määratlemata — ei tea, millisele formaadile kohandada;
3. käsikiri ei ole olemas — bakalaureusetöö ei ole publitseerimisvalmis ajakirjavorming.

Lünga sulgemiseks järgneb (a) selgitus, mida promptist puudus, ja (b) parima jõupingutuse vastus: realistlikud sihtajakirja kandidaadid antud teema jaoks ning üldine \emph{thesis \textrightarrow{} journal article} muudatuste loend, mis kehtib enne kui konkreetne ajakiri valitakse.

---

## A. Realistlikud sihtajakirja kandidaadid (parima jõupingutusena)

Teema (eestikeelne äratussõna ESP32-S3 mikrokontrolleril, FAPH-põhine voogedastushindamine, väikese ressursiga keele protokoll) sobib mitme rahvusvahelise foorumiga. Kuna prompt ootas \emph{kahte} ajakirja, pakutakse mõistlik paar arutelu lähtepunktiks; lõplik valik tuleb teha juhendaja ja TalTechi avaldamispoliitikaga kooskõlastades.

| Roll | Ajakirja kandidaat | Põhjendus |
|------|--------------------|-----------|
| Algne (sihiks seatud) | \emph{Interspeech} 2026/2027 või \emph{IEEE/ACM Transactions on Audio, Speech, and Language Processing} (TASLP) | Kõnetuvastuse / KWS valdkonna keskne tippfoorum; töö metoodiline panus (FAPH-põhine multikriteeriumiline hindamine) sobib selle auditooriumiga. |
| Alternatiiv (varuvalik) | \emph{Speech Communication} (Elsevier), \emph{IEEE Signal Processing Letters} või \emph{Applied Sciences} (MDPI, open access) | Laiem fookus, leebem tehniline uudsuse lävi; \emph{Applied Sciences} on madala ressursiga keelte tööde jaoks levinud teine valik. |

Eestikeelse keeletehnoloogia raami jaoks võiks lisada ka \emph{Eesti Rakenduslingvistika Ühingu aastaraamat} (ERÜ) või \emph{Northern European Journal of Language Technology} (NEJLT) kui regionaalsed alternatiivid; need eelistavad keele-spetsiifilist panust ja on teadusartikli formaadi suhtes paindlikumad.

\textbf{Hoiatus:} ülaltoodud paari ei ole võimalik kontrollida tegeliku autorijuhendi vastu ilma veebiotsinguta, mille promptis ette nähtud samm \enquote{1. Infohankimine} eeldas. Seetõttu on järgnev tegevuskava \emph{tüpoloogiline}, mitte ajakirja-spetsiifiline.

---

## B. Üldine üleminekuplaan (bakalaureusetöö \textrightarrow{} ajakirjaartikkel)

### 1. Muudatused artikli fookuses ja \enquote{nurgas} (narratiiv)

\textbf{Sihtgrupi muutus.} Bakalaureusetöö praegune tekst (vt nt `introduction.tex` ja `third_chapter.tex` §\ref{sec:eval-evolution}) on suunatud TalTechi retsensendile ja oponendile: see kirjeldab põhjalikult metoodika valikuid, kolme valideerimisringi ja agentpõhise arenduse rolli. Ajakirjaartikli puhul tuleb sihtgrupp uuesti määratleda:

- \emph{Interspeech / TASLP} suund: lugeja on KWS-ekspert, kes \emph{eeldab} streaming-evaluatsiooni alusteadmisi. Triviaalseid taustaselgitusi (nt \enquote{FAPH ehk valevallandumiste arv tunnis}) tuleb lühendada või kustutada; metodoloogiline panus tuleb sõnastada kontrastina kirjandusele (Lopez-Espejo et al.\ 2021, Sigtia et al.\ 2020), mitte üldhariva selgitusena.
- \emph{Applied Sciences / Speech Communication} suund: lugeja on rakenduslik, võib olla teisest valdkonnast (nutikodu, embedded). Siin võib taustaselgitusi pigem alles jätta, kuid kirjeldav agentpõhise arenduse osa (`third_chapter.tex` §\enquote{Agentpõhine arendus kui töövõimendaja}) tuleb kompaktsemaks suruda või eemaldada — see on bakalaureusetöö enesereflektsioon, mitte ajakirjale sobiv osa.

\textbf{Kaaskiri (Cover Letter).} Bakalaureusetööl ei olnud kaaskirja. Esmasel ajakirja-esitusel tuleks rõhutada:
- konkreetne uudsus: \enquote{esimene avalikult dokumenteeritud eestikeelne äratussõna mudel mikrokontrolleri sihtmasinal} + multikriteeriumiline hindamisprotokoll;
- empiiriline panus: 0,79 FAPH ekspertkonsensusel Common~Voice ET kõrvalejäetud komplektil;
- metoodiline ülekantavus: protokoll on rakendatav teistele madala ressursiga keeltele.

Uue ajakirja kaaskirjas (kui esimene esitamine ebaõnnestub ja töö liigub varuajakirja) tuleb rõhku nihutada: vähem \enquote{tippkvaliteet}-tüüpi väiteid, rohkem \enquote{rakenduslik tõenduspõhi ja reprodutseeritavus}.

\textbf{Pealkiri ja abstrakt.} Praegune eestikeelne abstrakt (`abstract-estonian.tex`) ja ingliskeelne (`abstract-english.tex`) on ${\sim}250$ sõna ja konteksti-rikkad. Ajakirja-abstraktid on tavaliselt 150--250 sõna ja struktureeritud (background / methods / results / conclusions). Vajalikud sammud:
- pealkiri tuleks ümber sõnastada uudsust väljendavalt, nt \enquote{An Estonian Wake-Word Detector on ESP32-S3: A Multi-Criterion Streaming Evaluation Protocol for Low-Resource Languages};
- abstraktist tuleks eemaldada bakalaureusetöö tüüpi sissejuhatav lause (\enquote{Käesoleva bakalaureusetöö eesmärk on\ldots}) ja asendada faktitihedama avalausega (panus, mitte protseduur);
- lisada märksõnad (5--7 tk): \emph{wake-word detection, keyword spotting, low-resource languages, Estonian, microcontroller, streaming evaluation, FAPH}.

### 2. Muudatused artikli struktuuris (ülesehitus)

\textbf{Sektsioonide järjestus.} Bakalaureusetöö struktuur (Sissejuhatus \textrightarrow{} Metoodika \textrightarrow{} Tulemused \textrightarrow{} Arutelu \textrightarrow{} Kokkuvõte) on suures osas IMRaD-iga ühilduv ja seda saab reprodutseerida ajakirjaartiklis. Konkreetsed muudatused:

- \emph{Interspeech} formaat (4-leheküljeline) nõuab agressiivset kompresseerimist: `first_chapter.tex` (138 rida metoodikat) ja `third_chapter.tex` (152 rida arutelu) tuleb mahutada kokku ${\sim}2$ leheküljele;
- \emph{TASLP / Speech Communication} on pikem (kuni 14 lk), kuid eeldab ranget \emph{Related Work} sektsiooni, mida bakalaureusetöös eraldi pole — praegu on see hajutatud sissejuhatusse ja `third_chapter.tex` §\ref{sec:benchmark-gap} alla. Tuleb konsolideerida;
- \emph{Methods} jääb keskele (mitte lõppu); ajakirjad ei kasuta \enquote{Methods after Discussion} mustrit, mis on iseloomulik osale bioloogia-ajakirjadele (\emph{Nature}, \emph{Cell});
- agentpõhise arenduse alapeatükk (`third_chapter.tex` §\enquote{Agentpõhine arendus\ldots}) tuleks kas täielikult eemaldada või viia \emph{Acknowledgments} / \emph{Author Notes} hulka. Ajakirjaartiklis ei kuulu see põhitekstist.

\textbf{Sõnade ja tähemärkide piirangud.} Tüüpilised piirangud, mida tuleb kontrollida valitud ajakirjas:
- pealkiri: 12--20 sõna (Interspeech), 95 tähemärki (TASLP);
- abstrakt: 150--250 sõna (enamus), 200 sõna (Interspeech);
- põhitekst: 4 lk (Interspeech), 8000--12000 sõna (TASLP), 6000--8000 sõna (Speech Communication);
- viidete arv ei ole tüüpiliselt piiratud, kuid Interspeech 4-lk piirang sunnib loomulikult kärpima.

Praegu töös ei ole sõnaarvu mõõdetud; enne kompresseerimist tuleb teha jooksev `wc` käsikirja korrektuurikoopial.

\textbf{Kohustuslikud lisad.} Enamus ajakirju eeldab tänapäeval:
- \emph{Data Availability Statement} — käesoleva töö puhul oluline, sest mainitakse Common~Voice ET, MUSAN, VOiCES, Speech Commands ning oma kogutud andmestikku. Tuleb eraldi sõnastada, mis on avalik, mis on osalejate nõusoleku alusel piiratud (vt `first_chapter.tex` §\ref{sec:user-test-methodology} kaheastmeline nõusolek);
- \emph{Code Availability Statement} — kui treeningskript ja `kratt` CLI on Githubis, tuleb seda mainida;
- \emph{Author Contributions} — üksikautoriga töö puhul triviaalne, kuid mõned ajakirjad nõuavad seda formaalselt (CRediT taksonoomia);
- \emph{Conflict of Interest} — vajalik;
- \emph{Funding Statement} — kui TalTech rahastas, tuleb mainida;
- \emph{Ethics Statement} — kasutajatesti puhul (20--30 osalejat, audio opt-in) tuleb mainida ESÜ / TalTechi eetikakomitee kooskõlastust.

### 3. Tehnilised ja vormistuslikud muudatused

\textbf{Viitamisstiil.} Bakalaureusetöö kasutab `\cite{}`-stiili (BibTeX), tõenäoliselt numbriline (TalTech mall). Ajakirjade nõuded varieeruvad:
- IEEE (TASLP, SPL): numbriline, [1] stiilis, IEEEtran.bst;
- Interspeech: numbriline, IEEE-laadne;
- Elsevier (Speech Communication): numbriline või (autor, aasta) sõltuvalt ajakirjast;
- MDPI (Applied Sciences): numbriline ACS-laadne.

Praegune `references.bib` peaks olema enamasti taaskasutatav, kuid tuleb kontrollida:
- DOI-d kõikidel kirjetel (paljud ajakirjad nõuavad);
- ühtne aastate vormindus (praegu segamini 2024, 2025, 2026);
- veebilehed (`@misc`) tuleb teisendada formaadiks, mis sisaldab \emph{accessed} kuupäeva.

\textbf{Joonised ja tabelid.} Bakalaureusetöö praegused joonised on tõenäoliselt 300 DPI Estonian-labelitega (vt `docs/CLAUDE.md`). Ajakirjadele tuleb:
- toota ingliskeelsed labelid kõikidele joonistele;
- kontrollida värvipimedusele sõbralikku paletti (TASLP nõuab seda explicit);
- esitada eraldi `figures/` kaustana (PDF/EPS vektorgraafika eelistatud, PNG ${\geq}600$ DPI bitmap'idele);
- tabelid LaTeX-koodina, mitte pildina;
- tabelid ja joonised \emph{kas} tekstis sees \emph{või} eraldi failidena vastavalt ajakirja eelistusele (Interspeech: tekstis sees; Elsevier: sageli eraldi).

\textbf{Üldvormistus.} Tüüpilised vormindusnõuded:
- reavahe: 1.5x või topeltpikkus käsikirjas (Elsevier eelistab topelt);
- reanumbrid: nõutud enamuses ajakirjades retsenseerimise lihtsustamiseks (`lineno` pakett);
- font: Times New Roman 11pt (Elsevier), Times 10pt (IEEE), erilist mallifaili kasutavates ajakirjades nende oma;
- leheküljenumbrid: nõutud kõikjal käsikirja-versioonis;
- LaTeX-mallid: TASLP, Interspeech ja MDPI pakuvad oma `cls` faili — tuleb kasutada nende oma, mitte TalTechi `tthesis.cls`.

---

## C. Lüngad, mida ilma konkreetsete ajakirjadeta ei saa katta

Järgmised punktid jäävad analüüsist välja, sest need sõltuvad ajakirja-spetsiifilisest informatsioonist:

1. \textbf{Aims and Scope võrdlus} — ei saa võrrelda kahte ajakirja, kui kumbki pole nimetatud. Tüüpiline nihe \emph{Nature \textrightarrow{} PLOS ONE} (prompti näide) tähendab \enquote{novelty/impact-driven} \textrightarrow{} \enquote{technically sound, reproducible, broader scope}, mis nõuab fookuse ümberkalibreerimist tugevamalt rakenduspõhisele.
2. \textbf{Sõnapiirangu täpne arv} — sõltub ajakirjast.
3. \textbf{Kohustuslike lisade täpne nimekiri} — sõltub ajakirjast (nt PLOS ONE nõuab CRediT, Nature ei nõua).
4. \textbf{Värske autorijuhendi link ja viimase muutmise kuupäev} — promptis ette nähtud veebiotsing ei ole käesolevas keskkonnas tehtud, sest ajakirjade nimed on lahtised.

Niipea kui Mattias määrab Ajakirja 1 ja Ajakirja 2 konkreetsed nimed, on võimalik need lüngad sulgeda struktureeritud Change Log'iga prompti algses formaadis.

---

## D. Soovitatav järgmine samm

1. Otsustada juhendajaga, kas teadusartiklit üldse plaanitakse ja millisesse ajakirja esmalt suunata (kandidaadid: Interspeech 2027, Applied Sciences, NEJLT).
2. Kui esmane sihtkoht on selge, käivitada see prompt uuesti konkreetsete väärtustega — alles siis muutub Change Log võrreldavaks ja teostatavaks.
3. Kuni siis: keskenduda lõputöö 2026-05-18 esitamisele, mitte ennetavale ajakirja-vorminduse tegemisele, sest see lisaks paindlikkust mille spetsiifika selgub alles pärast kaitsmist.
