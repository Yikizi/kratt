---
source_prompt: Süstemaatilise_kirjanduse_ülevaate_otsingustringid.txt
prompt_type: generative
generated: 2026-05-07
---

# Süstemaatilise kirjanduse ülevaate otsingustringid — Kratt (eesti äratussõna)

## Konteksti märkus (eesti keeles)

Käesolev väljund on **generatiivne**: lähteviiba ülesanne on uurimisküsimuste põhjal koostada süstemaatilise kirjanduse ülevaate (SLR) otsingustrateegiad. Lähteviiba enda **Keelenõue (KRIITILINE)** sätestab sõnaselgelt, et **otsingustrateegiate sisu peab olema inglise keeles** (kontseptsioonid, sünonüümid, Scholar-stringid), kuna otsing teostatakse ingliskeelsetes andmebaasides. Operaatori üldjuhis nõuab eestikeelset väljundit. Need kaks nõuet ei ole tegelikult vastuolus: eestikeelne raamistik (sissejuhatus, kontekst, kasutusjuhised, hoiatused) on allpool eesti keeles, kuid otsingusõnad ja Scholari süntaks ise on inglise keeles, sest muidu nad ei toimiks. Ühtegi väidet thesise sisu kohta ei ole leiutatud — uurimisküsimused on võetud sõna-sõnalt thesise sissejuhatusest (`introduction.tex`).

Thesises endas ei ole eraldi süstemaatilise kirjanduse ülevaate peatükki: kirjandus on käsitletud hajutatult sissejuhatuses (§probleem, §sihid), metoodikas (§hindamismõõdikud, §arhitektuur) ning aruteluosas (§benchmark-gap, §kaskaadarhitektuur). Käesolev otsingustrateegiate kogum on seega rakendatav **kahel viisil**:

1. *Tagantjärele*: kontrollida, kas autor on katnud peamised relevantsed valdkonnad — kasutada eelkõige RQ-1 ja RQ-2 stringe, et leida vahepeal ilmunud teoseid, mis tuleks `references.bib`-i lisada.
2. *Edasi*: kui kaitsmiskomisjon küsib SLR-laadset lisa, on alljärgnevad stringid kasutamiskõlblikud Scholaris/Scopuses ilma muudatusteta.

## Uurimisküsimused (thesisest tuletatud)

Sissejuhatuse põhiküsimus: *kuidas luua ja hinnata eestikeelset äratussõna tuvastust nii, et see oleks usaldusväärne nutikodu mikrokontrolleri piiratud ressursi tingimustes?*

Alamküsimused (sissejuhatuse loend):

- **RQ-1**: kuidas valideerida treeningu- ja hindamistoru enne eestikeelse andmestiku juurde liikumist;
- **RQ-2**: millist rolli mängivad positiivsed, negatiivsed ja taustaheli-andmed äratussõna mudeli kvaliteedi hindamisel;
- **RQ-3**: kuidas eristada andmestikust tulenevaid probleeme toru tehnilistest piirangutest;
- **RQ-4**: kas treenitud mudel saavutab eestikeelsel taustaheli korpusel pidevvoo FAPH < 1 ja lähikõne tuvastamismäära ≥ 0,95 sihi.

Lisaks ekstraheerin kaks valdkondlikku küsimust thesise aruteluosast, mille kohta kirjandust on otseselt tsiteeritud:

- **RQ-5** (tuletatud §sec:benchmark-gap): kui suur on lahknevus standardsete KWS-võrdlusaluste ja reaalse kasutuse vahel?
- **RQ-6** (tuletatud §sec:future-cascade): millised on kahe-astmelise (cascade) äratussõna arhitektuuri kompromissid?

Allpool on iga RQ jaoks struktureeritud otsingustrateegia inglise keeles, nagu lähteviip nõuab.

---

## RQ-1: How to validate the training and evaluation pipeline of a small-footprint keyword-spotting system before moving to a low-resource target language?

**1. Search Concepts & Synonyms**
- **Concept 1 (Wake-word / KWS task):** `"wake word"`, `"wake-word"`, `"keyword spotting"`, `"hotword detection"`, `"trigger word"`, `"voice trigger"`, `KWS`
- **Concept 2 (Pipeline / methodology validation):** `pipeline`, `"training pipeline"`, `"evaluation pipeline"`, `reproducibility`, `"sanity check"`, `"control experiment"`, `validation`, `"end-to-end test"`
- **Concept 3 (Public benchmark dataset for sanity-check):** `"Speech Commands"`, `"Google Speech Commands"`, `marvin`, `"benchmark dataset"`, `"public dataset"`

