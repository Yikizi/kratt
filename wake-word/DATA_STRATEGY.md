# Data Collection Strategy - Revised (Iterative Approach)

**Updated**: 2026-02-04
**Status**: Phase 1 in progress

## 🎯 Philosophy: Lean Start, Iterate Based on Results

Rather than committing to extensive manual data collection upfront, we adopt an **iterative, evidence-based approach**:

1. Start with minimal viable dataset
2. Train and evaluate
3. Expand ONLY if needed

This aligns with modern ML engineering best practices and manages thesis timeline risk.

## 📊 Three-Phase Strategy

### Phase 1: MVP Dataset (2-3 weeks) - IN PROGRESS

**Goal**: Achieve >95% accuracy with minimal data collection effort.

#### Data Sources:

**1. Neurokõne Synthetic (Target: 1000-3000 samples)**
- **Status**: Awaiting API access from TartuNLP
- **Backup**: Self-host via Docker OR eSpeak NG
- 6 speakers × multiple variations
- High-quality neural TTS

**2. Author's Voice (Target: 50-100 samples)**
- **Status**: Ready to start
- **Tool**: `record_samples.py`
- Quick to collect (1-2 hours)
- Provides real-world baseline

**3. Traditional Augmentation (Target: 1000-2000 samples)**
- Time stretching (0.8x - 1.2x)
- Pitch shifting (±2 semitones)
- Background noise addition
- Room acoustics simulation

**Total Phase 1**: 2000-5000 positive samples

#### Success Criteria:
```
IF test accuracy > 95% AND false positive rate < 5%:
    → PROCEED to deployment (Phase 3)
ELSE:
    → Analyze failure modes
    → PROCEED to Phase 2 (data expansion)
```

### Phase 2: Expansion (2-3 weeks) - CONDITIONAL

**Triggered ONLY if Phase 1 insufficient.**

**Goal**: Address specific weakness areas identified in Phase 1 evaluation.

#### Expansion Strategies:

**A. Targeted Real Data Collection**
- Recruit 5-10 additional speakers
- Focus on demographics underrepresented in Phase 1
- 20 recordings per person
- Total: +100-200 real samples

**B. Enhanced Synthetic Generation**
- If Neurokõne unavailable: explore other Estonian TTS
- Generate more variations (speeds, intonations)
- Total: +1000-2000 synthetic samples

**C. Negative Data Enhancement**
- Analyze false positives from Phase 1
- Add similar-sounding Estonian words
- Add more ambient noise variations

#### Re-evaluation:
```
Retrain model with expanded dataset
IF accuracy > 95%:
    → PROCEED to deployment
ELSE:
    → Deep dive analysis (may indicate model architecture issue)
```

### Phase 3: Deployment & User Testing (3-4 weeks)

**Prerequisite**: Model accuracy >95% from Phase 1 or 2.

- Deploy to Raspberry Pi (openWakeWord)
- Deploy to ESP32 (microWakeWord)
- Integrate with Home Assistant
- User testing: 20-30 participants, 1-2 weeks each
- Collect real-world performance data
- Fine-tune thresholds based on feedback

### Phase 4: Continuous Improvement (Optional)

**Post-thesis, if time permits:**

- Implement opt-in data collection
- Retrain with real-world data
- Release updated model

---

## 🔄 Current Status

### ✅ Completed
- [x] Project structure setup
- [x] Script development (record, download, test)
- [x] Neurokõne API investigation
- [x] Strategy documentation

### 🔄 In Progress
- [ ] Neurokõne API access (awaiting Tanel response)
- [ ] Author voice recording (50-100 samples)
- [ ] eSpeak NG backup testing

### ⏳ Upcoming
- [ ] Data augmentation pipeline
- [ ] Phase 1 model training
- [ ] Evaluation and decision point

---

## 📈 Advantages of This Approach

### 1. Risk Management
- Don't waste weeks collecting data if synthetic alone suffices
- Early validation of approach feasibility
- Multiple fallback options

