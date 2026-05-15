---
source_prompt: 02_Ülesandepüstitus/Kas_tehtav_AI_abil.txt
prompt_type: evaluative
generated: 2026-05-07
---

# AI-replikeeritavuse riskihinnang lõputööle "Kuule Kratt"

## 1. Hinnang: AI-replikeeritavuse risk

**Kas töö on 100% ulatuses AI poolt tehtav?** EI

**Riski tase:** MADAL

*(Põhjendus: AI ei saa replikeerida töö keskseid empiirilisi panuseid, mis nõuavad füüsilist riistvara, autori enda kogutud salvestusi, planeeritavat 20--30 osalejaga kasutajatesti ning eestikeelses nutikodu keskkonnas tehtud välivaatlusi. AI on selle töö juures jõuline abivahend kirjutamise, koodi ja analüüsi juures, kuid ei suuda asendada empiirilist tõendusbaasi.)*

## 2. Analüüs ja põhjendused

### 2.1 Miks "EI" (mis lülid puuduvad masinale)

Töö ei ole 100% AI poolt tehtav, sest selle keskses tõendusahelas on vähemalt seitse lüli, mis nõuavad masinale kättesaamatut tegevust:

1. **Eestikeelse "Kuule Kratt" positiivse andmestiku kogumine ESP32-S3-Korvo-2 plaadiga** --- 1076 klippi (661 mic1 + 415 mic2) salvestati füüsiliselt sihtseadmega. AI ei saa salvestada uut audiot oma häälega ega käivitada Korvo-2 mikrofone.
2. **Korvo-2 negatiivsete sessioonide salvestamine** --- 6,2-tunnine taustaheli- ja 2,8-tunnine kõnesessioon, mis on töö domeeninihke kontrolli alus. Need on lokaalse ruumi akustika salvestused.
3. **Cross-mic katsed (MacBook Pro sisemikrofon, ${\sim}50$ FAPH leid)** --- ${\sim}40$-min reaalajas test, mis paljastas streaming/clip-level lahknevuse. Eeldab füüsilist mikrofoni ja kasutamiskohta.
4. **Android-väliuuringu ${\sim}99$~h FAPH-mõõtmised** --- nõuavad pikaajalist seadet kasutusolukorras, päris elukeskkonnas, päris helitausta peal.
5. **Planeeritav 20--30 osalejaga kasutajatest (`§\ref{sec:user-test-methodology}`)** --- nõuab inimosalejaid, nõusolekulepingut, sessiooni läbiviimist (5 puhast äratust + 5 sarnast negatiivfraasi + 6 skripti käsku + valgusülesanne osaleja kohta). See on töö "neljas valideerimisring" ja töö lõppotsuse alus. AI ei saa ise olla ega rekruteerida 20--30 osalejat.
6. **ESP32-S3 + ESPHome + Home Assistant `voice_assistant` lokaalne juurutus** --- füüsiline flash, Wi-Fi konfiguratsioon, mikrofoni ja kõlari paigutus, päris mikrokontrolleri profileerimine (148\,KB TFLite + 45--50\,KB tensor-arena). AI saab koodi kirjutada, kuid ei saa flashida.
7. **TalTechi juhendamissuhe ja eetilise käsitluse otsustused** --- nõusolekuvormi käsitsi koostamine, eetikakomitee suhtlus, häälte taaskasutamise ja säilitamise inimotsused (vrd. minimaalne nõusolek vs. audio opt-in).

Ehk: ülesande "100% kriteerium" kukub kõige selgemalt läbi punktide 1, 2, 4 ja 5 juures. Need on kõik unikaalsed andmehulgad, mis pole avalikus internetis, ja unikaalsed mõõtmised, mis on tehtud konkreetses füüsilises keskkonnas.

### 2.2 Mida AI suudaks teha (ja kus see töös ka ausalt välja toodud on)

Töö ise ütleb otse välja, et agentpõhine arendus oli oluline tööriist (3. peatükk, jaotis "Agentpõhine arendus kui töövõimendaja, mitte tõendusmaterjali asendaja"). AI suudaks põhimõtteliselt asendada või suurel määral kiirendada järgmist:

- **Kirjandusülevaate koostamine ja viidete formaadi haldus** (microWakeWord, openWakeWord, Picovoice, KWS-Net, MixedNet, BC-ResNet, SpecAugment, Speech Commands, MUSAN, VOiCES, Common Voice).
- **Treening- ja hindamisskriptide esmamustand** --- `microWakeWord` raamistiku ümber kirjutatud `compare_models.py`, `assert_disjoint_from_training()`, `kratt user-test`, `kratt validate-user-test`, `kratt replay-user-test`, `kratt summarize-user-test` jms. Töö dokumenteerib ise, et selline tööriistakiht oli teostatav just tänu agentpõhisele arendusele.
- **Statistilise raamistiku rakendamine** --- Wilsoni usaldusvahemikud klipi-tasemel, Poissoni-Garwoodi täpne CI FAPH-ile, kolme reegel ($k=0$ juures). Need on standardsed ja AI suudab neid korrektselt rakendada.
- **Eestikeelse akadeemilise teksti redigeerimine ja struktureerimine** --- LaTeX-i tasemel kirjutamine, terminite ühtlustamine, viidetega lõikude koostamine.
- **Sünteetilise andmestiku tootmine** --- XTTS v2 ja Tartu Neurokõne kasutamine TTS-positiivsete ja sarnaste negatiivnäidete genereerimiseks. AI saab pipeline'i jooksutada, kuid ei saa muuta seda mitte-sünteetiliseks.
- **Kontrollkatse läbiviimine `Speech Commands` (marvin) andmestikul** --- avalik andmestik, valmis tööriistad. See *konkreetne* alamosa ongi väga lähedal "AI suudaks teha"-le, sest treeningu valideerimine avaliku andmestiku peal on kontrollitav ka ilma lokaalsete andmeteta.
- **Tabelite ja jooniste genereerimine andmete põhjal** --- `tab:fair-comparison-holdout`, `tab:expert-consensus`, `fig:faph_recall_pareto.pdf` jms. Andmed peavad olemas olema, aga vormistus on automatiseeritav.

### 2.3 Mis nõuab inimest (kättesaamatu lüli)

Lühikokkuvõte AI-le kättesaamatutest aspektidest:

| Lüli | Miks AI ei saa | Kus töös kajastub |
|---|---|---|
| Sihtseadmega tehtud lokaalne audio | Vajab füüsilist mikrofoni, ruumi, häält | 2. ptk, jaotis "Eestikeelse äratussõna eksperimendid" |
| Pikaajaline ambient-mõõtmine (MUSAN ei asenda elutuba) | Vajab kohalolu, kalibreeritud mikrofoni, päris taustsündmusi | 3. ptk, §\ref{sec:benchmark-gap}, §\ref{sec:cross-mic-asymmetry} |
| 20--30 osalejaga kasutajatest | Vajab nõusolekut, eetikakomitee suhtlust, sessioone | 1. ptk, §\ref{sec:user-test-methodology} |
| Foneetiliselt sarnaste fraaside tõsi-andmete märgendamine streaming-kontekstis (lausekontekst, koartikulatsioon) | Vajab inimkonteksti märgendamisotsust ja päris helilõike | 3. ptk, §\ref{sec:benchmark-gap}, "Põhjus 3" |
| ESP32-S3 + ESPHome + Home Assistant päris-juurutuse demo | Vajab flashi, Wi-Fit, ruumikatset | 1. ptk; ülesandepüstituse "tehniline teostus" |
| Juhendaja tagasiside, otsus kontrollpunkti valikukriteeriumi üle (komposiitne kriteerium) | Vajab tegelikku väitlust ja tõlgendust | 3. ptk, "Kolmas ring" |
| Andmelekke avastamine empiiriliselt | AI saaks teoreetiliselt soovitada disjointsuskontrolli, kuid päris leke avastati alles cross-mic anomaalia tagajärjel | 2. ptk, §\ref{sec:data-leakage} |
| Eestikeelse "Kule" vs "Kuule" häälduse analüüs reaalsete kõnelejate peal | Vajab eestikeelseid kõnelejaid (mitte ainult TTS-i) | Sissejuhatus, järeldused |

## 3. Soovitused riski hoidmiseks madalal

Kuna risk on hetkel **MADAL**, on soovitused ennetavad: hoida tõendusvoo elemente nähtaval kohal, nii et töö lugeja näeks, kus täpselt asub inimese ja AI panuse vaheline piir. Konkreetsed sammud:

1. **Tee kasutajatesti tõendusahel auditeeritavaks.** Iga `kratt user-test` sessiooni `trials.jsonl` ja vastav WAV peavad olema raporteeritavad agregaadina (nt N osalejat, kogumiskuupäevad, helinäidiste keskmine kestus, RMS-i jaotus). Lisa lõputöösse jaotis "Andmete päritolu kinnitus", mis nimetab, milline osa heliandmetest on autori salvestatud, milline TTS-iga genereeritud, milline kasutajatestilt kogutud ja milline avalikest korpustest. Praegu on see info hajutatud (1. ptk metoodika; 2. ptk eksperimendid) --- ühe "kindla lüli" kokkuvõte tugevdaks AI-replikeerimise vastast kaitset.

2. **Säilita ja viita Android-väliuuringu logifailile.** Töö viitab ${\sim}99$~h Android-väliuuringule (v6-residual 0,58 FAPH vs expert-a 2,79 FAPH) --- see on praktikas vaieldamatu *non-replicable* osa. Lisa joonealune märkus selle logi asukoha kohta repos (kui see jääb mitte-avalikuks privaatsuse tõttu, siis kinnita säilitamise koht ja juurdepääsupoliitika).

3. **Lisa eetikakomitee/nõusolekudokumentide viide.** Kasutajatesti metoodika peatükk (§\ref{sec:user-test-methodology}) räägib kaheastmelisest nõusolekumudelist --- see on inimotsus, mis tuleks lõputöö lisas viidata (vorm, allkirjastatud kuupäev, eetikakomitee number kui olemas). See on vahest kõige rangem signaal sellest, et töö pole AI-replikeeritav.

4. **Hoia "agentpõhise tööviisi" enesekontroll-jaotis 3. peatükis.** See on töö üks paremaid metoodilisi kaitsemehhanisme AI-replikeeritavuse süüdistuse vastu, sest dokumenteerib avalikult, kus AI aitas ja kus mitte. Soovitus: säilitada see jaotis terviklikuna ja mitte kärpida lõpufaasis kompaktsuse nimel.

5. **Demonstreerimisfilm (kaitsmise lisamaterjal).** Lühike (1--2 min) video, kus näidatakse Korvo-2 + ESPHome + Home Assistant päriselt äratusele reageerimas päris ruumis, eraldab töö igast puhtalt-tekstilisest AI-poolt-genereeritavast lõputööst. Selline lisa on praegu töö metoodikast loogiliselt tuletatav (juurutamise valideerimine), kuid mitte eraldi nimetatud.

6. **Märgi selgelt, kus tulemus on "punkthinnang".** Töö üksuses "Mida saab juba praegu väita" (3. ptk) on FAPH = 0,79 expert-A + expert-B2 konsensusele juba ettevaatlikult kommenteeritud --- jätka seda diskreetsust kõikjal, kus üksikust mõõtmisest on saanud "tulemus", sest just sellisel kohal on AI-genereeritud bakalaureusetöö üldjuhul nõrgem (väited liiga kindlalt sõnastatud, tõenduskestus liiga lühike).

7. **(Soovituslik) Lisa lühike "Tõendusbaasi laiendamise kava" lisana.** See dokumenteerib, mida tuleks edasi mõõta selleks, et töö järeldused üldistuks (laiem kõnelejatevaru, lapsekõne, aktsendid, pikem ambient-jada). See peegeldab "Aus piir: võimalik neljas ring" jaotuse mõtet ja jätab tõendusprotokolli avatuks.

## 4. Lühikokkuvõte

Töö ei ole AI-replikeeritav, kuna selle empiiriline tõendusbaas tugineb lokaalsele riistvaralisele kogumisele ja inimkasutusele, mis pole AI treeningandmetes ega masinale kätte saadav. AI on töös oluline *võimendaja* (kood, tööriistad, kirjutamine, statistika) ning autor toob selle ise välja. Risk püsib madalal seni, kuni töös säilib selge eraldus "mida tegi AI" (tarkvara, esmamustand, vormistus) ja "mida tegi autor" (audio, riistvara, kasutajatest, otsustused). Soovitused 1--7 ülal aitavad seda eraldust nähtavalt hoida.
