---
source_prompt: Kontrolli_kirjanduse_ülevaate_otsingu_märksõnu.txt
prompt_type: evaluative (rakendatud puuduva sisendiga: lünga selgitus + parima võimaliku rekonstruktsiooni hinnang)
generated: 2026-05-07
---

# Kirjanduse ülevaate otsingusõnade kontroll

## 0. Lünga selgitus (rakendatavuse piirang)

Lähteviipa eesmärk on hinnata üliõpilase koostatud **otsingustringi / märksõnade nimekirja**, mida kasutatakse süstemaatilise kirjanduse ülevaate (SLR) tegemiseks teadusandmebaasides (Scopus, Web of Science, IEEE~Xplore). Käesoleva töö LaTeX-allikfailides (sissejuhatus, peatükid 1--3, kokkuvõte, ülesandepüstitus, eesti- ja ingliskeelne annotatsioon) ei ole sellist eraldiseisvat otsingustringi ega märksõnade nimekirja kirja pandud. Kirjanduse käsitlemine toimub jooksvalt, allikaviidetena (\cite{...}) lause sees, mitte SLR-protokollina koos otsingulausega ja kaasamise/välistamise kriteeriumitega. Ülesandepüstituse fail (\texttt{ylesandepystitus.tex}) loetleb \texttt{pdfkeywords} väljas neli sõna --- \emph{äratussõna, nutikodu, Home Assistant, eesti keel} ---, kuid need on dokumendi metaandmed, mitte andmebaasiotsingu märksõnad.

Sellest tulenevalt rakendatakse viipa **parima võimaliku rekonstruktsioonina**: tuletan kasutatud allikate ja sissejuhatuse argumentatsiooni põhjal selle implitsiitse märksõnaruumi, mille pinnalt töö de facto kirjandust kogus, ja hindan seda viipa kriteeriumide kohaselt. Kõik allpool esitatud ,,olemasolevad'' märksõnad on tuletatud ainult tekstis tegelikult viidatud teemadest (mitte väljamõeldud).

### Rekonstrueeritud implitsiitne märksõnaruum (tuletus)

Tekstist nähtuvad teemaplokid, millele on viidatud (\texttt{references.bib} kaudu jooksvas tekstis):

- **Äratussõna tuvastus / kõnesõna tuvastus**: \emph{wake word, keyword spotting (KWS), small-footprint keyword spotting} (Chen~et~al.\ 2014; López-Espejo~et~al.\ 2021).
- **Mikrokontrolleri-klassi mudelid**: \emph{microWakeWord, openWakeWord, TensorFlow Lite Micro, ESP32-S3, ESPHome}.
- **Arhitektuur**: \emph{MixedNet / MixConv, SVDF, depthwise/pointwise convolution, BC-ResNet, residual connections, streaming inference}.
- **Treeningu- ja andmekorpused**: \emph{Speech Commands, MUSAN, VOiCES, Common Voice}.
- **Augmentatsioon**: \emph{SpecAugment, synthetic data augmentation, TTS-based data generation, Neurokõne}.
- **Hindamismõõdikud**: \emph{false accepts per hour (FAPH), false rejection rate (FRR), Wilson interval, Poisson--Garwood interval, rule of three, ROC, AUC}.
- **Eesti keel ja kõnetehnoloogia**: \emph{Estonian ASR, Kiirkirjutaja, TalTech ASR, Riigikogu stenograms}.
- **Suletud lähtekoodiga võrdluspunkt**: \emph{Picovoice Porcupine}.
- **Nutikodu / hääljuhtimine**: \emph{Home Assistant, Wyoming protocol, voice assistant, smart speaker}.

See on viite-allikaks olnud märksõnaruumi rekonstruktsioon ja seda hinnatakse alljärgnevalt nii, nagu oleks tegemist üliõpilase otsingustringi nimekirjaga.

---

## 1. Üldhinnang otsingustrateegiale

