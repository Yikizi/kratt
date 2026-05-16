# Kratt Source of Truth (2026-04-29, refreshed 2026-05-15)

Last updated: 2026-05-15

**Deadline context:** T-3 days to thesis submission.

Stable decisions and constraints only. Use this as the quick alignment note before new training, evaluation, user testing, or thesis-writing work.

> **Refresh note (2026-05-15):** the v17/v18/checkpoint-FAPH conclusions are unchanged, and the openWakeWord 50k diagnostic branch now gives the same high-level answer from a second framework: framework/capacity changes alone did not solve the recall–FAPH–confusable tradeoff. OWW artifacts live in `docs/research/openwakeword-framework-comparison-2026-05-15.md` and `docs/research/artifacts/openwakeword-comparison-2026-05-15/`. The remaining work is **closeout**, not new training: thesis wording/evidence hygiene, Home Assistant add-on validation if it will be used as demo evidence, consent-safe use of any existing pilot/demo logs, and final build/export checks. See `docs/PROJECT_TODO.md` for the current task breakdown.

## Thesis execution frame

1. **Hard deadline:** thesis document submission is **2026-05-18**. Writing, evidence hygiene, HA/demo validation, and final build/export now outrank new experiments.
2. **Scope rule:** after 2026-05-01, reject or defer experiments that do not directly improve the submitted thesis.
3. **Final claim must be conservative:** this project demonstrates an Estonian wake-word prototype and evaluation methodology, not a production-grade assistant unless final user-test evidence proves that claim.

## Current model truth

4. **No current single model/framework path is production-quality across all required dimensions.** The final thesis must report the metric trio together: ambient FAPH, real/unseen-speaker recall, and hard/prefix/confusable rejection.
5. **openWakeWord is diagnostic, not a replacement.** The 50k OWW runs (`oww-v4`, `oww-v6`, `oww-v17`, `oww-v18d`) can lower FAPH at strict thresholds, but external recall becomes uneven/collapses and confusable FPR remains high. Use this as evidence that the bottleneck is clean/diverse positives + phrase-selective negatives/objective design, not merely mWW architecture.
6. **`v16c` is the stable single-model baseline / active-demo candidate**, not a proven production model. It has strong recall in current probes, but still fails many prefix/confusable checks.
7. **`expert-a + expert-b2` remains the historical sub-1 FAPH MoE milestone** (~0.79 FAPH in the April benchmark), but recall and exact phrase selectivity remain blockers.
8. **`v18b-clean48-sa + expert-a` and similar v18 consensus results are diagnostic.** They can reduce ambient FAPH, but still do not solve prefix/confusable triggering.
9. **Checkpoint-FAPH models are diagnostic, not deployable.** `checkpoint-faph-v18d-*` collapses external recall; `checkpoint-faph10-*` improves ambient FAPH but fails Friend1 recall and confusable rejection.
10. **Deployment-proven evidence is separate from benchmark evidence.** `v11` has Android packaging/deployment evidence; `v16c` and later models need explicit real-device/user-test evidence before deployment claims.

**Diagnostic side-branch note (2026-05-04):** `v19a-kratt-only` / single-word `Kratt` is a separate target-policy ablation. Clean reviewed positives exist (`positive_kratt_only_v19a`, 551 accepted / 52 rejected) and a separate `kratt train-kratt-only` wrapper/HPC diagnostic submit exists, but this branch is **not** an active demo/user-test model, not a replacement for exact two-word detection, and not a thesis claim unless evaluated with matching `Kratt`-like hard negatives and clearly separated metrics. Detailed state: `wake-word/docs/kratt-only-segment-extraction-plan.md`.

## Methodology invariants

11. **Canonical evaluation baseline = streaming FAPH**, not clip-level reset/FPR. Use continuous streams with the fixed sliding-window/cooldown policy.
12. **Final reporting contract:** choose thresholds on validation/dev, freeze them, then report at the same thresholds:
    - FAPH on long-form negative audio,
    - recall on real/unseen speakers,
    - hard-negative / prefix / confusable FPR.
13. **Do not tune thresholds on the final test set.** Threshold sweeps are useful but exploratory unless pre-registered.
14. **Benchmark FAPH alone is insufficient.** It can improve while recall collapses, as shown by the checkpoint-FAPH and openWakeWord strict-threshold experiments.
15. **Small-N uncertainty is explicit.** Clip-level metrics (recall, FPR) report Wilson 95% CI; FAPH reports the exact Poisson-Garwood 95% CI, with the rule-of-three one-sided upper bound when $k=0$. Implementation: `wake-word/evaluation/wilson_ci.py`; usage: §2/§3 thesis table captions in `docs/thesis/thesis-tex-estonian/chapters/`.
16. **Prefix/confusable regression sets are now part of the story.** If a regression set overlaps with training for a model family, label it as diagnostic rather than final independent holdout.

