Kratt: eestikeelne äratussõnatuvastus nutikodu mikrokontrolleritele

Lühiülevaade projektist, mis loob esimese avatud lähtekoodiga eestikeelse äratussõna ("Kuule Kratt") mudeli ja integreerib selle Home Assistanti.

Põhipunktid:
- Lahendab eesti keele treeningandmete puuduse lokaalse kõnesünteesi (Tartu Neurokõne) ja andmete sünteetilise paljundamise abil, vältides GDPR probleeme.
- Treenib mikrokontrolleritele optimeeritud (Edge AI) mixednet arhitektuuriga mudeli, kasutades microWakeWord raamistikku.
- Kvantiseerib mudeli ESP32-S3-Korvo-2 arendusplaadile ja seob selle Wyoming protokolli abil Home Assistanti lokaalse hääljuhtimisega.
- Valideerib lahenduse tehniliselt (latentsus, täpsus) ja kasutuspõhiselt (erinevad kõnelejad mürarikkas keskkonnas), toetudes STT osas Kiirkirjutaja mudelile.
- Tulemuseks on avalik mudel, andmete genereerimise kood, ESPHome wake-word manifest ning modulaarsed Home Assistant add-on'id eestikeelse STT/TTS kasutuselevõtuks.
