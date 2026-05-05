# Kratt - Project TODO

> **Persistent task list** - source of truth for ongoing work across coding-agent sessions.  
> Last updated: 2026-05-04

## Status legend

- ⏳ pending
- 🔄 in_progress
- ✅ completed
- ❌ blocked / abandoned
- 🎯 critical path
- 🧊 frozen / do not expand unless explicitly decided

---

## 0. Current thesis-critical state (2026-05-04)

**Hard deadline:** thesis document submission **2026-05-18** (T-14 days). User testing + thesis writing outrank new training ideas unless they directly unblock the thesis. The user-test recorder, validator, replay scorer, and aggregate summarizer all exist; the open blocker is **frozen thresholds + a real-mic pilot run**, not tooling.

**Model state, in one sentence:** `v16c` remains the stable single-model demo/baseline candidate, but the v17/v18/checkpoint experiments showed that no current single model is a production-quality exact two-word detector; newer runs are diagnostic evidence, not replacements.

### Current model roles

| Role | Model / combo | Status |
|---|---|---|
| Stable active demo baseline | `v16c` | Best practical single-model baseline for user-test/demo unless pilot proves otherwise. Strong recall; weak prefix/confusable selectivity. |
| Field/recall reference | `expert-a` | Useful baseline; good field balance, but not exact-phrase selective. |
| Historical sub-1 FAPH milestone | `expert-a + expert-b2` | Important MoE result; recall/phrase-selectivity still block deployment claims. |
| v18 low-FAPH MoE diagnostic | `v18b-clean48-sa + expert-a` | Very low ambient FAPH, but prefix/confusable failure remains. Diagnostic only. |
| Checkpoint-FAPH gate diagnostic | `checkpoint-faph10 + v16c` | Extremely low ambient FAPH, but poor Friend1 recall and high confusable FPR. Diagnostic only. |
| Active diagnostic side branch | `v19a-kratt-only` / single-word `Kratt` ablation | Separate target policy, not an exact two-word `Kuule Kratt` replacement and not an active user-test/demo model. |
| Deployment-packaged historical model | `v11` | Android packaging/deployment path evidence; not final model quality. |

**Do not claim:** “v18 solved it”, “checkpoint-FAPH solved it”, “`Kratt`-only solved exact phrase selectivity”, or “production-ready Estonian wake word” without user-test + threshold-frozen evidence.

---

## 1. USER TESTING (critical path)

Goal: collect real-speaker wake-word evidence + one-bulb UX data with 20-30 participants.

### Completed

- ✅ Short high-yield protocol drafted: `docs/user-testing/ten-minute-shadow-demo-protocol.md`
- ✅ Questionnaire v1 drafted: `docs/user-testing/questionnaire-v1.md`
- ✅ 10-minute mini questionnaire drafted: `docs/user-testing/mini-questionnaire-form-v1.md`
- ✅ Labelled recorder implemented: `tools/user-testing/run_user_test.py` (with `--mic-smoke-test`, `--list-devices`, `--new-session-subdir` flags as of 2026-05-04 working tree)
- ✅ CLI wrapper added: `kratt user-test`
- ✅ Session validator implemented: `tools/user-testing/validate_user_test_session.py` / `kratt validate-user-test <session_dir>` (untracked, 2026-05-04)
- ✅ Offline replay scorer implemented and smoke-tested: `tools/user-testing/replay_user_test.py` / `kratt replay-user-test` (dry-run + synthetic fixture replay, 2026-05-04)
- ✅ Replay aggregate summarizer implemented: `tools/user-testing/summarize_user_test_replay.py` / `kratt summarize-user-test` (excludes dry-run/synthetic fixture rows by default)
- ✅ Protocol supports two consent levels: metrics-only vs audio opt-in
- ✅ Participant-facing consent script drafted: `docs/user-testing/consent-script-v1.md` (untracked, 2026-05-04)
- ✅ Dry-run recorder smoke validated: 17 trial rows + 17 WAVs (2026-05-04)
- ✅ No-audio consent smoke validated: 17 trial rows + 0 WAVs (2026-05-04)
- ✅ Microphone smoke-test mode added: `kratt user-test --mic-smoke-test --device <id>`
- ✅ Synthetic fixture path added and smoke-tested: `kratt user-test-fixtures` + `kratt user-test --audio-fixture-dir ... --auto-advance` (infrastructure smoke only, not user-study evidence)
- ✅ ESPHome local model copy prepared as `v16c` at cutoff `0.996` via `kratt prepare-esphome-model v16c --cutoff 0.996`; compile/flash still pending before ESP32 demo
- ✅ Pilot freeze candidate drafted: `docs/user-testing/frozen-threshold-policy.md`

