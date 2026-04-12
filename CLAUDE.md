# CLAUDE.md - Context for Claude Code

**Project**: Kratt - Estonian Wake Word & Voice Satellite System
**Type**: Bachelor's Thesis - TalTech Informatics
**Author**: Mattias
**Timeline**: February - June 2025
**Language**: Estonian (thesis), English (code/docs)

## 🎯 Project Overview

Building the **first Estonian wake word model** "Kratt" and integrating it with Home Assistant as a complete, privacy-first voice satellite system.

### Core Contributions
1. Estonian wake word model with data augmentation methodology
2. Dual hardware implementation (ESP32C3 + Raspberry Pi)
3. Home Assistant add-on with Wyoming protocol
4. User testing with 20-30 participants
5. (Optional) Opt-in data collection framework

### Key Insight
The missing link in Estonian smart home voice control is the wake word detection. Good STT already exists (Kiirkirjutaja ONNX model running on user's Raspberry Pi 5).

## 🏗️ Repository Structure

```
kratt/                          # Monorepo root
├── docs/                       # Hooldatud projektidokumentatsioon
│   ├── thesis/                 # LaTeX thesis (Estonian)
│   ├── architecture/           # ADRs and system design
│   ├── research/               # Evaluation methodology, literature
│   ├── user-testing/           # Test plans, questionnaires
│   └── user-guide/             # Installation & usage
│
├── notes/                      # Tööpäevik: märkmed, katsed, visandid
│   ├── demos/                  # Demo session notes
│   └── experiments/            # Hardware/firmware experiment logs
│
├── wake-word/                  # CORE: Wake word training
│   ├── data/                   # Data collection & augmentation
│   ├── training/               # Scripts, configs, HPC submit
│   ├── models/                 # Trained models (.tflite + analysis)
│   ├── evaluation/             # Benchmarks, fuzzer, live testing
│   └── deployment/             # ONNX/TFLite exports
│
├── android/                    # False-trigger logger app (Kotlin)
│
├── hardware/                   # Hardware implementations
│   ├── esp32/                  # ESP32C3 firmware (microWakeWord)
│   └── raspberry-pi/           # Raspberry Pi (openWakeWord)
│
├── home-assistant/             # HA integration planning (CLAUDE.md blueprint)
│
├── stt-integration/            # Kiirkirjutaja STT configs
├── cli/                        # kratt CLI tool
├── scripts/                    # Build, demo, deployment utilities
├── docker/                     # Docker compose for demos
├── tools/                      # Benchmarking, data validation, LLM eval
└── external-repos/             # Vendored mirrors (gitignored)
```

## 📋 Current Phase: Evaluation & Thesis Writing (April 2026)

**Priority Order**:
1. 🎯 Wake word model evaluation (v12 trained, threshold tuning)
2. ✅ User testing (20-30 participants, CRITICAL for thesis)
3. 📝 Thesis writing (chapters 1-2 drafted, 3-5 pending)
4. 🔌 Home Assistant integration polish
5. 📚 Comparative analysis (EuroEval LLM benchmarks done)

**Status**: See `docs/PROJECT_TODO.md` for detailed task breakdown.

## 🛠️ Technical Stack

### Python Environment
- **Python 3.9** (required for llvmlite < 0.37)
- **uv** for dependency management
- Key packages: tensorflow, librosa, audiomentations, sounddevice

### Wake Word Frameworks
- **microWakeWord** - ESP32 (TFLite INT8, ~200KB)
- **openWakeWord** - Raspberry Pi (ONNX/PyTorch)

### Hardware
- **Raspberry Pi 5** - Home Assistant + STT (Kiirkirjutaja)
- **10× ESP32C3 Supermini** - Voice satellites (need INMP441 mics)
- **USB microphone** - Data collection

### Existing Infrastructure
- Home Assistant running on Pi 5
- Kiirkirjutaja STT (ONNX) in Docker (1s latency, 3GB RAM)

## 🎤 Wake Word Details

**Primary**: "Kratt"
- Single syllable but distinctive (/kr/ + /tt/)
- Estonian mythology reference (kratt creature)
- Not common in everyday speech
- Culturally relevant and marketable

**Alternative**: "Kuule Kratt" (longer, more natural)
- May train as separate model or variation

## 📊 Success Metrics

### Model Performance
- Accuracy: >95%
- False Positive Rate: <5%
- False Negative Rate: <5%
- Wake word detection latency: <500ms

### System Performance
- End-to-end latency: <2s (wake word → action)
- ESP32 power: <1W idle, <100mA active
- Memory: <150KB (ESP32), <100MB (Pi)

### Thesis Requirements
- 20-30 user testing participants
- Quantitative evaluation (metrics above)
- Qualitative feedback (usability, satisfaction)
- Working HA add-on (deployed to add-on store)

## 🚫 Common Pitfalls to Avoid

1. **Python Version**: Must use 3.9 (not 3.12/3.14) due to llvmlite dependencies
2. **Scope Creep**: Focus on wake word, not full STT (that already exists)
3. **Data Collection**: Start simple (10 people) with augmentation, not 100+ people
4. **Hardware**: Order I2S mics early (1-2 week delivery from China)
5. **Thesis Writing**: Start documenting early, not last 2 weeks

## 🔗 Key References

### Repositories
- microWakeWord: https://github.com/kahrendt/microWakeWord
- openWakeWord: https://github.com/dscripka/openWakeWord
- Kiirkirjutaja: https://github.com/alumae/kiirkirjutaja
- ESPHome: https://esphome.io/components/voice_assistant.html

### Datasets
- Google Speech Commands v2 (negative samples)
- Mozilla Common Voice Estonian (background speech)

### Protocols
- Wyoming Protocol: https://github.com/rhasspy/wyoming
- Home Assistant Voice: https://www.home-assistant.io/voice_control/

## 📁 File Organization Guidelines

### Naming Conventions
- Python: `snake_case.py`
- Config: `kebab-case.yaml`
- Docs: `kebab-case.md`
- Models: `kratt-v1.2.3-{date}.{ext}`

### Git Workflow
- Main branch: `main` (stable, deployable)
- Development: `dev` (active work)
- Features: `feature/descriptive-name`
- Experiments: `experiment/what-im-testing`

### Documentation
- All public docs in English (wider audience)
- Thesis in Estonian (TalTech requirement)
- Code comments: English
- Commit messages: English

## 🎓 Thesis Structure (Tentative)

1. **Sissejuhatus** (Introduction)
   - Probleem: Puudub eestikeelne wake word
   - Eesmärk: Esimene "Kratt" mudel
   - Panus: Data augmentation + HA integratsioon

2. **Taust ja Eeltööd** (Background)
   - Wake word detection teooria
   - Eelnevad lahendused (Google, Alexa, jne)
   - Eesti keele spetsiifika

3. **Metoodika** (Methodology)
   - Data kogumine ja augmentation
   - Mudeli arhitektuur
   - Treeningprotsess
   - Hardware optimiseerimine

4. **Implementatsioon** (Implementation)
   - Raspberry Pi lahendus
   - ESP32 portimine
   - Home Assistant integratsioon
   - Privacy framework

5. **Evalueerimine** (Evaluation)
   - Tehniline testimine (metrics)
   - Kasutajatestid (20-30 inimest)
   - Võrdlus baseline'idega

6. **Arutelu** (Discussion)
   - Tulemuste analüüs
   - Piirangud
   - Edasiarendus

7. **Kokkuvõte** (Conclusion)

## 🔄 Migration from Old Structure

The project started as `iaib-proto` in `~/agents/loputoo/`:
- Original focus: Full STT pipeline with phone interface
- Pivot: Wake word is the missing piece, STT already exists
- Migration: Archive old experiments, keep relevant research

**Old work to preserve**:
- ✅ Kiirkirjutaja experiments (docs/research/experiments/)
- ✅ Whisper latency tests (docs/research/experiments/)
- ✅ LaTeX thesis template (docs/thesis/)
- ✅ Architecture diagrams (docs/architecture/)

**Old work to deprecate**:
- ❌ Phone/VoIP approach (out of scope)
- ❌ Full STT implementation (already exists)

## 💡 Tips for Claude

- **Always check Python version** before suggesting packages
- **Prefer data augmentation** over collecting 1000s of samples
- **Focus on wake word**, don't drift into STT/TTS territory
- **Remember this is a bachelor's thesis** - manageable scope
- **User is experienced dev** - can handle technical details
- **Privacy is critical** - always consider GDPR/opt-in

## 🎯 Next Immediate Actions

1. Fix Python environment (3.9, uv sync)
2. Port wake word scripts from ~/wakeword to wake-word/
3. Create data collection plan (10 people, who/how/when)
4. Order I2S microphones for ESP32 (2-3 weeks delivery)
5. Link LaTeX thesis template from old repo
6. Archive old experiments properly

---

**Remember**: This is a focused project - "Kratt" wake word is THE contribution. Everything else is supporting infrastructure.
