---
source_prompt: 04_Kontrollimine/Üldisem_tagasiside/Soovitused_hinde_maksimeerimiseks.txt
prompt_type: evaluative (triaaž / tegevusplaan ROI järgi)
generated: 2026-05-07
---

# Soovitused hinde maksimeerimiseks (triaaž 11 päeva enne tähtaega)

**Konteksti eeldused (üliõpilase varjatud parameetrite asemel):**
- Lõputöö tüüp: bakalaureusetöö (TalTech informaatika).
- Autorite arv: 1.
- Aega lõppversiooni esitamiseni: ${\sim}11$ päeva (kõva tähtaeg 2026-05-18, käesolev kuupäev 2026-05-07).
- Õppekava eesmärgid (eeldus, mitte ÕISist välja võetud): tarkvarasüsteemide insenertehniline arendus, eksperimentaalne valideerimine, akadeemiline argumenteerimisoskus ja iseseisev probleemilahendus.
- Käsitluse skoop on piiratud Teie poolt etteantud failide najal: töös on metoodika ja arutelu peatükk, kuid tulemuste peatüki sisu hindajale ei avanenud (`third_chapter.tex` viitab korduvalt `\ref{chapter:results}` osale). Allpool eeldatakse, et tulemuste peatükk eksisteerib eraldi failina ning et selle tabelid (`tab:checkpoint-headline`, `tab:expert-consensus`, `tab:fair-comparison-holdout`, `tab:full-comparison`, `tab:model-versions`) on juba olemas; soovitused puudutavad eelkõige seda, kuidas olemasolevat sisu argumenteerida ja sõnastada nii, et hindekomisjon näeks töö tugevusi.

Töö üldhinnang: sisuline tase on selgelt üle bakalaureuseastme keskmise --- metoodika peatükk eristab nelja FAPH-varianti, sissejuhatus seab konkreetsed projekti-spetsiifilised sihtmäärad ja arutelu peatükk dokumenteerib kolme valideerimisringi koos lühitee-mehhanismiga. Suurim hindeoht ei ole sisu nõrkus, vaid see, et **hindekomisjon võib jätta osa tugevaid panuseid lugemata**, kui need on hajutatud või kui kõige mõjusam metoodiline väide (mitmemõõtmeline hindamisprotokoll § 3 \ref{sec:eval-evolution}) ei ole sissejuhatuses ja kokkuvõttes võrdselt nähtav. Järgnevad viis soovitust on järjestatud kahaneva ROI järgi.

---

### Soovitus 1: Tõsta mitmemõõtmeline hindamisprotokoll töö esmaseks panuseks (sissejuhatus, kokkuvõte, abstrakt) sümmeetriliselt aruteluga

*   **Olulisuse hinne:** 9/10
*   **Põhjendus:** Arutelu peatüki §\ref{sec:eval-evolution} sõnastab selgelt, et töö tugevaim väide ei ole \enquote{esimene eestikeelne äratussõnamudel}, vaid madala ressursiga keele lokaalse äratussõna mitmemõõtmeline tõendusprotokoll (kolm valideerimisringi, lühiteede mehhanism, ülekantavus). See on töö \emph{kõige kaitstavam} panus ja ainus, mille puhul üliõpilane konkureerib kontseptuaalselt, mitte ressurssidega. Sissejuhatus (§\,17) ja kokkuvõte deklareerivad aga panust kolmeosalisena (mudel + FAPH-metoodika + integreerimismuster) ning hindamisprotokolli iseseisev intellektuaalne väärtus jääb arutelu peatükis varjule. Kui komisjon loeb järjestuses sissejuhatus -> kokkuvõte -> abstrakt -> arutelu, võib töö tugevaim panus jääda \enquote{uudseks järelmõtteks}, mis langetab metoodika hinnet alla teenitud taseme. Õppekava eesmärgi \enquote{akadeemiline argumenteerimisoskus} ja \enquote{eksperimentaalne valideerimine} mõlemad teenivad sellest muudatusest.
*   **Detailsed tööjuhised:**
    1.  Sissejuhatuses (rida 17, lause \enquote{Töö konkreetne panus on kolmeosaline...}) sõnastage panuse hierarhia ümber nii, et metoodiline panus on \emph{esimene} ja kõige tugevam, mitte teine kolmest. Soovituslik sõnastus: \enquote{Töö peamine panus on (a) mitmemõõtmeline tõendusprotokoll madala ressursiga keele lokaalse äratussõna hindamiseks, mille tuumaks on kolm valideerimisringi (kõrvalejäetud komplektid, positiivse klassi audit, komposiitne kontrollpunkti valik); seda protokolli rakendati eestikeelse \enquote{Kuule Kratt} mudeli näitel, mille kõrval töö pakub (b) reprodutseeritava \texttt{microWakeWord}-põhise treening- ja hindamistoru ning (c) ESP32-S3 ja Home Assistanti integratsioonimustri.}
    2.  Eestikeelses (`abstract-estonian.tex` rida 7) ja inglise (`abstract-english.tex` rida 7) abstraktis on see hierarhia juba lähedale jõudnud --- abstrakt ütleb \enquote{keskne probleem ei ole ainult mudeli treenimine, vaid metodoloogiliselt korrektne hindamine}. Korrake sama hierarhiat ühelauselise kokkuvõttena ka sissejuhatuses ja kokkuvõttes, et komisjon näeks töö enesepositsioneerimist kolmes kohas identselt.
    3.  Kokkuvõtte (`summary.tex` rida 9) lause \enquote{määrav metodoloogiliselt korrektne hindamine, mitte üksnes mudeli treenimine} jätke alles, kuid lisage \emph{otseviide} kolmele valideerimisringile ühe lausega: see ankurdab abstraktse väite konkreetse mehhanismi külge, mida arutelu peatükk juba toetab.
