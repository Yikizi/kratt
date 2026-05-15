# Kratt - Project TODO

> **Persistent task list** - source of truth for ongoing work across coding-agent sessions.  
> Last updated: 2026-05-13

## Status legend

- ⏳ pending
- 🔄 in_progress
- ✅ completed
- ❌ blocked / abandoned
- 🎯 critical path
- 🧊 frozen / do not expand unless explicitly decided

---

## 0. Current thesis-critical state (2026-05-13)

**Hard deadline:** thesis document submission **2026-05-18** (T-5 days). User testing + thesis writing outrank new training ideas unless they directly unblock the thesis. The user-test tooling and modular Home Assistant packaging are now landed in main (commits `91158ba`, `ee0d414`). The open blocker is no longer core tooling or HA packaging; it is **defensible evidence and cleanup**: a finalized threshold-freeze policy, full real-mic protocol sessions if any are used, consent-safe pilot data, and thesis wording that does not overclaim from limited pilot/demo logs.

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

Goal: collect limited real-speaker wake-word evidence and one-bulb voice-assistant UX/usefulness data with an up-to-10-participant pilot.

### Completed

- ✅ Short high-yield protocol drafted: `docs/user-testing/ten-minute-shadow-demo-protocol.md`
- ✅ Questionnaire v1 drafted: `docs/user-testing/questionnaire-v1.md`
- ✅ 10-minute mini questionnaire drafted: `docs/user-testing/mini-questionnaire-form-v1.md`
- ✅ Labelled recorder implemented: `tools/user-testing/run_user_test.py` (with `--mic-smoke-test`, `--list-devices`, `--new-session-subdir` flags as of 2026-05-04 working tree)
- ✅ CLI wrapper added: `kratt user-test`
- ✅ Session validator implemented: `tools/user-testing/validate_user_test_session.py` / `kratt validate-user-test <session_dir>` (untracked, 2026-05-04)
- ✅ Offline replay scorer implemented and smoke-tested: `tools/user-testing/replay_user_test.py` / `kratt replay-user-test` (dry-run + synthetic fixture replay, 2026-05-04)
- ✅ Replay aggregate summarizer implemented: `tools/user-testing/summarize_user_test_replay.py` / `kratt summarize-user-test` (excludes dry-run/synthetic fixture rows by default)
- ✅ Protocol supports two Estonian consent levels: `ainult mõõdikud` vs `mõõdikud + helisalvestis`
- ✅ Participant-facing consent script drafted: `docs/user-testing/consent-script-v1.md` (untracked, 2026-05-04)
- ✅ Dry-run recorder smoke validated: 17 trial rows + 17 WAVs (2026-05-04)
- ✅ No-audio consent smoke validated: 17 trial rows + 0 WAVs (2026-05-04)
- ✅ Microphone smoke-test mode added: `kratt user-test --mic-smoke-test --device <id>`
- ✅ Synthetic fixture path added and smoke-tested: `kratt user-test-fixtures` + `kratt user-test --audio-fixture-dir ... --auto-advance` (infrastructure smoke only, not user-study evidence)
- ✅ ESPHome local model copy prepared as `v16c` at cutoff `0.996` via `kratt prepare-esphome-model v16c --cutoff 0.996`; firmware build and ESP32 upload still pending before ESP32 demo
- ✅ Pilot freeze candidate drafted: `docs/user-testing/frozen-threshold-policy.md`
- ✅ Modular Home Assistant add-on stack committed in main (`ee0d414`): public repo metadata, STT/TTS add-ons, Docker compose stack, quickstart/validation docs, and v16c ESPHome manifest.
- ✅ Real-mic recorder path exercised on `output/user-tests/mattias/` self-pilot; **only 4 positive trials**, no hard negatives/session end, so this is smoke evidence only.
- ✅ 2026-05-13 demo/pilot log analysis produced for questionnaire-matched `m01`, `f02`, `m03`: `output/user-test-analysis/demo-log-analysis-20260513/README.md`. Use as limited UX/demo evidence only, not wake-word recall/FPR evidence.

### Next actions (T-5 days, ordered)

