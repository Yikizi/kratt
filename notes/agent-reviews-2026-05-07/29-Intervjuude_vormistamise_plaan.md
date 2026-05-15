---
source_prompt: Intervjuude_tulemuste_vormistamise_plaan.txt
prompt_type: generative
generated: 2026-05-07
---

# Juhend poolstruktureeritud intervjuude tulemuste vormistamiseks Kratti lõputöös

## Eelmärkus: rakendatavuse piir ja kohandus

Käesolev juhend on kohandatud, sest lisatud prompti ja Kratti lõputöö vahel on
oluline metodoloogiline lahknevus, mille üliõpilane peab eessõnas läbipaistvalt
kirja panema:

* **Prompt eeldab klassikalist poolstruktureeritud intervjuud** (avatud küsimustega
  vestlus, transkriptsioon, temaatiline kodeerimine).
* **Töös kavandatud andmekogumine on hübriidne ja valdavalt struktureeritud**:
  10-minutiline ühtsete ülesannetega varju-demo (`ten-minute-shadow-demo-protocol.md`),
  millele järgneb Likert-tüüpi küsimustik (`questionnaire-v1.md` /
  `mini-questionnaire-form-v1.md`) ja vaid 1--3 lühikest avatud küsimust (H2, H3,
  vajadusel C5/F2 selgitused). Seega ei ole tegemist täismahus poolstruktureeritud
  intervjuuga, vaid \emph{kvantitatiivse kasutajatesti kõrval kogutud kvalitatiivse
  jääkmaterjaliga}.

Sellele vaatamata kerkivad esituslogist (helilõik + tahvel) ja vabavastustest üles
narratiivid, tsitaadid ja korduvad teemad, mille käsitlemiseks kehtivad samad UX
Researchi vormistuspõhimõtted. Allolev juhend näitab, kuidas vormistada \emph{just
seda} hübriidset andmestikku nii, et lugeja näeks sõltumatust, GDPR-vastavust ja
metodoloogilist distsipliini, ega ootaks kogemata 60-minutilise intervjuu mahuga
analüüsi. Kus prompt eeldab tugevamat intervjuu-mahtu, esitatakse parim võimalik
lähendus ja täiendava materjali kogumise piir on selgesõnaliselt välja toodud.

---

## 1. Rakendamine lisatud küsitlusele (spetsiifika)

### 1.1. Andmestiku tüpoloogia: mis on kvant, mis on kvalit

Tulemused tuleb esitada kihiti, vastavalt sellele, kuidas konkreetne küsimus
kogutud sai. Igale kihile peab lugejal olema selge, milliste väidete tõendina see
toimib (vt §\ref{sec:eval-evolution} laiemat protokolli):

| Kiht | Kuidas kogutud | Esitusviis tulemustes | Esitusviis arutelus |
|------|----------------|------------------------|---------------------|
| Objektiivsed mõõdikud (äratuse tuvastamismäär, sarnaste negatiivnäidete FPR, otsast-lõpuni edukus, latentsus) | `kratt user-test` --- mõõdetuna salvestatud WAV-idelt taasmängu kaudu | Tabel + Wilsoni 95\% usaldusvahemikega tulpdiagramm | Tõlgendus disainikompromisside valguses |
| Suletud küsimustik (A--G, I) | Google Forms 7-punkt Likert / kategoorilised | Stacked bar (Likert) ja sagedusjaotused (kategoorilised); mediaan + kvartiilid | Lühike kommentaar mustri kohta |
| Vabad vastused (C5 selgitus, H2, H3) | Forms vaba tekst | Lühitabel teemadest + arvuline esinemissagedus | Otsetsitaadid kui näited, mitte tõendid |
| Vaatluslikud märkmed | Pilot-run sheet, sessioonilogi, tahvli vaatlused | Loetelu \emph{esinenud} käitumistest (ei nähtud, kuidas vältida) | Triangulatsioon kvant-tulemustega |