*   **Esitamine töös:** Muudatused tehakse kolmes failis (`introduction.tex` rida 17, `summary.tex` rida 5--9, mõlemad abstraktid). Mahukam tekstilisamine pole vajalik; tegemist on positsioneerimise ümbersõnastamisega 2--4 lause ulatuses iga faili kohta. Kogu töömaht alla 2 tunni.

---

### Soovitus 2: Vormistada arutelu peatüki §\ref{sec:eval-evolution} kolm ringi visuaalse tabelina (riskiklass -> hindamise piir -> mõõdetud lühitee -> parandus)

*   **Olulisuse hinne:** 8/10
*   **Põhjendus:** Töö metoodiline põhipanus (vt soovitus 1) on praegu esitatud kolme \texttt{\textbackslash textbf}-pealkirjaga lõikudena (read 101--105), kus iga ringi puhul on kolm-neli lauset. Sama sisu tabelina (4 veergu × 3 rida) annab komisjonile ühe pilguga arusaamise sellest, et tegemist on \emph{süstemaatilise} mehhanismiga, mitte juhusliku katselooga. Tabelite ja jooniste kogused on bakalaureusetöö hindamises sageli kvaliteedimärgistuse asendaja --- hea metoodiline tabel teisendab \enquote{huvitava jutu} \enquote{tõestatavaks raamistikuks}. Selle muudatuse ROI on kõrge, sest sisu on juba olemas; vajalik on ainult ümberkujundamine.
*   **Detailsed tööjuhised:**
    1.  Lisada arutelu peatükki, kohe pärast §\ref{sec:three-rounds} lõpetuse lõiku ja enne §\ref{sec:general-principle} algust, üks tabel järgmiste veergudega: \emph{Ring} | \emph{Hindamise piir} | \emph{Mis lühitee tegelikult mõõdeti} | \emph{Parandus / järgmine ring}. Read täita olemasolevatest lõikudest 101 (klipi-tasemel FPR -> mälu kontroll -> kõrvalejäetud komplektid + FAPH), 103 (kolm-mõõdikuline -> prefiksi tuvastamine -> rangem positiivsete poliitika + fraasistruktuuri testid), 105 (taustaheli FAPH miinimum -> kompromiss kaotab tuvastamismäära -> komposiitne valikukriteerium).
    2.  Tabeli pealkiri: \enquote{Hindamisprotokolli kolm valideerimisringi: kavandatud mõõdik, tegelikult mõõdetud lühitee ja vastav parandus.} Tabelile viidata sissejuhatuses (vt soovitus 1) lühikeses panuse-lauses ühe \texttt{\textbackslash ref}-iga, et komisjoni tähelepanu juhitaks juba esimesel lugemisel arutelu peatüki tabelisse.
    3.  Sama tabel (lihtsustatud kujul) sobib hästi kaitsmisslaididesse, kus see on visuaalselt mõjuvam kui jooksev tekst.