### Next actions (T-14 days, ordered)

- 🎯 ⏳ **BLOCKER** Commit user-test tooling/docs changes (`kratt replay-user-test`, `kratt summarize-user-test`, `kratt user-test-fixtures`, consent/protocol docs) before full participant collection.
- 🎯 ⏳ **BLOCKER** Decide what to do with uncommitted ESP32 captive-portal change (`hardware/esp32/firmware/recorder/main/main.c` +76 lines, `sdkconfig.defaults` +3 lines, new `components/dns_server/`) — commit, stash, or revert before user-test demo touches firmware. Owner: firmware agent.
- 🎯 ⏳ Decide what to do with uncommitted recorder/CLI tweaks (`run_user_test.py` +34 lines, `cli/commands/kratt-user-test` +3 lines) — commit before pilot.
- 🎯 ⏳ Choose a non-zero-RMS input device with `kratt user-test --list-devices` + `kratt user-test --mic-smoke-test --device <id>`
- 🎯 ⏳ Run real-mic self-pilot end-to-end with `kratt user-test TEST_REAL --new-session-subdir --device <id>`
- 🎯 ⏳ Validate each real-mic session immediately with `kratt validate-user-test <session_dir>`
- 🎯 ⏳ Replay each real-mic session immediately with `kratt replay-user-test <session_dir>`
- 🎯 ⏳ Aggregate replay outputs with `kratt summarize-user-test output/user-test-replay`
- 🎯 ⏳ Finalize `docs/user-testing/frozen-threshold-policy.md` after real-mic self-pilot by filling commit/date/path fields. Once finalized, do not retune for the rest of the study.
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
- 🎯 ✅ Add user-test protocol + consent model to methodology draft (`first_chapter.tex`, 2026-05-04).
- ✅ Wilson CI for clip-level metrics + Poisson/rule-of-three CI for FAPH integrated into thesis (`wake-word/evaluation/wilson_ci.py`; cited in `second_chapter.tex` table captions and `first_chapter.tex` §metoodika; commit `249f0dd` 2026-05-02 "Add Wilson CIs, two figures, cross-chapter reconciliation").
- 🔄 Comparison table vs Apple/Google/Picovoice/openWakeWord/microWakeWord — partially in place; Porcupine explicitly excluded with rationale (commits `758e33c`, `b2da6cf` 2026-05-03). Confirm coverage against the final §2/§5 layout.
- ✅ Literature review with 50+ citations integrated (commit `d49aad6` 2026-05-04).
- ⏳ Decide which metrics/figures are final vs exploratory threshold sweeps.
- ⏳ Final §5 evaluation closeout — depends on user-test data; not unblockable until pilot runs.

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
- ✅ `Kratt`-only segment extraction pipeline created for a **diagnostic** single-word ablation: `wake-word/data/processed/positive_kratt_only_v19a` has 551 manually reviewed accepted clips + 52 rejects; detailed state in `wake-word/docs/kratt-only-segment-extraction-plan.md`.
- ✅ Separate `Kratt`-only training wrapper exists: `kratt train-kratt-only` / `wake-word/training/scripts/submit_hpc_kratt_only.sh`, so the old two-word training preset is not reused accidentally.

### Current interpretation

- `v16c` remains the safest single-model **baseline/demo candidate**, not a proven production model.
- v17 failed because expanded positives were partly corrupt and the model collapsed into permissive prefix/general-speech behavior.
- v18 proved that clean positive labels are necessary but not sufficient: binary KWS still fires on partial/confusable phrases unless those are first-class negatives or the objective enforces phrase order.
- FAPH-optimized checkpoint selection can produce very low ambient FAPH, but can destroy unseen-speaker recall and still fail exact phrase selectivity.
- `Kratt`-only is a separate target-policy ablation. It may test whether the rare word `Kratt` is a better acoustic anchor, but it does **not** solve or replace exact two-word `Kuule/Kule Kratt` detection unless a later explicit decision changes the thesis target.

### Active diagnostic side branch — `v19a-kratt-only`