**Konkreetsed soovitused küsimustiku kaupa**:

* **0.1--0.7 (demograafia)** — esita \emph{koondtabelina} (üks rida vanusgrupi
  kohta, vastavad sagedused) ja kontrolli kvoodi täitumist (nt 18--34 vs 55+
  vahekord). \emph{Mitte} esitada osaleja-kaupa nimekirjana, see on
  Participant Matrixi (vt §3.2) ülesanne ja eeldab pseudonüümi.
* **A1--A6 (üldine kasutatavus)** — visualiseeri \emph{ühe pinotud
  tulpdiagrammina} (Likert-stack), kus iga küsimus on rida ja iga vastusekategooria
  on segment. Lõputöös tasub raporteerida ka koondskoor (Kratt usability score
  0--100), kuid see ei ole valideeritud VUS, mistõttu nimetada seda
  ``Kratt-spetsiifiline liitskoor''. Ärge tehke t-teste, kui valim on \emph{n}
  $\leq$ 30 ja jaotus ei ole normaalne.
* **B1--B2, C1--C3, D1--D2, E1--E2 (kiirus, äratus, keel, privaatsus)** —
  raporteeri \emph{küsimuste-kaupa boxplot} (mediaan, IQR), sest valim on liiga
  väike koondkeskväärtuse mõtestatud kasutamiseks. Lisa joonise pealkirja Likerti
  ankur (1 = ei nõustu üldse, 7 = täielikult).
* **C4 (tahtmatu vallandumine)** — kategooriline; esita \emph{sagedustabelina}
  ning triangileeri see C4-vastus reaalselt logitud FAPH-iga (sessioonilogist).
  See on töö üks kõige tugevamaid kvant-kvalit triangulatsioonipunkte.
* **C5 (kas eelistaksid muud äratussõna)** — Jah/Ei sagedus, järgnev vaba tekst
  esita \emph{teemade tabeli} kujul: ettepanek, kui paljud välja pakkusid,
  illustreeriv tsitaat. Vältige üksikute pakutud variandite tähestiku-loendit;
  see on müra.
* **F1--F2 (võrdlus)** — F1 esita sagedustulpadena (mitut süsteemi kasutati),
  F2 \emph{ainult} F1-le ``jah'' vastanutel ja eraldi kommentaariga, et
  alarühm on väiksem.
* **G1--G2 (NPS, kasutamissoov)** — esita NPS arvutuskäik (\% promoters --
  \% detractors), kuid eraldi rõhutusega, et $n < 30$ puhul on NPS
  punkthinnang, mitte tööstusstandardile vastav skoor; lisa \emph{toores
  jaotus} 0--10 skaalal.
* **H1 (käskude kordamise arv)** — sagedushistogramm.
* **H2--H3 (vabad vastused)** — \emph{ainsana} klassikalises kvalitatiivse
  analüüsi mõttes. Vt §4 koodipuu ja tsitaatide kasutamise kohta.
* **I1--I2 (UMUX-Lite)** — raporteeri valem, koondskoor 0--100,
  Wilsoni usaldusvahemik ja viide \cite{lewis2013umuxlite}-le. See on
  ainus valideeritud lühiskaala töös; käsitle seda eraldi alajaotusena.

### 1.2. Mida visualiseerida, mida üldistada, mida tsiteerida

* **Visualiseerida** (graafik): A1--A6 stacked bar; B/C/D/E box-plot;
  G2 jaotus 0--10; UMUX-Lite koondskoor.
* **Tabelina esitada**: demograafia, C4 kategooriad, F1 jaotus, NPS
  arvutuskäik, vabavastuste teema-tabelid, otsast-lõpuni edukus per käsk.
* **Üldistada (proosa)**: korduvad mustrid esitusandmetes (nt ``viiest
  osalejast neli ütlesid \enquote{Kule Kratt} esimese ütluse juures
  \enquote{Kuule Kratt} asemel''). See on kvalitatiivne üldistus, mis
  triangileerib §\ref{sec:eval-evolution}-s tõstatatud Kule/Kuule riski.
