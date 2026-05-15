# Bakalaureusetöö Ülesandepüstitus

**Ülikool**: Tallinna Tehnikaülikool
**Instituut**: Informaatika Instituut
**Õppekava**: Informaatika
**Kraad**: Bakalaureusekraad
**Semester**: Kevadsemester 2025
**Kaitsmise aeg**: Juuni 2025

---

## Töö Pealkiri

**Eestikeelne äratussõna tuvastuse mudel "Kratt" ja integratsioon Home Assistantiga**

*Estonian Wake Word Detection Model "Kratt" and Integration with Home Assistant*

---

## Autor

**Nimi**: Mattias Linholm
**Tudengikood**: [Sinu tudengikood]
**E-post**: [sinu@email]

---

## Juhendaja

**Nimi**: Tanel Alumäe
**Tiitel**: Teadur / Professor
**Instituut**: Informaatika Instituut, TalTech
**E-post**: tanel.alumae@taltech.ee

---

## 1. Sissejuhatus ja Probleem

### 1.1 Taustinformatsioon

Nutikodu häälassistendid on muutunud igapäevaseks osaks paljudes kodudes. Populaarsed lahendused nagu Amazon Alexa ("Alexa"), Google Assistant ("Ok Google") ja Apple Siri ("Hey Siri") kasutavad äratussõna (*wake word*) põhist aktiveerimist, mis võimaldab hands-free suhtlust seadmetega.

Eesti keele jaoks on viimaste aastate jooksul välja töötatud mitmeid kõnetuvastuse (*speech-to-text, STT*) lahendusi, sealhulgas TalTech NLP grupi poolt loodud "Kiirkirjutaja" süsteem, mis suudab reaalajas transkribeerida eestikeelset kõnet kõrge täpsusega. Samuti on olemas kõnesünteesi (*text-to-speech, TTS*) lahendused eesti keele jaoks.

**Puuduv lüli**: Vaatamata olemasolevale STT ja TTS infrastruktuurile **puudub eesti keele jaoks avalikult kättesaadav äratussõna tuvastuse mudel**, mis võimaldaks luua täielikku hands-free häälassistenti.

### 1.2 Probleem

Nutikodu platvorm **Home Assistant** toetab häälassistente läbi standardiseeritud Wyoming protokolli, kuid eesti keele jaoks puudub:
1. Eestikeelne äratussõna mudel
2. Integreeritud lahendus, mis ühendab wake word detection'i olemasoleva STT-ga
3. Kerge kättesaadav viis kasutajatele süsteemi paigaldada ja seadistada

See piirab eestikeelse häälassistendi loomist nutikodus, kuna kasutajad ei saa aktiveerida süsteemi hands-free viisil.

### 1.3 Vajadus

Kasvav trend privaatsust väärtustava tehnoloogia (*privacy-first technology*) suunas on loonud vajaduse täielikult lokaalsetele häälassistentidele, mis ei saada andmeid pilveteenustesse. Home Assistant platvorm võimaldab sellist lähenemist, kuid eesti keele toe loomiseks on vaja:
- Eestikeelset äratussõna mudelit
- Optimeeritud deployment'i ressurss-piiratud seadmetele (ESP32, Raspberry Pi)
- Kasutajasõbralikku integratsooni

---

## 2. Töö Eesmärgid

### 2.1 Peamine Eesmärk

Luua **esimene avalikult kättesaadav eestikeelne äratussõna tuvastuse mudel** "Kratt" ja integreerida see Home Assistant platvormiga täieliku häälassistendi süsteemina.

### 2.2 Alameeesmärgid

1. **Andmete kogumine ja ettevalmistamine**
   - Koguda eestikeelne äratussõna andmestik (vähemalt 10 kõnelejat)
   - Rakendada data augmentation tehnikaid väikese andmestiku suurendamiseks
   - Valideerida andmete kvaliteet ja mitmekesisus

2. **Mudeli arendamine**
   - Treenida kaks äratussõna mudelit:
     - microWakeWord (optimeeritud ESP32 mikrokontrollerile)
     - openWakeWord (optimeeritud Raspberry Pi-le)
   - Optimeerida mudelid embedded süsteemidele (INT8 kvantiseerimine)
   - Saavutada > 95% täpsus testimiskomplektil

3. **Riistvara implementatsioonid**
   - Implementeerida mudel ESP32-C3 Supermini mikrokontrollerile
   - Implementeerida mudel Raspberry Pi platvormile
   - Mõõta jõudlust (latentsus, täpsus, ressursikasutus)

4. **Home Assistant integratsioon**
   - Integreerida Wyoming protokolli kaudu
   - Luua Home Assistant addon, mida kasutajad saavad installida
   - Ühendada olemasoleva Kiirkirjutaja STT süsteemiga

