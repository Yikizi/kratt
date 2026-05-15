---
source_prompt: /Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/03_Lõputöö_alamosad/Joonised.txt
prompt_type: hibriidne (auditeeriv olemasolevate jooniste osas + generatiivne uute jooniste osas)
generated: 2026-05-07
---

# Jooniste audit ja täiendusettepanekud

Käesolev audit hindab töö praeguses LaTeX-allikas (`chapters/introduction.tex`,
`chapters/first_chapter.tex`, `chapters/second_chapter.tex`,
`chapters/third_chapter.tex`, `chapters/summary.tex` ning eesti- ja
ingliskeelne lühikokkuvõte) leiduvaid jooniseid. Autori kinnitust mööda
peatükiga 4 (Tulemused) töötavad alamtekstid ka tabelite ja lisajooniste osas
edasi; käesolev audit piirdub LaTeX-allikas otseselt nähtavate jooniste-
plokkidega. Koodilõike vorminduse-jooniseid käesolevas tekstis ei esinenud,
kuid prompti reegel nende kohta on järgitud.

## Osa 1: Olemasolevate jooniste audit

### Joonis 1 --- `fig:faph-recall-pareto`
*(Asukoht: \texttt{chapters/second\_chapter.tex}, rida 107--112; lisatud
fail: \texttt{figures/faph\_recall\_pareto.pdf}.)*

* **Joonise nimi/kirjeldus:** Üksiku läve $\theta=0{,}995$
  operatsioonipunktide hajuvusgraafik üle kõikide mudeliversioonide; punase
  joonega märgitud alumise-vasakpoolse mähise (madalaim FAPH iga
  tuvastamismäära taseme jaoks) mudelid. FAPH-telg on
  \texttt{faph\_cv\_et} (3,82\,h voogedastusrada), tuvastamismäära telg on
  \texttt{pos\_speaker\_a\_xtts} ($N=48$).
* **Hinnang:** 8/10
* **Analüüs:** Joonis kannab töö üht kandvat metoodilist sõnumit ---
  äratussõna mudelite valikul ei piisa ühe mõõdiku järjestusest, vaid tuleb
  vaadata FAPH-i ja tuvastamismäära kompromissi koos. Hajuvusdiagramm sobib
  kontseptsiooniks, sest see näitab kahe pideva mõõdiku ühisjaotust ja
  rõhutab, kui kitsas on mudelite alamhulk, mille kohta ei eksisteeri
  domineerivat alternatiivi. Tugevus on selles, et joonisealune kirjeldus
  täpsustab korrektselt, et tegemist ei ole läve-sõltumatu Pareto-rinde
  konstruktsiooniga, vaid ühe konkreetse läve juures arvutatud alumise
  mähisega --- see välistab tihti esineva metoodilise libastumise. Nõrkus
  on aga see, et joonis sõltub väga ühest läve valikust ($\theta=0{,}995$),
  samas kui kõrvaltabelid kasutavad teisi läve väärtusi (nt 0,97 või 0,99).
  Ühtlasi ei ole hajuvusdiagrammile peale kantud (vähemalt allikast loetavalt)
  Wilsoni usaldusvahemikke kummalgi teljel; kui $N=48$ tuvastamismäära
  hinnangud kannavad laiu UV-sid (vt tabel \ref{tab:fair-comparison-holdout}
  vertikaalsed UV-d), võib lugeja ülehinnata mähise lähedaste mudelite
  eristatavust.
* **Soovitus ja asukoht:** Säilitada põhiosas (jaotis 4.X --- mudelite
  korrigeeritud võrdlus). Tugevdamiseks tasub joonisele lisada vähemalt
  ühe-mõõtmelised veatulbad tuvastamismäära telje jaoks (kasvõi mähise
  mudelitele) ning korrata sama joonis ka teise läve (nt $\theta=0{,}97$)
  juures, et näidata mähise stabiilsust. Need on parandused olemasoleva
  joonise raamides, mitte selle väljavahetamine.

### Joonis 2 --- `fig:det-v6-v15-v16c-experta`
*(Asukoht: \texttt{chapters/second\_chapter.tex}, rida 359--364; lisatud
fail: \texttt{figures/det\_v6\_v15\_v16c\_expertA.pdf}.)*

* **Joonise nimi/kirjeldus:** DET-tüüpi (FA/h vs FRR, log-log) kõverad
  nelja mudeliperekonna kohta --- \texttt{v6-residual}, \texttt{v15},
  \texttt{v16c} ja \texttt{expert-a} ---, mille põhjal põhjendatakse
  konsensus-arhitektuuri valikut.
