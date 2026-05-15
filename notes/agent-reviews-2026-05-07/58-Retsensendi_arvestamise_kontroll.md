---
source_prompt: 04_Kontrollimine/Üldisem_tagasiside/Retsensendi_tagasisidega_arvestamise_kontroll.txt
prompt_type: evaluative (compliance check) — inapplicable in current state
generated: 2026-05-07
---

# Retsensendi tagasisidega arvestamise kontroll — käivitatavuse analüüs

## Käivitatavuse hinnang

Antud viip eeldab kahte sisendallikat:

1. **Retsensendi tagasiside** (struktureeritud märkused, mille suhtes vastavus tuvastatakse).
2. **Parandatud dokument** (käesolev lõputöö versioon, mille sisu vastavust märkustele kontrollitakse).

Käesolevas käivituses on saadaval ainult teine sisend — lõputöö Estonian-keelne LaTeX-allikas (sissejuhatus, peatükid 1–3, kokkuvõte, eestikeelne ja inglise abstract, ülesandepüstitus). **Retsensendi tagasiside dokumenti ei ole sisendina ette antud** ning seda ei eksisteeri ka töö repositooriumis (kontrollitud `find`-otsinguga `*retsen*`/`*review*`/`*reviewer*`). Olemas on üksnes automaatsete kvaliteedikontrolli väljundeid kataloogis `.hermes/thesis-quality-reviews/`, kuid need ei ole ametliku retsensendi tagasiside ja viip viitab konkreetselt välisele retsensendile (\enquote{retsensendi sisu}, \enquote{kriitilise tagasiside}).

Sellest tulenevalt ei ole **vastavusanalüüsi (compliance check)** korrektselt teostatav — puudub baas, mille suhtes võrdlus tehakse. Igasugune \enquote{märkus 1, märkus 2, …} loetelu oleks väljamõeldud retsensendi simulatsioon ning rikuks kahte töö selget reeglit: (a) viiba enda nõuet \enquote{ära eelda parandust, otsi konkreetset tõendit}, ja (b) käivituse piiranguid \enquote{no invented facts}.

## Lünk ja selle kõrvaldamise tee

Et viip muutuks käivitatavaks, on autoril vaja esitada üks järgmistest:

1. **Ametliku retsensendi tagasiside** TalTechi süsteemis (sisu nummerdatud märkustena või vabatekstina, mis on autori poolt mõtteüksusteks tükeldatud).
2. **Eelkaitsmise protokoll või suuline tagasiside** (transkribeeritud märkmetena), kui formaalset retsensiooni veel ei eksisteeri.
3. **Juhendaja kirjalik tagasiside** ühe asendava sisendina, mille puhul tuleb märkida, et tegemist ei ole klassikalise retsensiooniga, vaid juhendaja-poolse kvaliteedikontrolliga.

Vastavalt sellele tuleks viiba käivitamisel anda see dokument lisafailina (näiteks `--input retsensent.txt`) või kleepida selle sisu prompt-konteksti enne lõputöö allika lugemist.

## Parim võimalik tugi praegu (best-effort)

Kuna sisuline vastavusanalüüs ei ole võimalik, järgnev pakub kahte täiendavat tuge, mida saab kohe kasutada, kui retsensendi tagasiside saabub.

### A. Vastavustabeli mall

Kui retsensendi tagasiside saabub, soovitan vormistada vastavusanalüüs järgmise struktuuriga (täidetav konkreetsete tõenditega töö failidest):

| Märkus nr | Retsensendi sisu (lühend) | Töö asukoht (fail + jaotis/rida) | Sisuline muudatus | Hinne 0–10 | Soovitus parandamiseks |
|-----------|---------------------------|----------------------------------|-------------------|-----------|------------------------|
| 1 | … | nt `chapters/second_chapter.tex`, §X | … | … | … |
| 2 | … | … | … | … | … |

Sellise tabeli täitmiseks vajab agent kaht asja: märkuste loendit ja võimalust töö failide diff-i vaadata (vajadusel git ajaloos, et tõendada \emph{muutunud} sisu, mitte üksnes kohalolevat).

### B. Töö hetkeseisu sisuline auditeerimine eeldatavate retsensendi-küsimuste vastu

Allpool on praktiline ülevaade nendest töö osadest, mida tüüpiline TalTechi retsensent kõige tõenäolisemalt küsimuse alla seab — ning töö praegune positsioneering nendes punktides. See ei asenda vastavusanalüüsi, kuid annab autorile pildi, milliseid \emph{võimalikke} märkusi töö juba ennetab ja millised punktid jäävad nõrgaks.

**1. Eesmärgi ja uurimisküsimuse selgus.**
Töö eesmärk on sõnastatud nii sissejuhatuses (rida 2) kui kokkuvõttes (rida 1) ühtemoodi: \enquote{uurida, kuidas ehitada eestikeelset äratussõna tuvastust piiratud ressursiga nutikodu mikrokontrolleril}. Põhiküsimus ja neli alamküsimust on esitatud sissejuhatuse loendis (read 9–15). **Tugevus.** Võimalik retsensendi nõrkus: seos ülesandepüstituse \enquote{eesmärk on töötada välja eestikeelne äratussõna mudel} (`ylesandepystitus.tex`, rida 68) ja sissejuhatuses esitatud \enquote{uurida} sõnastuse vahel — esimene on tehnilis-praktiline, teine teaduslik-uuriv. Kui retsensent on selle vastuolu märkinud, vajaks kontrollimist, kas sissejuhatuse sõnastus kajastab ülesandepüstituse uuendatud versiooni.

