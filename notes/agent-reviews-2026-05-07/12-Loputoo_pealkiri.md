---
source_prompt: 03_Lõputöö_alamosad/Kohustuslikud/Lõputöö_pealkiri.txt
prompt_type: generative
generated: 2026-05-07
---

# Lõputöö pealkirja variandid

## 1. Sisu lühianalüüs

- **Uurimisobjekt:** eestikeelne äratussõna tuvastus (fraas „Kuule Kratt"), piiratud ressursiga nutikodu mikrokontrolleril (ESP32-S3 klass).
- **Probleem:** väikese keele lokaalse äratussõna tugi puudub avatud raamistikes ja kaubanduslikes võrdluspunktides; ainult mudeli treenimisest ei piisa, sest hindamisprotokoll ja andmelekke kontroll on metoodiliselt määravad.
- **Lahendus:** rekonstrueeritud `microWakeWord`-toru, sõltumatud kõrvalejäetud testikomplektid, FAPH-põhine pidevvoo hindamine, ekspertmudelite konsensus ja kontrollpunktide kombineerimine, ESP32-S3 + Home Assistant integratsioon.
- **Metoodika:** eksperimentaalne, reprodutseeritav treeningu- ja hindamistoru; klipi-taseme + voogedastuse FAPH; avalik kontrollkatse `Speech Commands` peal; piiratud kasutajatestid.
- **Põhipanus:** näidata, et väikse keele lokaalse äratussõna juures on keskne mitte ainult mudel, vaid metoodiliselt korrektne hindamine ja tõendusdistsipliin.

## 2. Olemasoleva pealkirja audit

- **Praegune (EE):** „Kratt: eestikeelne äratussõnatuvastus nutikodu mikrokontrolleritele"
- **Praegune (EN):** „Kratt: Estonian Wake Word Detection for Smart Home Microcontrollers"
- **Hinnang:** 7/10. Eelised: lühike, projektinimi „Kratt" annab identiteedi, sihtkeel ja sihtriistvara on selged. Puudused: ei vihja töö tegelikule metoodilisele panusele (hindamisprotokoll, FAPH, andmelekke kontroll); jätab mulje peamiselt insenerlikust mudelitööst, kuigi töö enda sõnastuse järgi on põhitulemus just hindamismetoodika täpsustamine. Liitsõna „äratussõnatuvastus" on aktsepteeritav, kuid „äratussõna tuvastus" (kahe sõnaga) on töö tekstis valdav vorm — ebajärjekindlus pealkirja ja sisu vahel.

## 3. Variandid (sorteeritud hinde järgi kahanevalt)

---

**Variant 1**
- **Eesti keeles:** Eestikeelse äratussõna „Kuule Kratt" tuvastus ja hindamine ESP32-S3 mikrokontrolleril
- **Inglise keeles:** Detection and Evaluation of the Estonian Wake Word "Kuule Kratt" on an ESP32-S3 Microcontroller
- **Hinnang:** 9/10
- **Selgitus:** Kõige täpsem: nimetab sihtfraasi, keele, sihtriistvara klassi ning rõhutab nii tuvastust kui ka hindamist — viimane on töö enda sõnul peamine panus. Lühike, terminoloogiliselt korrektne, akadeemiline. Väike puudus: ei vihja FAPH- või voogedastushindamise eripärale.

---

**Variant 2**
- **Eesti keeles:** Madala ressursiga eestikeelne äratussõna tuvastus: „Kratt" mikrokontrolleripõhise nutikodu satelliidi näitel
- **Inglise keeles:** Low-Resource Estonian Wake Word Detection: A Microcontroller-Based Smart Home Satellite Case Study
- **Hinnang:** 8,5/10
- **Selgitus:** Toob esile väikse keele konteksti („madala ressursiga") ja juhtumiuurimuse vormi, mis vastab töö tegelikule ulatusele (üks fraas, üks satelliidiseade). Akadeemilises stiilis ja sisuga kooskõlas. Puudus: pisut pikem ja kaksikpunkt võib mõnele lugejale tunduda mahukas.

---

**Variant 3**
- **Eesti keeles:** Eestikeelse äratussõna tuvastusmudeli arendus ja voogedastushindamine FAPH-mõõdikuga
- **Inglise keeles:** Development and Streaming Evaluation of an Estonian Wake-Word Detection Model Using the FAPH Metric
- **Hinnang:** 8/10
- **Selgitus:** Rõhutab töö metoodilist panust (voogedastushindamine, FAPH), mis on töö enda sõnul kõige olulisem tulemus. Sobib lugejale, kes hindab metoodika selgust. Puudus: kaotab nutikodu/mikrokontrolleri rakendusliku raami, mis on samuti pealkirja-vääriline.

---

**Variant 4**
- **Eesti keeles:** „Kuule Kratt": eestikeelse äratussõna mudeli loomine ja lõimimine Home Assistanti hääljuhtimisahelasse
- **Inglise keeles:** "Kuule Kratt": Building and Integrating an Estonian Wake-Word Model into the Home Assistant Voice Pipeline
- **Hinnang:** 7,5/10
- **Selgitus:** Rõhutab süsteemset lõimimist (Home Assistant), mis on üks kolmest töö panusest. Sihtfraas on kohe nähtav, identiteet tugev. Puudus: hindamise/metoodika osa, mis on töö suurim panus, jääb pealkirjas tahaplaanile; ka „Home Assistant" on tooteviide, mille akadeemilisus on piiripealne.

---

**Variant 5**
- **Eesti keeles:** Reprodutseeritav treening- ja hindamistoru madala ressursiga äratussõna jaoks: „Kuule Kratt" eesti keeles
- **Inglise keeles:** A Reproducible Training and Evaluation Pipeline for Low-Resource Wake Words: "Kuule Kratt" in Estonian
- **Hinnang:** 7/10
- **Selgitus:** Toob esile reprodutseeritavuse ja toru-aspekti, mis on töö üks kolmest deklareeritud panusest. Üldistatav teistele väikestele keeltele, mis tugevdab teaduslikku raami. Puudus: pealkiri on suhteliselt pikk, „madala ressursiga" + „reprodutseeritav" + sihtfraas tekitavad info-tiheduse, ja mikrokontrolleri/riistvara ulatus jääb varju.

---

## 4. Soovitus

Soovitatav on Variant 1 või Variant 2 sõltuvalt sellest, mida juhendaja ja kaitsmiskomisjon soovivad pealkirjas esiplaanile. Variant 1 on neutraalne ja ametliku tehnikatöö pealkirjana kõige tugevam; Variant 2 sobib paremini, kui soovitakse rõhutada metoodika üldistatavust ka teistele madala ressursiga keeltele. Praegune pealkiri on töökorras, kuid lisab vähe väärtust võrreldes Variant 1-ga, mis nimetab sihtfraasi ja toob hindamise sõnaselgelt sisse.
