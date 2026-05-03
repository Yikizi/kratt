# Kratt Source of Truth (2026-04-29)

Last updated: 2026-04-29

Stable decisions and constraints only. Use this as the quick alignment note before new training, evaluation, user testing, or thesis-writing work.

## Thesis execution frame

1. **Hard deadline:** thesis document submission is **2026-05-18**. User testing, analysis, and writing now outrank new experiments.
2. **Scope rule:** after 2026-05-01, reject or defer experiments that do not directly improve the submitted thesis.
3. **Final claim must be conservative:** this project demonstrates an Estonian wake-word prototype and evaluation methodology, not a production-grade assistant unless final user-test evidence proves that claim.

## Current model truth

4. **No current single model is production-quality across all required dimensions.** The final thesis must report the metric trio together: ambient FAPH, real/unseen-speaker recall, and hard/prefix/confusable rejection.
5. **`v16c` is the stable single-model baseline / active-demo candidate**, not a proven production model. It has strong recall in current probes, but still fails many prefix/confusable checks.
6. **`expert-a + expert-b2` remains the historical sub-1 FAPH MoE milestone** (~0.79 FAPH in the April benchmark), but recall and exact phrase selectivity remain blockers.
7. **`v18b-clean48-sa + expert-a` and similar v18 consensus results are diagnostic.** They can reduce ambient FAPH, but still do not solve prefix/confusable triggering.
8. **Checkpoint-FAPH models are diagnostic, not deployable.** `checkpoint-faph-v18d-*` collapses external recall; `checkpoint-faph10-*` improves ambient FAPH but fails Friend1 recall and confusable rejection.
9. **Deployment-proven evidence is separate from benchmark evidence.** `v11` has Android packaging/deployment evidence; `v16c` and later models need explicit real-device/user-test evidence before deployment claims.

## Methodology invariants

10. **Canonical evaluation baseline = streaming FAPH**, not clip-level reset/FPR. Use continuous streams with the fixed sliding-window/cooldown policy.
11. **Final reporting contract:** choose thresholds on validation/dev, freeze them, then report at the same thresholds:
    - FAPH on long-form negative audio,
    - recall on real/unseen speakers,
    - hard-negative / prefix / confusable FPR.
12. **Do not tune thresholds on the final test set.** Threshold sweeps are useful but exploratory unless pre-registered.
13. **Benchmark FAPH alone is insufficient.** It can improve while recall collapses, as shown by the checkpoint-FAPH experiments.
14. **Small-N uncertainty must be explicit.** For small recall sets and few false accepts, report Wilson/CI or an explicit caveat.
15. **Prefix/confusable regression sets are now part of the story.** If a regression set overlaps with training for a model family, label it as diagnostic rather than final independent holdout.

## Data and training guardrails

16. **Positive-label purity is non-negotiable.** Valid positive clips must contain the exact two-word wake phrase (`kuule/kule kratt`, with acceptable pronunciation/elongation only), not XML/SSML readout, filler, prefix-only snippets, reversed order, or full command tails.
17. **v17 positive-data incident is a thesis-relevant methodological finding.** The failure was not just bad architecture; corrupted positives and weak phrase-objective design both mattered.
18. **Clean positives are necessary but not sufficient.** v18 showed that binary clip KWS can still learn a permissive phonetic detector unless partial phrases and near phrases are treated as first-class negatives or the objective enforces order.
19. **Training defaults remain conservative:** recursive ingestion, strict positive gates, residual ON unless an ablation, negative weight not extreme, augmentation fixed, and manifests must record exclusions.
20. **Never delete datasets to regenerate.** Generate alongside and let the user decide what to keep.
21. **Do not train on user-test audio before final evaluation** unless the thesis explicitly separates training data from held-out analysis.

## User testing truth

22. **Current user-test protocol:** `docs/user-testing/ten-minute-shadow-demo-protocol.md`.
23. **Recorder implementation:** `kratt user-test` / `tools/user-testing/run_user_test.py` records labelled WAVs and `trials.jsonl` for replay.
24. **Recommended pilot active model:** `v16c`; shadow/replay models should include `v16c`, `expert-a`, `expert-b2`, `v6-residual`, `v10`, and `v15`.
25. **Primary user-test value:** real-speaker wake recall, human-spoken hard-negative FPR, end-to-end bulb task success, latency, and subjective UX.

## Documentation hierarchy

26. Tier-1 docs to keep synchronized after material changes:
    - `docs/PROJECT_TODO.md`
    - this file
    - `wake-word/docs/MODEL_LINEAGE.md`
    - `wake-word/evaluation/training_data_manifest.md`
    - `docs/research/wake-word-evaluation-methodology.md`
27. Historical plans such as the v17 dataset plan should be marked superseded rather than silently rewritten into current guidance.
