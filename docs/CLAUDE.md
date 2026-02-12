# Documentation

**Context**: Oled `kratt/docs/` kaustas - kõik projekti dokumentatsioon.

## 📁 Struktuur

```
docs/
├── thesis/                  # LaTeX lõputöö
│   ├── main.tex
│   ├── chapters/
│   │   ├── 01-sissejuhatus.tex
│   │   ├── 02-taust.tex
│   │   ├── 03-metoodika.tex
│   │   ├── 04-implementatsioon.tex
│   │   ├── 05-evalueerimine.tex
│   │   └── 06-kokkuvote.tex
│   ├── figures/
│   ├── appendices/
│   └── references.bib
│
├── architecture/            # Süsteemi disain
│   ├── system-overview.md
│   ├── data-flow.md
│   ├── component-diagrams/
│   └── decision-records/    # ADR (Architecture Decision Records)
│
├── research/                # Uurimistöö
│   ├── literature-review.md
│   ├── related-work.md
│   ├── experiments/
│   │   ├── whisper-vs-kiirkirjutaja.md
│   │   └── wake-word-frameworks.md
│   └── datasets.md
│
└── user-guide/              # Kasutajajuhendid
    ├── installation.md
    ├── configuration.md
    ├── troubleshooting.md
    └── contributing.md
```

## 🎓 Thesis Structure (Tentative)

### 1. Sissejuhatus (Introduction) ~5 lehte
- **Probleem**: Puudub eestikeelne wake word
- **Eesmärk**: Esimene "Kratt" mudel + täielik süsteem
- **Panus**: Wake word + data augmentation + integration
- **Struktuur**: Ülejäänud peatükkide ülevaade

### 2. Taust ja Eeltööd (Background) ~15 lehte
- **2.1 Wake Word Detection Teooria**
  - Kuidas töötab
  - CNN/RNN/Transformer arhitektuurid
  - Keyword spotting vs wake word

- **2.2 Olemasolevad Lahendused**
  - Google Assistant ("Ok Google")
  - Amazon Alexa
  - Apple Siri ("Hey Siri")
  - Rhasspy, Mycroft

- **2.3 Väikese Keele Väljakutsed**
  - Piiratud training data
  - Transfer learning võimalused
  - Data augmentation techniques

- **2.4 Eesti Keele Lahendused**
  - Kiirkirjutaja (Tanel Alumäe)
  - INT8 optimiseerimine
  - Miks wake word puudub

### 3. Metoodika (Methodology) ~20 lehte
- **3.1 Süsteemi Arhitektuur**
  - Wake word → STT → Intent → TTS
  - Wyoming protocol
  - Component diagram

- **3.2 Data Kogumine**
  - Participants: 10 inimest
  - Recording protocol: 20× per person
  - Validation criteria
  - Ethical considerations (GDPR, consent)

- **3.3 Data Augmentation**
  - Time stretching (0.8-1.2x)
  - Pitch shifting (±2 semitones)
  - Background noise addition
  - Room acoustics simulation
  - Expansion: 200 → 2000+ samples

- **3.4 Model Training**
  - microWakeWord (ESP32)
    - Architecture
    - Hyperparameters
    - INT8 quantization
  - openWakeWord (Raspberry Pi)
    - Architecture
    - Hyperparameters
  - Training procedure
  - Validation strategy

- **3.5 Evalueerimine**
  - Metrics: Accuracy, FPR, FNR, ROC-AUC
  - Test set (20% held-out)
  - Threshold optimization
  - Cross-validation

### 4. Implementatsioon (Implementation) ~20 lehte
- **4.1 Wake Word Mudel**
  - Training results
  - Model comparison (microWW vs openWW)
  - Optimization for embedded

- **4.2 Hardware Implementations**
  - ESP32C3 Supermini
    - ESPHome configuration
    - Memory optimization
    - Power consumption
  - Raspberry Pi
    - Wyoming server
    - Python implementation

- **4.3 Home Assistant Integratsioon**
  - Voice pipeline setup
  - Wyoming protocol integration
  - Configuration examples

- **4.4 End-to-End Flow**
  - Wake word → Kiirkirjutaja → HA
  - Latency breakdown
  - Error handling