- **Hinnang:** Rekonstrueeritud märksõnaruum on \textbf{teemakohaselt asjakohane, kuid struktuurilt fookusest hajutatud}. Märksõnad katavad korraga nelja eri tasandit (mudeliarhitektuur, andmestik, hindamismõõdikud, integratsioonikiht), ilma et oleks selgitatud, milline tasand on uurimisküsimuse seisukohast otsingu \emph{ankur} ja milline ainult tausta täiendav. Sellisena töötaks see otsingustring andmebaasis vaid siis, kui kõik tasandid kombineeritakse loogiliselt operaatoritega \texttt{AND}/\texttt{OR}; vastasel juhul pakuks otsing kas tuhandeid asjakohatuid vasteid (laiad terminid nagu \emph{voice assistant}, \emph{smart home}) või liiga väheseid (tootenimed nagu \emph{microWakeWord}).
- **Riskid:**
  1. Domineerib **toote- ja raamistikupõhine sõnavara** (microWakeWord, openWakeWord, ESPHome, Home Assistant), mis võib akadeemilises andmebaasis anda alla saagi --- need terminid esinevad sageli ainult inseneri-blogides ja GitHubi README-des, mitte eelretsenseeritud artiklites.
  2. Puuduvad **konkurentsivõimelised akadeemilised sünonüümid** (\emph{keyword spotting}, \emph{voice trigger}, \emph{always-on speech recognition}), mistõttu jääb suur osa kirjandust välja.
  3. Eestikeelse aspekti kohta on otsingupotentsiaal madal: ainult \emph{Estonian} ja \emph{Kiirkirjutaja} ei taga, et leitakse väikese keeleruumi äratussõna tuvastuse kirjandus laiemalt (\emph{low-resource}, \emph{cross-lingual}).
  4. Nutikodu ja Home Assistanti kihi märksõnad toovad kaasa müra (\emph{IoT, smart home, automation}), mis ei käsitle äratussõna tuvastust ennast.

---

## 2. Puuduvad märksõnad ja sünonüümid (lisada)

- **\emph{keyword spotting} / \emph{KWS} / \emph{small-footprint keyword spotting}**
  - *Põhjendus:* Akadeemilises kirjanduses kasutatakse äratussõna tuvastuse ülesande kohta enamasti just neid termineid (vt Chen~2014, López-Espejo~2021, mida töö juba viitab). Ainult \emph{wake word} otsing jätab välja suurema osa IEEE/ACM artikleid. \emph{KWS} akronüüm on andmebaasides eraldi indekseeritud.
- **\emph{voice trigger} / \emph{hotword detection} / \emph{trigger word detection}**
  - *Põhjendus:* Apple'i ja Amazoni publikatsioonid kasutavad \emph{voice trigger} ja \emph{hotword}; nende ärajätmine sulgeb olulise tööstusliku kirjandusplokki, mis käsitleb täpselt sama tuvastusprobleemi.
- **\emph{always-on speech recognition} / \emph{low-power speech detection}**
  - *Põhjendus:* Servaseadme ja energiaeelarve fookusega artiklid kasutavad neid termineid, mitte \emph{wake word}; see on otseselt seotud käesoleva töö ESP32-S3 ressursipiirangu argumentatsiooniga.
- **\emph{low-resource speech} / \emph{under-resourced languages} / \emph{small-language ASR}**
  - *Põhjendus:* Töö üks põhilisi väiteid on, et eesti keel kuulub väikese keeleruumi alla. Ilma nende terminiteta jääb metoodiline võrdluskirjandus (nt aafrika ja põhjamaa keelte kohta) leidmata. \emph{Estonian} üksinda ei ole piisav.
- **\emph{synthetic speech for training} / \emph{TTS-based data augmentation} / \emph{data augmentation for keyword spotting}**
  - *Põhjendus:* Töö kasutab Neurokõne põhiselt sünteetilisi positiivseid näiteid, kuid otsingusõnastikus puudub vastav akadeemiline mõiste, mis seoks selle laiema TTS-augmentatsiooni kirjandusega.
- **\emph{streaming inference} / \emph{on-device inference} / \emph{TinyML} / \emph{microcontroller deep learning}**
  - *Põhjendus:* TinyML on tänapäeval tunnustatud andmebaasi-termin (TinyML Foundation, ACM TinyML Research Symposium); see avab juurdepääsu mikrokontrolleri-suunalisele neurovõrkude kirjandusele, mis \emph{ESP32-S3} märksõna kaudu ei tule.
- **\emph{false alarm rate} / \emph{false trigger rate} / \emph{operating point analysis}**
  - *Põhjendus:* FAPH on kitsas raporteerimisviis; akadeemilised tööd kasutavad sageli \emph{false alarm rate (FAR)}, \emph{miss rate}, \emph{detection error tradeoff (DET)}. Ilma nendeta ei leita võrdlusmetoodikat eelretsenseeritud allikatest.
