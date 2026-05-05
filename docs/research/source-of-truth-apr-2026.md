# Kratt Source of Truth (2026-04-29, refreshed 2026-05-04)

Last updated: 2026-05-04

**Deadline context:** T-14 days to thesis submission.

Stable decisions and constraints only. Use this as the quick alignment note before new training, evaluation, user testing, or thesis-writing work.

> **Refresh note (2026-05-04):** the v17/v18/checkpoint-FAPH model conclusions are unchanged. What has moved since 2026-04-29: Wilson + Poisson/rule-of-three CIs are now integrated into the thesis tables and `wake-word/evaluation/wilson_ci.py`; user-test tooling (recorder, validator, replay scorer, aggregate summarizer) and consent script v1 exist but the replay/summarizer pieces are still being landed by a parallel agent; literature review with 50+ citations was folded in (commit `d49aad6`); Porcupine was excluded from the baseline comparison with documented rationale. A separate `Kratt`-only single-word diagnostic branch now exists, but it does **not** change the active two-word `Kuule/Kule Kratt` target policy or the user-test baseline. The remaining open blockers are **frozen thresholds** and a **real-mic self-pilot**, not tooling. See `docs/PROJECT_TODO.md` for the current task breakdown.

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

**Diagnostic side-branch note (2026-05-04):** `v19a-kratt-only` / single-word `Kratt` is a separate target-policy ablation. Clean reviewed positives exist (`positive_kratt_only_v19a`, 551 accepted / 52 rejected) and a separate `kratt train-kratt-only` wrapper/HPC diagnostic submit exists, but this branch is **not** an active demo/user-test model, not a replacement for exact two-word detection, and not a thesis claim unless evaluated with matching `Kratt`-like hard negatives and clearly separated metrics. Detailed state: `wake-word/docs/kratt-only-segment-extraction-plan.md`.

## Methodology invariants

10. **Canonical evaluation baseline = streaming FAPH**, not clip-level reset/FPR. Use continuous streams with the fixed sliding-window/cooldown policy.
11. **Final reporting contract:** choose thresholds on validation/dev, freeze them, then report at the same thresholds:
    - FAPH on long-form negative audio,
    - recall on real/unseen speakers,
    - hard-negative / prefix / confusable FPR.
12. **Do not tune thresholds on the final test set.** Threshold sweeps are useful but exploratory unless pre-registered.
13. **Benchmark FAPH alone is insufficient.** It can improve while recall collapses, as shown by the checkpoint-FAPH experiments.
14. **Small-N uncertainty is explicit.** Clip-level metrics (recall, FPR) report Wilson 95% CI; FAPH reports the exact Poisson-Garwood 95% CI, with the rule-of-three one-sided upper bound when $k=0$. Implementation: `wake-word/evaluation/wilson_ci.py`; usage: §2/§3 thesis table captions in `docs/thesis/thesis-tex-estonian/chapters/`.
15. **Prefix/confusable regression sets are now part of the story.** If a regression set overlaps with training for a model family, label it as diagnostic rather than final independent holdout.

## Data and training guardrails

16. **Positive-label purity is non-negotiable for the two-word target.** Valid default-target positive clips must contain the exact two-word wake phrase (`kuule/kule kratt`, with acceptable pronunciation/elongation only), not XML/SSML readout, filler, prefix-only snippets, reversed order, or full command tails. `Kratt`-only datasets are a separately documented ablation target and must never be silently mixed into two-word training/evaluation claims.
17. **v17 positive-data incident is a thesis-relevant methodological finding.** The failure was not just bad architecture; corrupted positives and weak phrase-objective design both mattered.
18. **Clean positives are necessary but not sufficient.** v18 showed that binary clip KWS can still learn a permissive phonetic detector unless partial phrases and near phrases are treated as first-class negatives or the objective enforces order.
19. **Training defaults remain conservative:** recursive ingestion, strict positive gates, residual ON unless an ablation, negative weight not extreme, augmentation fixed, and manifests must record exclusions.
20. **Never delete datasets to regenerate.** Generate alongside and let the user decide what to keep.
21. **Do not train on user-test audio before final evaluation** unless the thesis explicitly separates training data from held-out analysis.
22. **Do not start additional training branches before the critical path is safe.** The already-submitted `v19a-kratt-only` diagnostic may be monitored/evaluated if it finishes, but user testing and writing remain higher priority.

## User testing truth

23. **Current user-test protocol:** `docs/user-testing/ten-minute-shadow-demo-protocol.md`.
24. **Recorder implementation:** `kratt user-test` / `tools/user-testing/run_user_test.py` records labelled WAVs and `trials.jsonl` for replay. Before real sessions, verify input with `kratt user-test --mic-smoke-test --device <id>`. Validate sessions with `kratt validate-user-test <session_dir>`. Replay audio with `kratt replay-user-test <session_dir>` and aggregate with `kratt summarize-user-test output/user-test-replay` (dry-run/synthetic rows excluded by default). Synthetic smoke fixtures use `kratt user-test-fixtures` + `--audio-fixture-dir`, but are not user-study evidence.
25. **Recommended pilot active model:** `v16c`; shadow/replay models should include `v16c`, `expert-a`, `expert-b2`, `v6-residual`, `v10`, and `v15`. Pilot freeze candidate lives in `docs/user-testing/frozen-threshold-policy.md`; finalize commit/date/session fields after real-mic self-pilot. ESPHome local model copy can be prepared with `kratt prepare-esphome-model v16c --cutoff 0.996`; still compile/flash before ESP32 demo.
26. **Primary user-test value:** real-speaker wake recall, human-spoken hard-negative FPR, end-to-end bulb task success, latency, and subjective UX. Participant consent text lives in `docs/user-testing/consent-script-v1.md`.
27. **Hardware note (2026-05-04):** the ESP32 recorder firmware has an uncommitted captive-portal change (`hardware/esp32/firmware/recorder/main/main.c`, `sdkconfig.defaults`, new `components/dns_server/`). It must be committed, stashed, or reverted before the user-test demo touches firmware.

## Documentation hierarchy

28. Tier-1 docs to keep synchronized after material changes:
    - `docs/PROJECT_TODO.md`
    - this file
    - `wake-word/docs/MODEL_LINEAGE.md`
    - `wake-word/evaluation/training_data_manifest.md`
    - `docs/research/wake-word-evaluation-methodology.md`
29. Historical plans such as the v17 dataset plan should be marked superseded rather than silently rewritten into current guidance.
30. Newer research notes that supersede or extend portions of this file (do not rewrite — link instead):
    - `docs/research/wake-word-evaluation-methodology.md` (refreshed 2026-05-04 — authoritative on streaming FAPH variants and CI conventions)
    - `research/eval.md`, `research/metrics.md`, `research/comparison.md`, `research/two-stage.md`, `research/unseen-speaker.md`, `research/failure-analysis.md`, `research/asr-verifier.md`, `research/tts.md` (commit `893dbbc` 2026-05-03 — thesis-evidence working notes)
