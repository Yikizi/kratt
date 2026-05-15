---
source_prompt: 07_Teadusartikkel/Soovitused_konkreetse_konverentsi_jaoks.txt
prompt_type: evaluative (gatekeeper-roll: konverentsi programmikomitee juht)
generated: 2026-05-07
---

# Soovitused konkreetse konverentsi jaoks --- programmikomitee gatekeeper'i hinnang

## 0. Lünk lähtestuses (vajalik selgitus)

Lähteprompt nõuab konkreetset konverentsi (`<Sisesta konverentsi nimi>`),
mille programmikomitee juhi rolli ma võtaksin, ja kohustuslikku
"taustauuringut" (Aims and Scope, Guide for Authors, hiljutised artiklid)
veebiotsinguga. Käesolevas keskkonnas:

1. **Konverentsi nime ei ole sisendis täidetud** --- tegemist on
   placeholder-iga `<Sisesta konverentsi nimi>`, mitte konkreetse sihtkohaga.
2. **Veebiotsingu samm on piiratud** --- ma ei käivita selle ülesande
   raames live-otsinguid konverentside CFP-de kättesaamiseks; tuginen
   töös endas olevale viitebaasile (microWakeWord, openWakeWord, Picovoice,
   López-Espejo 2021 ülevaade, Apple Hey-Siri jms) ja oma teadmistele
   tüüpilistest CFP-piirangutest 2025--2026.

Selleks et prompt ei jääks rakenduseta, esitan **Go/No-Go otsuse**
kuue realistliku kandidaatkonverentsi/foorumi kohta, mille fookusesse
\enquote{Kuule Kratt} tüüpi töö üldse mõttekalt mahub. Lugeja saab valida
neist endale relevantse ja võtta vastava otsuse arvesse; teised on
selgesõnaliselt välja sõelutud. See on parim võimalik teostus
puuduva sihtkonverentsi nime ja keelatud live-otsingu tingimustes.

---

## 1. Sobivuse otsus (Go / No-Go) --- kandidaatfoorumite kaupa

Hindan kuut tüüpilist sihtfoorumit, mille profiili järgi seda tööd võib
proovida pakkuda. Igale neist annan ülemise piiri (kõige soosivam
tõlgendus tööst, mis on \emph{transformeeritud} bakalaureusetööst
artikliks). Hinne on tinglik ja lähtub töö praegusest seisust ja
viitebaasist.

### 1.1 Interspeech (ISCA, peaüritus)

**Hinne: 18\,\% --- TAGASI LÜKATUD (REJECT)**

Interspeech'i tase ja vastuvõtu konkurents on kõnetehnoloogia
laia spektri tipp. Töö praegune sõnum --- \enquote{esimene eesti
keele äratussõnamudel} ja kohalik valideerimisprotokoll --- ei vasta
Interspeech'i uudsuskünnisele:

* Mudel kasutab muutmata MixedNet/SVDF arhitektuuri \cite{microwakeword2026,
  alvarez2019svdf} ja standardvõtteid (SpecAugment, INT8-kvantiseerimine);
  arhitektuurset või õppealgoritmilist uudsust ei ole.
* Multi-mõõdikuline hindamine ja konsensus-kaskaad on Interspeech'i
  kogukonnas tuntud konstruktsioonid \cite{apple-heysiri2017,
  gruenstein2017cascade,sigtia2020multitask}; töö ise möönab, et
  panus ei ole nende leiutamine, vaid madala ressursiga keelele
  kohandamine (§\ref{sec:contribution-transferability}).
* Eksperimendi maht on liialt kitsas: üks äratusfraas, üks keel,
  kasutajatest veel teostamata, päriskõnelejate baas \enquote{kitsas}
  (§3.4 \enquote{Empiiriline tõendus lahknevusest}), välitingimuste
  FAPH-statistika tugineb Common Voice ET ühele kõrvalejäetud kogumile.
