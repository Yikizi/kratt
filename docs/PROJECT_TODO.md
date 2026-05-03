# Kratt - Project TODO

> **Persistent task list** - source of truth for ongoing work across coding-agent sessions.  
> Last updated: 2026-04-29

## Status legend

- ⏳ pending
- 🔄 in_progress
- ✅ completed
- ❌ blocked / abandoned
- 🎯 critical path
- 🧊 frozen / do not expand unless explicitly decided

---

## 0. Current thesis-critical state (2026-04-29)

**Hard deadline:** thesis document submission **2026-05-18**. From now on, user testing + thesis writing outrank new training ideas unless they directly unblock the thesis.

**Model state, in one sentence:** `v16c` remains the stable single-model demo/baseline candidate, but the v17/v18/checkpoint experiments showed that no current single model is a production-quality exact two-word detector; newer runs are diagnostic evidence, not replacements.

### Current model roles

| Role | Model / combo | Status |
|---|---|---|
| Stable active demo baseline | `v16c` | Best practical single-model baseline for user-test/demo unless pilot proves otherwise. Strong recall; weak prefix/confusable selectivity. |
| Field/recall reference | `expert-a` | Useful baseline; good field balance, but not exact-phrase selective. |
| Historical sub-1 FAPH milestone | `expert-a + expert-b2` | Important MoE result; recall/phrase-selectivity still block deployment claims. |
| v18 low-FAPH MoE diagnostic | `v18b-clean48-sa + expert-a` | Very low ambient FAPH, but prefix/confusable failure remains. Diagnostic only. |
| Checkpoint-FAPH gate diagnostic | `checkpoint-faph10 + v16c` | Extremely low ambient FAPH, but poor Friend1 recall and high confusable FPR. Diagnostic only. |
| Deployment-packaged historical model | `v11` | Android packaging/deployment path evidence; not final model quality. |

**Do not claim:** “v18 solved it”, “checkpoint-FAPH solved it”, or “production-ready Estonian wake word” without user-test + threshold-frozen evidence.

---

## 1. USER TESTING (critical path)

Goal: collect real-speaker wake-word evidence + one-bulb UX data with 20-30 participants.

### Completed

- ✅ Short high-yield protocol drafted: `docs/user-testing/ten-minute-shadow-demo-protocol.md`
- ✅ Questionnaire v1 drafted: `docs/user-testing/questionnaire-v1.md`
- ✅ Labelled recorder implemented: `tools/user-testing/run_user_test.py`
- ✅ CLI wrapper added: `kratt user-test`
- ✅ Protocol supports two consent levels: metrics-only vs audio opt-in

### Next actions

- 🎯 ⏳ Run self-pilot end-to-end with `kratt user-test TEST --dry-run --new-session-subdir`, then with real mic
- 🎯 ⏳ Verify each trial creates one WAV + one `trials.jsonl` row
- 🎯 ⏳ Freeze active model and thresholds before full data collection
  - recommended active model for pilot: `v16c`
  - shadow/replay set: `v16c`, `expert-a`, `expert-b2`, `v6-residual`, `v10`, `v15`
- 🎯 ⏳ Run 2-3 participant pilot sessions
- 🎯 ⏳ Full user testing: 20-30 participants
- 🎯 ⏳ Analyze:
  - wake recall on positive trials
  - hard-negative FPR on human voices
  - end-to-end task success / latency
  - UX questionnaire results
- 🎯 ⏳ Write user-study method + results into thesis §3/§5

---

## 2. THESIS WRITING (critical path)

### Status by chapter

| Chapter | Status | Current focus |
|---|---|---|
| §1 Sissejuhatus | 🔄 draft evolving | Tighten problem statement and contribution claims. |
| §2 Taust ja eksperimendid | 🔄 partially corrected | Keep methodology-audit narrative; avoid obsolete “breakthrough” claims. |
| §3 Metoodika | 🎯 🔄 in_progress | Evaluation protocol, user-test protocol, threshold policy, data quality gate. |
| §4 Implementatsioon | ⏳ draft | ESP32/Android/demo pipeline + training/eval tooling. |
| §5 Evalueerimine | 🎯 ⏳ pending data | v16/v17/v18/checkpoint results + user-test results. |
| §6 Kokkuvõte | ⏳ draft | Conservative conclusion: feasible prototype + known limitations. |

