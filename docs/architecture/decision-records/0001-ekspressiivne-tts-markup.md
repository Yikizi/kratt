# ADR-0001: Ekspressiivse markup-keele valik lokaalse TTS jaoks

**Staatus**: Vastu võetud — **Variant D (markup puudub)**
**Kuupäev**: 2026-04-07
**Otsustaja**: Mattias
**Kontekst**: Kratt häälassistendi runtime pipeline

## Otsus

Ekspressiivset markup-kihti TTS-ile **ei ehitata**. Runtime TTS töötab lihttekstiga, mida töötleb sox v2 efektiketi (pitch +300, overdrive 15 30, treble +3, contrast 70) kogu vastuse peal. See annab Krattile järjepideva karakteri ilma markup-parseri implementatsioonikuluta.

**Põhjendus**:
- Bakalaureuse skoop — iga tund SSML/markup implementatsioonis on tund vähem lõputöö peamisel panusel (wake word mudel ja treeningandmed)
- Karakter eksisteerib juba v2 sox efektist — kasutajatestid ei kannata
- Lõputööd ei kaitsta TTS ekspressiivsuse põhjal, vaid wake word'i ja tervikintegratsiooni põhjal
- Variant D on ADR § 3.D all juba kaitstava põhjendusega: "Karakter on juba olemas v2 efektist. Aeg vabaneb wake word treeningule"

**Ekspressiivne markup liigub lõputöö peatükki "Edasiarendus"** koos lühikese põhjendusega miks seda nüüd ei tehtud ja miks see võiks tulevikus huvitav olla.

Empiiriline võrdlus (§ 4) jääb siiski paika ja on viide tulevasele edasiarenduse kaalumisele.

---

## 1. Kontekst

Kratt on eestikeelne häälassistent mille pipeline on:

```
wake word → STT → LLM (intent + vastus) → MCP toiming → TTS → kasutaja kuuleb
```

LLM (Gemma 3 12B) toodab JSON struktuuri kus väli `response` sisaldab kasutajale ette loetavat eestikeelset vastust. Lokaalne TTS (TartuNLP TransformerTTS, kõneleja `meelis`) sünteesib selle audioks.

Praegune lahendus: `response` on lihttekst, sünteesitakse otse, post-processed sox-iga (v2 efektiketi: pitch +300, overdrive 15 30, treble +3, contrast 70) et anda Krattile karakterit.

**Probleem**: Lokaalne TartuNLP mudel ei toeta ekspressiivset markup'i — ainult kogu lause kohta käivat `speed` parameetrit. Kuid tahame anda Krattile rikkamat prosoodiat — pause, rõhk, tempo varieerumine, dünaamika — ilma kommertsteenuse (Google/Azure/AWS) kasutamiseta, sest täielikult lokaalne töö on lõputöö üks põhipanuseid.

Märkus: TartuNLP **hostitud Neurokõne API** (`api.tartunlp.ai/text-to-speech/v2`) **toetab W3C SSML 1.1 alamhulka** (prosody, emphasis, break). See preprocessing kiht eksisteerib ainult cloud serveris, mitte avatud lähtekoodiga `text-to-speech-worker` repos. Cloud API kasutamine runtime'is rikuks "fully offline" lubaduse, seega vaatame ainult lokaalseid lahendusi.

## 2. Otsuse ajurid

| # | Driver | Selgitus |
|---|---|---|
| D1 | **Offline garantii** | Lõputöö põhilubadus on et kogu pipeline töötab ilma internetita |
| D2 | **LLM produktiivsus** | Iga lisatud token suurendab vastuse latency'd ~40ms (25 tok/s) ja tõstab JSON parse error tõenäosust |
| D3 | **Mudeli võimete piirid** | TartuNLP TransformerTTS toetab natiivselt ainult `text + speaker + speed` per kutse — kõik muu peab olema preprocessing/postprocessing kihis |
| D4 | **Akadeemiline kaitstavus** | Lõputöös peab olema põhjendatav: "miks tegite just nii, mitte standardit" |
| D5 | **Implementatsioonikulu** | Bakalaureuse skoop — iga tund SSML peal on tund vähem wake word treenimisel |
| D6 | **LLM tugi** | LLM peab markup'i ise genereerima oma vastusesse — formaat peab olema talle kerge ja vea-tolerantne |

## 3. Vaadeldud variandid

### Variant A: W3C SSML 1.1 (XML-põhine)

Standardne markup, näiteks:
```xml
<speak><prosody rate="fast">Lülitasin elutoa lambi põlema</prosody>
<break time="400ms"/> ja muutsin värvi <emphasis level="strong">punaseks</emphasis>.</speak>
```