5. **Hindamine ja valideerimine**
   - Tehniline testimine: täpsus, FPR/FNR, latentsus
   - Kasutajatestid: kuni 10 osalejaga piloot tervikliku häälassistendi kasutusväärtuse ja kasutuskogemuse kontrollimiseks
   - Võrdlev analüüs: microWakeWord vs openWakeWord
   - Kasutatavuse hindamine

---

## 3. Oodatavad Tulemused ja Panus

### 3.1 Teaduslik/Tehniline Panus

1. **Esimene eestikeelne wake word mudel**
   - Avatud lähtekoodiga mudel "Kratt"
   - Treenitud kahe erineva raamistiku abil (microWakeWord, openWakeWord)
   - Optimeeritud embedded süsteemidele

2. **Data augmentation metoodika väikese keele jaoks**
   - Dokumenteeritud lähenemine väikese andmestiku (~200 samples) laiendamiseks
   - Synthetic data generation tehnikad
   - Hinnatakse effektiivsust mudeli täpsuse suurendamisel

3. **Süsteemi integratsioon**
   - Täielik arhitektuur: wake word → STT → intent → TTS
   - Wyoming protokolli integratsioon
   - Jõudlusmõõtmised end-to-end latentsuse kohta

4. **Empiirilised tulemused**
   - Kasutajatestide tulemused pärismaailma stsenaariumites
   - Võrdlev analüüs erinevate hardware platformide vahel
   - Kasutatavuse hindamine

### 3.2 Praktiline Väljund

1. **Home Assistant addon**
   - Valmis addon, mida kasutajad saavad installida
   - Dokumenteeritud paigaldus- ja seadistusjuhendid
   - Avaldamine Home Assistant addon store'is

2. **Avatud lähtekood**
   - GitHub repositoorium kõigi komponentidega
   - Treenimise skriptid ja juhendid
   - Reprodutseeritav uurimistöö

3. **Dokumentatsioon**
   - Täielik tehniline dokumentatsioon
   - Kasutajajuhendid
   - Troubleshooting guide

### 3.3 Originaalsus

- **Esimene** avalikult kättesaadav eestikeelne wake word mudel
- **Unikaalne** eestikeelse wake word fraas "Kratt" (seotud eesti müütoloogiaga)
- **Täielik süsteem** - ei ole ainult mudel, vaid ka riistvara impl ja HA integratsioon
- **Dual-platform** - nii low-cost embedded (ESP32) kui ka performant (Raspberry Pi)

---

## 4. Töö Ulatus ja Piirangud

### 4.1 Ulatus

**Hõlmatud**:
- Äratussõna mudeli treenimine ja optimeerimine
- ESP32 ja Raspberry Pi implementatsioonid
- Home Assistant integratsioon (addon)
- Kasutajatestid (kuni 10 osalejaga piloot)
- Tehniline ja empiiriline evalueerimine
- Täielik dokumentatsioon

**Väljaspool ulatust**:
- STT mudeli treenimine (kasutame olemasolevat Kiirkirjutaja mudelit)
- TTS süsteemi arendamine (kasutame olemasolevaid lahendusi)
- Multi-keelsus (fokus ainult eesti keelel)
- Cloud-based solutions (fokus ainult lokaalselt)

### 4.2 Piirangud

1. **Andmestiku suurus**: Piiratud 10-20 kõnelejaga (ressursipõhine piirang)
   - Kompenseeritakse data augmentation tehnikatega

2. **Hardware platvormid**: ESP32-C3 ja Raspberry Pi
   - Ei hõlma teisi mikrokontrollereid või SBC-sid

3. **Keele varieeruvus**: Üks peamine wake word ("Kratt")
   - Võib lisada alternatiivse variatsiooni ("Kuule Kratt")

4. **Testimine**: kuni 10 kasutajat, lühike pilootsessioon osaleja kohta
   - Piisav proof-of-concept'i ja kasutusväärtuse kontrolliks, kuid mitte pikaajaline uuring

---

## 5. Metoodika

### 5.1 Uurimismeetodid

1. **Kirjanduse ülevaade**
   - Wake word detection teooria ja practice
   - Olemasolevad lahendused (Alexa, Google, Mycroft)
   - Data augmentation techniques audio puhul
   - Embedded ML optimization

2. **Eksperimentaalne arendus**
   - Mudeli treenimine ja optimeerimine
   - Hyperparameter tuning
   - Model comparison (microWakeWord vs openWakeWord)

3. **Jõudluse mõõtmine**
   - Tehniline: accuracy, FPR, FNR, latentsus, ressursikasutus
   - Võrdlev: ESP32 vs Raspberry Pi
   - End-to-end: wake word → action latency

