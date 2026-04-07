# Vahekaitsmine: Kratt
## Eestikeelne äratussõnatuvastus nutikodu mikrokontrolleritele

**Mattias Linholm** | 233408IAIB | Juhendaja: Tanel Alumäe, PhD

24. märts 2026

> **MÄRKUS (post-vahekaitsmine, aprill 2026):** Vahekaitsmise ajal esitatud
> v3-v6 võrdlustabel slaidil 7 sisaldab numbreid (CV FPR 0,4%, KORVO-2 FPR 0,9%),
> mis arvutati treeningandmete osahulgalt – st mudel oli neid klippe juba näinud.
> Hilisem audit avastas selle andmelekke ja kogu hindamismetoodika kirjutati
> ümber. Korrigeeritud tulemused on lõputöö §2 (vt `chapters/second_chapter.tex`,
> alapeatükk "Andmelekke avastamine ja korrigeeritud hindamine") ja näitavad,
> et v6 \emph{ei ole} parim mudel – v7 saavutab parima FAPH (96 vs 154 tunni
> kohta) ja v8 parima foneetilise eristuse hard negatiivide peal (33% vs 100%).
> See metoodikaline õppetund on lõputöö üks tugevamaid leide.

Siinne versioon on timmitud umbes **10 minuti** jaoks. Eesmärk ei ole näidata kõiki detaile, vaid rääkida selge lugu:

1. miks probleem on päris;
2. mis oli tehniliselt raske;
3. mis oli peamine leid;
4. mis on juba töötav;
5. mis on veel teha.

---

## Slaid 1: Probleem ja väide

- Eesti keele jaoks puudub praktiline ja lokaalne wake word lahendus
- Home Assistanti hääljuhtimise toru on olemas, kuid eestikeelne äratussõna puudub
- Pilvepõhised lahendused ei sobi privaatsusnõudega kasutusjuhtudesse
- Selle töö väide: **"Kuule Kratt" on teostatav ka ESP32-klassi seadmel**

**Mida öelda**
- Alusta ühest lausest: "Probleem ei ole STT puudumine, vaid see, et kasutaja peab süsteemi kuidagi loomulikult äratama."
- Rõhuta, et töö eesmärk ei ole kogu voice assistant nullist ehitada, vaid täita kriitiline puuduolev lüli.

**Aeg:** ~45 s

---

## Slaid 2: Töö eesmärk ja uurimisküsimus

**Eesmärk**
- Treenida eestikeelne äratussõna mudel fraasile **"Kuule Kratt"**
- Käivitada see **ESP32-S3-Korvo-2** peal
- Siduda see **Home Assistanti lokaalsesse hääljuhtimisse**

**Uurimisküsimus**
- Kuidas ehitada väikese andmestikuga eestikeelne wake word, mis oleks ühtaegu
  - piisavalt täpne,
  - süsteemselt lõimitav,
  - päris riistvaral kasutatav?

**Mida öelda**
- Siin tasub raamida töö kolmeks plokiks: mudel, süsteem, valideerimine.

**Aeg:** ~45 s

---

## Slaid 3: Süsteemi arhitektuur

```text
[Mikrofon]
    ↓
[ESP32-S3 Korvo-2]
    ↓  wake word ("Kuule Kratt")
[Home Assistant]
    ↓
[Kiirkirjutaja STT] → [Intent] → [TTS / vastus]
```

- Wake word raamistik: **microWakeWord**
- Deploy formaat: **TFLite INT8**
- Sihtseade: **ESP32-S3-Korvo-2**
- Integratsioon: **ESPHome + Home Assistant + Wyoming**

**Mida öelda**
- Ütle selgelt, et STT/TTS on siin toetavad komponendid, mitte töö põhisisu.
- Selle töö põhiküsimus on: kas äratussõna töötab lokaalselt piisavalt hästi, et kogu ülejäänud toru üldse käima oleks mõistlik panna.

**Aeg:** ~50 s

---

## Slaid 4: Andmestiku strateegia

| Allikas | Roll |
|---------|------|
| Korvo-2 pärissalvestused | Positiivsed + sama-seadme negatiivsed |
| Neurokõne TTS | Positiivsete laiendus eri häältega |
| TTS hard negatives | "Hei Kratt", "Tere Kratt", "Kratt" jne |
| Common Voice ET | Üldised eestikeelsed negatiivsed |
| MUSAN + Korvo-2 ambient | Streaming false positive hindamine |

**Põhiidee**
- väikese keele andmepuudus lahendati **kombineeritud andmestrateegiaga**:
  - pärisandmed,
  - sünteetilised positiivsed,
  - rasked negatiivsed,
  - sama-seadme salvestused.

**Mida öelda**
- See on hea koht rõhutada, et probleem ei olnud ainult "rohkem andmeid", vaid "õiged andmed õiges rollis".

**Aeg:** ~60 s

---

## Slaid 5: Arendustee lühidalt