*   **Esitamine töös:** Uus tabel `tab:eval-rounds` arutelu peatüki §\ref{sec:eval-evolution} alguses (read 96--106 vahel). Töömaht alla 90 minuti, sealhulgas LaTeX-i vormistus ja viited. Sisuliselt on tegemist olemasoleva sisu ümberkujundamisega.

---

### Soovitus 3: Käsitleda \texttt{v16c} kandidaadi staatuse ebakõla sissejuhatuse, metoodika ja kokkuvõtte vahel

*   **Olulisuse hinne:** 7/10
*   **Põhjendus:** \texttt{v16c} on töös käsitletud kolme erineva nurga alt, mis võivad komisjonile jätta mulje põhjendamata kõikumisest. Sissejuhatus ei nimeta \texttt{v16c}-d. Metoodika §\,\ref{subsec:quantization} (rida 127) raporteerib \texttt{v16c} kvantiseeritud mahtu 148 KB-na ning kasutajatesti metoodika §\,\ref{sec:user-test-methodology} (rida 132) nimetab seda \enquote{piloodi vaikevalikuks} ja \enquote{stabiilseks üksikmudeli baasjooneks, mitte lõplikuks tootmiskvaliteedi väiteks}. Kokkuvõte (`summary.tex` rida 11) lisab eraldi lause: \enquote{\texttt{v16c} jääb eraldi kandidaatiks, mitte tootmisse rakendatavaks tõendiks, kuni ESPHome + \texttt{voice\_assistant} integreeritud Korvo-2 seadmes tehtud eraldi valideerimine seda kinnitab.} Kasutajatesti taasmängu FAPH-i loend (§\,\ref{subsec:faph-variants}) märgib selle \enquote{planeeritavaks}. Hindekomisjonile tähendab see, et töö lõplik mudelivalik on lugemisel ebaselge: kas \texttt{v16c} on tulemus, kandidaat või tühi rida? Ausus on tugev (vt arutelu §\,\ref{sec:fourth-round}), kuid praegu kõlab see ebakõla pigem kõhklusena kui distsipliinina. Õppekava eesmärgi \enquote{eksperimentaalne valideerimine} jaoks on kriitiline, et komisjon näeks: töö \emph{teadlikult} ei deklareeri \texttt{v16c}-d tootmismudelina, sest tõendusdistsipliin nõuab kasutajatesti.
*   **Detailsed tööjuhised:**
    1.  Lisage sissejuhatusse (`introduction.tex` rida 17--18 vahele) üks lause, mis seob piirangute loendi ja kandidaadi-staatuse: \enquote{Töö ei väida ühe konkreetse mudeliversiooni tootmisvalmidust; piloodi aktiivne kandidaat \texttt{v16c} on stabiilne üksikmudeli baasjoon, mille juurutusotsus sõltub veel käimasolevast kasutajatestist (vt §\,\ref{sec:user-test-methodology}).} See raamistab kõik järgmised \texttt{v16c}-viited samasse loogikasse.
    2.  Kokkuvõtte (`summary.tex` rida 11) lause hoidke alles, kuid sõnastage see \emph{aktiivseks tõendusdistsipliini-väiteks}, mitte hoiatuseks: nt \enquote{Töö hoiab teadlikult lahus piloodi kandidaadi (\texttt{v16c}) ja juurutusvalmiduse väite: viimane sõltub eraldi kasutajatesti taasmängust ja Korvo-2 integratsiooni valideerimisest, mis ei mahtunud käesoleva töö ajaraami.} Vahe on see, et lugeja näeb piiri \emph{kavatsetud projektitulemusena}, mitte puuduva komponendina.
    3.  Vältige \texttt{v16c}-le viitamist sõnaga \enquote{eksperiment} või \enquote{ablatsioon}, kus see ei ole täpselt nii --- need terminid on töös õigesti reserveeritud (nt v6-residual, v13a/v13b). Hoidke \texttt{v16c} terminoloogiaks: \enquote{piloodi aktiivne kandidaat} või \enquote{stabiilne baasjoon}.
*   **Esitamine töös:** `introduction.tex` rida 17 lõppu üks lause, `summary.tex` rida 11 ümbersõnastamine. Töömaht alla 60 minuti.

---

### Soovitus 4: Tugevdada uurimisküsimuste-vastuste sidumist kokkuvõttes (mapping table või loend)