* **Otsetsiteerida**: H2, H3 ja C5 selgitused. Eelistus piiratud arvule
  (3--6 kogu peatüki kohta), igaüks ankurdatud teksti väitega ja
  pseudonüümiga (P03, naine, 25--34, sagedane häälassistendi kasutaja).

---

## 2. Struktuurne jaotus (põhiosa vs lisad)

### 2.1. Metoodika peatükk (kuulub töö metoodika osasse, mitte tulemustesse)

Metoodika peatükk peab katma:

1. **Uurimisküsimus** — millele kasutajatest vastab (sellisel kujul, nagu see on
   sõnastatud §\ref{sec:user-test-methodology}-s: kas mudel käitub piisavalt
   usaldusväärselt päris kõnelejatega ja milline on subjektiivne rahulolu).
2. **Disain** — lühikese (\(\sim\)10 min) ülesande-keskse demo struktuur:
   5 puhast ütlust + 5 sarnast negatiivnäidet + 6 skriptitud käsku + 1 vaba
   ülesanne. Selgesõnaliselt välja tuua, et tegemist ei ole klassikalise
   poolstruktureeritud intervjuuga, vaid kvantitatiiv-domineeriva sessiooniga,
   kus kvalitatiivne kiht tuleb vaba teksti ja vaatlusmärkmete kaudu.
3. **Värbamine ja valim** — kvoodid (vanusgrupid, varasem häälassistendi
   kogemus), suurus (sihiks 20--30), saturatsiooni- vs võimsuspõhine
   põhjendus. Selgitada, et $n$ on kompromiss kaitsmistähtaja ja
   nullhüpoteesi pinnale toomise vahel.
4. **Aparatuur** — Pi 5, ESP32-S3 satelliit, mikrofon, valgustus, ruum
   (vt `portable-setup.md`).
5. **Mudelite seis** — külmutatud lävi, aktiivne mudel (\texttt{v16c}),
   varimudelid (\texttt{expert-a}, \texttt{expert-b2}, \texttt{v6-residual},
   \texttt{v10}, \texttt{v15}, konsensus). Viidata külmutuspoliitikale
   (`frozen-threshold-policy.md`).
6. **Andmekogumise tööriistad** — \texttt{kratt user-test},
   \texttt{kratt validate-user-test}, \texttt{kratt replay-user-test},
   \texttt{kratt summarize-user-test}.
7. **Eetika ja nõusolek** — kaheastmeline nõusolek (pseudonüümne baas + audio
   opt-in), GDPR-õiguslik alus, säilitamise tähtaeg, ligipääsu kontroll.
8. **Andmeanalüüsi metoodika** — kvant: Wilsoni usaldusvahemikud, NPS,
   UMUX-Lite valem; kvalit: induktiivne avatud kodeerimine H2/H3 vastustele
   ühe kodeerija (autori) poolt, koodipuu väljatöötamine peale 5 vastust ja
   kontroll järgmiste järgu vastuste vastu (vt §4).
9. **Piirangud** — väike $n$, üks lühike sessioon, ühe kodeerija subjektiivsus,
   sotsiaalse soovitavuse kalle, demoefekt.

### 2.2. Tulemuste peatükk

Tulemuste peatükk \emph{kirjeldab}, ei tõlgenda. Soovitatav alajaotus:

* Sessioonide ülevaade (kuupäevad, läbiviidud sessioonide arv, väljalangenud
  sessioonid).
* Osalejate koondprofiil (demograafiline tabel + kvoodi täitumise kommentaar).
* Objektiivsed mõõdikud per mudel (tabel: tuvastamismäär, sarnaste FPR,
  otsast-lõpuni edukus, latentsus, koos Wilsoni usaldusvahemikega).
* Subjektiivne rahulolu: A--E plokkide jaotused, UMUX-Lite, NPS.
* Vabavastuste temaatiline kokkuvõte (teema, esinemissagedus, näide).