### 2. Resource Efficiency
- Minimize volunteer burden (Phase 2 only if needed)
- Optimize time spent on data vs other thesis components
- Focus effort where it matters most

### 3. Thesis Value
- Demonstrates scientific method (hypothesis → test → iterate)
- Shows practical ML engineering skills
- Documents decision-making process
- Comparison of data sources (real vs synthetic)

### 4. Agile Methodology
- Rapid prototyping
- Evidence-based decision making
- Flexible adaptation to results

---

## 🎓 Thesis Documentation

Each phase will be documented in thesis:

**Chapter 3: Methodology**
```
3.2 Data Collection Strategy

3.2.1 Iterative Approach Rationale
  - Why lean start vs exhaustive upfront collection
  - Risk management in thesis timeline
  - Agile methodology in ML research

3.2.2 Phase 1: Minimum Viable Dataset
  - Synthetic generation (Neurokõne)
  - Author recordings
  - Traditional augmentation
  - Total: 2000-5000 samples

3.2.3 Evaluation Checkpoint
  - Success criteria (>95% accuracy)
  - Decision framework
  - Analysis of results

3.2.4 Phase 2: Conditional Expansion (if applicable)
  - Triggers for expansion
  - Targeted recruitment
  - Enhanced synthetic generation
  - Results comparison

3.2.5 Comparison of Data Sources
  - Real vs Synthetic performance
  - Quality vs Quantity trade-offs
  - Recommendations for Estonian wake words
```

---

## 🚦 Decision Flowchart

```
START
  ↓
Generate Phase 1 Dataset
  ├─ Neurokõne synthetic (or backup)
  ├─ Author voice recordings
  └─ Traditional augmentation
  ↓
Train Initial Model
  ↓
Evaluate on Test Set
  ↓
Accuracy > 95%?
  ├─ YES → Deploy & User Test → DONE ✅
  └─ NO ↓
Analyze Failure Modes
  ├─ Insufficient data diversity?
  ├─ Specific demographic missing?
  └─ Model architecture limitation?
  ↓
Phase 2: Expand Dataset
  ├─ Recruit more speakers
  ├─ Enhanced synthetic
  └─ Targeted augmentation
  ↓
Retrain Model
  ↓
Evaluate Again
  ↓
Accuracy > 95%?
  ├─ YES → Deploy & User Test → DONE ✅
  └─ NO → Deep Analysis (architecture?)
```

---

## 💾 Data Management

### Directory Structure
```
wake-word/data/
├── raw/
│   ├── author/              # Phase 1: Author recordings
│   ├── neurokone/           # Phase 1: Neurokõne synthetic
│   ├── espeak/              # Phase 1: Backup TTS
│   └── volunteers/          # Phase 2: Additional speakers (if needed)
├── processed/
│   ├── positive/
│   │   ├── phase1/          # ~2000-5000 samples
│   │   └── phase2/          # +100-2000 samples (if needed)
│   └── negative/
│       └── openwakeword/    # ~30k hours from openWakeWord
├── augmented/
│   ├── phase1/              # Augmented from phase 1
│   └── phase2/              # Augmented from phase 2 (if needed)
└── test/
    ├── positive/            # 20% held out
    └── negative/            # 20% held out
```

### Version Control
- Each phase tagged in git
- Model checkpoints saved with dataset version
- Reproducibility guaranteed

---

## 📞 Next Actions

### Immediate (This Week)
1. **Email Tanel** for Neurokõne API access
2. **Test eSpeak NG** as backup TTS
3. **Record 10 test samples** (own voice) to validate pipeline
4. **Prepare augmentation scripts**

### Short Term (Next 2 Weeks)
1. **Collect author voice**: 50-100 samples
2. **Generate synthetic** (Neurokõne or backup)
3. **Apply augmentation**
4. **Train Phase 1 model**

### Decision Point (Week 3)
1. **Evaluate model**
2. **IF >95%**: Proceed to deployment
3. **IF <95%**: Plan Phase 2 expansion

---

**Philosophy**: "Make data collection decisions based on evidence, not assumptions." 🎯