*   **Olulisuse hinne:** 7/10
*   **Põhjendus:** Sissejuhatuses (read 9--15) on neli alamküsimust selgelt sõnastatud. Kokkuvõte (`summary.tex`) ei seo neid otseselt vastustega, vaid esitab koondnarratiivi. Bakalaureusetöö hindamise standardne kriteerium on, kas töö \emph{vastab oma uurimisküsimustele eksplitsiitselt}. Kui komisjon võrdleb sissejuhatuse loendit kokkuvõtte tekstiga ja peab vastused ise välja noppima, langeb skoor \enquote{järelduste loogilisus} all. Iga alamküsimus on töös tegelikult vastatud:
    - \enquote{kuidas valideerida toru enne ET andmestikku} -> avaliku marvin-kontrollkatse §\,3.1 ja §\,3.\ref{sec:three-rounds}/ring 1;
    - \enquote{positiivsete/negatiivsete/taustaheli rollid} -> metoodika §\,\enquote{Andmeliikide eristamine} + arutelu §\,\enquote{Andmestiku põhipiirangud};
    - \enquote{kuidas eristada andmestiku ja toru piiranguid} -> arutelu §\,3.1 + ring 1 lekke audit;
    - \enquote{kas FAPH < 1 ja recall $\geq$ 0,95} -> osaline JAH (FAPH 0,79 hold-out konsensusel) + osaline EI (Kule-tuvastus alla läve), mis on selgelt välja toodud read 143--144.
    Need vastused on olemas, kuid lugeja peab need ise kokku panema.
*   **Detailsed tööjuhised:**
    1.  Lisage kokkuvõttesse (`summary.tex` rea 7 ja 9 vahele) üks neljarealine \texttt{itemize}-loend pealkirjaga \enquote{Uurimisküsimustele antud vastused:}, kus iga alamküsimus on lühidalt vastatud koos sektsiooni-viitega (\texttt{\textbackslash ref}). Kogumaht: 6--8 rida LaTeX-i.
    2.  Erilist tähelepanu pöörake neljanda alamküsimuse vastusele (FAPH < 1 ja recall $\geq$ 0,95): vorm \enquote{osaline JAH / osaline EI} on eelistatav peidetud osalisele vastamisele. Komisjon hindab teadlikku piiritlemist kõrgemalt kui ületoonistatud edu. Soovituslik sõnastus: \enquote{FAPH < 1 sihtväärtus saavutati Common Voice ET kõrvalejäetud komplektil ekspertkonsensuse seadistuses (FAPH = 0,79; vt tabel \texttt{tab:expert-consensus}); $\geq$ 0,95 lähikõne tuvastamismäär TTS-positiivsetel klippidel saavutati, kuid päris kõnelejate \enquote{Kule}-hääldustel jääb saagis juurutuslävel madalamaks ja lõpliku juurutusotsuse langetamiseks on vajalik kasutajatest.}
*   **Esitamine töös:** `summary.tex`, rea 7 järele uus alamlõik. Töömaht alla 45 minuti.

---

### Soovitus 5: Kalibreerida agentpõhise arenduse alapeatüki (§\,3.6) tasakaal --- vähendada kaitsetooni, suurendada metoodilist ettevaatlikkust

