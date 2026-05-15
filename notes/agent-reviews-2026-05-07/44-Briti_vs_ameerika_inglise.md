---
source_prompt: 04_Kontrollimine/Konkreetsed_vead/Vorm/Briti_vs_ameerika_inglise_keel.txt
prompt_type: evaluative
generated: 2026-05-07
---

# Audit: Briti vs Ameerika inglise keel

## Auditi ulatus ja eeldused

Töö ise on kirjutatud eesti keeles. Sidusas inglise keeles on praktiliselt
ainult ingliskeelne kokkuvõte (`misc/abstract-english.tex`). Eesti
keeles kirjutatud peatükkides esinev inglise keel piirdub:

- termini ingliskeelse vastega sulgudes (nt `(ingl \emph{wake word})`,
  `(ingl \emph{streaming inference})`, `(ingl \emph{ground truth})`),
- tehniliste lühendite avamisega (`false accepts per hour`,
  `false rejection rate`),
- raamistike, projektide ja andmestike pärisnimedega (`microWakeWord`,
  `openWakeWord`, `Speech Commands`, `Common Voice`, `MUSAN`, `VOiCES`),
- kirjandusest tsiteeritud terminitega (`partial-keyword`,
  `swapped-order`, `pre-context`, `tensor_arena`, `mmap`).

Need on terminoloogilised tsitaatlaenud, mitte sidus inglise keelne tekst,
ning UK/US-eristuse seisukohalt ei kanna nad õigekirjavalikut --- kõik
kasutatud kujud (`wake word`, `streaming`, `pre-context`, `pipeline`,
`recall`, `pointwise`, `depthwise`, `kernel size`, `internal state`,
`vanishing gradients`, `temporal reduction`, `redundant`,
`full integer quantization` (toode), `false accepts per hour`,
`false rejection rate`, `ground truth`) on kas üheselt rahvusvahelised
või järgivad raamistiku/teose enda kirjapilti, mida ei ole asjakohane
ümber kirjutada.

Seetõttu keskendub käesolev audit ingliskeelsele kokkuvõttele
`abstract-english.tex`. Faili `abstract-estonian.tex`, samuti eestikeelsed
peatükid, jäävad audit-ulatusest välja, kuna neis ei ole sidusat
inglise keelt, mille suhtes UK/US-eristust saaks kohaldada.

## Tuvastatud keelekuju konfliktid

### Dokumendi valitsev (või nõutud) standard

Nõutud keelekuju ei olnud parameetrina ette antud. Tekstianalüüs:
ingliskeelse kokkuvõtte sõnavarast on UK/US-eristuse seisukohalt eristav
ainult üks juhtum (`specialized`), mis vastab US-õigekirjale. Teisi
US-spetsiifilisi (`-ize`, `-or`, `-er`, `-se`) ega UK-spetsiifilisi
(`-ise`, `-our`, `-re`, `-ce`, kahekordne `-ll-`) markereid tekstis ei
esine. Üksiku tõendi põhjal ei saa statistilist \enquote{ülekaalu} 80\%
kindlusega kinnitada, kuid ainsa kallutatud signaali kohaselt järgib
tekst US-konventsiooni. Auditeerin teksti seetõttu **US inglise keele**
suhtes ning märgin lisaks ära neutraalsed kohad, kus US-i ja UK võimalik
lahknemine \emph{ei realiseerunud}, et kinnitada teksti üldist
järjepidevust.

### Leitud eksimused (US standardi suhtes)

Selle juhise alusel (US inglise keel) sidusas tekstis eksimusi ei ole.

### Leitud eksimused (UK standardi suhtes)

Kui töö juhendaja eelistab UK inglise keelt --- näiteks selleks, et olla
sidus TalTechi ametliku kirjasõna ja paljude Euroopa akadeemiliste väljaannete
tavaga ---, tuleb teha üks parandus.

- **Asukoht:** `misc/abstract-english.tex`, kolmas sisuline lõik
  (algupärases failis rida 5).
    - **Vigane/Ebasobiv tekst:**
      \enquote{consensus among specialized expert models}
    - **Põhjendus:** Kasutatud on US-õigekirja `-ize`. UK-konventsioon
      eelistab seda tüvi-/järelliite kombinatsiooni puhul üldjuhul
      `-ise`-vormi (Oxfordi väljaande \enquote{Oxford spelling}-erand
      siia ei ulatu, sest töö ülejäänud tekstis ei kasutata
      järjekindlat Oxfordi-stiili).
    - **Parandus:** \enquote{consensus among specialised expert models}

