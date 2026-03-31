# Kasutajatestide plaan

**Kuupäev**: 2026-03-31 (planeerimine)
**Testid planeeritud**: TalTech õpiõhtu / ürituse raames
**Osalejate arv**: ~20 inimest (sõbrad, tuttavad, kaasüliõpilased)
**Aeg inimese kohta**: ~6-7 minutit

## Eesmärk

Mõõta täieliku eestikeelse voice pipeline'i (wake word → STT → LLM → action) toimimist reaalsete kasutajatega reaalses keskkonnas. Fookus ei ole ainult wake word, vaid **end-to-end kasutajakogemus**.

## Kaasaskantav demo setup

### Hardware

| Seade | Roll |
|-------|------|
| MacBook Pro M1 Pro 32GB | HA server, STT, LLM, WiFi AP |
| iPhone (USB tether) | Interneti tagavara (kui vaja) |
| ESP32 + mikrofon | Wake word satellite |
| WiFi pirn (värviline) | Kontrollitav lõppseade |

### Software stack (MacBook Docker)

```
MacBook Pro
├── WiFi AP (macOS Internet Sharing)
├── Home Assistant (Docker)
├── Kiirkirjutaja STT (Docker, ~3GB RAM)
├── Ollama + Gemma 3 12B (lokaalne LLM, ~8GB RAM)
├── Piper TTS (valikuline)
└── Logging service (telemetria)
```

Kogu RAM: ~12-15GB kasutusel, ~17GB vaba. OK.

### Võrk

MacBook loob WiFi AP (macOS Internet Sharing). ESP32 ja pirn ühenduvad sellega.
Kui vaja internetti (API fallback), siis iPhone USB tethering → MacBook jagab edasi WiFi kaudu.
Eesmärk on täielikult offline-võimeline setup.

## Test flow (~6.5 min per osaleja)

### 0:00 — Sissejuhatus (30s)

> "See on eestikeelne häälassistent. Äratussõna on **Kuule Kratt**.
> Siin on lamp mida saad juhtida. Ma annan sulle ülesandeid."

### 0:30 — Ülesanne 1: Lülita tuli põlema (30s)

Juhis osalejale: *"Lülita tuli põlema."*
Osaleja sõnastab ise kuidas tahab (peale wake wordi).

### 1:00 — Ülesanne 2: Muuda värvi (30s)

Juhis: *"Muuda tule värv oma lemmikvärvi."*

### 1:30 — Ülesanne 3: Küsi midagi (30s)

Juhis: *"Küsi süsteemilt midagi — mis iganes pähe tuleb."*

### 2:00 — Ülesanne 4: Lülita tuli kinni (30s)

Juhis: *"Lülita tuli kinni."*

### 2:30 — Ülesanne 5: False positive test (60s)

Juhis: *"Nüüd räägime niisama minutikese."*
Testija vestleb osalejaga tavaliselt. Mõõdame kas wake word vallandub kogemata.

### 3:30 — Ülesanne 6: Kaugustest (30s)

Juhis: *"Proovi nüüd siit kaugemalt (3m) tuli uuesti põlema panna."*

### 4:00 — Vaba katsetamine (60s)

*"Proovi vabalt mida tahad."*

### 5:00 — Küsimustik (90s)

QR-kood → Google Forms (telefonist)

## Küsimustik (Google Forms)

1. **Kui lihtne oli süsteemi kasutada?** (1-5 skaala)
2. **Kui kiiresti süsteem reageeris?** (1-5 skaala)
3. **Kui tihti tuli käsku korrata?** (ei kordagi / 1 kord / 2+ korda)
4. **Kuidas meeldib äratussõna "Kuule Kratt"?** (1-5 skaala)
5. **Kas eelistaksid mõnda muud äratussõna?** (jah / ei)
   - Kui jah, siis millist? *(vaba tekst)*
6. **Kas kasutaksid sellist süsteemi kodus?** (jah / võibolla / ei)
7. **Vaba kommentaar** *(valikuline)*

## Automaatne telemetria

Iga interaktsioon logitakse automaatselt:

```json
{
  "participant_id": "P01",
  "task": "color_change",
  "timestamp": "2026-04-XX T12:34:56",
  "wake_word_triggered": true,
  "wake_word_latency_ms": 320,
  "stt_transcript": "kuule kratt tee tuli siniseks",
  "stt_latency_ms": 1100,
  "llm_intent": "light.turn_on(color=blue)",
  "llm_latency_ms": 850,
  "action_executed": true,
  "e2e_latency_ms": 2270,
  "attempts": 1
}
```

### Logimise implementatsioon

TODO: Selgitada välja kust HA voice pipeline'is timestampe kätte saab:
- Wake word activation event
- STT start/end
- Intent/LLM processing start/end
- Action execution

## Mõõdikud lõputöö jaoks

### Kvantitatiivsed (automaatsest logist)
- Wake word activation rate (% ülesannetest kus esimese katsega töötas)
- False positive rate (ülesanne 5 ajal)
- Keskmine E2E latency (ms)
- STT accuracy (transcript vs tegelik lausung)
- Intent parsing accuracy (% kus LLM sai õigesti aru)
- Kauguse mõju activation rate'ile

### Kvalitatiivsed (küsimustikust)
- Kasutusmugavuse skoor (1-5)
- Reageerimiskiiruse tajumine (1-5)
- Äratussõna meeldivus (1-5)
- Alternatiivsete äratussõnade kogu
- Koduse kasutamise valmisoleku jaotus

## Eetika ja nõusolek

- [ ] Osalejad annavad suulise nõusoleku enne testi
- [ ] Selgitada mida logitakse
- [ ] Audio salvestatakse ainult opt-in korras (eraldi nõusolek)
- [ ] Andmed pseudonümiseeritud (P01, P02, ...)
- [ ] GDPR-konformne: osaleja saab paluda oma andmete kustutamist

## Avatud küsimused

- [ ] Millal täpselt test läbi viia? (milline õpiõhtu/üritus)
- [ ] Kas audio salvestada? (re-analüüsi võimalus vs privaatsus)
- [ ] Logging layer: custom skript vs HA sisene logging?
- [ ] LLM mudeli valik: Gemma 3 12B vs alternatiivid — testida eesti keele parsimist enne kasutajateste
- [ ] Piper TTS eesti hääl — kas on piisavalt hea või kasutada Google TTS API-t?
