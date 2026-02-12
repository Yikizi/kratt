# STT Integration - Kiirkirjutaja INT8

Selles kaustas on dokumenteeritud **olemasolev eestikeelne STT süsteem**, mis töötab koostöös "Kratt" wake word'iga.

## 🔗 Kuidas See Sobib Kokku?

```
┌─────────────────────────────────────────────────────────┐
│              Täielik Voice Assistant Flow                │
└─────────────────────────────────────────────────────────┘

1. 🎤 Kasutaja:        "Kratt, lülita sisse elutoa valgus"
                       ↓
2. 🔊 Wake Word:       "Kratt" detected by wake word model
                       ↓ (Wake word mudel on SINU panus!)
                       ↓
3. 📡 Trigger:         Sends audio stream to Home Assistant
                       ↓
4. 🗣️  STT:            Kiirkirjutaja INT8 (see kaust!)
                       "lülita sisse elutoa valgus"
                       ↓
5. 🧠 Intent:          Home Assistant Conversation
                       Action: light.turn_on(entity_id=light.living_room)
                       ↓
6. ✅ Execute:         Lamp läheb põlema
                       ↓
7. 🔊 TTS:             "Elutoa valgus on sisse lülitatud"
```

## 📁 Struktu

ur

```
stt-integration/
├── README.md                           # See fail
├── kiirkirjutaja-source/              # Tanel Alumäe mudeli source
│   ├── DOKUMENTATSIOON.md             # Põhjalik dokumentatsioon
│   ├── QUICK_REFERENCE.md             # Kiirkäsud
│   ├── README.md                      # Originaal README
│   ├── main_wyoming_simple.py         # Wyoming server
│   ├── asr.py                         # ASR functions
│   ├── wyoming_handler.py             # Wyoming protocol
│   ├── Dockerfile.wyoming-int8        # Docker config
│   └── models/sherpa-int8/            # INT8 mudelid
├── docs/                              # Lisadokumentatsioon
│   ├── integration-guide.md           # Kuidas integreerida HA-ga
│   ├── performance-analysis.md        # Performance testid
│   └── comparison-with-whisper.md     # Whisper vs Kiirkirjutaja
└── configs/                           # Configuration files
    └── wyoming-config.yaml            # Wyoming seadistus
```

## 🎯 Sinu Lõputöö Kontekstis

### Olemasolev Töö (Tanel + Sina)
- ✅ **STT mudel**: TalTechNLP streaming-zipformer-transducer
- ✅ **INT8 kvantiseerimine**: Mudel optimeeritud Raspberry Pi jaoks
- ✅ **Wyoming integratsioon**: Töötab juba HA-ga
- ✅ **Performance**: 2-3x kiirem kui reaalajas, ~424MB RAM
- ✅ **Täpsus**: Parem kui FP32 mudel!

### Sinu Panus (Novel Contribution)
- 🎯 **Wake word mudel "Kratt"** ← MAIN CONTRIBUTION!
- 🎯 **Data augmentation methodology** väikese keele jaoks
- 🎯 **ESP32 implementation** (embedded optimiseerimine)
- 🎯 **User testing** (20-30 inimest)
- 🎯 **Complete system integration** (wake word + STT + HA)

## 📊 Kogu Süsteemi Performce

### Latency Breakdown

```
User: "Kratt, mis on kell?"

├─► Wake word detection:        200-500ms (ESP32/Pi)
│   └─► Sinu mudel!             [SINU TÖÖ]
│
├─► Network transmission:        20-50ms
│
├─► STT (Kiirkirjutaja INT8):   300-800ms
│   └─► Tanel mudel             [OLEMASOLEV]
│
├─► Intent parsing:              50-100ms
│   └─► Home Assistant
│
└─► TTS response:                500-1000ms
    └─► Piper TTS

TOTAL: ~1-2.5 sekundit (väga hea!)
```

### Ressursikasutus (Raspberry Pi 5)

```
Home Assistant Core:        ~500MB RAM, 10-20% CPU
Kiirkirjutaja INT8:         ~424MB RAM, 15-30% CPU (active)
                            ~277MB RAM, 0% CPU (idle)
Wake Word (openWakeWord):   ~100MB RAM, 5-10% CPU
────────────────────────────────────────────────────────
Total (active):             ~1GB RAM, 35-60% CPU
Available:                  ~7GB RAM, 40-65% CPU
```

Järeldus: Pi 5 saab suurepäraselt hakkama! 🎉

## 🔗 Viited Lõputöös

### Kuidas Viidata Sellele Tööle

