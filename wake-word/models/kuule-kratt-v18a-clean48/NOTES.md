# kuule-kratt-v18a-clean48

Overnight v18 clean-positive experiment submitted 2026-04-27; benchmarked 2026-04-28.

## Hypothesis

Strict two-word positive policy (only `kuule/kule kratt`, no filler/context/SSML/XML/full-command positives) should remove the v17 prefix-only failure mode.

## Delta / variant

strict clean baseline, 4×48 filters, residual ON, SpecAug OFF, 15000+5000 steps

## Data policy

- Generated strict positives built per job from Neurokõne phase1/phase2 + `kule_vs_kuule_test`.
- Known-bad SSML/XML and XTTS full-command positives quarantined by default.
- Positive duration gate: 0.50s–4.00s.
- Random positive cropping disabled by default.

## Data summary

- Positives: 1648 train positives, 290 test positives; 709 generated strict TTS candidates before train/test split plus real/augmented Mattias sources after duration filtering.
- Negatives: ~11.7k general negatives + 1002 ambient; no folded hard-negative dirs.
- Ambient: 1002 clips (~12.18h).
- TFLite size: 76KB.

## Observed result

@0.995: Rec Isa 100%, Rec Ode 91%, Rec Mattias 99%, Rec Friend1 93%; HN Mac FPR 87%, HN Isa FPR 72%; prefix-only FPR 97%, single-Kratt FPR 99.5%, reversed FPR 98%, confusable FPR 99%; FAPH CV 515, LS 304, Mac 573, DiPCo 195.

Source benchmark: `wake-word/evaluation/benchmark_v18_clean_20260428_0214.md`. Consensus follow-up: `wake-word/evaluation/benchmark_v18_consensus_20260428_0242.md`.

## Interpretation

Clean positives alone did not remove the prefix/general-speech failure mode. Compared with v17 it preserves recall but FAPH is even worse; not deployable as a single model.

## Next step

Do not promote. Use only as evidence that label cleanup must be paired with explicit partial/confusable negatives and/or a different objective.