**2. Metoodika rangus ja FAPH-i variandid.**
Peatükk 1 (`first_chapter.tex`, §FAPH-i variandid ja loendusreegel, read 62–71) eristab nüüd selgelt nelja FAPH-i mõõdiku varianti ja viitab loendusreegli ebareprodutseeritavusele kirjanduses \cite{lopezespejo2021deepkws}. **See on suure tõenäosusega vastus eelmisele tagasisidele**, kus mõõdiku ühetähenduslikkust oleks võinud kahtluse alla seada. Ilma ametliku retsensiooniteta ei saa seda kinnitada, kuid sektsiooni olemasolu viitab autori varasemale teadlikkusele riskist.

**3. Andmelekke audit ja kõrvalejäetud komplekt.**
Peatükk 2 (`second_chapter.tex`, \enquote{Esimene ring --- klipi-tasemeline FPR}, read 100–101) dokumenteerib ausalt v6 mudeli ${\sim}50$ FAPH/h reaalajas, lekke avastamise ja paranduse. Sama ausus kordub kontrollpunkti-FAPH eksperimendi puhul (kokkuvõte, rida 7). **Tugevus, mis ennetab kriitikat \enquote{tulemused on liiga roosilised}.** Võimalik retsensendi-küsimus, mille suhtes praegune tekst ei ole täielikult kaitstud: sõltumatu kõrvalejäetud komplekti täpne moodustamise protseduur (kuidas kõnelejad eraldati, kas ID-de kattuvuse kontroll on koodi-tasandil dokumenteeritud) — kui see küsimus on retsensiooni märkuste hulgas, peab autor osutama konkreetsele skripti- või konfiguratsioonifailile.

**4. Kasutajatesti staatus.**
Sissejuhatus ja kokkuvõte räägivad kasutajatestist tulevikuvormis (\enquote{kavandatud}, \enquote{järgmine kriitiline samm}, vt `second_chapter.tex` rida 134; kokkuvõte rida 9). **See on töö selgeim haavatavus.** Kui retsensent on märkinud, et bakalaureusetöö lubab empiirilist valideerimist (`ylesandepystitus.tex` §Tulemuste valideerimine, rida 88–93), kuid lõputekst kasutajatesti tulemusi ei sisalda, on see suure kaaluga märkus. Töö praegune \emph{vastus} sellele — \S\ref{sec:user-test-methodology} (peatükk 1, read 129–137) detailne metoodika kirjeldus — leevendab puudust üksnes osaliselt: metoodika on dokumenteeritud, aga reaalsed osalejate andmed puuduvad. Kui retsensent on seda märkinud ja autor pole vahepeal kasutajatesti läbi viinud, jääb hinne sellele märkusele paratamatult madalaks (5–7/10) sõltumata sõnastusest.

**5. Tulemuste kvantifitseerimine ja usaldusvahemikud.**
\S Hindamismõõdikud (peatükk 1, rida 60) lisab nüüd 95\% usaldusvahemikud (Wilson + Poisson-Garwood + kolmereegel). **Tugevus, ennetab statistilise ranguse kriitikat.** Sissejuhatuse rida 7 ja peatükk 2 rida 143 mõlemad rõhutavad, et 0,79 FAPH on \emph{punkthinnang}, mitte stabiilne tootmiskvaliteedi väide. **Tugevus, ennetab \enquote{ülemüümise} kriitikat.**

**6. Ülesandepüstituse ja sissejuhatuse vahelised tühimikud.**
Ülesandepüstituses on lubatud \enquote{kasutajapõhine valideerimine} ja \enquote{tehniline mõõtmine} (rida 88–93). Sissejuhatus ja kokkuvõte raporteerivad ainult tehnilise valideerimise tulemusi. Kui retsensent on osutanud \enquote{lubatu vs tehtu} lõhele, on see aus märkus, mille leevendamiseks on töös kaks teed: (a) kasutajatest enne kaitsmist läbi viia, või (b) muuta ülesandepüstitus retroaktiivselt nii, et kasutajatest oleks selgelt \enquote{järgmise sammu} positsioonis. Praegune töö valib mõlema vahel: kasutajatesti metoodika on detailne, kuid tulemused puuduvad.

**7. Ekspertmudelite konsensuse staatus.**
Kokkuvõttes (rida 7) on konsensus esitatud \enquote{praktilise laiendusena}, mitte töö lõpliku panusena. Sama hoiak peatükk 2 lõpus (rida 143). **Tugevus.** See on autori ette planeeritud kaitse \enquote{see polnud algses ülesandepüstituses} kriitika vastu.

### C. Soovitatav järgmine samm autorile

1. Lae üles või edasta konkreetse retsensendi (või eelkaitsmise) tagasiside teksti ning käivita viip uuesti — siis genereerib agent korrektse, tõendipõhise vastavustabeli iga märkuse kohta.
2. Kuni see ei ole tehtud, kasuta käesoleva dokumendi punkti B kontroll-loendina selleks, milliseid \emph{tõenäolisi} märkusi tuleks ennetavalt katta.
3. Kui retsensiooni veel pole, kuid on plaan see lähinädalatel saada, tasub samal ajal ette valmistada vastavustabeli skelett (punkt A) — see kiirendab tegelikku tagasiside-läbitöötamist olulises ulatuses.

## Kokkuvõte

Käesolev viip on **evaluatiivne / kontrollivat tüüpi**, mis nõuab konkreetset võrdlusalust (retsensendi märkused). See alus puudub praeguses sisendis, mistõttu nõuetekohast vastavusanalüüsi ei ole võimalik teostada ilma fakte väljamõtlemata. Selle dokumendi sisu on \emph{best-effort} — see selgitab lünka, pakub välja vastavustabeli malli ning kaardistab töö hetkeseisu eeldatavate retsensendi-küsimuste vastu, mis on kooskõlas viiba metoodilise vaimuga, kuid ei asenda tegelikku tagasiside-võrdlust.
