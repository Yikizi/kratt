---
source_prompt: /Users/mattias/Downloads/loputoo_viibad_2026_04_28-2/06_Kaitsmine/Slaidiettekanne.txt
prompt_type: generative
generated: 2026-05-07
---

# Slaidiettekanne — kaitsmise slaidikomplekt

**Märkus prompti tõlgendamise kohta.** Lähteprompt küsib ettekande kestust (`<Sisesta siia aeg minutites>`). TalTech IT-bakalaureusetöö kaitsmiste tüüpiline ajalimiit on ~10 minutit; sellest lähtutakse ka käesolevas mustandis. Tempos ~1–1,5 min slaidi kohta annab see ~8 sisuslaidi pluss tiitelslaidi — täpselt prompti narratiivi punktid 1–8. Numbrid ja faktid pärinevad lõputöö peatükkidest (sissejuhatus, peatükid 1–3, kokkuvõte, eestikeelne ja ingliskeelne resümee, ülesandepüstitus); midagi peale lõputöös tõestatud arvude ei ole välja mõeldud.

---

## Slaid 1: Tiitelslaid

* **Eestikeelne äratussõna \enquote{Kuule Kratt} mikrokontrolleril**
* Bakalaureusetöö, TalTech, IT-teaduskond
* Autor: Mattias Linholm
* Juhendaja: \supervisorNameEst
* Tallinn 2026

> **Kõneleja märkmed:**
> Tere, minu nimi on Mattias Linholm. Kaitsen täna oma bakalaureusetööd, mille teemaks on eestikeelne äratussõna tuvastus piiratud ressursiga nutikodu mikrokontrolleril. Töö keskmes on fraasi \enquote{Kuule Kratt} lokaalne tuvastamine ESP32-S3 klassi seadmel, ilma pilveteenusteta. Järgneva 10 minuti jooksul tutvustan probleemi, lahenduse käiku ja seda, mis on töö peamine teaduslik panus.

---

## Slaid 2: Kontekst ja hetkeolukord

* Eestikeelne kõnetuvastus (Kiirkirjutaja) on lokaalselt olemas
* Eestikeelne äratussõna tugi avalikes raamistikes puudub
* `openWakeWord` ega Picovoice Porcupine ei toeta eesti keelt
* Mikrokontrolleri-klassi KWS-võrdlusalused on ingliskeelsed

> **Kõneleja märkmed:**
> Eesti keele jaoks on olemas kõnetuvastusmudelid ja korpused, ent nutikodu hääljuhtimise esimene komponent on äratussõna tuvastus, mis otsustab, kas seade üldse hakkab kasutaja kõnet edasi töötlema. Eesti keel ei kuulu hetkel \texttt{openWakeWord} avalike mudelite hulka ega ole ka Picovoice Porcupine'i toetatud keelte hulgas. Mikrokontrolleritele suunatud KWS-võrdlusalused (Speech Commands, microWakeWord) tegelevad valdavalt ingliskeelsete sõnadega. Seega on keele ja riistvaraklassi ristumine kaetamata.

---

## Slaid 3: Probleem ja motivatsioon

* Hääljuhtimise esimene filter on äratussõna — tema vead kanduvad edasi
* Väikese keele projektil pole valmis treeningandmeid ega võrdlusalust
* Klipi-tasemel hindamine annab eksitavalt optimistliku pildi
* Pidev helivoog käitub teisiti kui lühikesed testklippid

> **Kõneleja märkmed:**
> Probleem ei ole pelgalt mudeli puudumine. Kui äratussõna tuvastus eksib, siis kasutaja jaoks ei ole vahet, kui hea on hilisem kõnetuvastus — süsteem ei reageeri kas üldse või reageerib vales kohas. Töö käigus selgus, et tüüpiline klipi-tasemel hindamine — sama, mida kasutatakse paljudes KWS-publikatsioonides — võib näidata 0,4\% valepositiivset määra, samas kui tegelik valehäirete arv on suurusjärk \(10^2\) tunnis. See on töö üks peamisi motivatsioone: väikese ressursiga keele puhul ei ole pelgalt mudeli treenimine raske, vaid raske on \emph{tõestada}, et mudel on kasutuskõlblik.

---

## Slaid 4: Eesmärk ja lahendus

* Eesmärk: lokaalne, reprodutseeritav eestikeelse äratussõna toru
* Sihtkonfiguratsioon: ESP32-S3 + ESPHome + Home Assistant
* Treening- ja hindamisraamistik: \texttt{microWakeWord}
* Operatsioonilised sihid: FAPH < 1, lähikõne tuvastamismäär \(\geq\) 0,95