* Töö enda ausad piirangud (§3 \enquote{Aus piir: võimalik neljas ring},
  v16c \enquote{ei ole tootmisse rakendatav tõendus} kokkuvõttes)
  on diagnoosivalt tugevad, kuid Interspeech'i kontekstis võrduvad
  väitega, et lõplik valideerimine on tegemata.

**Põhjus**: liiga lokaalne probleem, ebapiisav uudsus, lõpetamata
empiiriline kinnitus.

### 1.2 ICASSP (IEEE Signal Processing Society)

**Hinne: 12\,\% --- TAGASI LÜKATUD (REJECT)**

ICASSP nõuab signaalitöötluse või masinõppe meetodi tasemel uudsust
(uus arhitektuur, uus kadu, uus optimeerimismeetod, uus tunnusevorm).
Käesolev töö ei paku midagi sellisest:

* Tunnused, arhitektuur, kvantiseerimine, voogedastusrežiim --- kõik
  baasraamistiku vaikeväärtused.
* Töö metodoloogiline panus (kolme-ringi audit) on \emph{empiiriline
  tõendusprotokoll}, mitte signaalitöötluse algoritm.

**Põhjus**: vale valdkond ICASSP-i tuumikfookuse jaoks.

### 1.3 IEEE ASRU / IEEE SLT (workshop'id, kasutusjuhtumitele lähemal)

**Hinne: 28\,\% --- TAGASI LÜKATUD (REJECT)**

ASRU/SLT on Interspeech'ist veidi avaramad rakenduslike kõnetehnoloogia
sõnumite suhtes ja võtavad vastu ka kasutuskeskseid hindamistöid.
Sellegipoolest:

* Rangete usaldusvahemikega (Garwood-Poisson, Wilson) ja audit-narratiiviga
  artikkel oleks SLT-le sobivam kui Interspeech'ile, kuid tase eeldab
  vähemalt ühte uut empiirilist väidet, mis on kindlamini põhjendatud
  kui \enquote{kahe mudeli konsensusel 0,79 FAPH ühel kõrvalejäetud
  korpusel} (kokkuvõte; tab.\,\ref{tab:expert-consensus}).
* Kasutajatest pole teostatud (§\ref{sec:user-test-methodology}, ainult
  metoodika); ASRU/SLT eeldaks selle juba sisaldumist.
* Päriskõnelejate baasi nappus + ühe sõna fookus piiravad väite
  ülekantavust.

**Põhjus**: metoodika on värske ja huvitav, kuid empiiriline tugi on
liiga kitsas (üks fraas, üks keel, üks kõrvalejäetud korpus, kasutajatest
ootel). Selles seisus jääb pakkumus alla SLT/ASRU vastuvõtulati.

### 1.4 LREC-COLING (Resources \& Evaluation)

**Hinne: 35\,\% --- TAGASI LÜKATUD (REJECT)**

LREC-COLING on andmeressursside ja hindamise jaoks õige perekond ning
metoodikatöö, mis dokumenteerib madala ressursiga keele äratussõna
hindamisprotokolli, võiks siia kontseptuaalselt sobida. Aga:

* LREC eeldab tavaliselt \emph{avalikustatud} ressurssi: korpust,
  hindamistoru, evalviiteid. Käesolevas töös on andmestiku osa
  privaatsuskaalutlustel piiratud (ülesandepüstitus mainib \enquote{vältida
  toorsalvestuste avalikustamisest tulenevaid privaatsusriske}; töö ei
  luba avalikku eestikeelset wake-word korpust).
* Avaliku artefakti puudumine vähendab LREC-i jaoks väärtust kriitiliselt.
* Kasutajatesti andmed (kõige väärtuslikum osa LREC-i jaoks) on
  kogumata.

**Põhjus**: ressursi-konverents ilma avaliku ressursita jätab
panuse õhku rippuma. Kui hilisemas faasis avaldatakse kasutajatesti
salvestuste anonümiseeritud osa või sünteetiline negatiivkorpus, võiks
otsust üle vaadata.

