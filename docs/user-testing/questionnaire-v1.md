# Kasutajatesti küsimustik v1

> **Note (2026-04-29):** this is the fuller questionnaire bank. The current 10-minute protocol uses a 4-rating + 1-comment mini questionnaire from `ten-minute-shadow-demo-protocol.md`; use this file for optional extended Google Forms items if participant burden allows.

**Alus**: VUS-inspireeritud (Kocaballi et al., 2020) + Kratt-spetsiifilised lisaküsimused
**Formaat**: Google Forms, telefonis täidetav
**Aeg**: ~4 minutit
**Skaala**: 7-punkt Likert (1 = üldse ei nõustu, 7 = täiesti nõustun), kui pole teisiti märgitud

**Terminoloogia**: küsimustikus kasutatakse järjepidevalt nime "Kratt".

---

## 0. Demograafia ja staatus

**0.1.** Vanusegrupp
*(<18 / 18-24 / 25-34 / 35-44 / 45-54 / 55-64 / 65+ / Ei soovi öelda)*

**0.2.** Sugu
*(Naine / Mees / Muu / Ei soovi öelda)*

**0.3.** Emakeel
*(Eesti / Vene / Inglise / Muu: ____)*

**0.4.** Eesti keele oskus
*(A1-A2 / B1-B2 / C1-C2 / Emakeele tasemel)*

**0.5.** Peamine staatus
*(Üliõpilane / Töötav spetsialist / Pensionär / Muu: ____)*

**0.6.** Varasem häälassistendi kasutus
*(Mitte kunagi / Harva / Iganädalaselt / Iga päev)*

**0.7.** Nutikodu kasutus
*(Ei kasuta / Kasutan aeg-ajalt / Kasutan regulaarselt)*

---

## A. Üldine kasutatavus

> 7-punkt Likert: 1 = üldse ei nõustu ... 7 = täiesti nõustun

**A1.** Kratt'i vastused olid kergesti arusaadavad.

**A2.** Kratt sai hästi aru, mida ma temalt palusin.

**A3.** Kratt'i vastused olid asjakohased minu küsimustele.

**A4.** Suutsin Kratt'iga kõik soovitud ülesanded ära teha.

**A5.** Kratt'i oli lihtne kasutada.

**A6.** Kratt'i oli mugav kasutada ka mürarikkas keskkonnas.

---

## B. Kiirus ja reageerimine

**B1.** Äratussõna tuvastamine oli kiire.
*(7-punkt Likert)*

**B2.** Vastuse genereerimine pärast minu käsku oli kiire.
*(7-punkt Likert)*

---

## C. Äratussõna "Kuule Kratt"

**C1.** Äratussõna "Kuule Kratt" on meeldiv.
*(7-punkt Likert)*

**C2.** Äratussõna oli lihtne hääldada.
*(7-punkt Likert)*

**C3.** Süsteem tuvastas äratussõna usaldusväärselt, kui ma seda ütlesin.
*(7-punkt Likert)*

**C4.** Kas süsteem reageeris ka siis, kui sa polnud äratussõna öelnud?
*(Mitte kunagi / 1-2 korda kogu testi vältel / Mitu korda päevas / Häirivalt sageli)*

**C5.** Kas eelistaksid mõnda muud äratussõna?
*(Jah / Ei)*
- Kui jah, siis millist? *(vaba tekst)*

---

## D. Eesti keele kvaliteet

**D1.** Kratt sai hästi aru minu eestikeelsest kõnest.
*(7-punkt Likert)*

**D2.** Kratt'i eestikeelsed vastused olid loomuliku kõlaga.
*(7-punkt Likert)*

---

## E. Privaatsus ja kasutusvalmidus

**E1.** On oluline, et selline süsteem töötaks täielikult lokaalselt (ilma pilveteenusteta).
*(7-punkt Likert)*

**E2.** Kasutaksin sellist süsteemi oma kodus.
*(7-punkt Likert)*

---

## F. Võrdlus teiste süsteemidega

**F1.** Kas kasutad mõnda teist häälassistenti?
*(Mitu valikut: Siri / Alexa / Google Assistant / Home Assistant Voice / OK Nabu / Muu / Ei kasuta)*

**F2.** Kui jah, siis võrreldes nendega Kratt on:
*(Märksa parem / Pisut parem / Sarnane / Pisut halvem / Märksa halvem / Ei oska võrrelda)*

---

## G. Soovitusvalmidus (NPS)

**G1.** Kas sa kasutaksid Kratti edasi pärast testi lõppu?
*(Jah / Pigem jah / Pigem ei / Ei)*

**G2.** Kui tõenäoliselt soovitaksid sa Kratti oma sõpradele või pereliikmetele?
*(0 = ei soovitaks kunagi ... 10 = soovitaksin kindlasti)*

---

## H. Vaba tagasiside

**H1.** Tüüpilise käsu kohta — mitu korda pidid keskmiselt seda kordama, et Kratt reageeriks?
*(Valik: 0 / 1 / 2 / 3+)*

**H2.** Mis Kratt'i juures meeldis kõige rohkem?
*(Vaba tekst)*

**H3.** Mis häiris või vajaks parandamist?
*(Vaba tekst)*

---

## Skoorimise juhend

### Kratt Usability Score (A1-A6)
*VUS-inspireeritud, mitte valideeritud VUS skoor — kasutame Kratt-spetsiifilist liitskoori.*

- Iga küsimus: skoor = vastus - 1
- Skaala: 0-36 (6 küsimust × max 6 punkti)
- Normaliseeritud: (summa / 36) × 100 = 0-100 skoor

**NB**: Originaal-VUS kasutab osaliselt pööratud küsimusi. Siin on kõik sõnastatud
positiivselt, et vältida segadust lühikese testi puhul. Lõputöös seetõttu **ei
nimetata seda VUS skooriks** vaid "Kratt usability score" — VUS on inspiratsioon,
mitte valideeritud instrument selles vormis.

### Kratt-spetsiifilised (B-E)
- Iga küsimus raporteeritakse eraldi: mediaan + kvartiilid
- Lõputöös esitada visuaalselt (box plot / stacked bar chart)

### Valehäired (C4)
- Kategooriline jaotus (4 vastust)
- Võrrelda objektiivsete logidega (FAPH mõõtmine süsteemilogidest)

### Võrdlus (F)
- F1: sagedusjaotus (mis süsteeme kasutatakse)
- F2: filtreeritud nendele kes vastasid F1-le, jaotus 5 kategooriasse

### NPS (G2)
- Promoters (9-10) - Passives (7-8) - Detractors (0-6)
- NPS = % Promoters - % Detractors
- Tugev kvantitatiivne võrdlusmõõdik

### Avatud küsimused (H)
- H1: sagedusjaotus (histogramm)
- H2-H3: kvalitatiivne temaatiline analüüs

---

## Viited

- Kocaballi, A. B., et al. (2020). "Voice Usability Scale: Measuring the User
  Experience with Voice Assistants." IEEE International Symposium on Smart
  Electronic Systems (iSES).
- Hone, K. S., & Graham, R. (2000). "Towards a tool for the Subjective Assessment
  of Speech System Interfaces (SASSI)." Natural Language Engineering, 6(3-4).
- Brooke, J. (1996). "SUS: A 'Quick and Dirty' Usability Scale." (võrdluseks)
- Reichheld, F. F. (2003). "The One Number You Need to Grow." Harvard Business
  Review (NPS).
