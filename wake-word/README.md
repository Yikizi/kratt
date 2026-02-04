# Wake Word Training - "Kratt"

See on lõputöö **peamine panus** - esimene eestikeelne wake word mudel!

## 🚀 Kiire Alustamine

### 1. Setup Python Environment
```bash
cd ~/kratt/wake-word

# Python 3.9 (compatibility)
python3.9 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Salvesta Positive Samples
```bash
cd data/collection
python record_samples.py --phrase "kratt" --count 20
```

### 3. Laadi Negative Samples
```bash
python download_negatives.py
```

### 4. Treeni Mudel

#### Raspberry Pi (openWakeWord)
```bash
cd ../../external-repos/openWakeWord/training
python train_wake_word.py \
    --positive_dir ../../wake-word/data/processed/positive \
    --negative_dir ../../wake-word/data/processed/negative \
    --output_name kratt \
    --epochs 100 \
    --output_dir ../../wake-word/models/production/
```

#### ESP32 (microWakeWord)
```bash
cd ../../external-repos/microWakeWord
python generate_features.py \
    --positive_dir ../wake-word/data/processed/positive \
    --negative_dir ../wake-word/data/processed/negative \
    --output_dir ../wake-word/training/features/

python train.py \
    --feature_dir ../wake-word/training/features/ \
    --output_dir ../wake-word/models/production/ \
    --model_name kratt \
    --epochs 50
```

### 5. Testi Mudelit
```bash
cd evaluation
python test_model.py \
    --model ../models/production/kratt.onnx \
    --positive-dir ../data/processed/positive \
    --negative-dir ../data/processed/negative
```

## 📊 Data Collection Goals

- **Target**: 10 inimest × 20 salvestust = 200 base samples
- **Augmentation**: 200 → 2000+ samples
- **Negative**: 5000+ samples (Speech Commands + generated)

## 📁 Directory Structure

```
wake-word/
├── data/
│   ├── collection/          # Scripts
│   │   ├── record_samples.py
│   │   └── download_negatives.py
│   ├── raw/                 # Raw recordings (gitignore)
│   ├── processed/           # Validated + normalized
│   │   ├── positive/
│   │   └── negative/
│   └── augmented/           # Synthetic data
├── training/
│   ├── scripts/
│   ├── configs/
│   └── experiments/
├── models/
│   ├── checkpoints/
│   ├── production/          # Final models
│   └── benchmarks/
├── evaluation/
│   ├── test_model.py
│   ├── test-sets/
│   └── metrics/
└── deployment/
    ├── onnx/
    └── tflite/
```

## 🎯 Success Metrics

- Accuracy: >95%
- False Positive Rate: <5%
- False Negative Rate: <5%
- Latency: <500ms

## 📝 Documentation

See CLAUDE.md for detailed context and workflow.

Vaata ka:
- `docs/thesis/` - LaTeX lõputöö
- `hardware/` - Deployment ESP32/Pi
- `home-assistant/` - HA integratsioon
