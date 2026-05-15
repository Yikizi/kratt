---
source_prompt: 03_Lõputöö_alamosad/Veebiküsitlus_intervjueerimine/Tulemuse_hindamise_veebiküsitlus.txt
prompt_type: generative
generated: 2026-05-07
---

# Eestikeelse äratussõna lahenduse "Kuule Kratt" valideerimisküsitlus

## Analüüsi kokkuvõte (taust koostajale)

**Valideeritav tulemus:** ESP32-S3 satelliidil (ESPHome) ja Home Assistanti lokaalses hääljuhtimisahelas töötav eestikeelse äratussõna mudel ("Kuule Kratt") koos pidevvoo hindamismetoodikaga. Üliõpilase positsioneering töös on, et tehniline panus on äratussõna mudel + reprodutseeritav toru + mitmemõõtmeline hindamisprotokoll; kasutaja vaatest hinnatakse just satelliidi käitumist päris ruumis (vallandumise usaldusväärsus, kiirus, valeaktiveeringud, fraasi loomulikkus).

**Sihtgrupp:** eesti keelt kõnelevad nutikodu kasutajad, kes osalesid lühikeses (~10 min) varjudemos satelliidi ja Home Assistanti lihtsate käskude (valgustus, taimer, ilm) raames. Vastajad ei ole tingimata varem äratussõnu kasutanud.

**Fookus:** kuna olemasolev `mini-questionnaire-form-v1.md` katab juba kohapeal täidetava lühivormi (UMUX-Lite + SEQ + diagnostilised hinnangud), siis käesolev küsitlus on mõeldud **järelküsitlusena veebis** (täidetakse 24 h jooksul peale demot või iseseisva valideerimisringi raames). Seetõttu on rõhk pisut laiem: lisaks kohese kasutuskogemuse ülekontrollile mõõdetakse ka tajutavat **kasulikkust kodukontekstis**, **usaldusväärsust ajas** ja **valmidust süsteemi päriselt kasutusele võtta**.

**Maht:** 11 küsimust (8 kvantitatiivset, 3 avatud), eeldatav täitmisaeg 5--7 minutit.

---

## Sissejuhatav tekst (vastajale)

> Tere! Aitäh, et osalesid eestikeelse äratussõna "Kuule Kratt" katsetuses. See küsitlus aitab hinnata, kui hästi lahendus reaalsete kasutajate ootustele vastab. Vastamine võtab umbes 5--7 minutit. Vastused on pseudonüümsed (seotakse ainult sinu osaleja-tunnusega) ja neid kasutatakse Tallinna Tehnikaülikoolis kaitstavas bakalaureusetöös. Skaalaküsimused mõõdavad sinu üldist tajutud kogemust; vabatekst aitab töö autoril mõista, mis konkreetselt hästi või halvasti töötas.

**Eeltäidetav metaandmeplokk** (vastaja kontrollib):
- Osaleja tunnus (`P##`)
- Kuupäev
- Eesti keele tase (emakeel / C1--C2 / B1--B2 / A1--A2 / muu / ei soovi öelda)
- Varasem häälassistendi kasutuskogemus (mitte kunagi / harva / iganädalaselt / iga päev)

---

## Osa 1: Hinnangulised küsimused

Skaalad on tahtlikult ühtlustatud (1--5, kus 1 = "Ei nõustu üldse" ja 5 = "Nõustun täielikult"), välja arvatud küsimus 1 (UMUX-Lite-tüüpi 1--7 skaala võrreldavuse huvides) ja küsimus 8 (käitumiskavatsus 1--5). Ühtlustamine vähendab vastaja koormust ja võimaldab raporteerida mediaani + kvartiilivahemikku ka väiksema valimi (N $\approx$ 20--30) korral.

### 1. Küsimus
**Süsteemi võimekused vastasid mu ootustele eestikeelse hääljuhtimise osas.**
- **Skaala:** 1--7 (1 = ei nõustu üldse, 7 = nõustun täielikult)
- **Eesmärk:** UMUX-Lite-stiilis kasulikkuse mõõtmine, mis on otse võrreldav kohapealse lühivormiga (`mini-questionnaire-form-v1.md`). Annab võrreldava lugemi, kas kasutaja tajub lahendust eesmärgipärasena.

### 2. Küsimus
**Süsteem reageeris fraasile "Kuule Kratt" usaldusväärselt.**
- **Skaala:** 1--5 (1 = ei nõustu üldse, 5 = nõustun täielikult)
- **Eesmärk:** Mõõdab tajutud tuvastamismäära (recall) reaalses olukorras. Töö kontekstis on see otse seotud üheks juhtumeid lähikõne tuvastamismäära $\geq$ 0,95 sihiga; subjektiivne hinnang täiendab kasutajatesti objektiivset salvestuslogi (`kratt user-test`).

### 3. Küsimus
**Süsteem ei käivitunud demoseansi ajal valesti.**
- **Skaala:** 1--5
- **Eesmärk:** Mõõdab tajutud valeaktiveeringute (FAPH) sagedust kasutaja vaatest. Subjektiivne hinnang ei asenda objektiivset FAPH mõõdikut, kuid näitab, kas tehniliselt madal FAPH ka kasutaja jaoks "vaikne" tundub.