- 🔄 `v19a-kratt-only` was submitted to HPC as a diagnostic run (`job_id: 923301`, partition `common`, 2026-05-04) after the clean `Kratt`-only positive set was synced.
- 🎯 Do **not** switch the user-test/demo active model because of this branch. User-test active default remains `v16c` unless pilot evidence says otherwise.
- ⏳ If the run finishes, evaluate it only as a diagnostic ablation with its own target policy and do not mix its metrics into exact two-word model tables without a clear caveat.
- ⏳ Before any promotion beyond diagnostic: build `Kratt`-like hard negatives (`kurat`, `kraam`, `kraan`, `kraad`, `krats`, `ratas`, `rott`, etc.), run frozen held-out FAPH/recall/hard-negative evaluation, add model `NOTES.md`, update `wake-word/docs/MODEL_LINEAGE.md`, and update `wake-word/evaluation/training_data_manifest.md`.
- 🧊 Do not start additional `Kratt`-only variants before real-mic pilot/user testing and thesis writing are safe.

### Pending / optional

- 🎯 ⏳ Freeze the model/threshold set for user testing; avoid moving targets.
- ⏳ Replay real user-test audio across frozen shadow models with `kratt replay-user-test`.
- 🧊 Optional only if time permits after critical path: controlled **two-word** phrase-selectivity experiment:
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

- 🎯 ⏳ Freeze validation/dev thresholds before final user-test analysis (see §1 frozen-threshold policy item).
- ✅ Wilson 95% CI implemented (`wake-word/evaluation/wilson_ci.py`) and used in thesis tables (Poisson + rule-of-three for FAPH).
- ⏳ Add ROC AUC only if it helps the thesis; do not let it displace FAPH/recall/FPR.
- ⏳ Clearly label prefix/confusable regression sets that overlap with training for some model families as **diagnostic**, not final independent holdout.
- 🔄 `wake-word/evaluation/training_data_manifest.md` — uncommitted edits in working tree (2026-05-04); reconcile and commit.

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
- ⏳ Keep `Kratt`-only generated/probe datasets isolated from the two-word `Kuule/Kule Kratt` target policy unless a manifest explicitly documents a separate target-policy experiment.
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
- 🎯 ⏳ Resolve uncommitted ESP32 captive-portal change before user-test: `hardware/esp32/firmware/recorder/main/main.c` (+76 lines, adds `dns_server.h`, captive-portal DHCP option, AP netif key constant) and `sdkconfig.defaults` (+3 lines, softap/dhcps/httpd settings), plus untracked `hardware/esp32/firmware/recorder/components/dns_server/`. Owner: firmware agent. Decide commit/stash/revert before any participant uses the satellite.
- ⏳ Verify ESP32/Android/demo configs point to the intended active model and threshold before testing.
- ⏳ Capture enough logs to separate wake-word failures from STT/intent/bulb failures.
- ⏳ Document deployment path and limitations in thesis §4.

---

## 7. SCHEDULE OUTLOOK

```text
2026-04-29..30  │ docs/source-of-truth refresh │ self-pilot │ freeze protocol/model/thresholds │  (done in part)
2026-05-01..04  │ Wilson/Poisson CI integration │ literature review folded in │ replay/validator tooling │  (done)
2026-05-05..07  │ land replay/summarizer commits │ ESP32 captive-portal decision │ self-pilot real-mic │ freeze thresholds │ 2-3 pilot users │
2026-05-08..12  │ full user testing │ replay/shadow scoring │ thesis §3/§4 drafting │
2026-05-13..16  │ analysis tables/figures │ thesis §5 │ intro/summary tighten │
2026-05-17..18  │ final edits │ formatting │ submission │
```

**Rule:** after 2026-05-05, reject new experiments that do not directly improve the submitted thesis. Do not start additional training runs; only monitor/evaluate the already-submitted `v19a-kratt-only` diagnostic if it does not displace user testing or writing.

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
- **2026-05-01**: Hermes thesis-automation scheduler + research-distill lane added (commit `80315b9`).
- **2026-05-02**: Wilson CI + two figures + cross-chapter reconciliation merged into thesis (commit `249f0dd`).
- **2026-05-03**: Porcupine excluded from baseline comparison with rationale (commits `758e33c`, `b2da6cf`); operating-point convention pinned (commit `39c3325`).
- **2026-05-04**: 9-doc literature review with 50+ citations integrated (commit `d49aad6`); model lineage archived for diagnostic families (commit `470019c`); kratt-only segment workflow added (commit `4b249ec`); live-model selection improved (commit `0b3ca7e`); user-test recorder smoke validated; consent script v1, validator, replay scorer, and summarizer staged untracked.
- **2026-05-04**: `Kratt`-only diagnostic side branch advanced: reviewed clean positive set `positive_kratt_only_v19a` finalized (551 accepted / 52 rejected), `kratt train-kratt-only` wrapper added, and HPC diagnostic run `v19a-kratt-only` submitted as job `923301`. This does not change the active two-word target policy or user-test baseline.