* **Hinnang:** 9/10
* **Analüüs:** DET-kõver on antud kontekstis õige diagrammitüüp: ta
  esitab läve sõltumatu kompromissi FAPH-i ja FRR-i vahel ning võimaldab
  visuaalselt põhjendada konjunktsiooni-konsensuse loogikat (paralleelselt
  jooksvad kõverad $\Rightarrow$ kahe mudeli ühisaktivatsiooni nõue valib
  kõverate ühisosa, mitte ühe kindla läve). See joonis täiendab
  joonist 1 sisuliselt, sest ühelt operatsioonipunktilt liigutakse
  täismahuliselt lävede vahemiku peale. Joonisealune kirjeldus on aus
  selle kohta, et FRR on agregeeritud üle kahe positiivse komplekti ja
  ei eralda tuvastamismäära põrandat --- see sõnastus on metoodiliselt
  tugev. Väike nõrkus: lugejale jääb hetkel kohati ebaselgeks, kuidas
  konsensus ise (nt \texttt{expert-a + expert-b2} või \texttt{v10+v15})
  selles DET-ruumis paigutub --- see on lisainfo, mida visuaal hetkel ei
  kanna, kuigi tekst sellele konsensus-tabelis tugineb.
* **Soovitus ja asukoht:** Säilitada põhiosas. Kui joonise kandidaadid on
  olemas, tasub lisada samale graafikule ka konsensus-konfiguratsiooni
  punkt(id) (üksik märk, kus FA/h ja FRR vastavad konsensusele) --- nii
  saab visuaalselt näidata, et konsensus paikneb üksikute kõverate
  alla-vasakul, mis ongi konsensuse-loogika empiiriline tõestus. See on
  täiendus, mitte ümbertegemine.

### Üldine märkus jooniste hulga kohta
Töö keskne metoodiline narratiiv (sissejuhatus, metoodika peatükk 1,
arutelu peatükk 3) tugineb mitmele kontseptuaalselt rikkalikule
struktuurile --- (a) andmeliikide kolmik (positiivsed / negatiivsed /
taustaheli), (b) hindamise kolm valideerimisringi (klipi-FPR
$\rightarrow$ kolme-mõõdikuline raporteerimine $\rightarrow$
komposiitne kontrollpunkti valik), (c) FAPH-i nelja-variandi
loendusreeglid (raamistiku / skriptitud taasmängu / välitingimuste /
kasutajatesti taasmängu). Need on kõik kontseptid, mille puhul
tekstipõhine esitus on mahukas, kuid visuaalne taju oleks oluliselt
kiirem. Praegu kannab põhiosa ainult kaks kvantitatiivset
tulemus-joonist (need, mis on auditeeritud eespool); puudub aga
kontseptuaalne joonistik, mis aitaks lugejal sisse elada metoodika
peatüki andme- ja hindamiskihi struktuuri. Sellele on vastatud Osa 2 alguses.

## Osa 2: Uued soovituslikud joonised

### Uus joonis 1 --- Andmevoog ja andmeliikide eristamine
* **Joonise eesmärk ja tüüp:** Vooskeem, mis kujutab \enquote{Kratt}
  treeningu- ja hindamistoru ülevaadet: kuidas kolme tüüpi andmed
  (positiivsed, negatiivsed, taustaheli) liiguvad allikatest
  tunnusekstraheerimise kaudu treeningusse ja hindamisse, ning kuidas
  hindamine jaotub klipi-taseme ja voogedastuse-taseme komponentideks
  (sh \texttt{validation\_ambient} / \texttt{testing\_ambient} eraldi
  kogumid). Joonis aitab lugejal mõista, miks kolm andmeliiki on
  metoodikas eraldi käsitletud --- see on praegu tekstis kirjeldatud,
  kuid jääb visuaalselt nähtamatuks.
* **Asukoht töös:** Lisada metoodika peatüki (peatükk 1) jaotise
  \enquote{Andmeliikide eristamine} ja \enquote{Tunnused ja andmevorming}
  vahele või vahetult \enquote{Tunnused ja andmevorming} jaotise lõppu,
  et lugeja saaks andmeliikide kontseptsiooni ja
  \texttt{validation\_ambient}/\texttt{testing\_ambient} jaotuse ühe
  pildi peal kokku panna.
