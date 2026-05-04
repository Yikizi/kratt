# kuule-kratt-v18f-clean48-tts-hn-fast

Overnight v18 clean-positive experiment submitted 2026-04-27; benchmarked 2026-04-28.

## Hypothesis

Strict two-word positive policy (only `kuule/kule kratt`, no filler/context/SSML/XML/full-command positives) should remove the v17 prefix-only failure mode.

## Delta / variant

v18e fast backup, 4×48 filters, residual ON, SpecAug OFF, 6000+2000 steps

## Data policy

- Generated strict positives built per job from Neurokõne phase1/phase2 + `kule_vs_kuule_test`.
- Known-bad SSML/XML and XTTS full-command positives quarantined by default.
- Positive duration gate: 0.50s–4.00s.
- Random positive cropping disabled by default.

## Data summary

- Positives: same strict positives as v18e.
- Negatives: same ~19.3k TTS-hard-negative-augmented pool as v18e.
- Ambient: 1002 clips (~12.18h).
- TFLite size: 76KB.

## Observed result

@0.995: Rec Isa 52%, Rec Ode 82%, Rec Mattias 96%, Rec Friend1 66%; HN Mac FPR 47%, HN Isa FPR 37%; prefix-only FPR 88%, single-Kratt FPR 77%, reversed FPR 80%, confusable FPR 79%; FAPH CV 250, LS 140, Mac 309, DiPCo 130.

Source benchmark: `wake-word/evaluation/benchmark_v18_clean_20260428_0214.md`. Consensus follow-up: `wake-word/evaluation/benchmark_v18_consensus_20260428_0242.md`.

## Interpretation

Shorter training made the model more conservative on confusables but recall is too low and FAPH remains high. Not deployable.

## Next step

Do not continue the fast variant except as a negative-control data point for hard-negative ratio effects.
