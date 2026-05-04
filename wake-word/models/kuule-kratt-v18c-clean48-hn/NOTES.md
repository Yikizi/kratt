# kuule-kratt-v18c-clean48-hn

Overnight v18 clean-positive experiment submitted 2026-04-27; benchmarked 2026-04-28.

## Hypothesis

Strict two-word positive policy (only `kuule/kule kratt`, no filler/context/SSML/XML/full-command positives) should remove the v17 prefix-only failure mode.

## Delta / variant

v18a + real/folded hard negatives, 4×48 filters, residual ON, SpecAug OFF, 15000+5000 steps

## Data policy

- Generated strict positives built per job from Neurokõne phase1/phase2 + `kule_vs_kuule_test`.
- Known-bad SSML/XML and XTTS full-command positives quarantined by default.
- Positive duration gate: 0.50s–4.00s.
- Random positive cropping disabled by default.

## Data summary

- Positives: same strict positives as v18a.
- Negatives: ~12.2k negatives incl. real/folded hard negatives; no TTS hard-negative v2 set.
- Ambient: 1002 clips (~12.18h).
- TFLite size: 76KB.

## Observed result

@0.995: Rec Isa 31%, Rec Ode 91%, Rec Mattias 100%, Rec Friend1 84%; HN Mac FPR 40%, HN Isa FPR 13%; prefix-only FPR 82%, single-Kratt FPR 100%, reversed FPR 94%, confusable FPR 94%; FAPH CV 85, LS 67, Mac 445, DiPCo 119.

Source benchmark: `wake-word/evaluation/benchmark_v18_clean_20260428_0214.md`. Consensus follow-up: `wake-word/evaluation/benchmark_v18_consensus_20260428_0242.md`.

## Interpretation

Hard negatives improved hard-neg FPR but collapsed unseen-speaker recall and did not solve prefix/single-word rejection. Not deployable.

## Next step

Future hard-negative use needs controlled ratio/curriculum, not broad folded hard-neg additions.