### 1.5 EACL / NAACL Industry Track või kohalik kõnetehnoloogia workshop (nt Interspeech satellite, SIGUL/CCURL madala ressursiga keelte workshop)

**Hinne: 55\,\% --- GO** (tingimuslik; ainukene reaalne sihtmärk
praeguses seisus).

Madala ressursiga keelte workshop'id (CCURL, SIGUL, ComputEL, EURALI,
samuti ACL Findings madala ressursiga radade jaoks) ja Interspeech'i
satelliit-workshop'id ootavad just sellist tüüpi tööd: kohaliku keele
süsteem, dokumenteeritud hindamisprobleemid, ülekantav metoodika
teistele madala ressursiga keeltele.

* Töö §\ref{sec:contribution-transferability} \enquote{Töö-tasemel panus
  ja selle ülekantavus} on praktiliselt valmis raamistus
  CCURL/SIGUL-tüüpi panuseks.
* §\ref{sec:benchmark-gap} \enquote{Standardsete võrdlusaluste ebapiisavus}
  haakub otseselt kogukonnaga, kes on aastaid argumenteerinud, et
  inglise-keskne benchmark-kultuur ei kanna üle.
* Konsensus-FAPH 0,79 ja kolme-ringi audit on workshop-formaadis
  esitatav ka ilma kasutajatesti lõpetamiseta, kui see piirang
  ausalt välja öelda.

Otsus on tingimuslik selles mõttes, et töö tuleb \emph{halastamatult
ümber kirjutada} bakalaureusetöö narratiivist 6--8-leheküljelisesse
artiklisse (vt §2). Kui see transformatsioon tehakse korralikult,
on workshop-vastuvõtu tõenäosus mõõdukalt soosiv.

### 1.6 BalticHLT (Baltic Conference on Human Language Technologies) või Eesti Rakenduslingvistika Ühingu konverents

**Hinne: 70\,\% --- GO**

BalticHLT-il ja kohalikel ELT-foorumitel on selgesõnaline ja
deklareeritud huvi just selliste tööde vastu: balti keele
kõnetehnoloogia, kohalik infrastruktuur, väikese ressursiga
hindamine. Üks äratusfraas ühes keeles on siin täiesti aktsepteeritav
ulatus, eriti kui sõnum keskendub \enquote{kuidas hinnata madala
ressursiga keele äratussõna mudelit usaldusväärselt}, mitte
\enquote{state-of-the-art võit}. Töö praegune sisu mahub selle
profiiliga 12--16-leheküljelisse formaati ilma sisulise
mahareltimiseta.

**Selle hinde kohta jätkan järgneva transformatsiooniplaaniga
(§2--§3).** Ülejäänud foorumite jaoks (1.1--1.4) lõpetan vastuse
siinkohal: sellisel kujul ei tohiks neisse esitada.

---

## 2. Teisenduse plaan: bakalaureusetööst BalticHLT/CCURL-tüüpi
artikliks

### 2.1 Kärpimine (halastamatu)

Bakalaureusetöö maht ja struktuur ei kanna üle 8--12-leheküljelisesse
artiklisse. Välja tuleb visata või drastiliselt lühendada:

* **Sissejuhatuse õpikulaadne osa** (eestikeelse ASR-i olukord,
  microWakeWord/openWakeWord raamistike võrdlus üldisel tasemel,
  Picovoice'i taustaülevaade). Artiklisse jääb 1 lõik motivatsiooni
  + 1 lõik sõnumit.
* **Metoodika peatüki andmeliikide klassifikatsioon**
  (§\enquote{Andmeliikide eristamine}, MUSAN/VOiCES/Common Voice
  rolli kirjeldus üldisel tasemel). Asendada 1 lõiguga
  Andmestiku alajaotuses.
* **MixedConv ploki õpikuselgitused**, residuaalühenduste teooria,
  SpecAugmenti motivatsioon. Need on kirjandusest tuntud
  (\cite{he2016resnet,park2019specaugment,choi2021bcresnet}); mainida
  ühe lausega koos viidetega.
* **Kvantiseerimise õpikulaadne lõik** (§\ref{subsec:quantization}):
  jätta ainult \enquote{INT8 TFLite, $148\,\mathrm{KB}$ + tensor-arena
  $\sim$50\,KB, mahub ESP32-S3 kohale} ja vastavad numbrid tabelisse.
* **\enquote{Agentpõhine arendus kui töövõimendaja}** (§3 vastav
  alapeatükk): ei kuulu konverentsiartikli teadusliku
  argumendi sisse. Maksimaalselt 2-lauseline märkus
  Limitations/Threats-osas. Ülejäänud välja.
* **FAPH variantide nelikjaotus** (§\ref{subsec:faph-variants}):
  artiklisse jääb 1 lõik selgitusega, miks reporteerime
  \enquote{scripted offline FAPH} ja \enquote{field FAPH} eraldi;
  täielik nelikjaotus läheb appendix'i, kui pikkus lubab, muidu
  välja.
* **Edasised suunad: kaskaadarhitektuur** (§\ref{sec:future-cascade}):
  tihendada üheks Discussion'i lõiguks. Praegune maht (eraldi peatükk
  + 6 viidet kirjandusele) on liialdus.
* **Ülesandepüstitus, abstrakt-eesti, abstrakt-inglise, kokkuvõte**:
  bakalaureusetöö formaadi rudimendid; ei migreeru.
* **Mitmed keskmise pikkuse seletavad lõigud**, mis eessõnalistab
  juba esitatud argumente (nt korduv väide, et \enquote{multi-mõõdikuline
  hindamine on parem}). Üks selge formuleering ja edasi.

### 2.2 Fookus --- üks väide, mille ümber artikkel kerib

Kõige tugevam teaduslik väide, mille see töö suudab käesolevas
seisus kanda, ei ole \enquote{esimene eesti äratussõnamudel} ega
\enquote{0,79 FAPH konsensusel}. See on:

> **Kolme-ringi audit (data-leakage $\rightarrow$ positiive-class
> labeling $\rightarrow$ checkpoint-objective shortcut) tõestab
> empiiriliselt, et madala ressursiga keele äratussõna projektis
> ühe hindamismõõdiku optimeerimine toodab süstemaatiliselt
> \enquote{lühitee}-mudeleid, mis paistavad benchmark'il tugevad ja
> kasutuses nõrgad. Sama mehhanism kordub kolmel sõltumatul tasemel.**

Kõik muu --- konsensus-FAPH 0,79, MixedNet-i konfiguratsioon, ESP32-S3
juurutus, ESPHome-integratsioon --- on selle väite \emph{tõendusmaterjal},
mitte iseseisev panus. Artikkel peab sellel hingel kerima ja kõik,
mis ei toeta seda väidet, kärbitakse.

### 2.3 Lisamine

Artikli vastuvõtuks (eriti §1.5 workshop-perekond) on praeguses tekstis
mitu auku, mis tuleb täita:

* **Otsene võrdlus state-of-the-art lahendusega**: Picovoice Porcupine
  ei toeta eesti keelt (töö ise mainib), kuid avaliku Porcupine'i
  ingliskeelne mudel võiks joosta sama hindamistoru läbi avaliku
  ingliskeelse äratussõna peal --- näitamaks, et auditi mehhanism
  on raamistikust sõltumatu. Alternatiivina: openWakeWord eraldi
  ingliskeelne mudel sama torustikul.
* **Numbritabel transformatsiooni järel**: artikli põhitulemus peab
  mahtuma ühte 6--10-realisesse tabelisse, mis kõrvuti näitab kõiki
  kolme ringi (FPR-1 baseline $\rightarrow$ FAPH-2 nakkuseta $\rightarrow$
  composite-3) ja igal real, milline mõõdik liikus ja milline mitte.
* **Statistilise ranguse minimum**: iga FAPH-väärtuse juurde Wilsoni
  või Garwood-Poissoni 95\% CI; \enquote{0,79} ilma vahemikuta ei
  läbi retsensiooni.