### 2.3. Arutelu peatükk

Arutelu peatükk \emph{seob} tulemused töö keskse väitega
(§\ref{sec:eval-evolution}: mitmemõõtmeline hindamine). Konkreetselt:

* Kas C4 (subjektiivselt tunnetatud valeaktiveeringud) ja logitud FAPH
  langevad kokku?
* Kas Kule/Kuule jaotusliku riski (vt §\ref{sec:user-test-results}) prognoos
  kinnitus reaalsete kõnelejate peal?
* Kas konsensuse-mudel (expert-a + expert-b2) säilitab kasutajatestis sama
  $0,79$ FAPH-eelise, mis kõrvalejäetud komplektis?
* Mida vabad vastused lisavad, mida kvant-mõõdikud ei näita
  (nt häiriv kogemus, ootuse-reaalsuse vahe)?
* Triangulatsiooni jälgida selgelt --- iga arutelu väidet peab toetama
  vähemalt \emph{kaks} sõltumatut allikat (kvant + kvalit; või kvant +
  vaatlus).

### 2.4. Lisad (Appendix)

Lisadesse \emph{peavad} minema:

1. **Sessiooniprotokoll** (puhastatud `ten-minute-shadow-demo-protocol.md`
   versioon, ilma sisemiste TODO-märkmeteta).
2. **Pilootide tagasiside ja tehtud muudatused** (`pilot-run-sheet-v1.md`
   alusel), et lugeja näeks evolutsiooni piloodist põhitestiks.
3. **Nõusolekuvorm ja -skript** (`consent-script-v1.md`).
4. **Küsimustik tervikuna** (Forms eksport või `mini-questionnaire-form-v1.md`),
   nii eesti kui ka inglise tõlge, kui mõni osaleja oli mitte-eesti emakeelega.
5. **Koodipuu (codebook)** vaba teksti analüüsi jaoks (vt §4): koodi nimi,
   määratlus, näide.
6. **Pseudonüümitud Participant Matrix** (vt §3).
7. **Värbamiskanalid ja kutsekirja tekst**, kui see oli formaliseeritud.

Lisadesse \emph{ei kuulu} toored transkriptsioonid ega WAV-failid:
audiomaterjal on isikuandmed ja peab jääma kontrollitud säilituskohta.
Lisas viidata, kus ja kui kaua need on hoiul ning kuidas saab neid
päringu korral läbi vaadata (juhendaja kaudu, mitte avaliku repo kaudu).

---

## 3. Intervjueeritavate taust ja anonüümsus

### 3.1. Üldine põhimõte

GDPR-i järgi on \emph{hääl} biomeetriline isikuandmete liik. Sama kehtib
demograafiliste andmete kombinatsioonile, mis võivad lubada
de-anonüümistamist (nt naine, 18--24, vene emakeel, üliõpilane,
Lasnamäelt --- selliste detailide kombinatsioon võib olla ühene). Seetõttu
peab tabelitestus rakendama \emph{minimeerimise printsiipi}: avalikkusele
nähtavas dokumendis hoida vähim, mis lugejale konteksti annab.

### 3.2. Participant Matrix --- soovitatav formaat

| Pseudonüüm | Vanusgrupp | Sugu | Eesti keele tase | Häälassistendi kogemus | Sessiooni kestus | Audio opt-in |
|------------|------------|------|------------------|------------------------|-------------------|---------------|
| P01 | 25--34 | M | Emakeel | Iga päev | 11 min | Jah |
| P02 | 55--64 | N | Emakeel | Mitte kunagi | 9 min | Ei |
| ...  | ... | ... | ... | ... | ... | ... |

**Reeglid**:

* Pseudonüüm formaadis P01, P02, ... ja **mitte initsiaalid**.
* Vanus alati gruppi rühmitatud, mitte aastates.
* Linnaosa, töökoht, õppeasutus jms väljas; kui konkreetne tausta-detail
  on \emph{vajalik} mõne väite jaoks (nt ``üks osaleja töötas raadiojaamas''),
  siis lisa see ainult selle ühe tsitaadi juurde, mitte koondtabelisse.