- 🎯 ⏳ **BLOCKER** Resolve the 2026-05-13 consent issue before using pilot logs: `f02` is marked `ainult mõõdikud` but has a matched WAV segment. Quarantine/delete/exclude the audio or correct consent with an auditable note.
- 🎯 ⏳ **BLOCKER** Finalize `docs/user-testing/frozen-threshold-policy.md` by filling date, commit, active model path, threshold, and pilot-session evidence. If not finalized, thesis must present it as a policy candidate/limitation, not as a completed freeze.
- 🎯 ⏳ Run one complete real-mic 17-trial self-pilot with non-zero RMS input, including hard negatives and `session_end`; validate, replay, and summarize immediately.
- 🎯 ⏳ If time permits, run 2-3 complete participant pilot sessions under the frozen policy; otherwise use the 2026-05-13 demo logs only as limited UX/prototype evidence with caveats.
- 🎯 ⏳ Keep the thesis aligned to an up-to-10-participant pilot framing. Current evidence does **not** support a full user study claim; absent protocol-complete data, write user testing as planned/future/limitation and use demo logs only as limited UX/prototype evidence.
- 🎯 ⏳ Analyze only consent-safe, protocol-complete data:
  - wake recall on positive trials;
  - hard-negative FPR on human voices;
  - end-to-end task success / latency;
  - UMUX-Lite/SEQ and diagnostic questionnaire results.
- 🎯 ⏳ Write user-study method/results into the actual thesis chapter structure (`Metoodika`, `Tulemused`, `Arutelu`), with caveats if only pilot/demo data exists.

---

## 2. THESIS WRITING (critical path)

### Status by chapter

| Chapter | Status | Current focus |
|---|---|---|
| Sissejuhatus | 🔄 mostly tightened | Keep contribution framed as methodology/prototype, not production model. |
| Metoodika | 🎯 🔄 in_progress | Freeze policy, evaluation protocol, user-test protocol, data quality gates. |
| Tulemused | 🎯 🔄 in_progress | Conservative model/eval results + only consent-safe pilot/demo evidence. |
| Arutelu ja järeldused | 🎯 🔄 in_progress | Limitations, feasibility, deployment reflection, no overclaiming. |
| Kokkuvõte | 🔄 draft tightened | Short final answer to research questions and known limitations. |

### Specific TODO

#### Review-derived closeout priorities (from 2026-05-07 agent review batch)

Tracked review action plan: `docs/automation/thesis-review-deficiencies-2026-05-07.md`; runtime automation steering copy: `.hermes/thesis-automation/memory/review-deficiencies-2026-05-07.md`.

- 🎯 ⏳ Reframe the thesis claim everywhere: primary contribution is a **multidimensional evaluation protocol + prototype**, not a production-ready Estonian wake-word model.
- 🎯 ⏳ Add or tighten a compact research-question answer mapping: question → answer → evidence → status. Explicitly state that FAPH < 1 and recall ≥ 0.95 are not achieved together with all selectivity requirements by any current model.
- 🎯 ⏳ Keep user-test evidence honest: if frozen participant data is absent, all user-test wording must be planned/future/limitation; if data appears, add only factual results from tracked sessions/replay summaries.
- 🎯 ⏳ Fix the statistical-reporting contract: either add Wilson/Poisson intervals where data is available, or narrow wording/captions so diagnostic FPR/FAPH rows are clearly point estimates.
- 🎯 ⏳ Finalize or quarantine threshold-freeze language: fill `docs/user-testing/frozen-threshold-policy.md` before using user-test results, otherwise treat it as a limitation/policy candidate.
- ⏳ Reflect on the ESP32-S3-Korvo-2 firmware/deployment work and integrate it into the thesis only as a **high-quality concise implementation reflection** (target: ~0.5--1 page, or a tight subsection). It should connect the ESPHome voice-satellite test, custom ESP-IDF recorder firmware, same-device data collection, and v16c deployment packaging to the main evaluation/prototype narrative; it must not become a low-level debug diary. Source notes: `notes/experiments/2026-02-12-esp32-s3-korvo2-voice-satellite.md`, `notes/experiments/2026-03-16-korvo2-recorder-firmware.md`, `hardware/esp32/esphome/`, `hardware/esp32/firmware/recorder/`.
- ⏳ Add/compact a metric-threshold register and validation-ring table only if they replace scattered prose rather than expanding the thesis.
- ⏳ Continue language cleanup flagged by review: remove English/Estonian hybrids, avoid colloquial `peal`, and standardize `valevallandumine`, `tuvastamismäär`, and `mittekattuvuse kontroll`.

- 🎯 ⏳ **Single TODO location rule:** do not keep TODO/platsihoidja blocks in active thesis chapter sources (`docs/thesis/thesis-tex-estonian/chapters/*.tex`). Track open thesis work here only, so automation can find it and the PDF never silently carries placeholders.
- 🎯 ⏳ If user-test data is added before submission, fill `second_chapter.tex` §`sec:user-test-results` with exactly these result blocks: participant/session overview; frozen-threshold per-model wake recall with Wilson 95% CI; human-spoken similar-negative/prefix FPR; one-bulb end-to-end task success + latency; short questionnaire/UMUX-Lite results. If no sufficient data arrives, keep it as an explicit limitation/future-work paragraph, not empty subsections.
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

