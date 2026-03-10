# Bakalaureusetöö ülesandepüstitus (1. iteratsioon)

**Ülikool:** Tallinna Tehnikaülikool  
**Instituut:** Infotehnoloogia teaduskond, informaatika õppekava (IAIB)  
**Autor:** Mattias Linholm (233408IAIB)  
**Juhendaja:** Tanel Alumäe (kooskõlastada kinnitamisel)  
**Koostamise kuupäev:** 22.02.2026  
**Planeeritud kaitsmine:** 2025/2026 kevadsemestri kaitsmisperioodis (02.02.2026-12.06.2026)

## Teema esialgne sõnastus

**Eestikeelse äratussõna "Kratt" tuvastuse arendus ja integreerimine Home Assistanti lokaalsesse hääljuhtimise torustikku.**

## Probleemi kirjeldus

Eesti keele jaoks on olemas kõnetuvastuse ja kõnesünteesi lahendusi, kuid praktilises nutikodu kasutuses on puudu hästi toimiv eestikeelne äratussõna tugi, mis töötaks lokaalselt ja oleks integreeritav Home Assistantiga. See tähendab, et süsteemi käivitamine häälkäsklusega on kas ebastabiilne, ingliskeelsetest äratussõnadest sõltuv või vajab pilveteenuseid.

Praegune projektiseis näitab, et ESP32-S3 Korvo-2 + ESPHome `micro_wake_word` torustik töötab, kuid kohandatud "Kratt" mudel vajab paremat andmestikku ja mudeli häälestust, et jõuda stabiilse päriskasutuseni. Lõputöö keskne probleem on: kuidas ehitada ja valideerida eestikeelne äratussõna mudel, mis toimib ressursipiiratud seadmel ning on kasutatav Home Assistanti lokaalses häälassistendi voos.

Fookuse nihe varasema plaaniga võrreldes on teadlik: varasem "täieliku STT-LLM-TTS assistendi" ulatus on kitsendatud nii, et teaduslik põhipanus on äratussõna mudel ja selle kvaliteet, samal ajal kui STT komponent (Kiirkirjutaja Wyoming INT8) on toetav infrastruktuur.

## Eesmärk ja oodatav tulemus

Töö eesmärk on luua ja hinnata eestikeelne äratussõna lahendus "Kratt", mis töötab lokaalselt ning on reprodutseeritavalt juurutatav Home Assistanti keskkonda.

Oodatav tulemus:
- Treenitud ja dokumenteeritud "Kratt" mudel `microWakeWord` raamistikus (ESP32-S3 jaoks).
- Võrdlus- või kontrollkatse `openWakeWord` lahendusega Raspberry Pi platvormil (kui ajaraam lubab).
- Reprodutseeritav andmete ettevalmistuse, treenimise ja hindamise töövoog (skriptid + juhised).
- Töötav integratsioon Home Assistanti häälvooga ning tehniline hindamisraport.

Edu kriteeriumid (esimese iteratsiooni versioon):
- Äratussõna tuvastus töötab stabiilselt vähemalt ühel sihtplatvormil (ESP32-S3).
- Valehäirete ja möödalaskmiste tase on praktilises kodukeskkonnas vastuvõetav (mõõdetud teststsenaariumitega).
- Lahendus on teisele arendajale reprodutseeritav olemasoleva repositooriumi põhjal.

## Metoodika ja valideerimine

Metoodika on iteratiivne:
1. **Nõuete ja seotud tööde analüüs**: wake word lahendused, Home Assistanti ja ESPHome piirangud.
2. **Andmestiku ettevalmistus**: olemasolevad salvestused, täiendav kogumine ning andmete laiendamine (augmentation).
3. **Mudeli treenimine ja häälestus**: `microWakeWord` mudeli treenimine, lävendeid ja akna parameetreid optimeerides.
4. **Seadme- ja süsteemitestid**: jooksutamine ESP32-S3 Korvo-2 peal, integratsioon Home Assistantiga.
5. **Hindamine**: offline testid (positiivsed/negatiivsed näited) ja kontrollitud kodukeskkonna katsed (latentsus, valehäired, möödalaskmised).

Valideerimine toimub nii tehniliste mõõdikute (tuvastustäpsus, valehäirete määr, latentsus) kui ka funktsionaalse kasutatavuse kaudu (äratussõna käivitab häältoru usaldusväärselt pärisstsenaarumis).

## Ulatus ja piirid

Töö fookus on äratussõna tuvastusel ja selle integratsioonil. Töö **ei** hõlma nullist uue eestikeelse STT/TTS mudeli arendust ega täieliku telefoni-/LLM-assistendi arhitektuuri realiseerimist; olemasolevaid komponente kasutatakse toetava taristuna. Vajadusel tehakse kompromiss platvormide osas (kohustuslik siht ESP32-S3, Raspberry Pi võrdlus lisandub ajavaru korral).

## Esialgsed allikad

1. TalTech informaatika lõputööde info: <https://taltech.ee/informaatika-bakalaureusetoo-ja-oppepraktika>  
2. IAIB bakalaureusetöö ülesandepüstituse nõuded (alates kevad 2022): <https://haldus.taltech.ee/sites/default/files/news-editors/Infotehnoloogia_teaduskond/oppekorraldus_juhendid/juhendid/IAIB_bakalaureusetoo_ulesandepystitus_alates_kevad_2022.pdf>  
3. IT teaduskonna lõpetaja leht (kaitsmisperioodid ja juhendid): <https://taltech.ee/loppetajale/it-teaduskond>  
4. TalTech IT teaduskonna lõputöö koostamise ja vormistamise juhend (kehtiv 11.08.2025): <https://haldus.taltech.ee/sites/default/files/2025-08/Juhend_loputoo_koostamiseks_ja_vormistamiseks_2025.pdf>  
5. Projekti tehniline alus: `/Users/mattias/kratt/wake-word/README.md`, `/Users/mattias/kratt/notes/experiments/2026-02-12-esp32-s3-korvo2-voice-satellite.md`