* Audio opt-in veerg näitab lugejale, mis alusel tsitaat võib olla nii
  kirjalik kui kuuldav (kuigi kuuldavat ei avaldata).
* Tabel peaks mahtuma ühele leheküljele. Kui osalejaid on 30, kasuta
  kompaktset versiooni (4--5 veergu).

### 3.3. Tsitaatide atribuudid

Tsitaadi juurde lisatakse \emph{atribuutide miinimumkomplekt}, mis on
piisav konteksti jaoks ja ei vähenda anonüümsust:

> ``Ma ei saanud aru, kas peaksin ootama või proovima uuesti.''
> --- P14, naine, 35--44, häälassistente kasutab harva.

Mitte: linnaosa, ametinimetus, perekonnaseis, lapse vanus jms.

### 3.4. Audio ja transkriptide säilitus

* Audiofaile (kus on opt-in antud) säilitada krüpteeritud kohas
  (TalTech OneDrive või kohalikul šifritud ketta-osal), mitte avalikus
  repos.
* Säilitustähtaeg: kuni kaitsmiseni + nõutud arhiiviperiood; pärast seda
  kustutus ja kustutusakti dokumenteerimine.
* Lõputöös \emph{ei lisata} audio QR-koodi ega lingi avalikku audiofaili.
* Toored transkriptid (kui need üldse tehakse vabavastustest) jäävad
  pseudonüümituna autori privaatsesse arhiivi ja juhendajale taotluse
  korral kättesaadavaks.

---

## 4. Analüüs, üldistamine ja tsitaadid

### 4.1. Tasakaal üldistuse ja tsitaadi vahel

Kvalitatiivse osa põhiväide on \emph{üldistus} (``mustrid, mis ilmnesid''),
mitte üksiktsitaat. Tsitaat töötab \emph{ankruna}, mitte tõendina.
Praktiline reegel:

1. Iga kvalit-väide peab olema sõnastatud kui muster (``viiest osalejast
   neli ...''; ``valdav hoiak oli ...'').
2. Tsitaat järgneb mustrile illustratsioonina, mitte vastupidi.
3. Vältige arvulist esitlust (``nelja osaleja arvates ...'') väikeste $n$-de
   puhul, kus \emph{neli} võib olla 4/5 või 4/30. Kasuta `4 osalejat 21-st`
   tüüpi sõnastust.
4. Kui $n$ on alla 10 ühe alarühma kohta, ärge raporteerige protsente, vaid
   absoluutarve.

### 4.2. Kodeerimine vabavastustele (H2, H3)

Kuna tegemist on lühikeste vabade kommentaaridega (mitte 60-min intervjuu
transkriptsiooniga), piisab \emph{kerglahjast induktiivsest avatud
kodeerimisest}. Soovitatav protseduur:

1. Loe kõik H2/H3 vastused läbi ühel istumisel.
2. Genereeri esmane koodikomplekt (5--10 koodi: nt
   ``äratuse-tundlikkus'', ``vastuse-loomulikkus'', ``privaatsus'',
   ``kõrvalmüra'', ``kasutusjuht'', ``ettepanek'').
3. Kodeeri uuesti süstemaatiliselt; ühel vastusel võib olla mitu koodi.
4. Loe veelkord, koonda väikeste juhtumite koodid (1 esinemine) ülemkoodi
   alla või eraldi ``muu'' kategooriasse.
5. Esita \emph{koodipuu lisas} ja \emph{koondtabel tulemustes}: kood,
   määratlus, kui mitmel osalejal esines, üks näide.

