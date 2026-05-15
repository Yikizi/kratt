# Kratt kasutajatesti nõusoleku tekst v1

**Status:** participant-facing draft for 10-minute pilot/full user test. Use before every session; store only participant ID + chosen consent level, not names.

## Operator note

- Default thesis user-test mode should be local/offline. If the demo uses any external/cloud service for transcript, intent parsing, LLM, or telemetry, do **not** use this consent text unchanged; add explicit external-processing consent first.
- If participant chooses `ainult mõõdikud`, run `kratt user-test ... --audio-consent no` or delete raw WAVs immediately after extracting allowed non-identifying metrics.
- Voice is potentially identifying personal data. Treat the `mõõdikud + helisalvestis` choice as stronger consent than `ainult mõõdikud`.

## Short spoken introduction

Tere! See on umbes 10-minutiline TalTechi bakalaureusetöö kasutajatest. Testime eestikeelset äratussõna **„Kuule Kratt“** ja ühe nutipirni hääljuhtimist.

Testis palun Sul öelda mõned etteantud fraasid, mõned sarnased fraasid, mis ei tohiks süsteemi käivitada, ja mõned lihtsad pirnikäsud. Lõpus on lühike tagasisideküsimustik.

Osalemine on vabatahtlik. Võid igal ajal pausi teha, küsimusele vastamata jätta või testi katkestada.

## Mida kogutakse

Kogume vähemalt järgmisi pseudonüümseid andmeid:

- osaleja ID, nt `P01`;
- testikatsete tulemused: kas äratussõna tuvastati, kas käsk õnnestus, latentsus, vajadusel STT tekst;
- lühike tagasisideküsimustik;
- tehnilised logid, mis aitavad eristada äratussõna, kõnetuvastuse, käsu mõistmise ja pirni juhtimise vigu.

Kui valid variandi `mõõdikud + helisalvestis`, salvestame ka lühikesed WAV-heliklipid testifraasidega. Neid kasutatakse äratussõna mudelite võrdlemiseks ja vajadusel mudeli edasiseks parandamiseks.

## Nõusoleku valikud

Palun vali üks kahest variandist.

### Variant A — ainult mõõdikud

Nõustun, et minu anonüümseid/pseudonüümseid testitulemusi ja tehnilisi logisid kasutatakse Kratt bakalaureusetöös.

- Toorheli ei säilitata.
- Lõputöös esitatakse ainult koondtulemused või pseudonüümsed näited.

**Osaleja valik:** ainult mõõdikud: jah / ei

### Variant B — mõõdikud + helisalvestis

Lisaks Variant A-le nõustun, et minu testifraaside lühikesi heliklippe salvestatakse ja kasutatakse äratussõna hindamiseks ning võimaliku mudeli parandamiseks.

- Heliklippe ei avaldata avalikult ilma eraldi nõusolekuta.
- Heliklipid seotakse ainult osaleja ID-ga, mitte nimega.
- Võin hiljem paluda oma heliklipid kustutada, kuni need pole koondanalüüsiks lõplikult anonümiseeritud.

**Osaleja valik:** mõõdikud + helisalvestis: jah / ei

## Withdrawal / deletion

Kui soovid hiljem oma andmete kustutamist, anna operaatorile oma osaleja ID. Enne lõputöö lõplikku analüüsi saab pseudonüümse sessiooni ja heliklipid eemaldada. Juba anonümiseeritud koondstatistikat ei pruugi olla võimalik eraldi tagasi pöörata.

## Minimal operator record

```text
participant_id: P__
date: YYYY-MM-DD
consent_level: ainult mõõdikud / mõõdikud + helisalvestis
language note (optional): native Estonian / second-language Estonian / other
smart-home experience (optional): none / occasional / regular
operator notes (optional):
```