4. **Empiiriline hindamine**
   - Kasutajatestid reaalses keskkonnas
   - Küsimustikud (System Usability Scale)
   - Kvalitatiivsed intervjuud

### 5.2 Töövoog

#### Phase 1: Uurimine ja Planeerimine (Nädal 1-2)
- Kirjanduse ülevaade
- Süsteemi arhitektuuri disain
- Data collection protokolli väljatöötamine
- Eetika kinnituse hankimine (kui nõutav)

#### Phase 2: Andmete Kogumine (Nädal 3-4)
- Kuni 10 osalejat
- Iga osaleja: 20-50 salvestust
- Kokku: 200-1000 base samples
- Valideeritakse ja eeltöödeldakse

#### Phase 3: Data Augmentation (Nädal 5)
- Time stretching, pitch shifting
- Background noise addition
- Room acoustics simulation
- Expansion: 200 → 2000+ samples

#### Phase 4: Mudeli Treenimine (Nädal 6-8)
- microWakeWord treening (ESP32)
- openWakeWord treening (Raspberry Pi)
- Hyperparameter tuning
- Model validation

#### Phase 5: Hardware Impl (Nädal 9-11)
- ESP32 ESPHome configuration
- Raspberry Pi Wyoming server
- Performance optimization
- Integration testing

#### Phase 6: Home Assistant Integration (Nädal 12-13)
- Addon development
- Voice pipeline configuration
- Local testing

#### Phase 7: Kasutajatestid (Nädal 14-16)
- Kuni 10 osalejat
- Umbes 10-minutiline pilootsessioon osaleja kohta
- Data collection (FP/FN, latency, usability)
- Qualitative feedback

#### Phase 8: Analüüs ja Kirjutamine (Nädal 17-22)
- Tulemuste analüüs
- Comparative evaluation
- Lõputöö kirjutamine
- Dokumentatsiooni viimistlemine

#### Phase 9: Kaitsmine (Juuni 2025)
- Presentatsioon
- Demo
- Kaitsmine

### 5.3 Tööriistad ja Tehnoloogiad

**Data Collection**:
- Python (sounddevice, soundfile)
- ffmpeg (audio processing)

**Machine Learning**:
- TensorFlow / PyTorch
- microWakeWord framework
- openWakeWord framework
- ONNX, TFLite (model formats)

**Hardware**:
- ESP32-C3 Supermini
- Raspberry Pi 5
- INMP441 I2S microphone

**Software**:
- ESPHome (ESP32 firmware)
- Python (Raspberry Pi)
- Home Assistant
- Wyoming Protocol
- Docker (containerization)

**Development**:
- Git / GitHub (version control)
- Jupyter Notebooks (exploration)
- LaTeX (thesis writing)

---

## 6. Ajaplaan

| Periood | Tegevused | Tulem |
|---------|-----------|-------|
| **Veebruar (N 1-4)** | Uurimine, planeerimine, data kogumine | Andmestik kogutud |
| **Märts (N 5-8)** | Data augmentation, mudeli treenimine | Mudelid treenitud |
| **Aprill (N 9-13)** | Hardware impl, HA integratsioon | Addon valmis |
| **Mai (N 14-18)** | Kasutajatestid, tulemuste analüüs | Empiirilised tulemused |
| **Juuni (N 19-22)** | Lõputöö kirjutamine, kaitsmine | Bakalaureusetöö |

---

## 7. Oodatav Töö Maht ja Struktuur

### 7.1 Maht

- **Lehekülgi**: 70-90 (ilma lisadeta)
- **Kood**: ~2000-3000 rida (skriptid, seadistused)
- **Andmed**: 200-1000 audio samples + augmented data

### 7.2 Struktuuri Eevaade

1. **Sissejuhatus** (~5 lk)
   - Probleem, eesmärgid, panus, struktuur

2. **Taust ja Eeltööd** (~15 lk)
   - Wake word detection teooria
   - Olemasolevad lahendused
   - Eesti keele lahendused (STT/TTS)
   - Väikese keele väljakutsed

3. **Metoodika** (~20 lk)
   - Süsteemi arhitektuur
   - Data kogumine ja augmentation
   - Mudeli treenimine
   - Evalueerimine

4. **Implementatsioon** (~20 lk)
   - Wake word mudel
   - ESP32 ja Raspberry Pi
   - Home Assistant integratsioon

5. **Evalueerimine** (~15 lk)
   - Tehnilised testid
   - Kasutajatestid
   - Võrdlev analüüs
   - Piirangud

6. **Arutelu ja Kokkuvõte** (~10 lk)
   - Tulemuste analüüs
   - Praktiline väartus
   - Edasiarendus