## Data and training guardrails

17. **Positive-label purity is non-negotiable for the two-word target.** Valid default-target positive clips must contain the exact two-word wake phrase (`kuule/kule kratt`, with acceptable pronunciation/elongation only), not XML/SSML readout, filler, prefix-only snippets, reversed order, or full command tails. `Kratt`-only datasets are a separately documented ablation target and must never be silently mixed into two-word training/evaluation claims.
18. **v17 positive-data incident is a thesis-relevant methodological finding.** The failure was not just bad architecture; corrupted positives and weak phrase-objective design both mattered.
19. **Clean positives are necessary but not sufficient.** v18 and OWW-v18d showed that binary clip KWS can still learn a permissive phonetic detector unless partial phrases and near phrases are treated as first-class negatives or the objective enforces order.
20. **Positive diversity is now the likely bottleneck.** More steps/capacity did not fix the issue; future improvement needs cleaner and more diverse real-speaker positives plus hard negatives that distinguish `kuule`, `kratt`, reversed order, and `kuule/kule <confusable>`.
21. **Training defaults remain conservative:** recursive ingestion, strict positive gates, residual ON unless an ablation, negative weight not extreme, augmentation fixed, and manifests must record exclusions.
22. **Never delete datasets to regenerate.** Generate alongside and let the user decide what to keep.
23. **Do not train on user-test audio before final evaluation** unless the thesis explicitly separates training data from held-out analysis.
24. **Do not start additional training branches before the critical path is safe.** The completed `v19a-kratt-only` and openWakeWord diagnostics may be cited, but user testing, HA validation, and writing remain higher priority.

## User testing truth

25. **Current user-test protocol:** `docs/user-testing/ten-minute-shadow-demo-protocol.md`.
26. **Recorder implementation:** `kratt user-test` / `tools/user-testing/run_user_test.py` records labelled WAVs and `trials.jsonl` for replay. Before real sessions, verify input with `kratt user-test --mic-smoke-test --device <id>`. Validate sessions with `kratt validate-user-test <session_dir>`. Replay audio with `kratt replay-user-test <session_dir>` and aggregate with `kratt summarize-user-test output/user-test-replay` (dry-run/synthetic rows excluded by default). Synthetic smoke fixtures use `kratt user-test-fixtures` + `--audio-fixture-dir`, but are not user-study evidence.
27. **Recommended demo/pilot active model:** `v16c`. OWW models are not active demo defaults unless a separate ONNX live-test path is explicitly chosen. ESPHome local model copy can be prepared with `kratt prepare-esphome-model v16c --cutoff 0.996`; compile/flash status determines whether it can be cited as device-demo evidence.
28. **User-test evidence rule:** use only data that actually exists and is consent-safe. If protocol-complete participant sessions are absent, do not claim a full user study; limited demo/pilot logs may support only prototype/UX observations. Participant consent text lives in `docs/user-testing/consent-script-v1.md`.
29. **Home Assistant/deployment validation is pending.** Public packaging exists (`ee0d414`), but the story needs the corrected architecture before strong thesis/demo claims: STT add-on can stay local; TTS should use the local TartuNLP `text-to-speech-worker` path (`tools/text-to-speech-worker`, upstream `v3.1.0`) instead of the public Neurokõne API wrapper; wake-word UX should be a ready ESPHome firmware image for supported boards, with YAML only as the developer/reproducibility path. Do not rely on HA deployment as final evidence until repository install/build, local STT/TTS startup, ESPHome firmware/device flow, and one-bulb command are validated.

## Documentation hierarchy

30. Tier-1 docs to keep synchronized after material changes:
    - `docs/PROJECT_TODO.md`
    - this file
    - `wake-word/docs/MODEL_LINEAGE.md`
    - `wake-word/evaluation/training_data_manifest.md`
    - `docs/research/wake-word-evaluation-methodology.md`
31. Historical plans such as the v17 dataset plan should be marked superseded rather than silently rewritten into current guidance.
32. Newer research notes that supersede or extend portions of this file (do not rewrite — link instead):
    - `docs/research/openwakeword-framework-comparison-2026-05-15.md` (OWW diagnostic framework comparison and artifacts)
    - `docs/research/wake-word-evaluation-methodology.md` (refreshed 2026-05-04 — authoritative on streaming FAPH variants and CI conventions)
    - `research/eval.md`, `research/metrics.md`, `research/comparison.md`, `research/two-stage.md`, `research/unseen-speaker.md`, `research/failure-analysis.md`, `research/asr-verifier.md`, `research/tts.md` (commit `893dbbc` 2026-05-03 — thesis-evidence working notes)
