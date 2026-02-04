# Wake Word Training - CORE CONTRIBUTION

**Context**: Oled `kratt/wake-word/` kaustas - see on **lõputöö peamine panus**.

## 🎯 Mis See On?

Siin toimub "Kratt" wake word mudeli:
- **Data kogumine** (10 inimest, 200+ samples)
- **Data augmentation** (synthetic data generation)
- **Mudeli treenimine** (microWakeWord + openWakeWord)
- **Evalueerimine** (accuracy, FPR, FNR)
- **Optimeerimine** (INT8 quantization)

## 📁 Kausta Struktuur

```
wake-word/
├── data/
│   ├── collection/          # Salvestamise skriptid
│   │   ├── record_samples.py
│   │   └── download_negatives.py
│   ├── raw/                 # Raw salvestused (gitignore)
│   ├── processed/           # Preprocessed + validated
│   └── augmented/           # Synthetic augmented data
│
├── training/
│   ├── notebooks/           # Jupyter explorations
│   ├── scripts/             # Training scripts
│   │   ├── train_microwakeword.py
│   │   └── train_openwakeword.py
│   ├── configs/             # Hyperparameters
│   └── experiments/         # MLflow/WandB tracking
│
├── models/
│   ├── checkpoints/         # Training checkpoints
│   ├── production/          # Final models
│   │   ├── kratt-microww-v1.0.0.tflite
│   │   └── kratt-openww-v1.0.0.onnx
│   └── benchmarks/          # Performance metrics
│
├── evaluation/
│   ├── test-sets/           # Hold-out test data
│   ├── metrics/             # ROC curves, confusion matrices
│   │   └── optimal_threshold.json
│   └── reports/             # Human-readable reports
│
└── deployment/
    ├── onnx/                # ONNX exports (Pi)
    └── tflite/              # TFLite INT8 (ESP32)
```

## 🎤 Wake Word Details

**Fraas**: "Kratt"
- Eesti müütoloogia creature
- Unikaalne, ei ole igapäevases kõnes
- Lühike aga distinctive (/kr/ + /tt/)

**Alternative**: "Kuule Kratt" (longer, more natural)

## 🔬 Training Approach

### Phase 1: Data Collection (CURRENT)
1. **Positive samples**: 10 inimest × 20 salvestust = 200 base
   - Erinevad häälekõrgused
   - Erinevad vahemaad (30cm - 3m)
   - Erinevad taustahelid

2. **Negative samples**:
   - Google Speech Commands v2 (~5000 samples)
   - Mozilla Common Voice Estonian
   - Generated noise/silence

3. **Augmentation**: 200 → 2000+ samples
   - Time stretching (0.8x - 1.2x)
   - Pitch shifting (±2 semitones)
   - Background noise addition
   - Room acoustics simulation

### Phase 2: Training
1. **microWakeWord** (ESP32):
   ```bash
   cd ../external-repos/microWakeWord
   python train.py \
       --positive_dir ../wake-word/data/processed/positive \
       --negative_dir ../wake-word/data/processed/negative \
       --model_name kratt \
       --epochs 50
   # Output: kratt_quantized.tflite (~200KB)
   ```

2. **openWakeWord** (Raspberry Pi):
   ```bash
   cd ../external-repos/openWakeWord/training
   python train_wake_word.py \
       --positive_dir ../../wake-word/data/processed/positive \
       --negative_dir ../../wake-word/data/processed/negative \
       --output_name kratt \
       --epochs 100
   # Output: kratt.onnx (~2-5MB)
   ```

### Phase 3: Evaluation
- Test set: 20% held out
- Metrics:
  - Accuracy > 95%
  - False Positive Rate < 5%
  - False Negative Rate < 5%
  - Optimal threshold finding (ROC curve)

### Phase 4: User Testing
- 20-30 participants
- Real-world usage (1-2 weeks each)
- Collect:
  - Quantitative: FP/FN rates, latency
  - Qualitative: usability, satisfaction

## 🔗 Integration Points

### With STT (../stt-integration/)
```
Wake Word Detection → Audio Stream → Kiirkirjutaja INT8 → Text
```

### With Hardware (../hardware/)
- ESP32: TFLite model (~200KB)
- Raspberry Pi: ONNX model (~2-5MB)

### With Home Assistant (../home-assistant/)
- Wyoming protocol
- Voice pipeline configuration

## 📊 Success Metrics

### Technical
- **Accuracy**: >95% on test set
- **Latency**: <500ms wake word detection
- **Memory**: <150KB RAM (ESP32), <100MB (Pi)
- **False Positives**: <1 per hour (idle)
- **False Negatives**: <5% (when spoken)

### User Experience
- Setup time: <30 minutes
- Activation reliability: >90%
- User satisfaction: >4/5

## ⚠️ Common Pitfalls to Avoid

1. **Overfitting**: Use proper train/val/test split
2. **Data leakage**: Keep test set completely separate
3. **Threshold tuning**: Don't optimize on test set!
4. **Augmentation balance**: Don't over-augment, keep real samples
5. **Platform differences**: Test on actual hardware (ESP32/Pi), not desktop

## 🛠️ Tools and Dependencies

```bash
# Already in venv
pip install sounddevice soundfile librosa audiomentations
pip install tensorflow  # For training
pip install onnx onnxruntime  # For openWakeWord
```

## 📝 Documentation Requirements

For thesis:
- Data collection methodology
- Augmentation techniques and rationale
- Model architecture choices
- Training hyperparameters
- Evaluation metrics and results
- Comparison: microWakeWord vs openWakeWord
- User testing protocol and results

## 🎯 Current Priority

**IMMEDIATE**: Data collection
- Recruit 10 people
- Set up recording environment
- Collect 200 base samples
- Validate audio quality

**NEXT**: Data augmentation
- Implement augmentation pipeline
- Generate 2000+ samples
- Split train/val/test

**THEN**: Training
- Train both models
- Evaluate and compare
- Iterate if needed

---

**Remember**: This is your MAIN CONTRIBUTION. Take time to do it properly. Document everything!