Ärge nimetage seda ``temaatiline analüüs Brauni-Clarke meetodil'', kui te
ei läbinud nende kuut sammu (familiarisation $\to$ generating codes $\to$
searching for themes $\to$ reviewing themes $\to$ defining $\to$ writing).
Sõnastage realistlikult: ``induktiivne avatud kodeerimine ühe kodeerija
poolt; piiranguks intercoder reliability puudumine.''

### 4.3. Tsitaatide vormistamine akadeemilises tekstis

* Eesti keeles kasutada `\enquote{...}` (käesolev töö juba kasutab) või
  ladusalt eesti keele tsitaatmärke „...''.
* Pikad tsitaadid (üle 40 sõna): plokk-tsitaat, väiksema reasammuga,
  tagataande tasandil.
* Lühitsitaadid (alla 40 sõna): tekstis joonel.
* Iga tsitaadi järel pseudonüüm + atribuudid (vt §3.3).
* Ärge muutke sõnu; lubatud on `[...]` lühenduse näitamiseks ja `[selgitus]`
  mitmemõttekuse lahendamiseks.
* Kui osaleja kasutab kõnekeelt (``noh'', ``ee''), võib seda kärpida
  `[...]`-ga ainult siis, kui see ei muuda tähendust ega afektiivset varjundit.

### 4.4. Tsitaat toetab autori väidet, mitte vastupidi

Vale muster: tsitaat $\to$ ``see näitab, et ...''. Õige muster: autori
väide $\to$ tsitaat illustratsiooniks $\to$ ühenduspaus järgmise lõiguni.

Näiteks vale:

> ``Ma ei saanud aru, miks Kratt ei vasta.'' --- P14. See näitab, et
> äratussõna oli ebausaldusväärne.

Õige:

> Üks korduv muster oli ootuse ja tegelikkuse vahe äratuse hetkel: kui
> esimene ütlus ebaõnnestus, ei olnud osalejatele intuitiivne, kas
> probleem oli häälduses, ajastuses või süsteemi vaikuses. Üks osaleja
> sõnastas selle nii: ``Ma ei saanud aru, miks Kratt ei vasta.''
> --- P14. See ootuse-ebakindlus on töö
> §\ref{sec:fourth-round}-s prognoositud ``võimaliku neljanda ringi''
> klassis, mis nõuab eraldi disainivastust.

### 4.5. Kvalitatiiv-kvant triangulatsioon

Iga peamine järeldus arutelus peab vastama küsimusele: \emph{Kas kvant
ja kvalit jutustavad sama lugu?} Kolm võimalikku tulemust:

* \textbf{Kokkulangevus} --- tugevdab järeldust.
* \textbf{Erinevus} --- tuleb \emph{eraldi raporteerida}, mitte ühtlustada.
  Sotsiaalse soovitavuse kalle kallutab Likert-skoore üles, samas kui H3
  vabad vastused võivad näidata pingeid.
* \textbf{Vaikus} --- mõni teema esineb ainult ühel kihil; sõnastada
  ettevaatlikult.

---

## 5. Andmete visualiseerimine

### 5.1. Mis sobib tabelisse

Tabel on parim:

* **Demograafia** (vt §3.2 Participant Matrix).
* **Koodisagedus** (kood, määratlus, esinemissagedus, näide). Esita
  esinemissageduse järgi sorteerituna kahanevas järjekorras.
* **Per-mudel objektiivsed mõõdikud** (mudel, tuvastamismäär, FPR,
  e2e edukus, latentsus 50/95, Wilsoni CI). See on töö keskne tulemustabel.
* **Kategooriliste küsimuste jaotused** (C4, F1).
* **NPS arvutuskäik**.

### 5.2. Mis sobib graafikule

* **Likert-jaotused** (A1--A6, B--E) --- pinotud tulpdiagramm
  (``stacked Likert chart''), kus iga rida on küsimus, iga segment on
  vastusekategooria, värviskaala diverteeruv (negatiivne $\leftrightarrow$
  positiivne).
* **Boxplot** alarühmade võrdluseks (nt UMUX-Lite ``häälassistendi
  igapäevased kasutajad'' vs ``mitte kunagi kasutajad''), kui $n$
  alarühma kohta $\geq 5$.
