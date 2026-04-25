# Kratt Source of Truth (2026-04-23)

Stable decisions and constraints only. Use this as quick alignment note before new training/eval runs.

1. **Canonical evaluation baseline** = streaming FAPH (continuous stream), not clip-level reset/FPR (`6e76e0a`, `371bc3f`).
2. **Report trio together**: FAPH + Recall + Hard-negative FPR, and at the **same deployment threshold**.
3. **Benchmark FAPH alone is insufficient** for model choice; include live-domain and hard-negative behavior. v15 was worst on bench (243) but best IRL.
4. **Residual connections default ON** for training; use `--no-residual` only for controlled ablations (`7c3ed4c`).
5. **Program direction**: multi-model consensus (MoE) achieves sub-1 FAPH (0.79 @ 0.996/0.996 with Expert A + Expert B2), no single model achieves all three metrics simultaneously.
6. **MoE milestone reached**: Expert A + Expert B v2 achieved sub-1 FAPH (~0.79 around 0.996/0.996), but recall remains deployment blocker.
7. **ex2a lesson**: all-positive / TTS-heavy gatekeeper degraded practical balance; keep real-speech dominance in positives (>70%).
8. **Eval ingestion must be recursive** (`rglob`) to avoid missing nested WAV corpora.
9. **openWakeWord is currently patched-path work**: requires explicit 16kHz normalization + resource/setup checks on HPC.
10. **Persist measurements to artifacts** (JSON/CSV/files), not only session chat tables.
11. **Data guardrails stay fixed**: mic symmetry (pos+neg), Neurokõne dedup, only "Kuule Kratt" as positive label, never delete existing datasets for regeneration.
12. **Augmentation settings (fixed)**: PitchShift 0.4, BGNoise 0.5, RIR 0.3, EQ 0.2 (session-findings 2026-04-13).
13. **Training defaults (updated)**: residual ON, negative_class_weight 5 (not 20), LR schedule [15000, 5000], steps [15000, 5000].
14. **v16c is latest production candidate**: 148KB, 4×96f, residual ON, SA ON. Best overall balance (100% recall, 100% HN rejection, FAPH 75).
15. **v6-residual still best single-model FAPH**: 14.4 FAPH CV, but 100% hard neg FPR makes it unusable alone.
16. **Thesis execution frame**: 312h target by 2026-06-01 milestone. Latest session tracked via Clockify.
