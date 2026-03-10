# Bakalaureusetöö ülesandepüstitus (2. iteratsioon)

**Ülikool:** Tallinna Tehnikaülikool  
**Instituut:** Infotehnoloogia teaduskond, informaatika õppekava (IAIB)  
**Autor:** Mattias Linholm (233408IAIB)  
**Juhendaja:** Tanel Alumäe (kooskõlastada kinnitamisel)  
**Koostamise kuupäev:** 22.02.2026  
**Planeeritud kaitsmine:** 2025/2026 kevadsemestri kaitsmisperioodis (02.02.2026-12.06.2026)

## Teema

**Eestikeelse äratussõna "Kratt" tuvastuse arendus, Home Assistanti add-oniks pakendamine ja valideerimine väliste kasutajatega.**

## Probleemi kirjeldus

Eestikeelne lokaalne hääljuhtimine Home Assistantis on tehniliselt võimalik, kuid praktiliselt puudub lahendus, mis ühendaks kolm kriitilist elementi:  
1) eestikeelne äratussõna usaldusväärne tuvastus ressursipiiratud seadmel,  
2) lihtne paigaldus lõppkasutajale (installitav add-on),  
3) tõendatud toimivus päriskasutajatega, mitte ainult arendaja enda testides.

Praegused projekti tulemused näitavad, et ESP32-S3 Korvo-2 + ESPHome `micro_wake_word` töötab tehnilise torustikuna, kuid kohandatud "Kratt" mudeli täpsus ja stabiilsus vajavad sihipärast andmestiku ning parameetrite optimeerimist. Lõputöö keskne uurimisprobleem on, kuidas viia see lahendus prototüübist tootlikuks artefaktiks, mida teised kasutajad saavad installida ja realistlikes tingimustes kasutada.

## Eesmärk ja oodatav tulemus

Töö eesmärk on luua eestikeelne wake word lahendus "Kratt", mis on:
- tehniliselt toimiv,
- reprodutseeritav,
- lõppkasutajale paigaldatav Home Assistanti add-onina,
- valideeritud väliste kasutajatega.

### Kohustuslikud tulemused

1. **Wake word mudel ("Kratt") ESP32-S3 jaoks**  
   Treenitud ja dokumenteeritud `microWakeWord` mudel koos häälestatud lävedega.

2. **Installitav Home Assistant add-on**  
   Add-oni pakend, konfiguratsioon ja paigaldusjuhend, et kasutaja saaks lahenduse lisahoidlast installida ilma käsitsi koodimuudatusteta.

3. **Valideerimispakett**  
   Tehnilised mõõtmised (täpsus, valehäired, latentsus) + väliste kasutajatega testid, mille tulemused on analüüsitud ja dokumenteeritud.

### Lisatulemus (kui ajaraam lubab)

- `openWakeWord` võrdluskatse Raspberry Pi platvormil.

## Metoodika

1. **Nõuete ja seotud tööde analüüs**  
   Wake word lahendused, Home Assistant/ESPHome piirangud, olemasolevad eesti STT/TTS komponendid.

2. **Andmestiku ettevalmistus ja iteratiivne mudeliarendus**  
   Reaalsed salvestused + andmete laiendamine, mudeli treenimine, offline hindamine, parameetrite häälestus.

3. **Süsteemi integratsioon**  
   Mudeli ühendamine Home Assistanti häälvooga ning add-oni pakendamine installitavaks artefaktiks.

4. **Valideerimine kahes etapis**  
   a) labori-/tehnilised testid,  
   b) väliste kasutajate testid.

## Valideerimisplaan (rõhutatud fookus)

### A. Tehniline valideerimine

- **Offline testkomplekt**: kõnelejate kaupa eraldatud train/test jaotus.  
- **Mõõdikud**: äratundmise määr (recall), valehäirete määr, möödalaskmiste määr, äratuslatentsus, end-to-end latentsus (äratussõnast käsu täitmiseni).  
- **Stsenaariumid**: vaikus, taustmüra, erinev kaugus mikrofonist, erinevad kõnelejad.

### B. Väliste kasutajate valideerimine

- **Valim (kohustuslik miinimum)**: 6-8 välist kasutajat (mitte autor), erineva taustaga.  
- **Valim (eesmärk ajavaru korral)**: 10-12 kasutajat.  
- **Testistsenaarium**: standardiseeritud ülesannete komplekt Home Assistantis (nt valgustus, stseenid, päringud).  
- **Kogutavad näitajad**: ülesande õnnestumise määr, katseni jõudmise aeg, valekäivitused, kasutaja hinnangud (nt SUS-küsimustik + lühike kvalitatiivne tagasiside).  
- **Võrdlus**: vähemalt ühe baseline'iga (nt manuaalne PTT käivitus), et hinnata wake word lahenduse tegelikku lisaväärtust.

Valideerimise eesmärk ei ole ainult näidata, et süsteem "töötab", vaid hinnata, kas lahendus on kasutatav ja usaldusväärne teistel inimestel päris kontekstis.

## Edukriteeriumid (esialgne versioon)

- Add-on on paigaldatav ja dokumenteeritud nii, et sõltumatu kasutaja saab selle tööle juhendi järgi.  
- Wake word töötab stabiilselt vähemalt ühel sihtplatvormil (ESP32-S3).  
- Tehnilised mõõdikud on raporteeritud ja põhjendatud (sh piirangud).  
- Väliste kasutajate test on läbi viidud vähemalt 6 kasutajaga ja analüüsitud (mitte ainult enesetest).

## Ulatus ja piirid

Töö fookus on wake wordil, süsteemi integreerimisel ja valideerimisel.  
Töö **ei** hõlma nullist uue STT/TTS mudeli arendamist; neid kasutatakse toetavate komponentidena.  
Kõige olulisemad artefaktid on: mudel, installitav add-on ja valideerimisraport.

## Esialgsed allikad

1. TalTech informaatika lõputööde info: <https://taltech.ee/informaatika-bakalaureusetoo-ja-oppepraktika>  
2. IAIB bakalaureusetöö ülesandepüstituse nõuded (alates kevad 2022): <https://haldus.taltech.ee/sites/default/files/news-editors/Infotehnoloogia_teaduskond/oppekorraldus_juhendid/juhendid/IAIB_bakalaureusetoo_ulesandepystitus_alates_kevad_2022.pdf>  
3. IT teaduskonna lõpetaja leht: <https://taltech.ee/loppetajale/it-teaduskond>  
4. TalTech IT teaduskonna lõputöö koostamise ja vormistamise juhend (11.08.2025): <https://haldus.taltech.ee/sites/default/files/2025-08/Juhend_loputoo_koostamiseks_ja_vormistamiseks_2025.pdf>  
5. Projekti tehniline alus: `/Users/mattias/kratt/wake-word/README.md`, `/Users/mattias/kratt/notes/experiments/2026-02-12-esp32-s3-korvo2-voice-satellite.md`
