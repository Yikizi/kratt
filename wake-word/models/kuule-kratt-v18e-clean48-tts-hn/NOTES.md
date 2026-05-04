# kuule-kratt-v18e-clean48-tts-hn

Overnight v18 clean-positive experiment submitted 2026-04-27; benchmarked 2026-04-28.

## Hypothesis

Strict two-word positive policy (only `kuule/kule kratt`, no filler/context/SSML/XML/full-command positives) should remove the v17 prefix-only failure mode.

## Delta / variant

v18a + legacy TTS hard negatives in general negative pool, 4×48 filters, residual ON, SpecAug OFF, 15000+5000 steps

## Data policy

- Generated strict positives built per job from Neurokõne phase1/phase2 + `kule_vs_kuule_test`.
- Known-bad SSML/XML and XTTS full-command positives quarantined by default.
- Positive duration gate: 0.50s–4.00s.
- Random positive cropping disabled by default.

## Data summary

- Positives: same strict positives as v18a.
- Negatives: ~19.3k negatives incl. negative_tts_hard and negative_tts_hard_v2.
- Ambient: 1002 clips (~12.18h).
- TFLite size: 76KB.

## Observed result

@0.995: Rec Isa 75%, Rec Ode 91%, Rec Mattias 100%, Rec Friend1 90%; HN Mac FPR 33%, HN Isa FPR 45%; prefix-only FPR 85%, single-Kratt FPR 99.5%, reversed FPR 89%, confusable FPR 88%; FAPH CV 356, LS 192, Mac 492, DiPCo 203.

Source benchmark: `wake-word/evaluation/benchmark_v18_clean_20260428_0214.md`. Consensus follow-up: `wake-word/evaluation/benchmark_v18_consensus_20260428_0242.md`.

## Interpretation

TTS hard negatives reduce confusable/hard-neg FPR but at high recall and FAPH cost. Still not deployable; the confusable regression set partly overlaps its training negatives, so even this improvement is not an independent generalization win.

## Next step

Use as evidence that explicit confusable negatives are necessary, but tune ratios/curriculum and keep independent holdouts.