> **Kõneleja märkmed:**
> Eesmärk on uurida, kuidas üldse ehitada eestikeelne äratussõna tuvastus piiratud ressursiga seadmele nii, et lahendus oleks lokaalne, reprodutseeritav ja reaalses kasutuses hinnatav. Sihtplatvorm on ESP32-S3 ESPHome integratsiooniga, mis ühendub Home Assistanti voice-assistant liidesega. Operatsioonilised sihid — alla ühe valehäire tunnis ja vähemalt 0,95 lähikõne tuvastamismäär — ei ole universaalsed kirjandusstandardid, vaid käesoleva projekti otsustuskriteeriumid, mis ühtivad avatud raamistike soovituslike praktiliste sihtidega.

---

## Slaid 5: Teostus ja väljakutsed

* MixedNet arhitektuur, ~22\,000 parameetrit, INT8 TFLite
* Andmed: kogutud Korvo-2 positiivsed, Common Voice ET, MUSAN, TTS
* Hindamine: Wilsoni UV klipi-tasemel, Poissoni UV FAPH-il
* Auditid paljastasid: andmelekke, prefiksi-õppe, kontrollpunkti lühitee

> **Kõneleja märkmed:**
> Tehniliselt põhineb mudel \texttt{microWakeWord} raamistikul: MixedNet arhitektuur SVDF-ja MixedConv-plokkidega, kogu mudel ~22\,000 parameetrit, kvantiseeritud INT8 vormingusse. Andmestik on kombinatsioon ühelt kõnelejalt kogutud sama-seadme positiivsetest, Neurokõne TTS sünteetilistest variantidest, Common Voice ET negatiividest ja MUSAN taustaheli korpusest. Töö praktiline väljakutse ei olnud mudeli treenimine kui selline, vaid hindamise auditeerimine. Kolme valideerimisringi käigus paljastusid kolm erinevat lühiteed: esimeses ringis andmeleke, kus testikomplekt kattus treeningandmetega; teises ringis prefiksi-õpe, kus mudel reageeris üksikule sõnale \enquote{kuule}; kolmandas ringis kontrollpunkti valik, mis sihtis ainult madalat FAPH-i ja kaotas selle hinnaga reaalsete kõnelejate tuvastamise. Iga lühitee parandamine laiendas hindamisprotokolli.

---

## Slaid 6: Tulemused ja uus teadmine

* Ekspert A + Ekspert B v2 konsensus: **FAPH = 0,79** (Common Voice ET hold-out, 3,82 h)
* MacBook 70-min taustamonitor: 0 valehäiret, ülempiir reegli \enquote{kolm} järgi
* Ristkeelne FAPH: ET 44,5 vs EN 6,6 — sihtkeel tuleb domineerida negatiivides
* Lühitee-leid: parem benchmark ei tähenda paremat reaalkasutust

> **Kõneleja märkmed:**
> Numbrilises mõttes saavutas töö parima üksiku tulemuse kahe spetsialiseerunud ekspertmudeli konsensusena: Ekspert A (\enquote{väravavaht}, 96 filtrit, residuaalühendustega, 148\,KB) filtreerib üldist kõnet ja taustamüra, Ekspert B v2 (\enquote{kontrollija}, 48 filtrit, 55\,KB) eristab foneetilisi lähisugulasi. Konjunktsiooni-konsensus annab Common Voice ET hold-out komplektil FAPH = 0,79, mis on sama suurusjärgus tööstuslike süsteemide tulemustega — kuid saavutatud ~5 tunni eestikeelsete negatiividega, kus näiteks openWakeWord kasutab ~31\,000 tundi. Olulisem epistemoloogiline leid on aga see, et standardsed KWS-võrdlusalused ei ennusta reaalset kasutuskogemust: paremad benchmark-numbrid läksid mõnel juhul lahku reaalse kõneleja tuvastamise tulemustest. See on töö metoodikapanuse keskne tõend.

---

## Slaid 7: Mõju ja rakendatavus

* Esimene avalikult dokumenteeritud eesti äratussõna mudel
* Reprodutseeritav protokoll: ülekantav teistele väikestele keeltele
* Privaatsus säilib: heli ei lahku seadmest
* Kasutajatesti raamistik 20–30 osalejaga, opt-in audio nõusolek

> **Kõneleja märkmed:**
> Mõju on kahetine. Tehniliselt loob töö aluse eestikeelsetele lokaalsetele häälassistentidele — Home Assistant on Eestis kasutusel paljudel kodukasutajatel ja praeguseks pole sealsel platvormil eestikeelset äratussõna komponenti. Metoodiliselt — mis on minu hinnangul olulisem panus — pakub töö protokolli, mille kolm sammu (sõltumatu hold-out, positiivse klassi audit, mitmekriteeriumiline kontrollpunkti valik) on otse kohaldatavad teistele madala ressursiga keelte projektidele. Privaatsuse poolelt: kogu järeldamine toimub seadmel, audio ei lahku kasutaja kodust. Kasutajatest on kavandatud 20–30 osalejaga kahekihilise nõusolekumudeliga: minimaalne nõusolek pseudonüümseteks tehnilisteks tulemusteks, eraldi opt-in audio säilitamiseks.

