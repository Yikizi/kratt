# kuule-kratt-v18b-clean48-sa

Overnight v18 clean-positive experiment submitted 2026-04-27; benchmarked 2026-04-28.

## Hypothesis

Strict two-word positive policy (only `kuule/kule kratt`, no filler/context/SSML/XML/full-command positives) should remove the v17 prefix-only failure mode.

## Delta / variant

v18a + SpecAugment ON, 4×48 filters, residual ON, 15000+5000 steps

## Data policy

- Generated strict positives built per job from Neurokõne phase1/phase2 + `kule_vs_kuule_test`.
- Known-bad SSML/XML and XTTS full-command positives quarantined by default.
- Positive duration gate: 0.50s–4.00s.
- Random positive cropping disabled by default.

## Data summary

- Positives: same strict positives as v18a.
- Negatives: same general negatives as v18a; no folded hard-negative dirs.
- Ambient: 1002 clips (~12.18h).
- TFLite size: 76KB.

## Observed result

@0.995: Rec Isa 96%, Rec Ode 100%, Rec Mattias 100%, Rec Friend1 92%; HN Mac FPR 93%, HN Isa FPR 57%; prefix-only FPR 100%, single-Kratt FPR 98%, reversed FPR 98%, confusable FPR 99%; FAPH CV 132, LS 84, Mac 194, DiPCo 79.

Source benchmark: `wake-word/evaluation/benchmark_v18_clean_20260428_0214.md`. Consensus follow-up: `wake-word/evaluation/benchmark_v18_consensus_20260428_0242.md`.

## Interpretation

SpecAugment reduced FAPH substantially versus v18a but the model still fires on partial/confusable phrases. Not deployable alone. As consensus with expert-a it is useful for FAPH (CV 3.9, LS 0.36, Mac 0.86) but still fails prefix/confusable controls.

## Next step

Keep as a possible MoE/consensus FAPH partner only; do not use as the front-line wake detector.