* **Joonis, mis võtab kokku \enquote{benchmark vs reality} lahknevuse}:
  praegu on see verbaalne; vaja vähemalt scatter-graafikut
  (benchmark-FAPH x-teljel, field-FAPH y-teljel, paaridega mudelid).
  Sama graafiku puudumist Reviewer #2 tuvastab kohe.
* **Ausalt deklareeritud piirang**: kasutajatest \emph{ei ole
  teostatud}, see on töö järgmine kriitiline samm. Workshop'is
  on see aktsepteeritav, kui see seisab Threats to validity'is
  selgelt; tipp-tasemel konverentsil mitte.

### 2.4 Soovituslik konkreetne struktuur (BalticHLT/CCURL-formaat)

8--10 lk:

1. **Sissejuhatus: madala ressursiga keele äratussõna ja benchmark-realiteedi
   lõhe** (1 lk) --- ei \enquote{Krati taust}, vaid \enquote{lõhe
   tehniliste mõõdikute ja kasutusvalmiduse vahel madala ressursiga
   keelte äratussõna projektides}.
2. **Seotud töö: KWS-i benchmarking, lühitee-õppimine ja madala
   ressursiga keele kõnetehnoloogia** (1 lk).
3. **Seadistus: \enquote{Kuule Kratt} kui kontrollkeskkond, andmestik,
   torustik, hindamiskonventsioonid} (1 lk).
4. **Kolm valideerimisringi: empiiriline tõendus lühitee-õppimisest}
   (3--4 lk; üks alapeatükk ringi kohta + kokkuvõttev tabel).
5. **Disainiprintsiip: hindamise piirid kui treenitavad lühiteed} ja
   ülekantavus (1 lk).
6. **Limitations ja future work: kasutajatest, neljas ring,
   kaskaadarhitektuur} (0,5 lk).
7. **Järeldus} (0,3 lk).

### 2.5 Pealkiri (ei mingeid üldsõnalisi)

Praegune töö \enquote{eestikeelne äratussõna \enquote{Kuule Kratt}}
ei kanna artikli sõnumit. Konkreetsed kandidaadid:

* \enquote{Kolme valideerimisringi audit: kuidas madala ressursiga
  keele äratussõna mudel õpib lühiteid, kui hindamine on liiga kitsas}
* \enquote{Benchmark vs.\ reality madala ressursiga äratussõna jaoks:
  kolm sõltumatut juhtu eesti keele \enquote{Kuule Kratt}-i näitel}
* \enquote{Kui \enquote{0,4\,\% FPR} tähendas \enquote{50 FAPH}:
  väikese keele äratussõna mudeli hindamise tõendusdistsipliin}

---

## 3. Kokkuvõte gatekeeper'i seisukohalt

* **Interspeech / ICASSP / ASRU / SLT / LREC-COLING**: \emph{Reject}
  käesolevas seisus. Nõutud uudsus, empiiriline ulatus või avalik
  ressurss puuduvad.
* **Madala ressursiga keelte workshop (CCURL, SIGUL, ComputEL vms)**:
  \emph{conditional Go (55\,\%)}, kui §2 transformatsioon
  tehakse ära ja kasutajatesti puudumine deklareeritakse selgelt.
* **BalticHLT või kohalik HLT-foorum**: \emph{Go (70\,\%)}, kus töö
  praegune sisu kannab juba enam-vähem konverentsiartikli mahtu, kui
  fookus nihutatakse \enquote{esimene eesti äratussõna} pealt
  \enquote{kolme-ringi audit ja lühitee-õppimine madala ressursiga keele
  äratussõnas} peale.

Lugejale: kui sihtkonverentsi nimi on tegelikult juba teada (nt töö
juhendaja on soovitanud konkreetset foorumit), siis selle prompti
uuesti käivitamine täidetud nime ja \emph{värske} CFP-ga annab
täpsema otsuse. Käesolev hinnang on parim võimalik teostus puuduva
sihtkohaga sisendi ja ilma live-otsinguta.