### Specific TODO

- 🎯 ⏳ Write the corrected evaluation contract: report **FAPH + recall + hard-negative/confusable FPR** together at frozen thresholds.
- 🎯 ⏳ Explain data leakage and the April methodology fix clearly, without overstating earlier results.
- 🎯 ⏳ Add the positive-data quality incident (v17) as a methodological lesson.
- 🎯 ⏳ Add v18 and checkpoint-FAPH as negative/diagnostic results: label purity and FAPH-only checkpointing are necessary but not sufficient.
- 🎯 ⏳ Add user-test protocol + consent model.
- ⏳ Add comparison table vs Apple/Google/Picovoice/openWakeWord/microWakeWord with conservative caveats.
- ⏳ Implement or explicitly caveat Wilson CI / small-N uncertainty in final tables.
- ⏳ Decide which metrics/figures are final vs exploratory threshold sweeps.

---

## 3. MODEL TRAINING / MODEL SELECTION

### Completed major milestones

- ✅ v1-v16c historical model family trained and re-evaluated with canonical streaming FAPH.
- ✅ MoE/consensus breakthrough: `expert-a + expert-b2` reached sub-1 benchmark FAPH, but recall remained a blocker.
- ✅ v17 recall-cv sprint run.
- ✅ v17 positive-data incident found: SSML/XML readout, full-command XTTS positives, and too-short/prefix clips contaminated the positive class.
- ✅ Positive data audit completed: `wake-word/docs/POSITIVE_DATA_QUALITY_AUDIT_20260427.md`.
- ✅ v18 clean-positive matrix trained and benchmarked.
- ✅ Prefix/confusable regression sets built.
- ✅ Checkpoint-FAPH v18d family exported and benchmarked.

### Current interpretation

- `v16c` remains the safest single-model **baseline/demo candidate**, not a proven production model.
- v17 failed because expanded positives were partly corrupt and the model collapsed into permissive prefix/general-speech behavior.
- v18 proved that clean positive labels are necessary but not sufficient: binary KWS still fires on partial/confusable phrases unless those are first-class negatives or the objective enforces phrase order.
- FAPH-optimized checkpoint selection can produce very low ambient FAPH, but can destroy unseen-speaker recall and still fail exact phrase selectivity.

### Pending / optional

- 🎯 ⏳ Freeze the model/threshold set for user testing; avoid moving targets.
- ⏳ Replay user-test audio across frozen shadow models.
- 🧊 Optional only if time permits: `v19` controlled phrase-selectivity experiment:
  - strict positives
  - explicit `kuule/kule`-only, `kratt`-only, reversed-order, and `kuule/kule <confusable>` negatives
  - independent holdout regression set
  - controlled ratio, not hard-negative overdose
- 🧊 Defer broad negative-pool expansion and new architecture searches until after thesis-critical writing/testing.

---

## 4. EVALUATION METHODOLOGY

### Completed

- ✅ `evaluation/test_sets.py` registry for held-out sets and disjointness assertions.
- ✅ Canonical streaming FAPH: sliding window + cooldown on continuous streams.
- ✅ FAPH sets: CV ET, LibriSpeech, DiPCo, MacBook background.
- ✅ Positive recall anchors: Isa XTTS, Ode real, Friend1 real, Mattias probes.
- ✅ Hard-negative sets: Mac holdout, Isa XTTS, v10 canary.
- ✅ Prefix/confusable regression sets after v17 incident.
- ✅ Unified benchmark artifacts for v16/v17/v18/checkpoint families.
- ✅ DET/threshold sweep tooling exists.

### Pending