### 5. Evalueerimine (Evaluation) ~15 lehte
- **5.1 Tehnilised Testid**
  - Accuracy metrics
  - False positive/negative analysis
  - Latency measurements
  - Resource usage (CPU, RAM, power)

- **5.2 Võrdlev Analüüs**
  - microWakeWord vs openWakeWord
  - ESP32 vs Raspberry Pi
  - Comparison with commercial solutions

- **5.3 Kasutajatestid**
  - 20-30 participants
  - Real-world usage (1-2 weeks)
  - Usability questionnaire
  - Qualitative feedback
  - Issues discovered

- **5.4 Piirangud**
  - Data set size limitations
  - Single speaker variability
  - Background noise sensitivity
  - Latency in different scenarios

### 6. Arutelu ja Kokkuvõte (Discussion & Conclusion) ~10 lehte
- **6.1 Tulemuste Analüüs**
  - Did we achieve goals?
  - What worked well?
  - What could be improved?

- **6.2 Praktiline Väärtus**
  - Home Assistant add-on
  - Community impact
  - Privacy benefits

- **6.3 Edasiarendus**
  - Multi-wake-word support
  - Continuous learning (opt-in)
  - More languages
  - Better models

- **6.4 Kokkuvõte**
  - Main contributions
  - Lessons learned
  - Final thoughts

**Total: ~85-90 lehte** (ilma lisadeta)

## 📐 Architecture Documentation

### System Overview
```
User → Microphone → Wake Word Detection → Audio Stream →
    → STT (Kiirkirjutaja) → Intent (HA) → Action → TTS → Speaker
```

### Component Diagram
```
┌─────────────────────────────────────────────────┐
│              Home Assistant                      │
│  ┌──────────────────────────────────────────┐  │
│  │      Voice Assistant Pipeline             │  │
│  │  ┌──────┐ ┌─────┐ ┌──────┐ ┌─────┐      │  │
│  │  │ Wake │→│ STT │→│Intent│→│ TTS │      │  │
│  │  │ Word │ │     │ │      │ │     │      │  │
│  │  └──┬───┘ └─────┘ └──────┘ └─────┘      │  │
│  └─────┼──────────────────────────────────── │  │
└────────┼─────────────────────────────────────┘
         │
    ┌────┴────┐
    │ Wyoming │ (TCP/10400)
    └────┬────┘
         │
    ┌────┴────────┐
    │ ESP32 / Pi  │
    │ Wake Word   │
    │  "Kratt"    │
    └─────────────┘
```

## 📚 Literature Review

Key papers to cite:
- Zipformer architecture (streaming transducers)
- INT8 quantization for ASR
- Wake word detection (keyword spotting)
- Data augmentation for audio
- Privacy-preserving voice assistants

## 📝 Writing Guidelines

### Language
- **Thesis**: Estonian (TalTech requirement)
- **Code/README**: English (wider audience)
- **Comments**: English (industry standard)

### Citations
Use BibTeX in `references.bib`:
```bibtex
@misc{alumae2024kiirkirjutaja,
  author = {Alumäe, Tanel},
  title = {Kiirkirjutaja: Real-time Estonian Speech Recognition},
  year = {2024},
  url = {https://github.com/alumae/kiirkirjutaja}
}
```

### Figures
- High resolution (300 DPI for print)
- Clear labels in Estonian
- Caption describes what reader should see
- Reference in text: "Joonis 3.1 näitab..."

### Code Listings
```latex
\begin{lstlisting}[language=Python, caption=Wake word detection]
def detect_wake_word(audio):
    features = extract_mfcc(audio)
    prediction = model.predict(features)
    return prediction > threshold
\end{lstlisting}
```

## 🎯 Documentation TODO

- [ ] Write ülesandepüstitus (thesis proposal)
- [ ] Complete literature review
- [ ] Document data collection protocol
- [ ] Write architecture decision records
- [ ] Create system diagrams (draw.io / Mermaid)
- [ ] User testing protocol and forms
- [ ] Installation guide for users
- [ ] Troubleshooting guide

## 🔗 Useful Links

- TalTech thesis template: https://www.taltech.ee/teadus/doktorantuur/doktoritoo/
- LaTeX help: https://www.overleaf.com/learn
- Diagrams: https://app.diagrams.net/
- Citation manager: Zotero, Mendeley

---

**Remember**: Start writing early! Don't wait until implementation is done. Document as you go.