Kui valitakse UK-versioon, on see kogu töös ainus muudatus, mis on
vajalik. Muid `-ize/-ise`, `-or/-our`, `-re/-er`, `-ce/-se` ega
kahekordse konsonandi vorme inglise tekstis ei kasutata.

## Kontroll-loend (sõnad, mille puhul kontrollitakse, et lahknevus puudub)

Need vormid kas \emph{esinevad ja on neutraalsed}, või on \emph{tahtlikult
puudu} ja seega ei saa eksimust põhjustada. Loend on antud läbipaistvuse
huvides, et hilisem retsensent ei peaks neid otsima.

- Tüvedest \texttt{analyse/analyze}, \texttt{recognise/recognize},
  \texttt{organise/organize}, \texttt{realise/realize},
  \texttt{optimise/optimize} ei esine ükski tekstis (sõna
  \enquote{optimistic} on UK ja US ühisvorm ning ei kuulu
  \texttt{-ise/-ize} reeglistiku alla).
- Sõnu \texttt{behavior/behaviour}, \texttt{color/colour},
  \texttt{labor/labour}, \texttt{favor/favour} ei esine.
- Sõnu \texttt{center/centre}, \texttt{meter/metre},
  \texttt{fiber/fibre} ei esine.
- Sõnu \texttt{defense/defence}, \texttt{license/licence},
  \texttt{practice/practise} ei esine.
- Sõnu \texttt{traveling/travelling}, \texttt{modeling/modelling},
  \texttt{labeling/labelling}, \texttt{canceled/cancelled} ei esine.
- Sõnu \texttt{program/programme}, \texttt{story/storey} ei esine.

## Kirjavahemärgid ja vormistus

Sidusas inglise tekstis (`abstract-english.tex`) kasutatakse jutumärkide
sees `\enquote{...}` makrot, mis renderdatakse \texttt{babel}-i poolt
keelekonteksti järgi. See on \emph{semantiline}, mitte stilistiline
valik ega kuulu UK/US otsuse alla --- vormi (üksikud vs topeltjutumärgid)
määrab seadistus, mitte autori tippimisotsus. Punkti ja koma asukoht
jutumärkide suhtes ei tule esile, sest tsiteeritakse vaid pärisnimesid
(\enquote{Kratt}, \enquote{Kuule Kratt}, \enquote{sufficient}-tüüpi sõnu
ei tsiteerita). Kuupäeva- ja kellaajavorme ingliskeelses tekstis ei ole.

Üks tähelepanek vormistuse järjepidevuse, mitte UK/US eristuse kohta:
ingliskeelses kokkuvõttes kasutatakse pikka mõttekriipsu (em-dash) kujul
\enquote{---} kahel korral, mis vastab nii US-i kui UK akadeemilise
kirjastuse tavale, ning seda soovituse korras muuta ei ole. Kui aga
juhendaja nõuab range UK-stiili, võiks kaaluda em-dash'i ümbruses
tühikute lisamist (UK \enquote{ -- } on samuti aktsepteeritav, kuid
muutus on stilistiline, mitte ortograafiline, ja jääb käesoleva auditi
ulatusest välja).

## Kokkuvõte ja soovitus

- Sidus ingliskeelne tekst (kokkuvõte, ${\sim}$~lehekülg) on UK/US
  eristuse mõttes **peaaegu täiesti puhas**: ainus eristav sõna on
  \texttt{specialized}.
- Kui jätta keelekuju määramata, kaldub kokkuvõte juba praegu **US
  inglise keele** poole ja muudatusi pole vaja.
- Kui valitakse **UK inglise keel** (soovitatav, kui ülejäänud TalTechi
  ametlik dokumentatsioon või juhendaja eelistus seda nõuab), tuleb teha
  täpselt üks parandus: \texttt{specialized} $\rightarrow$
  \texttt{specialised}.
- Eestikeelsetes peatükkides esinevad inglise terminid on
  terminoloogilised tsitaatlaenud ega kuulu UK/US auditi alla; nende
  ühtlustamine pärisnimede kirjapildiga (`microWakeWord`,
  `openWakeWord`, `Speech Commands`) on vajaduse korral eraldi
  vormistusotsus.
- Soovitus autorile: fikseerida valitud keelekuju (UK või US) ühe
  reaga töö stiilijuhise faili või README-sse, et hilisem
  keeletoimetaja saaks teha lõppvooru auditi sama eelduse alusel.