* **PlantUML kood:**
  ```plantuml
  @startuml
  skinparam shadowing false
  skinparam defaultFontSize 12
  skinparam rectangle {
      BackgroundColor White
      BorderColor Black
  }
  skinparam database {
      BackgroundColor #F8F8F8
      BorderColor Black
  }

  title Treening- ja hindamistoru: andmevoog ja andmeliigid

  package "Andmeallikad" {
    database "Positiivsed klipid\n(Kuule Kratt)\nKorvo-2 + TTS" as POS
    database "Negatiivsed klipid\nCommon Voice ET\n+ Korvo-2 negatiivsed" as NEG
    database "Sarnased negatiivnaited\n(kuule rott, kuule kraam, ...)" as HARD
    database "Taustaheli\nMUSAN / VOiCES /\nCommon Voice (pikad)" as AMB
  }

  rectangle "Tunnusekstraheerimine\n(spektrogramm + mmap)" as FEAT

  POS --> FEAT
  NEG --> FEAT
  HARD --> FEAT
  AMB --> FEAT

  package "Andmekogumid" {
    rectangle "training" as TRAIN
    rectangle "validation" as VAL
    rectangle "testing" as TEST
    rectangle "validation_ambient" as VAMB
    rectangle "testing_ambient" as TAMB
  }

  FEAT --> TRAIN
  FEAT --> VAL
  FEAT --> TEST
  FEAT --> VAMB
  FEAT --> TAMB

  rectangle "Treening\n(MixedNet, microWakeWord)" as TR
  TRAIN --> TR
  VAL --> TR : varajane peatumine

  package "Hindamine" {
    rectangle "Klipi-tase\nrecall, FPR, Wilson UV" as CLIP
    rectangle "Voogedastus\nFAPH (Poisson UV)\nROC / DET" as STREAM
  }

  TR --> CLIP
  TEST --> CLIP
  TR --> STREAM
  TAMB --> STREAM

  note right of STREAM
    FAPH-i variandid:
    raamistik / skriptitud /
    valitingimuste / kasutajatest
  end note

  @enduml
  ```

### Uus joonis 2 --- Hindamisprotokolli kolme valideerimisringi areng
* **Joonise eesmärk ja tüüp:** Seisundi-/jadadiagramm (\texttt{state}
  või \texttt{activity}), mis võtab kokku peatüki 3 jaotise
  \enquote{Mitmemõõtmeline hindamisprotokoll kui töö metoodiline
  põhipanus} kolm ringi: (1) klipi-tasemel FPR $\rightarrow$ avastatud
  andmeleke $\rightarrow$ kõrvalejäetud komplektid + voogedastus-FAPH;
  (2) kolme-mõõdikuline raporteerimine $\rightarrow$ avastatud
  prefiksi-/üksiku-sõna lühitee $\rightarrow$ fraasistruktuuri testid;
  (3) ainult-FAPH-i kontrollpunkt $\rightarrow$ avastatud
  tuvastamismäära kollaps $\rightarrow$ komposiitne kontrollpunkti
  kriteerium. Iga ring kujutab paari \enquote{tahtmine vs mõõtmine}
  diagrammilises vormis ning näitab, milline tõendusparandus järgnes.
  See on töö metoodiline põhipanus ja tekstis kirjeldatuna nõuab
  lugejalt mitut lehekülge sammude koos hoidmist.
* **Asukoht töös:** Lisada peatüki 3 jaotise
  \enquote{Mitmemõõtmeline hindamisprotokoll kui töö metoodiline
  põhipanus} (\texttt{sec:eval-evolution}) algusesse, vahetult enne
  alajaotist \enquote{Kolm valideerimiskihti: muster}
  (\texttt{sec:three-rounds}). Sellega saab lugeja jaotise
  \emph{üldvaate} enne tekstipõhist süüvimist.
* **PlantUML kood:**
  ```plantuml
  @startuml
  skinparam shadowing false
  skinparam defaultFontSize 12
  skinparam ArrowColor Black

  title Hindamisprotokolli kolm valideerimisringi

  state "Ring 1: klipi-FPR" as R1 {
    state "Tahtmine:\ngeneralisatsioon" as R1A
    state "Motmine:\nmalukapatsiteet\n(treeningandmete leke)" as R1B
    R1A --> R1B : audit avastas\nandmelekke
  }

  state "Parandus 1:\nkorvalejaetud komplektid +\nvoogedastus-FAPH" as F1

  state "Ring 2: kolme-moodikuline\nraporteerimine" as R2 {
    state "Tahtmine:\naratussona eristamine" as R2A
    state "Motmine:\nkuule/kule prefiksi tuvastus\n(positiivse klassi probleem)" as R2B
    R2A --> R2B : audit avastas\nprefiksi luhitee
  }

  state "Parandus 2:\nrangem positiivsete poliitika +\nfraasistruktuuri testid" as F2

  state "Ring 3: kontrollpunkti\nFAPH-miinimum" as R3 {
    state "Tahtmine:\nvaikne mudel taustaheli peal" as R3A
    state "Motmine:\nvaikne ka sihtkonelejal\n(tuvastamismaara kollaps)" as R3B
    R3A --> R3B : reaalsete\nkonelejate test
  }

  state "Parandus 3:\nkomposiitne kontrollpunkti\nkriteerium" as F3

  state "Aus piir:\nvoimalik 4. ring\n(kasutajatest)" as R4

  [*] --> R1
  R1 --> F1
  F1 --> R2
  R2 --> F2
  F2 --> R3
  R3 --> F3
  F3 --> R4
  R4 --> [*]

  @enduml
  ```