- **\emph{quantization-aware training} / \emph{post-training quantization} / \emph{INT8 inference}}**
  - *Põhjendus:* Töö kvantiseerimise jaotis põhineb Jacob~et~al.\ 2018 ideel, kuid otsingusõnastikus puudub vastav termin, mis on kvantiseerimise kirjanduses standardne.
- **\emph{wake-up word} (sidekriipsuga variant) ja \emph{wakeword} (kokku)**
  - *Põhjendus:* Erinevad andmebaasid indekseerivad neid eri viisil; sidekriipsu kasutus \emph{ei} kao automaatselt --- vajalik mõlemad lisada operaatoriga \texttt{OR}.
- **\emph{Wyoming protocol} / \emph{voice satellite}**
  - *Põhjendus:* Home Assistanti integratsioonikihi puhul on \emph{Wyoming} just see termin, mille kaudu integreerimispoolset kirjandust ja dokumentatsiooni leitakse; \emph{Home Assistant} üksinda on liiga lai.
- **UK/US õigekirja variandid:** \emph{recognise / recognize}, \emph{modelling / modeling}, \emph{centred / centered}
  - *Põhjendus:* Kohustuslik andmebaasiotsingu hügieen --- ilma nende paaride lisamiseta jääb 30--50\% IEEE Xplore'i ja Web of Science'i kirjest leidmata.

---

## 3. Üleliigsed või ohtlikud märksõnad (eemaldada/muuta)

- **\emph{smart home} / \emph{nutikodu}**
  - *Põhjendus:* Liiga üldine; tagastab tuhandeid IoT-, energiajuhtimise- ja turvalahenduste artikleid, mis ei puuduta äratussõna tuvastust. Kattub osaliselt sõnaga \emph{Home Assistant}, mis on juba spetsiifilisem.
  - *Soovitus:* Eemaldada peamise otsingustringi tuumast; jätta valikuliseks lisanditeks teisejärgulises otsingus, alati operaatoriga \texttt{AND} äratussõna ploki vastu.
- **\emph{TensorFlow} (üksinda)**
  - *Põhjendus:* Liiga üldine; tagastab kõik TensorFlow'd kasutavad masinõppetööd. Ei lisa otsingule fookust, mis on juba kaetud spetsiifilisemate \emph{TensorFlow Lite Micro} või \emph{microWakeWord} terminite kaudu.
  - *Soovitus:* Asendada terminiga \emph{TensorFlow Lite Micro} või \emph{TFLite Micro}; eraldi \emph{TensorFlow} jätta välja.
- **\emph{voice assistant} (üksinda)**
  - *Põhjendus:* Liiga lai --- domineerivad turundusartiklid Alexa, Google Assistanti ja Siri kohta, mitte tehniline äratussõna kirjandus.
  - *Soovitus:* Asendada täpsema fraasiga \emph{voice assistant wake word} või kombineerida ploki sees teiste terminitega \texttt{AND}-iga.
- **\emph{Home Assistant} (eelretsenseeritud kirjanduse jaoks)**
  - *Põhjendus:* Akadeemilises kirjanduses esineb harva; toode kuulub avatud lähtekoodi/inseneripraktika maailma. Ei tasu eeldada, et sellest sõnast tuleb otsingu suur saagis.
  - *Soovitus:* Hoida ainult **integratsiooni- ja insenerikirjanduse** otsingus (GitHub, dokumentatsioon, blogid), mitte teadusandmebaasi peamises stringis.
- **\emph{microWakeWord}, \emph{openWakeWord}, \emph{ESPHome}, \emph{Picovoice Porcupine} (eelretsenseeritud kirjanduse jaoks)**
  - *Põhjendus:* Tegemist on tootenimedega, mille kohta otsing teadusandmebaasides annab harva eelretsenseeritud vasteid; need on hallide allikate (GitHub, dokumentatsioon, ettevõtte avalikud raportid) tasandi terminid.
  - *Soovitus:* Eraldada **kaheks otsingutasandiks**: (a) akadeemiline string ilma tootenimedeta, (b) hallide allikate string nendega koos. Töös on see eraldus juba implitsiitselt olemas (\texttt{microwakeword2026}, \texttt{openwakeword2026} on viidatud kui ,,Võrguteavik''), kuid metoodika kirjeldab seda ebaselgelt.