- ✅ `v19a-kratt-only` diagnostic run (`job_id: 923301`, partition `common`, 2026-05-04) completed and was downloaded/benchmarked locally as a separate target-policy ablation.
- ✅ Context-aware positive dataset for a possible later `v19b-context` ablation prepared locally: `wake-word/data/processed/positive_kratt_context_v19b` (2836 fixed-1s clips; target offsets 40/160/280/400ms; no new training submitted). Builder: `kratt build-kratt-context`.
- 🎯 Do **not** switch the user-test/demo active model because of this branch. User-test active default remains `v16c` unless pilot evidence says otherwise.
- ⏳ Treat v19a/v19b-context as diagnostic only with their own target policy; do not mix metrics into exact two-word model tables without a clear caveat.
- ⏳ Before any promotion beyond diagnostic: build `Kratt`-like hard negatives (`kurat`, `kraam`, `kraan`, `kraad`, `krats`, `ratas`, `rott`, etc.), run frozen held-out FAPH/recall/hard-negative evaluation, add model `NOTES.md`, update `wake-word/docs/MODEL_LINEAGE.md`, and update `wake-word/evaluation/training_data_manifest.md`.
- 🧊 Do not submit additional `Kratt`-only training variants before real-mic pilot/user testing and thesis writing are safe.

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
- ✅ Modular Home Assistant v0.1 install path committed in `ee0d414`: repo-root add-on repository metadata, `kratt-kiirkirjutaja-stt/`, `kratt-neurokone-tts/`, `docker/kratt-stack.yml`, public ESPHome v16c manifest, quickstart, validation docs, and public-repo legal docs.
- 🔄 Follow-up HA add-on changes are now in the working tree after `ee0d414` (Dockerfile base-image simplification, pip retry settings, version `0.1.2`, deleted `build.yaml`). Validate against Home Assistant add-on build expectations before committing; otherwise restore the committed `build.yaml` path and docs.

### Pending

- 🎯 ⏳ Decide the active model for the user-test demo; default: `v16c` unless pilot proves worse than `expert-a`.
- ⏳ Verify ESP32/Android/demo configs point to the intended active model and threshold before testing.
- ⏳ Capture enough logs to separate wake-word failures from STT/intent/bulb failures.
- ⏳ Document deployment path and limitations in thesis §4.

---

## 7. SCHEDULE OUTLOOK

```text
2026-04-29..30  │ docs/source-of-truth refresh │ self-pilot │ freeze protocol/model/thresholds │  (done in part)
2026-05-01..04  │ Wilson/Poisson CI integration │ literature review folded in │ replay/validator tooling │  (done)
2026-05-05..07  │ replay/summarizer/validator commits │ ESP32 captive-portal closed │ thesis review-deficiency action plan drafted │  (done)
2026-05-08..11  │ Android dev voice bridge │ terminology lint workflow │ thesis pruning sweeps │ TalTech best-practices delta │  (done)
2026-05-12      │ docs refresh │ HA add-on stack drafted │ partial self-pilot smoke │
2026-05-13      │ HA add-on stack committed │ limited N=3 demo-log analysis │ consent issue found │ hook/time backlog found │
2026-05-14..16  │ freeze thresholds or demote freeze claim │ protocol-complete pilot if possible │ analysis tables/figures │ thesis closeout │
2026-05-17..18  │ final edits │ formatting │ submission │
```

**Rule:** after 2026-05-05, reject new experiments that do not directly improve the submitted thesis. Do not start additional training runs; only monitor/evaluate the already-submitted `v19a-kratt-only` diagnostic if it does not displace user testing or writing.

