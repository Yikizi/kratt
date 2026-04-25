# CLAUDE.md - Context for Claude Code

**Project**: Kratt - Estonian Wake Word & Voice Satellite System
**Type**: Bachelor's Thesis - TalTech Informatics
**Author**: Mattias
**Timeline**: February 2025 - June 2026
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
1. 🎯 Wake word model evaluation (v16c ready, MoE consensus validated — sub-1 FAPH achieved)
2. ✅ User testing (20-30 participants, CRITICAL for thesis)
3. 📝 Thesis writing (chapters 1-2 drafted, 3-5 pending)
4. 🔌 Home Assistant integration polish
5. 📚 Comparative analysis (EuroEval LLM benchmarks done)

**Status**: See `docs/PROJECT_TODO.md` for detailed task breakdown.

**Important framing note**: before major planning or thesis-shaping work, also read `docs/research/agentic-thesis-positioning-and-shortcomings-2026-04-14.md`. It captures the current methodological weaknesses, thesis-positioning advice, and the role/limits of agentic engineering in this project.

## Technical Stack

- **Python 3.9** + **uv** (required for llvmlite/tensorflow compatibility)
- **microWakeWord** — TFLite INT8 models for ESP32 (~56KB)
- **openWakeWord** — ONNX models for Raspberry Pi (planned)
- **ESP32-S3 Korvo-2** — primary voice satellite hardware
- **Raspberry Pi 5** — Home Assistant + Kiirkirjutaja STT
- **TalTech HPC** — model training (SLURM)

## Wake Word

**"Kuule Kratt"** — two-word Estonian wake phrase.
- Estonian mythology reference (kratt creature)
- Distinctive phonetics, not in everyday speech
- Current best model: **v16c** (148KB, 100% recall + 100% hard neg rejection + FAPH 75)
- MoE consensus (Expert A + Expert B2) achieves **0.79 FAPH** @ 0.996/0.996

## Key References

- microWakeWord: https://github.com/kahrendt/microWakeWord
- openWakeWord: https://github.com/dscripka/openWakeWord
- Kiirkirjutaja: https://github.com/alumae/kiirkirjutaja
- Wyoming Protocol: https://github.com/rhasspy/wyoming

## Conventions

- Python: `snake_case.py`, configs: `kebab-case.yaml`, docs: `kebab-case.md`
- Thesis in Estonian, code/docs in English
- Commit messages: English, conventional commits
- All Python packages managed with `uv` (project-scoped)
- All workflow scripts must have a `kratt <name>` CLI wrapper (`cli/commands/kratt-*`)

### Model documentation (per-version)

Every model version in `wake-word/models/kuule-kratt-*/` MUST have:

1. **`NOTES.md` in the model's own directory** — hypothesis, delta from previous version, data, observed results, interpretation, next step. Discoverable when someone opens the model dir directly.
2. **Entry in `wake-word/docs/MODEL_LINEAGE.md`** — single chronological timeline of all versions. Same content, condensed.

This prevents confusion about whether a version was a new experiment, a re-run, or an ablation. Especially important for "orphan" models that would otherwise appear unexplained (e.g. v2 which looked like a duplicate of v1 but was actually a silence-trimming preprocessing experiment).

## Guidelines for Claude

- Focus on wake word — STT/TTS already exist, don't reinvent
- This is a bachelor's thesis — manageable scope over perfection
- Privacy-first: always consider GDPR/opt-in for voice data
- See `docs/PROJECT_TODO.md` for current task breakdown
- Read `docs/research/agentic-thesis-positioning-and-shortcomings-2026-04-14.md` before making broad methodological or thesis-direction proposals
- See sub-package CLAUDE.md files for area-specific context