**Background/Related Work chapter**:
```
Eesti keele jaoks on olemas mitmeid kõnetuvastuse lahendusi.
TalTech NLP grupp on välja töötanud streaming-zipformer-transducer
mudeli [Alumäe2023], mis on optimeeritud reaalajas transkribeerimiseks.
Käesoleva töö raames kasutame selle mudeli INT8 kvantiseeritud versiooni,
mis töötab tõhusalt Raspberry Pi 5 platvormil (~424MB RAM, RTF 0.3-0.5).

Wake word tuvastuse komponent, mis on käesoleva töö peamine panus,
integreerub selle olemasoleva STT süsteemiga läbi Home Assistanti
Wyoming protokolli.
```

**System Architecture chapter**:
```
Süsteemi STT komponent põhineb TalTechNLP streaming-zipformer mudelil,
mis on post-training quantization meetodil konverteeritud INT8 formaati.
Mudel kasutab Sherpa-ONNX inference library't ja on pakendatud Docker
konteinerisse. Kommunikatsioon Home Assistantiga toimub Wyoming protokolli
kaudu (TCP port 10300).

Meie töö fookuses olev wake word mudel aktiveerib selle STT süsteemi,
luues täieliku hands-free voice assistant'i eesti keele jaoks.
```

## 🎓 Lõputöö Peatükid Kus See Tuleb Sisse

1. **Sissejuhatus** (1.1 Probleem):
   - "...kusjuures eesti keele jaoks on STT lahendused juba olemas [Alumäe2023],
     kuid wake word tuvastus puudub..."

2. **Taust ja Eeltööd** (2.2 Eesti Keele Lahendused):
   - Detailne kirjeldus Kiirkirjutaja süsteemist
   - INT8 optimiseerimise tulemused
   - Võrdlus Whisper'iga (miks see on parem)

3. **Metoodika** (3.1 Süsteemi Arhitektuur):
   - Wake word → STT → Intent → TTS flow
   - Wyoming protokoll
   - Performance requirements

4. **Implementatsioon** (4.3 Home Assistant Integratsioon):
   - Kuidas wake word käivitab STT-d
   - Wyoming server konfiguratsioon
   - Voice pipeline setup

5. **Evalueerimine** (5.2 Süsteemi Performance):
   - End-to-end latency
   - Ressursikasutus
   - User experience metrics

## 🚀 Järgmised Sammud

### Sul on juba valmis:
- ✅ STT mudel töötab Pi peal
- ✅ Wyoming integratsioon töötab
- ✅ Performance on mõõdetud ja dokumenteeritud

### Sul on vaja teha (wake word pool):
- [ ] "Kratt" wake word mudeli treenimine
- [ ] Integreerida wake word'i HA voice pipeline'i
- [ ] Testida end-to-end flow
- [ ] User testing

### Integratsioon:
```yaml
# Home Assistant configuration.yaml
assist_pipeline:
  - name: "Eesti Kratt"
    language: et

    # SINU TÖÖ ↓
    wake_word_entity: wake_word.kratt

    # OLEMASOLEV ↓
    stt_engine: wyoming_stt.kiirkirjutaja_int8
    stt_language: et

    # HA BUILT-IN ↓
    conversation_engine: conversation.home_assistant
    tts_engine: tts.piper
    tts_language: et-EE
```

## 📄 Tsiteerimine

```bibtex
@misc{alumae2024kiirkirjutaja,
  author = {Alumäe, Tanel},
  title = {Kiirkirjutaja: Real-time Estonian Speech Recognition},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/alumae/kiirkirjutaja}
}

@misc{taltechnlp2024zipformer,
  author = {TalTech NLP Group},
  title = {Streaming Zipformer Transducer for Estonian and English},
  year = {2024},
  publisher = {HuggingFace},
  url = {https://huggingface.co/TalTechNLP/streaming-zipformer.et-en}
}
```

## 💡 Oluline Punkt Lõputöös

**Su lõputöö EI OLE "veel üks eesti keele STT"** - see on juba olemas ja töötab!

**Su lõputöö ON "esimene eestikeelne wake word mudel + täielik süsteem"**:
- Wake word mudel (novel)
- Data augmentation methodology (contribution)
- System integration (engineering)
- User validation (empirical)

STT osa on **supporting infrastructure**, mitte main contribution. See on täiesti OK ja isegi parem - näitab, et oskad kasutada existing work'i ja fokuseerida omale panusele!

---

**Kokkuvõte**: Sel sul on juba 50% süsteemist valmis. Nüüd keskendume wake word mudelile, mis on su peamine panus!
