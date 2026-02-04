# External Repositories

Selles kaustas on kolmandate osapoolte repositooriumid, mida me kasutame projekti käigus.

## 📚 Repositooriumid

### Wake Word Frameworks

#### microWakeWord
- **Repo**: https://github.com/kahrendt/microWakeWord
- **Otstarve**: ESP32 wake word training ja deployment
- **Model format**: TFLite INT8
- **Target**: ESP32-C3, ESP32-S3
- **Miks**: Optimeeritud embedded devices'idele, madal memory footprint (~50KB RAM)

**Kasutamine projekti's**:
```bash
cd kratt/external-repos/microWakeWord
python generate_features.py \
    --positive_dir ../../wake-word/data/processed/positive \
    --negative_dir ../../wake-word/data/processed/negative \
    --output_dir ../../wake-word/training/features/

python train.py \
    --feature_dir ../../wake-word/training/features/ \
    --output_dir ../../wake-word/models/production/ \
    --model_name kratt \
    --epochs 50
```

#### openWakeWord
- **Repo**: https://github.com/dscripka/openWakeWord
- **Otstarve**: Raspberry Pi wake word training
- **Model format**: ONNX / PyTorch
- **Target**: Raspberry Pi, Desktop, Server
- **Miks**: Täpsem kui microWakeWord, sobib Pi ressurssidega

**Kasutamine projekti's**:
```bash
cd kratt/external-repos/openWakeWord/training
python train_wake_word.py \
    --positive_dir ../../wake-word/data/processed/positive \
    --negative_dir ../../wake-word/data/processed/negative \
    --output_name kratt \
    --epochs 100 \
    --output_dir ../../wake-word/models/production/
```

### Varasem Töö (Archive)

#### iaib-proto
- **Originaal**: ~/agents/loputoo/iaib-proto
- **Periood**: Oktoober 2025 - Jaanuar 2026
- **Fookus**: Esialgsed uuringud eesti keele voice assistant'i kohta
- **Olulised tulemused**:
  - Whisper liiga aeglane (latentsus >2s)
  - Kiirkirjutaja sobib paremini (~1s latentsus)
  - Wyoming protokoll sobib HA integratsiooniks
  - Phone/VoIP lähenemine keeruline

**Millal kasutada**:
- Literature review (mida on varem uuritud)
- Architecture decisions (miks valiti teatud tehnoloogiad)
- Mitte viimistletud kood (archive ainult)

## 🔄 Update Strategy

### Kui uuendada?

**microWakeWord ja openWakeWord**:
```bash
cd kratt/external-repos/microWakeWord
git pull origin main

cd kratt/external-repos/openWakeWord
git pull origin main
```

**⚠️ Hoiatus**: Kui framework uuendub, võib see mõjutada training pipeline'i. Testi alati pärast uuendamist!

### Versioonid

Dokumenteeri, millise versiooniga töötad:

```bash
# Kontrolli versioone
cd kratt/external-repos/microWakeWord
git log -1 --format="%H %ai %s"

cd kratt/external-repos/openWakeWord
git log -1 --format="%H %ai %s"
```

Kirjuta need üles lõputöö reprodutseeritavuse jaoks:
```
microWakeWord: commit abc123... (2026-02-04)
openWakeWord: commit def456... (2026-02-04)
```

## 📝 Lõputöös Tsiteerimine

### microWakeWord
```bibtex
@misc{kahrendt2024microwakeword,
  author = {Kahrendt, Kevin},
  title = {microWakeWord: Wake Word Detection for Embedded Systems},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/kahrendt/microWakeWord}
}
```

### openWakeWord
```bibtex
@misc{scripka2024openwakeword,
  author = {Scripka, David},
  title = {openWakeWord: An Open-Source Wake Word Detection Framework},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/dscripka/openWakeWord}
}
```

## 🔗 Seos Sinu Tööga

```
┌───────────────────────────────────────────────────────┐
│                   Sinu Lõputöö                         │
├───────────────────────────────────────────────────────┤
│                                                        │
│  1. Data Collection (wake-word/data/)                 │
│     ├─► Record samples: 10 people × 20 recordings     │
│     └─► Download negatives: Speech Commands          │
│                                                        │
│  2. Data Processing (wake-word/training/)             │
│     ├─► Augmentation: pitch/speed/noise              │
│     └─► Feature extraction                            │
│                                                        │
│  3. Model Training                                     │
│     ├─► [microWakeWord] ◄─ See repo!                 │
│     │   └─► TFLite INT8 (ESP32)                      │
│     └─► [openWakeWord] ◄─ See repo!                  │
│         └─► ONNX (Raspberry Pi)                       │
│                                                        │
│  4. Deployment (hardware/*)                            │
│     ├─► ESP32 (ESPHome + TFLite)                     │
│     └─► Raspberry Pi (Python + ONNX)                 │
│                                                        │
│  5. Integration (home-assistant/)                      │
│     └─► Wyoming protocol + HA Voice Pipeline         │
│                                                        │
│  6. Evaluation (wake-word/evaluation/)                │
│     └─► User testing: 20-30 participants             │
│                                                        │
└───────────────────────────────────────────────────────┘
```

## ⚠️ Git .gitignore

Need repositooriumid on suuremad (100MB+). Lisa `.gitignore`'i:

```gitignore
# External repos - clone separately
external-repos/microWakeWord/
external-repos/openWakeWord/

# Keep only archive
!external-repos/iaib-proto/
```

Või kasuta git submodules:

```bash
cd ~/kratt
git submodule add https://github.com/kahrendt/microWakeWord.git external-repos/microWakeWord
git submodule add https://github.com/dscripka/openWakeWord.git external-repos/openWakeWord
```

## 📦 Setup Uues Masinas

```bash
# Clone main repo
git clone <your-kratt-repo> kratt
cd kratt

# Clone external frameworks
cd external-repos
git clone https://github.com/kahrendt/microWakeWord.git
git clone https://github.com/dscripka/openWakeWord.git

# Install dependencies
cd microWakeWord
pip install -r requirements.txt

cd ../openWakeWord
pip install -r requirements.txt
```

## 🎓 Miks Eraldi Kaust?

1. **Selgus**: Eristab sinu töö kolmandate osapoolte koodist
2. **Versioonihaldus**: Saad uuendada frameworks'e sõltumatult
3. **Litsentsid**: Erinevad litsentsid (microWakeWord: MIT, openWakeWord: Apache 2.0)
4. **Reprodutseeritavus**: Teised saavad sinu tulemusi korrata
5. **Lõputöö**: Selge, mis on sinu panus vs olemasolevad tööriistad

---

**Põhimõte**: Kasutame olemasolevaid tööriistu targalt, aga meie **panus** on eestikeelne "Kratt" mudel ja täielik süsteemi integratsioon!