### Uus joonis 3 --- Süsteemiarhitektuur seadmest Home Assistantini
* **Joonise eesmärk ja tüüp:** Komponendi-/juurutusdiagramm
  (\texttt{component} või \texttt{deployment}), mis näitab äratussõna
  mudeli paiknemist tervel hääljuhtimise rajal: ESP32-S3 Korvo-2 seadmel
  jooksev kvantiseeritud TFLite-mudel $\rightarrow$ ESPHome-i
  \texttt{voice\_assistant} liides $\rightarrow$ Home Assistant
  $\rightarrow$ STT (Kiirkirjutaja, lokaalne) $\rightarrow$ käsutoru.
  See joonis aitab lugejal aru saada, kus äratussõna paikneb suuremas
  süsteemis ja miks just selle komponendi madal FAPH on kasutuskogemuse
  esimene filter. Praegu on see suhe kirjeldatud sõnaliselt
  sissejuhatuses ja ülesandepüstituses, kuid puudub lugejasõbralik
  visuaalne kokkuvõte.
* **Asukoht töös:** Lisada metoodika peatüki (peatükk 1) jaotise
  \enquote{Kasutatud tehnoloogiad} lõppu või sissejuhatuse
  \enquote{Praktiliseks sihtplatvormiks on ESP32-S3 \ldots} lõigu järele.
  Sissejuhatuses paiknemine on motiveeriv (lugeja saab kohe
  kogusüsteemi ette); metoodikas paiknemine on tehniline (tehnoloogiavalik
  saab visuaalse kokkuvõtte). Soovitus on paigutada joonis sissejuhatuse
  lõppu, et lugeja saaks juba enne metoodikat skeemi näha.
* **PlantUML kood:**
  ```plantuml
  @startuml
  skinparam shadowing false
  skinparam defaultFontSize 12
  skinparam rectangle {
      BackgroundColor White
      BorderColor Black
  }

  title Lokaalse haalejuhtimise raja arhitektuur

  node "ESP32-S3 Korvo-2\n(satelliit)" as DEV {
    rectangle "Mikrofon +\neelvotrtlus" as MIC
    rectangle "microWakeWord\n(MixedNet, INT8 TFLite)\n~57 - 148 KB" as MWW
    rectangle "ESPHome firmware\n+ voice_assistant" as ESPH
    MIC --> MWW : 16 kHz heli
    MWW --> ESPH : aratus-sundmus
  }

  node "Koduvork (lokaalne)" as LAN

  node "Raspberry Pi 5\n(Home Assistant host)" as HA {
    rectangle "Home Assistant\n(automaatika)" as HACORE
    rectangle "Wyoming /\nvoice_assistant" as WY
    rectangle "Kiirkirjutaja STT\n(eestikeelne ASR)" as STT
    rectangle "Intent / kasutoru\n(seadmete juhtimine)" as INT
    WY --> STT : audio puhver
    STT --> INT : transkriptsioon
    INT --> HACORE : tegevus
  }

  ESPH -down-> LAN
  LAN -down-> WY

  rectangle "Nutikodu seadmed\n(valgustus, anduri, ...)" as DEVS
  HACORE --> DEVS

  note right of MWW
    Aratussona on kasutuskogemuse
    esimene filter: tema FAPH
    maarab kogu raja kasutatavuse
  end note

  @enduml
  ```

---

## Kokkuvõte audiitorile

Praeguses LaTeX-allikas leidub kaks põhiosasse paigutatud kvantitatiivset
joonist (\texttt{fig:faph-recall-pareto} ja
\texttt{fig:det-v6-v15-v16c-experta}). Mõlemad on metoodiliselt
kaitstavad ja kannavad konkreetset väitepanust; mõlemad teenivad lisaks
joonisealustes kirjeldustes esitatavat metoodilist täpsust (mähis ei ole
Pareto-rinne; FRR on agregeeritud). Töö nõrkus jooniste osas ei ole
seega olemasolevate jooniste kvaliteet, vaid \emph{kontseptuaalsete
jooniste puudus}: töö kannab keerukat tõendusdistsipliini-narratiivi
ainult tekstis. Soovitatud kolm uut joonist (andmevoog, hindamise kolm
ringi, süsteemiarhitektuur) katavad just need kohad, kus visuaalne
esitus toetaks lugejat kõige tõhusamalt, ilma et need dubleeriks
olemasolevaid kvantitatiivseid tulemusjooniseid.