**2. Exclusion Criteria**
- **Terms:** `-review`, `-survey`, `-"meta-analysis"`, `-tutorial`, `-overview`
- **Reasoning:** SLR keskendub esmastele uuringutele; välistame sekundaarse kirjanduse, tutoriaalid ja entsüklopeedilised ülevaated, sest need ei kvalifitseeru SLR-i tõendusallikaks.

**3. Recommended Google Scholar Search Strings**
- **Broad String (Full text):** `("wake word" OR "keyword spotting" OR "hotword detection") (pipeline OR reproducibility OR "control experiment") "Speech Commands" -review -survey -"meta-analysis"`
- **Targeted String (Title only):** `allintitle: ("keyword spotting" OR "wake word") ("Speech Commands" OR benchmark)`
- **Reproducibility-leaning variant:** `("keyword spotting" OR "wake word") (reproducibility OR "training pipeline" OR "data leakage") -review -survey`
- **Notes on usage:** Esimene string on lai ja võib anda 200+ tabamust; piirata `since:2018`. Teine (title-only) annab tavaliselt < 50 puhast tulemust ja on heaks ringluse-alguseks. Kolmas keskendub selgelt RQ-1 alusele — eraldi kontrollkatse + andmelekke teema, mis on thesise §sec:data-leakage keskmes.

---

## RQ-2: What is the role of positive, negative, and ambient/background audio data in evaluating wake-word model quality?

**1. Search Concepts & Synonyms**
- **Concept 1 (Wake-word / KWS):** `"wake word"`, `"keyword spotting"`, `"hotword"`, `KWS`, `"voice trigger"`
- **Concept 2 (Data composition):** `"negative samples"`, `"hard negatives"`, `"confusable phrases"`, `"phonetic confusables"`, `"ambient audio"`, `"background noise"`, `"non-speech"`, `"speech-negative"`, `"data augmentation"`
- **Concept 3 (Evaluation / quality):** `evaluation`, `"false accept"`, `"false reject"`, `FAPH`, `"false accepts per hour"`, `FRR`, `FPR`, `streaming`

**2. Exclusion Criteria**
- **Terms:** `-review`, `-survey`, `-"meta-analysis"`, `-"speech recognition"` (selektiivselt — vaata märkust)
- **Reasoning:** Sekundaarne kirjandus välistatakse SLR-printsiibist; `-"speech recognition"` on **vabatahtlik** filter, sest paljud ASR-uuringud kasutavad sama terminoloogiat, kuid ei käsitle KWS-spetsiifilisi väikseid alati-kuulavaid mudeleid. Kasuta seda välistust ainult kui esimese stringi tabamuste hulk on liiga suur.

**3. Recommended Google Scholar Search Strings**
- **Broad String:** `("wake word" OR "keyword spotting") ("hard negatives" OR "confusable" OR "ambient" OR "background noise") (evaluation OR "false accept") -review -survey`
- **Targeted String (Title only):** `allintitle: ("keyword spotting" OR "wake word") (negative OR ambient OR confusable)`
- **Streaming-evaluation variant:** `("wake word" OR "keyword spotting") streaming ("false accepts per hour" OR FAPH OR FRR) -review`
- **Notes on usage:** FAPH on kirjanduses ebaühtlaselt nimetatud — proovi paralleelselt `"false alarms per hour"`, `"FA/h"`, `"false trigger rate"`. Stringi-pikkuse piirangu tõttu hoia iga päring < 200 tähemärki.

---

## RQ-3: How to distinguish dataset-related quality issues from technical pipeline limitations in low-resource keyword-spotting development?

**1. Search Concepts & Synonyms**
- **Concept 1 (Low-resource / under-resourced language):** `"low-resource language"`, `"under-resourced"`, `"low-resource speech"`, `"small language"`, `"minority language"`
- **Concept 2 (KWS / wake-word):** `"keyword spotting"`, `"wake word"`, `"hotword"`, `KWS`
- **Concept 3 (Diagnosis / failure attribution):** `"data leakage"`, `"data contamination"`, `"label noise"`, `debugging`, `"failure analysis"`, `ablation`, `"error analysis"`, `diagnosis`

**2. Exclusion Criteria**
- **Terms:** `-review`, `-survey`, `-"meta-analysis"`, `-"machine translation"`
- **Reasoning:** `-"machine translation"` on lisatud, sest "low-resource language" annab Scholaris valdavalt MT- ja ASR-tabamusi; ilma selle välistuseta lõhkeb müra hulk. Sekundaarne kirjandus välistatakse SLR-printsiibist.

