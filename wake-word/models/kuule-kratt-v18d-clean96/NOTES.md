# kuule-kratt-v18d-clean96

Overnight v18 clean-positive experiment submitted 2026-04-27; benchmarked 2026-04-28.

## Hypothesis

Strict two-word positive policy (only `kuule/kule kratt`, no filler/context/SSML/XML/full-command positives) should remove the v17 prefix-only failure mode.

## Delta / variant

strict clean baseline, wider 4×96 filters, residual ON, SpecAug OFF, 15000+5000 steps

## Data policy

- Generated strict positives built per job from Neurokõne phase1/phase2 + `kule_vs_kuule_test`.
- Known-bad SSML/XML and XTTS full-command positives quarantined by default.
- Positive duration gate: 0.50s–4.00s.
- Random positive cropping disabled by default.

## Data summary

- Positives: same strict positives as v18a.
- Negatives: same general negatives as v18a; no folded hard-negative dirs.
- Ambient: 1002 clips (~12.18h).
- TFLite size: 152KB.

## Observed result

@0.995: Rec Isa 98%, Rec Ode 100%, Rec Mattias 100%, Rec Friend1 98%; HN Mac FPR 80%, HN Isa FPR 77%; prefix-only FPR 100%, single-Kratt FPR 100%, reversed FPR 94%, confusable FPR 100%; FAPH CV 536, LS 382, Mac 670, DiPCo 232.

Source benchmark: `wake-word/evaluation/benchmark_v18_clean_20260428_0214.md`. Consensus follow-up: `wake-word/evaluation/benchmark_v18_consensus_20260428_0242.md`.

## Interpretation

Wider capacity increased recall but amplified the permissive/prefix detector behavior. Not deployable alone. Consensus with expert-a gives low FAPH (CV 9.7) and high recall, but still fails prefix/confusable controls.

## Next step

Do not pursue wider-only scaling until the data/objective includes partial-phrase negatives.
