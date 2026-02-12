# 🔥 Kratt - Eestikeelne Wake Word ja Voice Satellite Süsteem

> Bakalaureusetöö projekt - TalTech Informaatika 2025

**Autor**: Mattias
**Juhendaja**: Tanel Alumäe
**Kaitsmise aeg**: Suvi 2025

## 🎯 Projekti Eesmärk

Luua **esimene eestikeelne wake word mudel** "Kratt" ja integreerida see **Home Assistant**'iga kui täielik, privaatsust väärtustav helisatelliit süsteem.

### Miks See On Oluline?

Eesti keele jaoks puudub praegu:
- ❌ Custom wake word mudel
- ❌ Kerge kättesaadav voice satellite lahendus
- ❌ Täielikult lokaalne (privacy-first) voice assistant

See projekt täidab selle tühimiku.

### Peamised Panused (Contributions)

1. **Esimene eestikeelne wake word mudel** "Kratt"
2. **Data augmentation methodology** väikese keele jaoks
3. **Täielik Home Assistant integratsioon** (Wyoming protocol)
4. **ESP32 ja Raspberry Pi implementatsioonid**
5. **Opt-in data collection framework** (iterative improvement)

## 📁 Monorepo Struktuur

```
kratt/
├── README.md                          # See fail
├── CHANGELOG.md                       # Versioonid ja muudatused
├── LICENSE                            # Open source litsents (MIT/Apache 2.0)
│
├── docs/                              # Dokumentatsioon
│   ├── thesis/                        # LaTeX lõputöö
│   │   ├── main.tex
│   │   ├── chapters/
│   │   ├── figures/
│   │   └── references.bib
│   ├── architecture/                  # Süsteemi arhitektuur
│   │   ├── system-overview.md
│   │   ├── data-flow.md
│   │   └── diagrams/
│   ├── research/                      # Uurimismaterjalid
│   │   ├── literature-review.md
│   │   ├── related-work.md
│   │   └── experiments/
│   └── user-guide/                    # Kasutajajuhendid
│       ├── installation.md
│       ├── configuration.md
│       └── troubleshooting.md
│
├── wake-word/                         # Wake word mudel ja treening
│   ├── README.md
│   ├── data/                          # Data kogumine
│   │   ├── collection/                # Salvestamise skriptid
│   │   ├── raw/                       # Raw audio (gitignore)
│   │   ├── processed/                 # Töödeldud data
│   │   └── augmented/                 # Augmented data
│   ├── training/                      # Mudeli treenimine
│   │   ├── notebooks/                 # Jupyter notebooks
│   │   ├── scripts/                   # Training scripts
│   │   ├── configs/                   # Hyperparameters
│   │   └── experiments/               # Experiment tracking
│   ├── models/                        # Treenitud mudelid
│   │   ├── checkpoints/
│   │   ├── production/                # Production-ready models
│   │   └── benchmarks/                # Performance metrics
│   ├── evaluation/                    # Testimine ja hindamine
│   │   ├── test-sets/
│   │   ├── metrics/
│   │   └── reports/
│   └── deployment/                    # Model deployment
│       ├── onnx/                      # ONNX exports
│       └── tflite/                    # TFLite (ESP32)
│
├── hardware/                          # Hardware implementatsioonid
│   ├── esp32/                         # ESP32C3 Supermini
│   │   ├── esphome/                   # ESPHome configs
│   │   │   ├── voice-satellite.yaml
│   │   │   └── secrets.yaml.example
│   │   ├── firmware/                  # Custom firmware (if needed)
│   │   └── schematics/                # Wiring diagrams
│   └── raspberry-pi/                  # Raspberry Pi implementation
│       ├── wyoming/                   # Wyoming satellite
│       ├── systemd/                   # Service files
│       └── setup-scripts/
│
├── home-assistant/                    # Home Assistant integratsioon
│   ├── addon/                         # HA Add-on
│   │   ├── Dockerfile
│   │   ├── config.yaml
│   │   ├── run.sh
│   │   └── rootfs/
│   ├── custom-component/              # Custom integration (if needed)
│   └── configurations/                # Example configs
│       └── voice-pipeline.yaml
│
├── backend/                           # Backend teenused
│   ├── api/                           # REST API (opt-in data collection)
│   │   ├── src/
│   │   ├── tests/
│   │   └── docker-compose.yml
│   └── retraining/                    # Automated retraining pipeline
│       └── scripts/
│
├── tools/                             # Utility tools
│   ├── audio-processing/              # Audio utilities
│   ├── data-validation/               # Data quality checks
│   └── benchmarking/                  # Performance testing
│
├── experiments/                       # Varased eksperimendid (archive)
│   ├── whisper/                       # Old Whisper experiments
│   ├── kiirkirjutaja/                 # STT experiments
│   └── voip/                          # Phone interface experiments
│
├── scripts/                           # Helper scripts
│   ├── setup/                         # Initial setup
│   ├── build/                         # Build automation
│   └── deployment/                    # Deployment automation
│
└── tests/                             # Integration tests
    ├── unit/
    ├── integration/
    └── e2e/
```