**3. Recommended Google Scholar Search Strings**
- **Broad String:** `("low-resource" OR "under-resourced") ("keyword spotting" OR "wake word") ("data leakage" OR "label noise" OR ablation) -review -survey -"machine translation"`
- **Targeted String (Title only):** `allintitle: ("keyword spotting" OR "wake word") ("low-resource" OR ablation)`
- **Pipeline-debugging variant:** `("wake word" OR "keyword spotting") ("error analysis" OR "failure analysis" OR debugging OR audit) -review -survey`
- **Notes on usage:** Lisaks Scholarile tasub seda RQ-d sondeerida ka **arXiv `cs.SD`** ja **`eess.AS`** teemades, kuna paljud ablation-uuringud avaldatakse seal enne eelretsenseeritud ringi.

---

## RQ-4: Does a trained Estonian wake-word model achieve streaming FAPH < 1 and near-field recall ≥ 0.95 on representative ambient corpora?

**1. Search Concepts & Synonyms**
- **Concept 1 (Estonian language):** `Estonian`, `eesti`, `"Estonian language"`
- **Concept 2 (Wake-word / KWS):** `"wake word"`, `"keyword spotting"`, `KWS`, `"hotword"`
- **Concept 3 (Performance targets):** `"false accepts per hour"`, `FAPH`, `recall`, `"detection rate"`, `"true positive rate"`

**2. Exclusion Criteria**
- **Terms:** `-review`, `-survey`, `-"meta-analysis"`
- **Reasoning:** Otsime esmaseid uuringuid; sekundaarne kirjandus eemaldatud.

**3. Recommended Google Scholar Search Strings**
- **Broad String:** `(Estonian OR "Estonian language") ("wake word" OR "keyword spotting" OR KWS) -review -survey`
- **Targeted String (Title only):** `allintitle: Estonian ("keyword spotting" OR "wake word" OR "speech recognition")`
- **Adjacent-language fallback:** `(Finnish OR Latvian OR Lithuanian OR "Uralic") ("wake word" OR "keyword spotting") -review`
- **Notes on usage:** RQ-4 on **lokaalselt nõrk otsing**: tõenäoliselt on eestikeelsete KWS-uuringute vähesus juba thesise seisukoht. Selle stringi peamine roll on **negatiivse tõendi kogumine** (st näidata, et töid pole) ning teisene roll lähikeelte (soome, läti, leedu) tabamuste leidmine. Lisa Scholar Alert, et autor saaks kaitsmise eel teada, kui mõni uus eesti KWS-töö ilmub.

---

## RQ-5: How large is the gap between standard KWS benchmark performance and real-world deployed wake-word behaviour?

**1. Search Concepts & Synonyms**
- **Concept 1 (Wake-word / KWS):** `"wake word"`, `"keyword spotting"`, `"hotword"`, `"voice trigger"`
- **Concept 2 (Real-world / deployment / unintended):** `"real world"`, `"in-the-wild"`, `deployment`, `"unintended activation"`, `"accidental trigger"`, `"false trigger"`, `"smart speaker"`
- **Concept 3 (Benchmark gap / mismatch):** `"benchmark gap"`, `"domain mismatch"`, `"evaluation gap"`, `"out of distribution"`

**2. Exclusion Criteria**
- **Terms:** `-review`, `-survey`, `-"meta-analysis"`, `-marketing`
- **Reasoning:** `-marketing` lisatud, sest paljud "smart speaker" tabamused on tootetutvustused; sekundaarne kirjandus eemaldatud.

**3. Recommended Google Scholar Search Strings**
- **Broad String:** `("wake word" OR "keyword spotting") ("unintended activation" OR "accidental trigger" OR "false trigger") "smart speaker" -review -marketing`
- **Targeted String (Title only):** `allintitle: ("smart speaker" OR "wake word") (accidental OR unintended OR triggers)`
- **Domain-mismatch variant:** `("wake word" OR "keyword spotting") ("domain mismatch" OR "out of distribution" OR "real-world") -review -survey`
- **Notes on usage:** Thesise §sec:benchmark-gap viitab juba Dubois 2020 ja Schönherr 2022 töödele — esimene string peaks need taastootma. Kui ei taasto, on see katvuse kontroll-fail, mis viitab, et string on liiga kitsas.

---

## RQ-6: What are the design trade-offs of two-stage cascade architectures for wake-word detection?