*   **Olulisuse hinne:** 6/10
*   **Põhjendus:** Alapeatükk \enquote{Agentpõhine arendus kui töövõimendaja, mitte tõendusmaterjali asendaja} (read 81--89) on intellektuaalselt huvitav ja metoodiliselt aus, kuid esitab samaaegselt kaks rolli: (a) seletab, miks kogu mõõte- ja tugivahendite kiht oli üksiku autori jaoks võimalik, (b) hoiatab agentpõhise arenduse mõju ületõlgendamise eest. See kahene rõhk võib mõnedele hindajatele jätta mulje, et üliõpilane \emph{kaitseb} oma töökorraldust, mis võib paradoksaalselt vähendada usaldusväärsust. Alternatiivne, riskivabam raamistus oleks esitada agentpõhine arendus \emph{metodoloogilise piiranguna ja läbipaistvuse aktina}, mitte tugevuste loendina. Komisjon hindab teadlikku enesepiiritlemist alati kõrgemalt kui enesekaitset. Õppekava eesmärgi \enquote{iseseisev probleemilahendus} vaatest on oluline, et komisjon näeks, et üliõpilane mõistab, milline osa tööst on \emph{tema oma} ja milline on \emph{võimendatud}.
*   **Detailsed tööjuhised:**
    1.  Vahetage alapeatüki \emph{esimene} ja \emph{kolmas} lõik järjekorra järgi: alustage piiranguga (\enquote{tehisagendid ei vähenda tõendusmaterjali kogumise kulu}), seejärel kirjeldage võimendava mõju kasu, lõpetage sünteesiga (\enquote{tööviis nihutab pudelikaela teostuselt tõendusmaterjalile}). See ümberpaigutamine teeb peatüki narratiivseks: piirang -> kasu -> järeldus, mitte: kasu -> piirang -> kompromiss-järeldus.
    2.  Kustutage avalõigu kõrvallause \enquote{ei oleks üksiku autori jaoks olnud selles mahus jõukohased ilma agentpõhise tarkvaraarenduseta} kui rõhk: see jätab kaitsetooni. Asendage neutraalsema sõnastusega, nt: \enquote{Eelnevalt kirjeldatud hindamistoru, valevallandumiste logija ja taustaheli korpuse tööriistastik kasvas töö käigus mahukamaks, kui üksiku autori tavapärases töövoos oleks olnud teostatav. Selle võimaldas osaline koodi mustandamise ja dokumenteerimise delegeerimine tehisagentidele, mille metodoloogilised piirid tuleb järgnevalt eraldi avada.}
    3.  Säilitage selgelt formuleeritud lause read 87--88 (tehisagendid ei loo päris kõnelejaid, ei asenda sõltumatuid testikomplekte) --- see on töö üks tugevamaid auste piiritlemise lauseid ja võiks olla isegi peatüki \emph{sissejuhatav} väide, mitte keskmine.
*   **Esitamine töös:** Sama alapeatükk (`third_chapter.tex` read 81--89), lõikude järjekorra muutmine ja ühe lause neutraliseerimine. Töömaht alla 60 minuti. \emph{Ärge kustutage seda alapeatükki} --- see on töö üks eristavamaid panuseid ja näitab kaasaegse arendustööviisi metoodilist refleksiooni, mida vähesed BSc-tööd julgevad teha. Eesmärk on ainult tooni kalibreerimine.

---

## Mida käesolev triaaž teadlikult välja jätab

- **Tulemuste peatükk** ei olnud sellele juhendajale kättesaadav (`third_chapter.tex` viitab `\ref{chapter:results}` mitmest kohast, kuid eraldi failina seda ei avanenud). Kui tulemuste peatükis on viiteid katkiseid, tabeleid puuduvaid või arvulisi vastuolusid sissejuhatuse 0,79 FAPH väitega, on need eraldi triaažikorraldus.
- **Kasutajatesti tegelik läbiviimine 11 päeva jooksul** ei ole soovituste skoobis. Kui see lähiajal teostub, mahub selle tulemus eraldi alajaotusena tulemuste peatüki lõppu (suurendab töö tugevust, kuid ei ole ROI-järjekorras esimene viiest, sest hindekomisjoni jaoks loevad eelkõige sissejuhatuse, kokkuvõtte ja arutelu sõnastamisstandardid).
- **Keeletoimetamine ja vormistus** on triaažist väljas (vt prompti reegel 3).
- **Vormistuse kohustuslikud osad** (annotatsioon, abstraktid, litsents) eeldatakse hiljem lisatavaks (vt prompti reegel 3a) --- abstraktid on Teil juba olemas; nende sõnastust käsitleb soovitus 1.

## Lõppsõna

Töö on metoodiliselt küpsem kui keskmine TalTechi BSc-töö samas valdkonnas: §\,\ref{subsec:faph-variants} nelja FAPH-variandi eristus, §\,\ref{sec:benchmark-gap} benchmark-vs-reaalsus lõhe analüüs ja §\,\ref{sec:eval-evolution} kolme valideerimisringi mehhanism on iseseisvalt avaldamiskõlbliku artikli tasemel argumendid. Suurim hindeoht ei ole sisu nõrkus, vaid see, et hindekomisjon võib jätta osa tugevamaid panuseid \emph{lugemata}, sest sissejuhatus ja kokkuvõte ei tõsta neid samale tasemele kui arutelu peatükk. Viis ülaltoodud soovitust on kõik puhtalt sõnastuse ja struktuuri parandused, mille kogumaht jääb alla 8 töötunni ja millest igaüks tõstab töö ROI-d ilma uut sisu loomata.