- **\emph{Kiirkirjutaja} (üksinda)**
  - *Põhjendus:* Konkreetse Eesti tööriista nimi; sobib ainult eestikeelse kõnetuvastuse kontekstis. Ainsa eesti keele märksõnana jätab kogu väikese keeleruumi metoodilise kirjanduse leidmata.
  - *Soovitus:* Säilitada, kuid ainult kõrvalmärksõnana; põhitelg peab olema \emph{Estonian} \texttt{OR} \emph{low-resource language} \texttt{OR} \emph{under-resourced language}.

---

## 4. Soovituslik otsingustringi struktuur (boonus)

Soovitan jagada otsingustringi viieks loogiliseks plokiks, mis vastab käesoleva töö ülesehitusele (PICO-laadne kohandus: \emph{Population} = väikese keele kõnelejad ja servaseadmed; \emph{Intervention} = äratussõna mudel + augmentatsioon; \emph{Comparison} = avatud raamistikud vs.\ Picovoice; \emph{Outcome} = FAPH/recall):

```
( "wake word" OR "wake-up word" OR "wakeword"
  OR "keyword spotting" OR "KWS" OR "small-footprint keyword spotting"
  OR "hotword" OR "hot-word" OR "voice trigger" OR "trigger word" )

AND

( "low-resource" OR "under-resourced" OR "low resource language"
  OR "Estonian" OR "small language"
  OR "data augmentation" OR "synthetic speech"
  OR "TTS-based" OR "text-to-speech augmentation" )

AND

( "microcontroller" OR "MCU" OR "edge device"
  OR "TinyML" OR "on-device" OR "embedded"
  OR "TensorFlow Lite Micro" OR "TFLite Micro"
  OR "streaming inference"
  OR "quantization" OR "INT8" )

AND

( "false accepts per hour" OR "FAPH"
  OR "false alarm rate" OR "FAR"
  OR "false trigger rate"
  OR "miss rate" OR "FRR"
  OR "detection error tradeoff" OR "DET curve"
  OR "ROC" OR "operating point" )
```

Eraldi, **hallide allikate plokk** (GitHub, dokumentatsioon, ettevõtte raportid), mida ei ühendata akadeemilise stringiga, vaid hoitakse SLR-protokollis eraldi inkluseerimisreeglitega:

```
( "microWakeWord" OR "openWakeWord" OR "ESPHome"
  OR "Picovoice Porcupine" OR "Wyoming" OR "Home Assistant voice" )
```

### Märkused viite ühendamise kohta

1. Soovitan andmebaasiotsingu logi (kuupäev, andmebaas, otsingustring, vastete arv enne ja pärast skriiningut) lisada käesoleva töö repositooriumi --- praegu seda dokumenti ei eksisteeri ja seetõttu ei ole otsingu reprodutseeritavus täielikult tagatud.
2. Soovitan kirjeldada metoodikas eraldi, milline osa kirjandusest on **eelretsenseeritud** (Scopus/WoS/IEEE) ja milline on **insener-tehnilise hallide allikate** päritolu (GitHub, ESPHome dokumentatsioon, Picovoice'i avalikud võrdlusalused). Praegune sissejuhatus segab need allikaklassid ühte lausesse, mis vähendab metoodika selgust.
3. Inkluseerimis- ja välistamiskriteeriumid (nt ainult viimase ${\sim}10$~aasta tööd, ainult ingliskeelsed, ainult kõneaudio domeen) tuleks otsingulausele lisada, et string oleks SLR-mõttes täielik.

---

## Kokkuvõte juhendaja vaates

Töö praegune kirjanduse käsitlus on **kvaliteetne sisuliselt**, kuid \textbf{metoodiliselt mitte SLR-vorming}: puudub eraldi otsingustringi nimekiri ja andmebaasiotsingu protokoll. Sellisena ei ole võimalik teist sõltumatut otsijat nõuda, et ta sama tulemuseni jõuaks --- mis on SLR-i põhinõue. Soovitan kas (a) lisada metoodika peatükki lühike alajaotis ,,Kirjanduse otsing'' eelpool soovitatud nelja-ploki stringiga, otsingukuupäeva ja vastete arvuga, või (b) sõnaselgelt deklareerida, et tegemist ei ole süstemaatilise ülevaatega, vaid suunatud (\emph{narrative}) kirjanduse käsitlusega, mis põhineb autori praktilise toru kaudu kogutud allikatel. Mõlemad on bakalaureusetöö tasemel akadeemiliselt aktsepteeritavad, kuid see valik tuleb teha ja kirja panna.