### 4. Küsimus
**Süsteemi vastuse kiirus oli minu jaoks vastuvõetav.**
- **Skaala:** 1--5
- **Eesmärk:** Mõõdab tajutud latentsust (äratus -> Home Assistanti tagasiside). Eraldab usaldusväärsuse küsimuse kiiruse küsimusest, sest töö arutelu peatükis on need kaks erinevat riskiklassi.

### 5. Küsimus
**Fraasi "Kuule Kratt" oli kerge ja loomulik välja öelda.**
- **Skaala:** 1--5
- **Eesmärk:** Mõõdab fraasivaliku ergonoomikat. Töös on dokumenteeritud "Kule" vs "Kuule" hääldusvariandid; kui see hinnang on madal, viitab see fraasivaliku, mitte mudeli probleemile.

### 6. Küsimus
**Tunnen, et saaksin sellisest süsteemist oma igapäevases kodukasutuses kasu.**
- **Skaala:** 1--5
- **Eesmärk:** Mõõdab tajutud kasulikkust (utility) väljaspool demoolukorda. Eristub küsimusest 1, mis küsib ootuste täitmist; siin küsitakse rakendatavust kodukontekstis.

### 7. Küsimus
**Pean lokaalset, pilveteenusteta hääljuhtimist enda jaoks oluliseks.**
- **Skaala:** 1--5
- **Eesmärk:** Valideerib töö üht põhilist väiteargumenti --- privaatsust ja lokaalsust panusena. Kui hinnang on madal, viitab see, et lokaalsuse kasuargument on kasutaja jaoks teisejärguline ning töös tuleb seda esitusena tasakaalukamalt sõnastada.

### 8. Küsimus
**Kui süsteem oleks praegusel kujul olemas, oleksin valmis seda kodus kasutama.**
- **Skaala:** 1--5 (1 = kindlasti mitte, 5 = kindlasti jah)
- **Eesmärk:** Käitumiskavatsuse (behavioural intention) lähedane mõõdik. Kasutusele võtmise valmidus on tugevam tagasiside kui pelk meeldivus; eraldab "demos huvitav" arvamuse "päris kasutaks" arvamusest.

---

## Osa 2: Avatud küsimused

### 1. Küsimus
**Mis hetkel demos tundus süsteem kõige paremini või kõige halvemini töötavat? Palun kirjelda võimalikult konkreetselt (näiteks ruum, kaugus mikrofonist, taustaheli, kõnetempo).**
- **Eesmärk:** Kogub kvalitatiivset tõendusmaterjali olukordade kohta, mida objektiivne logi (recall, FAPH) üksinda ei seleta. Konkreetsuse nõue (ruum, kaugus, taustaheli) seob vastuse töö arutelupeatüki domeeninihke ja stsenaariumipõhise hindamise raamistikuga, võimaldades hiljem kasutajatesti leide klastritesse jagada.

### 2. Küsimus
**Mis aspekt sind häiriks või takistaks, kui sa peaksid seda süsteemi enda kodus iga päev kasutama? (Näiteks äratussõna ise, valeaktiveeringud, kiirus, paigaldamise keerukus, midagi muud.)**
- **Eesmärk:** Toob välja praktilise juurutuse takistused, mida lühike demo ei jõua paljastada. Suunab vastajat eristama mudeli-tasemel probleeme (äratussõna, valeaktiveeringud) ja süsteemi-tasemel probleeme (paigaldus, integratsioon Home Assistantiga), mis on töö kahe erineva panuse (mudel vs. integratsioonimuster) jaoks oluline eristus.

### 3. Küsimus
**Kui sa saaksid lahenduse autorile soovitada ühe parenduse, mis see oleks?**
- **Eesmärk:** Kogub prioriseeritud parendusettepanekuid. "Üks soovitus" sunnib vastajat valima olulisima, vältides nimekirja koostamist, kus kõik tundub võrdselt tähtis. Annab töö järelduste peatükile materjali edasiste suundade põhjendamiseks.

---

## Märkused koostajale

- Küsitlust on eelistatav rakendada **iseseisva veebivormina pärast** kohapealset `mini-questionnaire-form-v1.md` täitmist, mitte selle asemel; kohese vormi UMUX-Lite ja SEQ jäävad esmaseks võrreldavaks lugemiks. Käesolev veebiküsitlus täiendab seda laiema kasutus- ja vastuvõtuvaatega.
- Küsimuste 2--5 sõnastus on tahtlikult positiivne ("oli", "ei käivitunud valesti"), et vältida sega-orientatsiooniga skaalaga seotud raporteerimisvigu väikeses valimis. Kui koostaja eelistab balansseeritud sõnastust valiidsuse huvides, peaks ta muutma kõik küsimused samasuunaliseks (mitte segama).
- Suunavate küsimuste vältimiseks on küsimused 6--8 sõnastatud kasutaja perspektiivist ("tunnen", "pean", "oleksin valmis"), mitte tehnoloogia perspektiivist ("kas süsteem on...").
- Raporteerimise soovitus N $\approx$ 20--30 valimi puhul: mediaan + kvartiilivahemik iga skaalaküsimuse kohta; vabatekstid kodeeritakse temaatiliselt vähemalt kahe kodeerija poolt, et töö kasutajatesti peatükis oleks kvalitatiivne osa metoodiliselt kaitstav.
- Ükski küsimus ei küsi otse mudeli tehnilisi metrikaid (FAPH, recall) vastajalt; need jäävad objektiivse logi ülesandeks. See on teadlik valik, et vältida kasutaja-eksperdi rolli sundimist kasutajale.