* **Joonis ootuse-tegelikkuse lõhest**: prognoositud äratuse
  tuvastamismäär (TTS-positiivsetel klippidel) vs reaalne kasutajatestis
  (Kule/Kuule jaotusega). See on töö keskse väite (lähtuvalt
  §\ref{sec:benchmark-gap}) kõige otsesem visuaalne tõestus ja peaks
  olema arutelu peatüki ankur-joonis.
* **Histogramm**: H1 (kordamiste arv), G2 (NPS toores jaotus 0--10).

### 5.3. Mis ei kuulu visualiseerimisele

* Vabavastuste \emph{sõnapilv} --- mitte kasutada. Kaotab konteksti,
  raskendab lugejal mustri tagasiteed eelmisesse osakesse.
* Iga osaleja Likert-rida \emph{eraldi spaghetti-jooniseks} --- liiga müra,
  ei aita.
* 3D-tulpdiagrammid mis tahes vormis.
* Pirukadiagrammid üle nelja kategooriaga.

### 5.4. Joonise pealkirjastamine

Iga joonis peab kandma kahekihilist pealkirja:

> Joonis X. Subjektiivse rahulolu jaotus küsimuste A1--A6 lõikes ($n=24$).
> Värvigradient diverteerub punktist 4 (neutraalne); 1 = ei nõustu üldse,
> 7 = täielikult nõustun.

Pealkirjas peab olema $n$, skaala ankur ja küsimuste nimekiri lugeja
abimaterjaliks.

---

## 6. Üldised kvaliteedikriteeriumid (kontroll-loend kaitsmiseks)

Enne peatüki lukustamist kontrolli järgmist:

* [ ] Iga avalikul leheküljel olev osaleja-konkreetne fakt on pseudonüümitud.
* [ ] Iga tsitaat on ankurdatud autori väitele, mitte ümberpidi.
* [ ] Iga arvulise väite juures on $n$ ja Wilsoni usaldusvahemik (kus
      asjakohane).
* [ ] Iga visuaali pealkiri kannab $n$-i ja skaala selgitust.
* [ ] Lisas on intervjuukava/sessioniprotokoll, küsimustik, nõusolek,
      koodipuu.
* [ ] Metoodika, tulemused ja arutelu \emph{ei korda} sama infot.
      Metoodika kirjeldab, tulemused esitavad, arutelu seob.
* [ ] Piirangud on eraldi alajaotus, mitte peidetud joonealustes.
* [ ] Sotsiaalse soovitavuse kalle ja demoefekt on nimetatud.
* [ ] Kvalit-kihti ei nimetata ``temaatiliseks analüüsiks'', kui ei läbitud
      kõiki Brauni-Clarke samme; selle asemel kasutatakse täpset terminit
      (``induktiivne avatud kodeerimine ühe kodeerija poolt'').
* [ ] Triangulatsioon kvant-kvalit-vaatlusandmete vahel on selgesõnaliselt
      vormistatud.

---

## 7. Lõppmärkus

Käesoleva töö kontekstis on intervjuude vormistuse \emph{tugevus} mitte selles,
et oleks läbi viidud klassikaline 60-minutiline poolstruktureeritud intervjuu
20+ inimesega (selleks ei ole tähtaja $2026{-}05{-}18$ valguses ressurssi),
vaid selles, et hübriidne 10-minutiline ülesande-keskne sessioon koos
külmutatud mudelitel taasmängitud helimaterjaliga annab mitmemõõtmelise
tõendi --- objektiivsed logid, struktureeritud küsimustik, vabavastused ja
vaatluslikud märkmed --- mille triangulatsioon on metodoloogiliselt aus.
Vormistus peab seda ausust nähtavaks tegema: mitte üle paisutada kvalit-kihti
intervjuuks, mille seda pole, ega alla raporteerida tegelikult kogutud
materjali rikkust.
