---
source_prompt: TI_kasutuse_deklaratsioon.txt
prompt_type: generative
generated: 2026-05-07
---

# Tehisintellekti kasutamise deklaratsioon — kaks varianti

Allpool on välja pakutud kaks varianti TI-kasutuse avaldusest, mida saab paigutada lõputöösse. Mõlemad on koostatud käesoleva töö (eestikeelse äratussõna tuvastuse bakalaureusetöö) tegeliku tööprotsessi põhjal: töös on kasutatud nii suure keelemudeliga (Anthropic Claude, sh agentlik töövoog Claude Code) tekstimustandite ja koodi mustandeid kui ka keelekorrektuuri ja vormistuse kontrolli. Konkreetseid faktilisi väiteid (mudelite versioonid, FAPH-väärtused, peatükkide nimed) variandid teadlikult ei dubleeri, et avaldus ei satuks vastuollu ülejäänud töö sisuga ega tekitaks topelt-numbreid.

Märkus: kohad, mis sõltuvad lõplikust juhendaja-/instituudi vormistusnõudest või lõpliku versiooni mudelite loetelust, on jäetud nurksulgudesse \texttt{[\dots]}, et autor saaks need enne esitamist üle kontrollida.

---

## Variant 1 — põhjalik selgitus (sobib metoodika peatükki või eraldi alajaotusena)

\paragraph{Tehisintellekti tööriistade kasutamine.}
Käesoleva lõputöö koostamisel on autor kasutanud tehisintellektil põhinevaid abivahendeid, eelkõige Anthropicu suurt keelemudelit Claude (sh agentlikku arenduskeskkonda Claude Code) [täienda vajadusel teiste tööriistade nimedega, nt ChatGPT, GitHub Copilot]. Tööriistu kasutati \emph{abivahendina}, mitte töö autori asendajana: kõik mudeli pakutud tekstilõigud, koodijupid ja struktuuriettepanekud on autor kriitiliselt üle vaadanud, vajaduse korral ümber kirjutanud, lühendanud või tagasi lükanud.

TI-d rakendati järgmiste \emph{mustandite ja ideede} loomiseks:
\begin{itemize}
    \item peatükkide ja alajaotuste struktuuri esmane visandamine ning üksikute lõikude ümbersõnastamine;
    \item korduvate tekstiplokkide (nt joonealused selgitused, mõistete sissejuhatus) variantide pakkumine;
    \item treenings- ja hindamisskriptide ning CLI-tööriistade prototüüpide mustandid (nt andmestiku ettevalmistus, FAPH-arvutuse tugiskriptid, logide analüüsi abivahendid);
    \item kirjanduses kasutatavate ingliskeelsete mõistete eestikeelsete vastete eelvalik enne autoripoolset lõplikku otsust.
\end{itemize}

TI-d kasutati ka \emph{kontrollimiseks ja toimetamiseks}:
\begin{itemize}
    \item eesti keele õigekirja, kirjavahemärkide ja stiili korrektuur;
    \item LaTeX-vormistuse kontroll (sh viidete, joonealuste märkuste, jooniste ja tabelite ühtlustamine);
    \item loogikavigade, vastuolude ja kordustega lõikude ülesotsimine pikemate peatükkide lõikes;
    \item ingliskeelse kokkuvõtte (\emph{abstract}) keelekontroll.
\end{itemize}

TI-d \emph{ei kasutatud} eksperimentaalsete tulemuste, mõõtmisandmete ega kasutajauuringu vastuste genereerimiseks. Kõik töös esitatud arvulised tulemused (sh treenitud mudelite jõudlusnäitajad, FAPH-väärtused ja kasutajauuringu kokkuvõtted) põhinevad autori läbi viidud katsetel ning kogutud andmetel. Samuti ei ole TI-d kasutatud allikate referaadina ilma autori-poolse kontrollita: iga viidatud allika sisu on autor üle vaadanud ning tsitaat või parafraas vastutab originaali eest.

Lõplik otsustusõigus töö sisu, struktuuri, väidete ja järelduste üle kuulub autorile. Autor vastutab kogu lõputöös esitatud teksti, koodi, jooniste ja andmete õigsuse, sõltumatu tõlgenduse ning akadeemilise eetika nõuetele vastavuse eest.

---

## Variant 2 — lühike teadaanne (sobib sissejuhatuse lõppu või joonealuseks märkuseks)

\paragraph{Tehisintellekti kasutamine.}
Lõputöö kirjutamisel on autor kasutanud suurel keelemudelil põhinevaid abivahendeid (eelkõige Anthropic Claude / Claude Code [täienda vajaduse korral]) teksti mustandite, ümbersõnastuste, koodinäidiste ja keelekorrektuuri toetamiseks. Kõik TI poolt pakutud tekstid ja koodilõigud on autor üle vaadanud, vajadusel ümber kirjutanud või tagasi lükanud. TI-d ei ole kasutatud eksperimenditulemuste ega kasutajauuringu andmete genereerimiseks. Lõplik vastutus töö sisu, väidete ja järelduste eest lasub autoril.

---

## Lühikommentaar autorile (ei lähe töö lõppversiooni)

\begin{itemize}
    \item Variant 1 sobib paremini, kui juhendaja või instituut ootab eraldi metoodilist alajaotust TI-kasutuse kohta, sest käesolevas töös on TI roll koodi- ja tekstimustandite tasandil olnud märkimisväärne (nt agentlik tööriistade ahel, vt CLAUDE.md / agentic-thesis-positioning dokumentatsioon).
    \item Variant 2 sobib, kui mahupiirang on range või kui juhendaja eelistab lühikest kinnitust sissejuhatuse lõpus / joonealuses märkuses.
    \item Mõlemas variandis on \texttt{[täienda vajadusel \dots]} kohad meelega jäetud, et lõpliku esitusversiooni jaoks saaksid mudelite ja tööriistade loetelu üle kontrollida (nt kas lisada GitHub Copilot, ChatGPT, Gemini, lokaalsed mudelid vms).
    \item Variandid väldivad konkreetsete mudeliversioonide (nt v6, v16c, expert-a) ja FAPH-numbrite kordamist, sest need esinevad juba sissejuhatuses ja peatükkides ning topeltesitus tooks vastuolude riski.
\end{itemize}