**Slippage as of 2026-05-13:** original schedule put full user testing in 2026-05-08..12; only tooling, thesis writing, HA packaging, and limited demo/pilot evidence happened in that window. Treat any further side-quest tooling (translation MT, intent regression, questionnaire server, airfryer/MCP experiments) as out of scope unless a submitted-thesis sentence depends on it.

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
- **2026-05-05..07**: user-test tooling + protocol + consent docs landed (commit `91158ba`); ESP32 captive-portal change closed in `hardware/esp32/firmware/`; thesis review batch produced `docs/automation/thesis-review-deficiencies-2026-05-07.md` action plan and three `.hermes/thesis-quality-reviews/` review artifacts.
- **2026-05-10**: BLE voice pipeline checkpoint and helper-routing/persona demo work landed (commits `4fae836`, `97d1c9d`); translation MT benchmark scaffold and quick FAPH spot check were produced (`notes/experiments/2026-05-10-translation-mt-benchmark.md`, `tools/demo-pipeline/bench_translation_models.py`, `tools/demo_pipeline/translation.py`, `benchmark_faph_praam_quick_20260510.csv`). Treat these as side-quest evidence unless explicitly cited.
- **2026-05-11**: Android dev voice bridge landed (commit `a5b0170`); githook/project-tracking automation improved (commits `ea17215`, `dc0f703`).
- **2026-05-12**: terminology lint workflow landed (commit `40028fb`); agent token usage stats landed (commit `5b53374`); TalTech thesis best-practices research artifacts produced under `docs/research/`.
- **2026-05-13**: modular Home Assistant add-on stack and public packaging committed (`ee0d414`). Limited demo/pilot log analysis created for `m01`, `f02`, `m03`; it supports UX/prototype caveats, not wake-word recall/FPR. Consent issue found for `f02` `ainult mõõdikud` audio. Time-tracking hook misconfiguration found and local `core.hooksPath` restored to `.githooks` for future commits.

---

## 9. SCOPE DECISIONS NEEDED (side quests in working tree, 2026-05-13)

Tooling/material exists outside critical path; decide commit + thesis scope before submission window closes. Do not let these displace threshold/evidence/thesis closeout.

- ⏳ Translation MT benchmark (`tools/demo-pipeline/bench_translation_models.py`, `tools/demo_pipeline/translation.py`, `cli/commands/kratt-translation-bench`, `notes/experiments/2026-05-10-translation-mt-benchmark.md`) — decide: commit + ignore for thesis, commit + reference as future work, or stash. Default: out of scope unless one thesis paragraph cites a result.
- ⏳ Intent regression harness (`tools/demo-pipeline/intent_regression.py`, `tools/demo-pipeline/intent-regression-cases.json`, `cli/commands/kratt-demo-intent-test`) — same decision; commit only if it backs an implementation/eval paragraph.
- ⏳ Questionnaire server + Google Forms artifacts (`tools/user-testing/questionnaire_server.py`, `cli/commands/kratt-questionnaire`, `docs/user-testing/questionnaire-v1` Google variants, `pilot-run-sheet-v1.md`, `create-google-form-v1.gs`, `google-forms-build-sheet-v1.md`) — keep only if pilot actually uses Google Forms; otherwise leave on disk and use the existing markdown questionnaire.
- ⏳ Korvo serial streamer / serial-audio path (`hardware/esp32/firmware/korvo-serial-streamer/`, `cli/commands/kratt-korvo-streamer`, `tools/demo_pipeline/serial_audio.py`) — useful for demo capture, but commit only with a concise validation note.
- ⏳ Airfryer/MCP side quest (`scripts/mcp/airfryer.py`, `tools/airfryer-server/`) — quarantine unless explicitly needed; it controls a physical appliance and is outside thesis scope.
- ⏳ `cli/CLAUDE.md` staged edits add `kratt thesis-lint` and `kratt terms` but **not** `kratt-translation-bench`, `kratt-questionnaire`, `kratt-demo-intent-test`; sync the CLI table to whichever commands actually land.
- ⏳ Loose root files: `research.md` and `false` look accidental/out-of-place — move/delete before next commit so they do not get accidentally added.

---

## 10. TIME TRACKING / GIT HOOK HYGIENE

- ✅ Local git hook path restored on 2026-05-13: `git config core.hooksPath .githooks`. Future commits should again append to `~/.kratt-time-log/commits.jsonl` and generate proposals.
- ⚠️ Time hooks were inactive because `core.hooksPath` pointed at `.git/hooks`; the local commit log/proposal stream effectively stopped around 2026-05-12 11:07. This is why recent thesis/HA/demo work is under-logged.
- ⏳ Pending proposal backlog: `.githooks/lib/apply_proposals.py --since 2026-05-12 --dry-run` reports 8 applyable records / **0h50m** from existing proposals. Apply only after confirming no manual duplicate entries.
- ⏳ Manual backfill still needed for commits and uncommitted work after the hook cutoff, especially:
  - thesis polishing commits after `5b53374` (`#19` / `#23` / `#25`);
  - Home Assistant public packaging commit `ee0d414` (`#20`);
  - 2026-05-13 demo/pilot runs, questionnaire handling, and log analysis (`#28` / `#20`);
  - this repo-audit/TODO/time-hook cleanup (`#29`).