**Lisad**:
- A: Andmete kogumise protokoll
- B: Kasutajatestide küsimustik
- C: Seadistuste näited
- D: Koodinäited

---

## 8. Ressursid

### 8.1 Riistvara

- **Olemas**:
  - Raspberry Pi 5 (8GB RAM)
  - 10× ESP32-C3 Supermini
  - USB mikrofon

- **Tellida**:
  - 10× INMP441 I2S mikrofon (~€30)

### 8.2 Tarkvara

Kõik tarkvara on open-source ja tasuta kättesaadav.

### 8.3 Inimressurss

- **Juhendaja**: Tanel Alumäe (konsultatsioonid)
- **Testijad**: kuni 10 vabatahtlikku pilootuuringuks (sõbrad, pere, kolleegid)

---

## 9. Riskid ja Leevendamine

| Risk | Tõenäosus | Mõju | Leevendus |
|------|-----------|------|-----------|
| Väike andmestik annab halva mudeli | Keskmine | Kõrge | Data augmentation, transfer learning |
| ESP32 mälu piiratud | Keskmine | Keskmine | INT8 kvantiseerimine, mudeli optimeerimine |
| Vähe kasutajatestijaid | Madal | Keskmine | Varased katsed sõpradega, värbamine ülikoolis |
| Home Assistant API muutub | Madal | Keskmine | Wyoming protocol on stabiilne, versioonikontroll |
| Ajaplaan hilineb | Keskmine | Keskmine | Buffer time, fokus core features'idel |

---

## 10. Eetilised Kaalutlused

### 10.1 Andmekaitse

- **GDPR vastavus**: Kõik osalejad annavad informeeritud nõusoleku
- **Anonümiseerimine**: Audio samples ei sisalda tuvastav ust
- **Õigus kustutada**: Osalejad saavad igal ajal oma andmed kustutada
- **Turvalisus**: Andmed salvestatakse krüpteeritult

### 10.2 Privaatsus

- **Fully local**: Mudel töötab 100% lokaalselt, ei saada andmeid kuhugi
- **Opt-in ainult**: Kasutajad peavad eksplitselt nõustuma
- **Transparent**: Kogu süsteem on open-source

### 10.3 Eetika Komitee

Kontrollin TalTech eetika komitee nõudeid inimeste kaasamisel uuringutesse. Kui nõutav, esitan taotluse.

---

## 11. Avalikustamine ja Levitamine

### 11.1 Avatud Lähtekood

- **GitHub**: Avalik repositoorium kogu koodiga
- **Litsents**: MIT või Apache 2.0 (kasutajasõbralik)
- **Dokumentatsioon**: Täielik README, setup guides

### 11.2 Home Assistant Addon Store

- Addon avaldamine HA addon store'is
- Community support

### 11.3 Teaduslik Levitamine

- Võimalik short paper või blog post
- Presentation TalTech informaatika päevadel
- Võimalik ettekanne konverentsil (BalticHLT, SLTU)

---

## 12. Kokkuvõte

Käesolev bakalaureusetöö loob **esimese avalikult kättesaadava eestikeelse äratussõna mudeli** "Kratt" ja integreer ib selle Home Assistant platvormiga täieliku häälassistendi süsteemina. Töö hõlmab kogu protsessi andmete kogumisest ja mudeli treenimisest kuni hardware implementatsiooni ja kasutajatestimisenini.

**Originaalpanus** seisneb mitte ainult esimese eestikeelse wake word mudeli loomises, vaid ka:
- Data augmentation metoodikas väikese keele jaoks
- Dual-platform implementation (ESP32 + Raspberry Pi)
- Täielikus süsteemi integratsioonis olemasoleva eesti STT-ga
- Empiirilises valideerimises pärismaailma kasutajatestidega

Töö praktiline väljund on valmis Home Assistant addon, mida igaüks saab kasutada oma nutikodus, luues täielikult lokaalse ja privaatset väärtustava eestikeelse häälassistendi.

---

## Allkirjad

**Üliõpilane**:
________________________
Mattias Linholm
Kuupäev: ____________

**Juhendaja**:
________________________
Tanel Alumäe
Kuupäev: ____________

**Instituudi direktor / õppetöö korraldaja**:
________________________
[Nimi]
Kuupäev: ____________

---

**Märkused juhendajale**: Palun vaata üle ja anna tagasisidet järgmiste aspektide kohta:
1. Kas töö ulatus on realistlik bakalaureuse tasemele?
2. Kas metoodika on piisavalt detailne?
3. Kas ajaplaan on realistlik?
4. Kas puuduvad olulised komponendid või kaalutlused?

**Kontakt**:
- Email: [sinu@email]
- GitHub: [sinu-github]
- Phone: [sinu-number]
