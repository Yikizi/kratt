# Next Steps — April 2026

## Priority 1: Fix Training Fundamentals (Before Next Training Run)

### Augmentation (DONE — committed)
- PitchShift: 0.05 → 0.40 (speaker F0 diversity)
- SevenBandParametricEQ: 0.05 → 0.30 (mic diversity)
- AddBackgroundNoise: 0.0 → 0.50 (needs MUSAN noise paths)
- RIR: 0.0 → 0.30 (needs MIT IR paths)
- Background/impulse paths now passed from submit script

### negative_class_weight (TODO)
- Current: 20 (100x combined with sampling_weight 5x)
- Target: 5 (25x combined — still negative-biased but not extreme)
- This is the most likely single cause of low recall
- microWakeWord code default is 1, notebook example is 20

### Training steps + LR schedule (TODO)
- Current: [10000] / [0.001]
- Target: [15000, 5000] / [0.001, 0.0001]
- 96-filter model: [20000, 5000, 5000] / [0.001, 0.0001, 0.00001]
- microWakeWord supports multi-phase natively via list configs

### VTLP — Vocal Tract Length Perturbation (TODO)
- Most effective speaker diversification technique
- Warp mel frequency axis α=0.85-1.15
- ~20 lines numpy in generate_microwakeword_mmaps.py
- Not currently in microWakeWord augmentation class

## Priority 2: Data Quality

### Expand positive test sets to 100+ clips
- Current: 11 sister clips (CI: ±30%), 48 isa XTTS (CI: ±14%)
- Need: 100+ per speaker/condition for meaningful comparison
- XTTS can generate more isa variations
- Record more from sister, self, other family

### RMS normalize all positives
- ex3a/ex3b testing this now
- 3x energy difference between mic clips and TTS clips
- Model may be learning energy rather than phonetics

### Reduce Neurokone TTS count
- 1560 → 120 (12 speakers × 10 clips)
- Keep mic at 72-84% of positives
- Mix from phase1 + phase2 + SSML for variety

## Priority 3: Evaluation

### Scenario test stream (2h annotated)
- Record in real room with real mic
- Mix: silence (30min) + TV (10min) + conversation (10min) + confusable phrases in context (5min) + wake word at various distances/speakers (5min)
- Annotate timestamps
- This is the only eval that predicts real-world deployment quality

### Fix FAPH matrix (OOM)
- 48GB not enough for 9 models × 5 datasets with rglob
- Need 64GB or split into smaller batches
- MUSAN speech alone is 49h = massive feature computation

### Run okay_nabu on DiPCo for framework baseline
- Currently tested on CV ET (0.0 FAPH) and MacBook bg
- DiPCo is the canonical microWakeWord reference corpus

## Priority 4: Architecture

### MoE consensus — improve recall
- Expert A (gatekeeper): works well, 9/11 recall
- Expert B v2 (verifier): works for HN discrimination (13% FPR)
- Consensus: 0.79 FAPH but only 45-64% recall
- Fix: augmentation improvements should help Expert A recall
- After aug fix: retrain Expert A with proper augmentation

### openWakeWord
- 10+ crashes, sample rate + empty neg_test + Piper import + config issues
- submit script now does sox resample (not symlinks)
- Should work on next attempt
- Provides thesis comparison: different architecture, same data

## Priority 5: Thesis Writing

### Chapters status
- ✅ Sissejuhatus (Introduction)
- ❌ Taustapeatükk (#23) — NOT STARTED, 20h estimate
- ✅ Metoodika — architecture section written (residual, SA, quantization)
- ⚠️ Tulemused — 4 new sections written but old numbers need updating
- ⚠️ Arutelu — bench-vs-real section written, needs integration
- ❌ Kokkuvõte — interim placeholder
- ❌ Abstraktid — placeholders

### Key thesis contributions
1. First Estonian wake word model
2. Residual connections -37% FAPH (clean ablation)
3. MoE consensus sub-1 FAPH
4. Bench ≠ real-world finding
5. Canonical FAPH methodology adoption
6. Hard negative mining iterative loop
7. Expert model specialization design

## HPC Jobs Status (as of Apr 13)
- ex3a (918769): RMS-norm gatekeeper — RUNNING
- ex3b (918770): RMS-norm + pitch shift — RUNNING
- FAPH matrix (918678): OUT_OF_MEMORY — needs 64GB resubmit
- oWW v2 (918699): FAILED (neg_test empty) — needs resubmit with fix