## 🚀 Kiire Alustamine

### 1. Clone Repository

```bash
cd ~
git clone <your-repo-url> kratt
cd kratt
```

### 2. Setup Python Environment

```bash
# Python 3.9 (compatibility)
python3.9 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Salvesta Esimesed Näited

```bash
cd wake-word/data/collection
python record_samples.py --phrase "kratt" --count 20
```

### 4. Loe Dokumentatsiooni

- 📖 [Arhitektuur](docs/architecture/system-overview.md)
- 📖 [Uurimistöö](docs/research/literature-review.md)
- 📖 [Kasutajajuhend](docs/user-guide/installation.md)

## 🎓 Lõputöö Timeline

| Milestone | Tähtaeg | Staatus |
|-----------|---------|---------|
| ✅ Projekti setup | Nädal 1 | ✅ Done |
| 🔄 Data kogumine (10 inimest) | Nädal 2-3 | 🔄 In Progress |
| ⏳ Data augmentation | Nädal 4 | ⏳ Planned |
| ⏳ Initial model training | Nädal 5-6 | ⏳ Planned |
| ⏳ Raspberry Pi prototype | Nädal 7-8 | ⏳ Planned |
| ⏳ ESP32 implementation | Nädal 9-10 | ⏳ Planned |
| ⏳ HA Add-on development | Nädal 11-12 | ⏳ Planned |
| ⏳ User testing (20-30 users) | Nädal 13-14 | ⏳ Planned |
| ⏳ Opt-in collection pilot | Nädal 15-16 | ⏳ Optional |
| ⏳ Thesis writing | Nädal 17-20 | ⏳ Planned |
| ⏳ Defense preparation | Nädal 21-22 | ⏳ Planned |
| 🎯 Kaitsmine | Juuni 2025 | 🎯 Goal |

## 🏆 Eesmärgid

### Minimaalsed (Guaranteed)

- ✅ Töötav "Kratt" wake word mudel (>95% accuracy)
- ✅ Raspberry Pi + Home Assistant integratsioon
- ✅ 20+ kasutajaga user testing
- ✅ Published HA add-on
- ✅ Täielik dokumentatsioon

### Lisaeesmärgid (If Time Permits)

- 🎁 ESP32C3 implementation
- 🎁 Opt-in data collection framework
- 🎁 Multi-wake-word support ("Kuule Kratt")
- 🎁 Mobile app (data collection)
- 🎁 Published paper/blog post

## 🛠️ Tehnoloogiad

### Wake Word Detection
- **microWakeWord** - ESP32 (TFLite INT8)
- **openWakeWord** - Raspberry Pi (ONNX/PyTorch)
- **Data Augmentation**: audiomentations, pyroomacoustics

### Hardware
- **ESP32C3 Supermini** - €5, 400KB RAM, WiFi
- **Raspberry Pi 5** - Home Assistant host
- **INMP441** - I2S microphone

### Software Stack
- **Python 3.9** - Core development
- **TensorFlow/PyTorch** - Model training
- **ESPHome** - ESP32 firmware
- **Home Assistant** - Smart home platform
- **Wyoming Protocol** - Voice pipeline
- **Docker** - Containerization

### Existing Estonian STT
- **Kiirkirjutaja** (Tanel Alumäe) - 1s latency, 3GB RAM

## 📊 Metrics ja Success Criteria

### Model Performance
- **Accuracy**: >95% (wake word detection)
- **False Positive Rate**: <5%
- **False Negative Rate**: <5%
- **Latency**: <500ms (end-to-end wake word detection)

### System Performance
- **End-to-End Latency**: <2s (wake word → action)
- **Power Consumption**: <1W (ESP32 idle)
- **Memory Usage**: <150KB (ESP32 active)

### User Satisfaction
- **Usability Score**: >4/5
- **Setup Time**: <30min
- **Daily Active Usage**: Data collected during testing

## 🤝 Kaastöö ja Privaatsus

### Data Collection Ethics
- ✅ Opt-in ainult
- ✅ Anonümiseeritud
- ✅ GDPR compliant
- ✅ Selge privacy policy
- ✅ Õigus andmeid kustutada

### Open Source
- MIT/Apache 2.0 litsents
- Avalik GitHub/GitLab repo
- Community contributions oodatud
- Dokumenteeritud koodi standard

## 📞 Kontakt

- **Email**: mattiaslinholm@gmail.com
- **GitHub**: [your-github]
- **Discord**: [if relevant]

## 📄 Viited ja Tunnustused

### Key References
- microWakeWord: https://github.com/kahrendt/microWakeWord
- openWakeWord: https://github.com/dscripka/openWakeWord
- Kiirkirjutaja: https://github.com/alumae/kiirkirjutaja
- Home Assistant: https://www.home-assistant.io/

### Inspiratsioon
- Rhasspy (multilingual voice assistant)
- Mozilla Common Voice (crowdsourced speech data)
- ESPHome Voice Kit

---

**⚡ "Kuule Kratt!" - Esimene eestikeelne privaatne voice assistant**