---

## Slaid 8: Kokkuvõte (Research Highlights)

* Eestikeelne äratussõnatoru valideeritud avaliku \texttt{marvin} kontrollkatsega
* MoE-konsensus saavutab eesti hold-outil FAPH = 0,79 ühel operatsioonipunktil
* Töö peapanus: mitmemõõtmeline hindamisprotokoll, mitte üksik mudel
* Jääkrisk: tuvastamismäär \enquote{Kule}-hääldustel — kasutajatest kinnitab või kummutab
* \texttt{v16c} on kasutajatesti aktiivne kandidaat, mitte tootmisväide

> **Kõneleja märkmed:**
> Kokkuvõtteks: töö esimene panus on reprodutseeritav eestikeelne äratussõna treening- ja hindamistoru, mis on otsast lõpuni valideeritud avaliku Speech Commands kontrollkatsega. Teine ja, ma arvan, kõige kindlamini kaitstav panus on mitmemõõtmeline hindamisprotokoll: andmelekke audit, positiivse klassi audit ja kontrollpunkti komposiitne valikukriteerium. Kolmas tulemus on ekspertmudelite konsensuse demonstratsioon, mis saavutab alla ühe valehäire tunnis eesti keele hold-out komplektil. Aus piir: tuvastamismäär reaalsetel \enquote{Kule}-hääldustel jääb juurutusläve juures madalamaks kui TTS-positiivsetel klippidel, mistõttu lõplik juurutusotsus sõltub veel käimasolevast kasutajatestist. Mudel \texttt{v16c} on selle testi aktiivne kandidaat, mitte tootmiskvaliteedi tõend. Aitäh kuulamast — vastan hea meelega küsimustele.

---

## Lisamärkused ettekandjale

**Üldine slaidijaotuse tasakaal (~10 min):**

| Slaid | Sisu | Soovituslik aeg |
|-------|------|-----------------|
| 1 | Tiitel | 0:30 |
| 2 | Kontekst | 1:00 |
| 3 | Probleem | 1:00 |
| 4 | Eesmärk | 1:00 |
| 5 | Teostus | 1:30 |
| 6 | Tulemused | 2:00 |
| 7 | Mõju | 1:00 |
| 8 | Kokkuvõte | 1:00 |
| Reserv | Üleminekud, küsimused | ~1:00 |

**Visuaalsed soovitused (ei ole prompti otsene nõue, ent toetab \enquote{visuaalselt puhas} kriteeriumi):**

* Slaidile 6 tasub lisada DET-kõvera joonis (`figures/det_v6_v15_v16c_expertA.pdf`) või FAPH–recall Pareto (`figures/faph_recall_pareto.pdf`); mõlemad on töös juba viidatud ning kannavad ettekande keskset numbrit visuaalselt.
* Slaidile 5 tasub lisada lihtne kahe-mudeli konsensuse skeem (Ekspert A → AND-värav ← Ekspert B v2), mis muudab \enquote{ekspertmudelite konsensus} kõlava termini ühe pilguga arusaadavaks.
* Slaidil 3 (probleem) on eelistatav graafik-ilma-numbrita: jätta arvulised väited (367 → 154 → 96 → 0,79) slaidile 6, kus need on koos kontekstiga; muidu kannavad kaks slaidi sama narratiivi.

**Slaididel teadlikult välja jäetud detailid (kõneleja võib küsimuste korral kasutada):**

* Andmelekke täpne sisu (sama 5000 CV ET klippi treeningus ja hindamises) — sobib küsimusele \enquote{kuidas avastasite metoodika probleemi?}.
* Degradatsiooni org Park et al. järgi ja v3 V-kuju — sobib küsimusele \enquote{miks v3 oli halvem kui v1?}.
* Ekspert B v1 100\% HN treeningu läbikukkumine ja 20\% üldiste negatiividega kalibreerimine — sobib küsimusele \enquote{mis on oluline ekspertmudeli treeningandmestiku koosseisu juures?}.
* Reegli \enquote{kolm} kasutamine \(k=0\) FAPH-i ülemise piiri raporteerimiseks — sobib statistilise rangust uurivale küsimusele.

**Terminoloogiline puhtus (prompti reegel \enquote{vaba slängist ja lühenditest}):**

* Lühend FAPH on slaididel kasutatud, ent slaidi 4 \enquote{Kõneleja märkmetes} avatud; samuti kohe pärast esmamainimist (\enquote{valehäirete arv tunnis}). See on kooskõlas töös kasutatud praktikaga.
* Lühend KWS, MoE, FRR, FPR jäävad teadlikult ainult kõneleja märkmetesse, slaidil mitte. \enquote{Mixture of Experts} on slaidil 6 sõnastatud kui \enquote{kahe spetsialiseerunud ekspertmudeli konsensus}.