- 🎯 ⏳ Freeze validation/dev thresholds before final user-test analysis.
- ⏳ Implement Wilson 95% CI in final reporting code or compute separately for thesis tables.
- ⏳ Add ROC AUC only if it helps the thesis; do not let it displace FAPH/recall/FPR.
- ⏳ Clearly label prefix/confusable regression sets that overlap with training for some model families as **diagnostic**, not final independent holdout.
- ⏳ Keep `wake-word/evaluation/training_data_manifest.md` aligned for v17/v18/checkpoint runs where exact manifests are available.

---

## 5. DATA / QUALITY GUARDS

### Completed

- ✅ Positive-data audit identified corrupt SSML/XML readout and full-command XTTS positives.
- ✅ Known-bad positive sources quarantined by default in training scripts.
- ✅ Strict positive policy documented: valid positives must be exactly `kuule/kule kratt` variants.
- ✅ Duration gate raised toward 0.80s minimum for future positives unless manually whitelisted.
- ✅ Prefix/confusable regression sets materialized.

### Pending / deferred

- 🎯 ⏳ Collect user-test real-speaker data with consent; this is now the highest-value data source.
- ⏳ If new training happens, record positive exclusions in manifests and keep strict source policy.
- 🧊 Defer large MUSAN/CV/VOiCES/podcast expansion unless thesis writing is safe.
- 🧊 Do not ingest user-test audio into training before final evaluation unless the thesis explicitly separates training and held-out analysis.

---

## 6. HARDWARE / DEPLOYMENT / DEMO

### Completed

- ✅ ESP32-S3-Korvo-2 recorder and wake-word-logger firmware exist.
- ✅ ESPHome integration path exists.
- ✅ Android false-trigger logger exists and supports bundled/selectable models.
- ✅ `kratt user-test` recorder exists for labelled trial capture.
- ✅ Demo pipeline tooling exists.

### Pending

- 🎯 ⏳ Decide the active model for the user-test demo; default: `v16c` unless pilot proves worse than `expert-a`.
- ⏳ Verify ESP32/Android/demo configs point to the intended active model and threshold before testing.
- ⏳ Capture enough logs to separate wake-word failures from STT/intent/bulb failures.
- ⏳ Document deployment path and limitations in thesis §4.

---

## 7. SCHEDULE OUTLOOK

```text
2026-04-29..30  │ docs/source-of-truth refresh │ self-pilot │ freeze protocol/model/thresholds │
2026-05-01..05  │ 2-3 pilot users │ fix only blocking bugs │ start full user tests │
2026-05-06..10  │ full user testing │ replay/shadow scoring │ thesis §3/§4 drafting │
2026-05-11..15  │ analysis tables/figures │ thesis §5 │ intro/summary tighten │
2026-05-16..18  │ final edits │ formatting │ submission │
```

**Rule:** after 2026-05-01, reject new experiments that do not directly improve the submitted thesis.

---

## 8. EVENTS / DECISIONS LOG

- **2026-03-24**: Vahekaitsmine presented v6 as breakthrough; later corrected after data-leak audit.
- **2026-04-07**: Evaluation methodology audit revealed test/train leakage; canonical held-out FAPH workflow created.
- **2026-04-12-13**: Session findings: benchmark FAPH alone does not predict real-world performance; MoE explored.
- **2026-04-13**: `expert-a + expert-b2` sub-1 FAPH benchmark milestone.
- **2026-04-21**: Unified v1-v16c benchmark table produced.
- **2026-04-26**: v17 recall-cv runs benchmarked; high recall but severe hard-negative/prefix collapse.
- **2026-04-27**: Positive-data quality audit found corrupt SSML/XML and full-command positives; guard rails added.
- **2026-04-28**: v18 clean-positive matrix showed label cleanup is necessary but not sufficient.
- **2026-04-29**: Checkpoint-FAPH v18d family showed ambient-FAPH checkpointing alone can overfit / collapse recall.
- **2026-04-29**: Project docs refreshed toward thesis/user-test critical path.