- Algusfaasis sõnastasin probleemi ja proovisin erinevaid voice assistant radu
- Seejärel ehitasin andmestiku- ja treeningutoru ning tegin esimese Korvo-2 katse
- Märtsis nihkus fookus kahele asjale:
  - toru metodoloogiline parandamine
  - `Kuule Kratt` mudeli iteratiivne arendus

**Mida öelda**
- Selle slaidi ainus eesmärk on näidata, et töö ei olnud lineaarne.
- Üks lause piisab: "Algul oli suurem risk infrastruktuuris, hiljem andmestikus ja mudelis."

**Aeg:** ~30 s

---

## Slaid 6: Mis ei töötanud alguses

- Esialgne custom `kratt` mudel **ei triggerdanud** Korvo-2 peal usaldusväärselt
- Selgus kolm eraldi probleemiklassi:
  - treeningukeskkonna / sõltuvuste probleemid,
  - katkine või eksitav evaluatsioon,
  - domeeninihe päris seadme ja treeningandmete vahel
- Esialgne hea tulemus osutus osaliselt **mõõtmise illusiooniks**, mitte päris kvaliteediks

**Oluline metoodiline õppetund**
- wake word mudelit ei tohi hinnata ainult lühikeste klippide peal;
- vaja on ka **streaming ambient** hindamist.

**Mida öelda**
- See on üks tugevamaid teaduslikke kohti kogu töös.
- Ütle otse: "Ma ei parandanud ainult mudelit, vaid pidin parandama ka selle, kuidas üldse otsustada, kas mudel on hea."

**Aeg:** ~75 s

---

## Slaid 7: Peamine leid - degradatsiooni org

| Versioon | Muutus | Recall | FPR (CV) | FPR (K-2) |
|----------|--------|--------|----------|-----------|
| v1 | Baseline | 92.8-94.8% | 8.0% | 13.8% |
| v3 | +109 sama-seadme neg | 98.0-98.8% | **98.0%** | 24.8% |
| v4 | +1311 sama-seadme neg | 100% | 36.8% | 7.3% |
| v5 | +TTS pos + hard neg | 99.6-100% | 41.6% | 1.8% |
| **v6** | **+3345 session2 neg** | **99.6-100%** | **0.4%** | **0.9%** |

**Tõlgendus**
- väike kogus sama-seadme andmeid tegi asja hullemaks;
- piisavalt suur kogus sama-seadme negatiive + hard negatives viis läbimurdeni.

**H1: sama seadme negatiivsed parandavad eristusvõimet** ✅
- kinnitatud
- Korvo-2 FPR langes 13.8% → 0.9%

**H2: sisutunnuseid õppinud mudel generaliseerub teisele mikrofonile** ✅ / esialgselt
- v6 töötas MacBook Pro sisemikrofoniga
- ei triggerdanud vaikuse, müra ega fraaside "Hei Kratt", "Tere Kratt" peale

**Mida öelda**
- Siin on töö põhitulemus.
- Ära loe tabelit rida-realt; ütle ainult: baseline, v3 läks hullemaks, v6 tõi läbimurde.
- Seo see Park et al. "valley of degradation" ideega, aga ära jää kirjandusse kinni.
- H2 puhul ütle ausalt, et see on veel esialgne kinnitus, mitte lõplik laia valimi test.

**Aeg:** ~100 s

---

## Slaid 8: Mis on juba praktiliselt töötav

- `v6` mudel jookseb **ESP32-S3-Korvo-2** peal
- Home Assistanti lõimimine on olemas
- Korvo-2 recorder firmware võimaldab koguda uut sama-seadme andmestikku
- Seega projekt ei ole ainult analüüs, vaid **töötav prototüüp**

**Demo valik**
- Kui demo teed, siis hoia see lühike:
  - "ütlen 'Kuule Kratt'"
  - seade tuvastab
  - Home Assistant reageerib

**Mida öelda**
- Kui demo on riskantne, siis ütle lihtsalt, et süsteem on deploy’itud ja demonstreeritav, kuid vahekaitsmise fookus on pigem metoodikal.

**Aeg:** ~60 s

---

## Slaid 9: Mis on veel teha ja miks töö on kaitstav

**Veel teha**
- suurem kasutajatest
- rohkem kõnelejaid positiivsetesse
- laiem ristseadme test
- Home Assistanti täielik kasutusstsenaarium lõpuni
- lõputöö kirjutamine ja formaliseerimine

**Miks töö on juba tugev**
- olemas on töötav mudel
- olemas on töötav ESP32 deploy
- olemas on selge metoodiline leid
- olemas on dokumenteeritud iteratiivne arendus, mitte must kast

**Mida öelda**
- Lõpeta ühe lausega:
  - "Selle töö väärtus ei ole ainult lõppmudel, vaid ka see, et nüüd on olemas reprodutseeritav tee, kuidas väikese keeleruumi wake word'i üldse usaldusväärselt arendada."

**Aeg:** ~55 s

---

## Slaid 10: Küsimused

**Mattias Linholm**  
mattias.linholm@taltech.ee

Repo: gitlab.cs.taltech.ee/malinh/iaib