**1. Search Concepts & Synonyms**
- **Concept 1 (Cascade / two-stage):** `cascade`, `"two-stage"`, `"two stage"`, `"second-pass"`, `"second stage"`, `"verifier"`, `"stage two"`, `"hierarchical"`
- **Concept 2 (Wake-word / KWS):** `"wake word"`, `"keyword spotting"`, `"hotword"`, `"voice trigger"`
- **Concept 3 (Trade-offs):** `"false accept"`, `latency`, `"power consumption"`, `"on-device"`, `efficiency`, `recall`

**2. Exclusion Criteria**
- **Terms:** `-review`, `-survey`, `-"meta-analysis"`, `-"object detection"`, `-"image classification"`
- **Reasoning:** "Cascade" annab Scholaris palju arvutinägemise tabamusi (Viola-Jones jt) — eemaldame need otsesõnu. Sekundaarne kirjandus välistatakse.

**3. Recommended Google Scholar Search Strings**
- **Broad String:** `(cascade OR "two-stage" OR "second-pass") ("wake word" OR "keyword spotting") -review -"object detection" -"image classification"`
- **Targeted String (Title only):** `allintitle: (cascade OR "two-stage") ("keyword spotting" OR "wake word")`
- **On-device-trade-offs variant:** `("wake word" OR "keyword spotting") ("on-device" OR latency OR power) (cascade OR verifier) -review`
- **Notes on usage:** Thesises tsiteeritud Apple voice-trigger 2023 ja Gruenstein 2017 peavad olema esimese stringi top-20 hulgas; kui pole, on string parandust vajav. Lisaks tasub kaaluda **IEEE Xplore** otsest otsingut sama Concept 1 + Concept 2 kombinatsiooniga, sest cascade-KWS uuringud on Apple/Amazon/Google töödes ja paljud neist asuvad ICASSP-konverentsi materjalides.

---

## Üldised kasutusjuhised (eesti keeles, lähteviiba `Notes on usage` raamistikus)

1. **Pikkuse piirang.** Iga ülaltoodud Scholar-string on sihilikult hoitud < 256 tähemärki, et mahtuda Scholari piiranguse sisse. Kui kombineerite mitut RQ-d, jagage päring 2–3 osaks ja koondage tabamused käsitsi.
2. **Tüvelõikuse vältimine.** Lähteviiba juhise kohaselt ei kasuta ükski ülaltoodud string `*` operaatorit; kõik olulised variatsioonid (nt `"wake word"` vs `"wake-word"`) on välja kirjutatud.
3. **Välistuste süntaks.** Miinusmärk on igal pool **kohe sõna ees ilma tühikuta** (`-review`, mitte `- review`), nagu Scholar nõuab.
4. **Title-only versioonid.** `allintitle:` versioone tasub kasutada esimese ringi triaažiks; need annavad vähe, kuid kõrge täpsusega tabamusi, mis on hea seemnekomplekt edasi-snowballimiseks.
5. **Snowballing.** Pärast esimest passi tee iga relevantse uuringu osas **forward citation** otsing Scholari "Cited by" kaudu; see katab tüüpiliselt rohkem RQ-5 ja RQ-6 uusi töid kui pelgalt stringipäringud.
6. **Eksklusioonide piirangud.** SLR-protokoll tüüpiliselt välistab `review`, `survey`, `meta-analysis` esmaste uuringute filtrina. Selles thesises kasutavad vaheülevaadeteena Lopez-Espejo 2021 (deep KWS survey) ja Picovoice'i benchmark-aruanded — neid tuleks **eraldi käsitleda kui taustakirjandust**, mitte SLR-i esmastest uuringutest.

## Erialane reservatsioon (eesti keeles)

Selle thesise jaoks **ei ole formaalselt vajalik** PRISMA-tasemel SLR — bakalaureusetöö skoop ja TalTechi nõuded ei sea seda nõuet. Käesolev otsingustrateegiate kogum on kavandatud kahe praktilise eesmärgi jaoks: (a) kirjandus-katte audit enne kaitsmist, et veenduda, et `references.bib` ei ole vahepeal vananenud või ühe-tahuline; (b) varuvariant juhuks, kui retsensent küsib süsteemse kirjanduse otsingu metoodikat. Mõlemal juhul tuleks reaalse kasutamise korral päringud käivitada ja salvestada CSV-na (kuupäev, string, andmebaas, tabamuste arv, kaasatud tööde arv, välistuse põhjus) — see on standardne SLR-i auditeeritav läbipaistvustabel.

Vältima peab tõlgendust, et need stringid asendaksid thesise olemasolevat kirjandusekäsitlust. Thesise `introduction.tex`, `first_chapter.tex` ning `third_chapter.tex` viited kannavad SLR-laadse argumendi raskuse; käesolevad stringid on metoodiline tugi, mitte lisaks olev iseseisev tõendusallikas.