**Plussid**:
- W3C standard — tunnustatud ja tsiteeritav
- Tools olemas: `xml.etree.ElementTree` (Python stdlib), `lxml`
- Migreerides cloud TTS-ile (Azure/Google/Polly) töötaks sama markup
- LLM treeningandmetes on palju SSML näiteid → mudel teab juba semantikat

**Miinused**:
- **Sõnaderikas**: empiirilises testis sama vastus 182 tähemärki SSML-iga vs 72 lihttekstiga (+150%)
- **JSON escape põrgu**: SSML sees olevad jutumärgid (`pitch="+20%"`) tuleb LLM-il oma JSON väljundis backslash-eskapeerida (`pitch=\"+20%\"`). Iga jutumärk on koht kus mudel võib eksida ja JSON murda. Mõõdetult 6 escape'i rikka näite kohta.
- LLM peab tooma 52 tokenit vs 31 (rikas markup) — **21 tokenit lisa** = ~0.84s lisa latency per vastus
- Suur osa SSML semantikat (per-sõna emfaas, contour) on meie sentence-level mudelile **võltsitav, mitte loomulik**

### Variant B: Kohandatud nurksulu-markup

Omakirjeldatud, lühike formaat:
```
[fast]Lülitasin elutoa lambi põlema[/fast] [pause 400] ja muutsin värvi [emph]punaseks[/emph].
```

**Plussid**:
- **Kompaktne**: 110 tähemärki rikast versiooni (vs SSML 182), **+17%-53% lihtteksti üle**
- **Null JSON escape'i**: nurksulud ei ole JSON erimärgid, läbib puhtalt
- LLM toodab vähem tokeneid → kiirem vastus + vähem vigu
- Lihtne parsida (regex piisab, ~50 rida koodi)
- Saab kavandada täpselt nii et semantika kaardub mudeli võimetele 1:1
- Defineeritav: ei toeta seda mida mudel ei oska, seega pole "valeootuse" probleemi

**Miinused**:
- **Mitte-standardne**: tuleb dokumenteerida ja juhendajale selgitada
- LLM ei tea seda formaati alguses → vajab süsteempromptis näiteid (few-shot)
- Cloud TTS-ile migreerimisel vaja translation layer'it
- Risk et nurksulud satuvad eestikeelses tekstis kokku (väga harv aga võimalik)

### Variant C: Hübriidne — SSML peamine, lihttekst fallback

Pipeline aktsepteerib mõlemat: kui `response` algab `<speak>`-iga, parsib SSML, muidu käsitleb lihttekstina. Vea korral SSML parsimisel langeb tagasi lihttekstile.

**Plussid**:
- Maksimaalne paindlikkus
- Hea kui LLM on mõnikord tark, mõnikord ei
- Failure mode on graceful

**Miinused**:
- Implementatsioonikulu = A + extra loogika (~400 rida)
- LLM-il pole selget juhist millal kasutada — trade-off seletada
- Test pinda kahekordistab

### Variant D: Markup üldse mitte (status quo)

Jätta lihttekst, jätkata sox v2 efektiketiga kogu vastuse peal. SSML jätta lõputöö "edasiarendus" peatükki.

**Plussid**:
- **Null lisakulu**
- Karakter on juba olemas v2 efektist
- Aeg vabaneb wake word treeningule (mis on lõputöö põhipanus)

**Miinused**:
- Üks pikk monotoonne lause tervele vastusele — pole pause, pole tempo varieerumist
- Krati persona on staatiline
- Vähem demo "wow factor'it"

### Variant E: Lihtne pause-only markup (minimaalne ekspressiivsus)

Toetada ainult ühte tagi: `[pause Nms]`. Kõik muu — lihttekst.

**Plussid**:
- ~30 rida koodi
- 1h töö
- Pause on kõige enam tajutav prosody efekt
- LLM-il triviaalne genereerida

**Miinused**:
- Päris piiratud — pole tempo, pitch, rõhku
- Kui hiljem soovid rohkem, peab uuesti tagasi tulema

## 4. Empiiriline võrdlus

Sama vastus ("Lülitasin elutoa lambi põlema [pause] ja muutsin värvi punaseks") JSON-eskapeeritud kujul mida LLM peab tegelikult tootma:

| Variant | Tähemärke | ≈Tokenid | JSON escape'e | Lisa-latency vs lihttekst |
|---|---|---|---|---|
| Plain text | 72 | 20 | 0 | 0 ms |
| SSML minimaalne (`<break>`) | 111 | 31 | 2 | ~440 ms |
| SSML rikas (prosody+emphasis) | 182 | 52 | 6 | ~1280 ms |
| Bracket minimaalne | 84 | 24 | 0 | ~160 ms |
| Bracket rikas | 110 | 31 | 0 | ~440 ms |

(Latency hinnang Gemma 3 12B @ ~25 tok/s baseline'iga.)

**Tähelepanek**: Bracket rikas (31 tokenit, 0 escape'i) annab sama tokenikulu kui SSML minimaalne (31 tokenit, 2 escape'i) — aga rohkem ekspressiivsust ja vähem error'eid.

## 5. Soovitus

**Variant B (kohandatud nurksulu-markup)**, järgmise põhjendusega:

Lõputöö akadeemiline narratiiv: *"FastSpeech2-klassi mudel toetab loomulikult ainult lause-tasemel prosoodia kontrolli. W3C SSML semantika sisaldab nõudeid (per-sõna rõhk, contour pitch) mida selline mudel ei suuda loomulikult väljendada — neid saab vaid simuleerida segmenteerides ja audiosplaisides, mis lisab kuuldavaid üleminekuid. Selle tehnilise piirangu tunnistamiseks kavandasime kompaktse markup-keele mis vastab täpselt mudeli võimetele: pause, prosody rate, voice switching ja prosody pitch (sox post-processing kaudu). Empiiriline võrdlus näitas et SSML kasutamine sama semantilise sisu kohta tooks ~70% suurema LLM-i tokenivoo ja tooks JSON-eskapeerimise tõttu kasvava parse error määra; nende kompromisside vältimiseks valisime kohandatud syntax'i."*

See on **aus, mõõdetud, kaitstav** otsus — mitte "ehitasin oma standard sest niimoodi tahtsin".

Toetatud tagid (kavand, võib täiendada):

| Tag | Semantika | Implementatsioon |
|---|---|---|
| `[pause Nms]` | N millisekundit vaikust | `numpy.zeros` |
| `[slow]...[/slow]` | Aeglasem segment | Synthesizer `speed=0.85` |
| `[fast]...[/fast]` | Kiirem segment | Synthesizer `speed=1.15` |
| `[high]...[/high]` | Kõrgem pitch segment | sox `pitch +200` |
| `[low]...[/low]` | Madalam pitch segment | sox `pitch -200` |
| `[soft]...[/soft]` | Vaiksem | numpy gain -6dB |
| `[loud]...[/loud]` | Valjem | numpy gain +3dB |
| `[as:speaker]...[/as]` | Vaheta kõneleja | Synthesizer eri `speaker` |

Tagid on **idempotentsed ja non-nesting** (lihtsuse mõttes — esimene iteratsioon).

## 6. Lahtised küsimused otsustajale

1. **Kas eelistad B (kohandatud) või A (SSML)?** Soovitus: B. Kui akadeemiline traditsiooniline narratiiv on olulisem kui token-kulu, siis A.
2. **Kas alustame kõikide tagidega või MVP-ga (ainult `[pause]`)?** Soovitus: alustada `[pause]`-ga + rate kontroll, lisada teised järk-järgult.
3. **Kuhu logime LLM-i poolt genereeritud markup'i?** Soovitus: `pipeline.py --log` lipu alla samasse JSONL-i mis muu telemetria.

## 7. Tagajärjed

**Kui valime B**:
- ~150 rida Pythonit + ~50 rida teste
- ~2-3h töö
- LLM süsteempromptis ~5-8 näidet markup'i kasutusest
- Pipeline.py-sse uus moodul `expressive_synth.py`
- Lõputöösse eraldine alapeatükk (3.X) "Ekspressiivse vastuse markup"

**Kui valime A**:
- ~300 rida Pythonit + ~80 rida teste
- ~4-5h töö
- LLM süsteempromptis ~10 SSML näidet
- Lisa parse error käsitlus
- Lõputöösse rohkem standardile viitamist

**Kui valime D (status quo)**:
- 0 lisakulu
- Lõputöösse "Edasiarendus" peatükki üks lõik
- v2 sox karakter jääb staatiliseks

## 8. Viited

- W3C Speech Synthesis Markup Language 1.1: https://www.w3.org/TR/speech-synthesis11/
- TartuNLP Neurokõne API SSML kasutus: `wake-word/data/collection/generate_neurokone_ssml_positives.py`
- Coqui TTS SSML diskussioon (kunagi merge'imata): https://github.com/coqui-ai/TTS/issues/752
- Empiirilised mõõtmised: see ADR § 4
