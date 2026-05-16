# Kratt — Project TODO

> Persistent task list / current source of truth for coding-agent sessions.
> Last updated: 2026-05-16

## Status legend

- ⏳ pending
- 🔄 in progress
- ✅ completed
- 🧊 frozen / defer unless explicitly reopened
- ⚠️ caveat / do not overclaim

---

## 0. Current state — thesis closeout, not new experiments

**Hard deadline:** thesis document submission **2026-05-18**.

The project is now in **closeout mode**. The useful model/evaluation evidence is already available; the remaining work is to write it defensibly, validate the demo/deployment path if it will be shown, and avoid adding new experimental scope.

### Active priorities

1. ✅ **Integrate the openWakeWord diagnostic comparison into the thesis** without overclaiming a full framework benchmark.
2. ⏳ **Finish thesis evidence/wording cleanup:** primary contribution = evaluation methodology + prototype, not production-ready Estonian wake-word model.
3. ⏳ **Validate the corrected Home Assistant packaging story** before using it as demo/thesis evidence: local STT is OK; TTS add-on now targets local TartuNLP `text-to-speech-worker`; wake-word UX should be a ready ESPHome firmware image, not manual YAML for normal users.
4. ⏳ **Keep user-test/demo evidence conservative:** only use consent-safe, actually available logs/sessions; otherwise present user testing as limited/pilot/future work.
5. ⏳ **Final build/export hygiene:** no placeholders in thesis sources, bibliography compiles, final PDF/ZIP artifacts ready.

### Current model/evidence truth

| Area | Current status |
|---|---|
| Active demo baseline | `v16c` remains the safest default unless a concrete pilot/demo run says otherwise. |
| microWakeWord result | Good prototype evidence, but no single model satisfies recall + low FAPH + phrase/confusable selectivity together. |
| openWakeWord result | Completed as diagnostic comparison. OWW can lower FAPH at strict thresholds, but recall becomes uneven/collapses and confusable FPR remains high. Not a replacement/demo default. |
| Main bottleneck | Not just convergence or architecture: too little clean/diverse real positive data + weak phrase-selective objective/hard negatives. |
| Deployment claim | Prototype/demo path only unless HA/add-on/device validation logs are produced. Public/default TTS should use local TartuNLP `text-to-speech-worker` (`v3.1.0`) with attribution, not the public Neurokõne API wrapper. |

**Do not claim:** production-ready wake word, full user study, full framework benchmark, or that OWW/`Kratt`-only/checkpoint-FAPH solved exact two-word detection.

---

## 1. Thesis writing closeout

### Completed / available evidence

- ✅ Canonical evaluation methodology: streaming FAPH + recall + hard/prefix/confusable FPR.
- ✅ Wilson CI for clip metrics and Poisson/rule-of-three CI for FAPH integrated in tooling/thesis tables.
- ✅ v1–v16c historical benchmark family evaluated.
- ✅ v17 positive-data quality incident documented.
- ✅ v18/checkpoint-FAPH diagnostics available: clean labels and low-FAPH checkpointing are necessary but not sufficient.
- ✅ openWakeWord diagnostic comparison completed and documented:
  - `docs/research/openwakeword-framework-comparison-2026-05-15.md`
  - `docs/research/artifacts/openwakeword-comparison-2026-05-15/`
- ✅ Modular Home Assistant add-on stack exists in main (`ee0d414`); TTS has been reframed toward the local TartuNLP `text-to-speech-worker` path, and wake-word UX is now specified as a ready ESPHome firmware-image path. Validation is still pending.

### Pending thesis edits

- ✅ Add OWW result to the framework-comparison / results discussion:
  - phrase as **diagnostic alternative framework test**;
  - state that it supports the data/objective bottleneck conclusion;
  - avoid “OWW is simply worse” and avoid “full framework benchmark”.
- ⏳ Add/tighten research-question answer mapping: question → answer → evidence → limitation.
- ⏳ Ensure final claim says: **prototype + multidimensional evaluation protocol**, not production system.
- ⏳ Keep FAPH, recall, and hard/confusable FPR together in final result prose/tables.
- ⏳ Explain data leakage and the April methodology correction clearly.
- ⏳ Mention positive-data quality incident as a methodological lesson.
- ⏳ Make user-test wording match available evidence only. If no protocol-complete participant data is used, describe user testing as limited/pilot/future work.
- ⏳ Remove active TODO/placeholders from thesis `.tex` files before final build.
- ⏳ Final compile/export check: bibliography, figures, tables, Estonian terminology, PDF output.

### Thesis review TODO — 2026-05-16 critique pass

#### P0 — must fix before submission

- [ ] **Fix v6 FAPH contradiction:** `chapters/second_chapter.tex` reports v6 CV ET FAPH as `154` in the v1--v8 table and `44,5` in the cross-language FAPH table, apparently at the same threshold (`0,97`) and same CV ET stream. Verify whether the difference is model artifact, corpus version, smoothing/cooldown, script, or typo; align the numbers and update derived statements.
- [ ] **Fix v16c hard-negative sign/wording error:** text says `v16c` achieved “100% Maci sarnaste negatiivnäidete tõrjumise”, while later table shows `HN Mac FPR = 100,0` for `v16c`. Correct either the metric interpretation or the referenced result.
- [ ] **Clarify real-device / Home Assistant deployment status:** add one explicit status paragraph/table stating whether `v16c` was flashed/run on ESP32-S3-Korvo-2, which threshold/config was used, whether ESPHome/HA/one-bulb demo worked, and what evidence/logs exist. If not fully validated, label as prototype/demo artifact only.

#### P1 — high defense risk / thesis claim alignment

- [ ] **Align confidence-interval promise with tables:** metoodika says every reported metric gets 95% CI, but several FPR/FAPH values are point estimates only. Either add Wilson/Poisson intervals to key tables or narrow the method claim to selected recall/FAPH metrics.
- [ ] **Unify FAPH target language:** introduction/summary use FAPH `< 1`, while one results paragraph uses `0,5 FA/h`. Define `0,5` as stricter internal comparison point or remove it.
- [x] **Add compact openWakeWord results evidence or soften OWW claims:** include a small results table with OWW model, threshold, recall, confusable FPR, and CV/Libri/DiPCo/Mac FAPH; otherwise describe OWW only as background/diagnostic note, not an empirical framework comparison.
- [ ] **Reframe user-test content as next validation layer:** keep protocol, but make clear that no protocol-complete participant dataset is used as thesis evidence. Rename/result wording should avoid sounding like an unfinished promised study.
- [ ] **Clarify held-out vs regression/dev-test roles:** state that `faph_cv_et` and related sets became regression/model-comparison sets after repeated iteration, not a final untouched test set; keep “true held-out” as future work.
- [ ] **Name concrete model versions in discussion §4.4:** replace “üks versioon / teine versioon” and bare numbers like “243 korda tunnis” with model IDs, thresholds, and table references, or remove the vague comparison.
- [ ] **Add public artifact reference:** if claiming open-source/reproducible outputs, add repository URL plus commit/tag/release (or appendix/footnote) for the submitted thesis version.

#### P2 — polish / readability / final build hygiene

- [ ] **Shorten and strengthen the summary:** reduce repeated limitations; end with positive contribution framing: prototype + multidimensional evaluation protocol + open workflow + next validation steps.
- [ ] **Improve dense tables and overfull hboxes:** address LaTeX overfull warnings, especially long `\texttt{...}` tokens and very wide checkpoint/consensus tables; split or simplify if needed.
- [ ] **Make abstracts self-contained:** define KWS in Estonian abstract as “märksõna-/äratussõnatuvastus (KWS)” before using the abbreviation; mirror if needed in English abstract.
- [ ] **Clean thesis-facing terminology:** prefer “treeningu- ja hindamisahel/konveier” over “toru”; replace “skoobist välja” with “töö ulatusest välja”; standardize “MacBook”; keep “valeaktiveering”/FAPH terminology consistent.
- [ ] **Check figure/table lists and final front matter:** confirm list of figures/tables is present and matches TalTech requirements; verify annotation counts after final compile.
- [ ] **Final PDF sanity pass:** rebuild PDF from current sources, inspect PDF text around changed sections, ensure no stale output, no visible placeholders, no merge-conflict markers, bibliography compiles, and log has no critical warnings.

---

## 2. Wake-word model/evaluation state

### Current roles

| Role | Model / family | Status |
|---|---|---|
| Stable demo/baseline | `v16c` | Best practical single-model default; strong recall, weak phrase/confusable selectivity. |
| Historical balanced anchor | `v6-residual` | Useful comparison point; lower FAPH than `v16c`, still not selective enough. |
| Field/recall reference | `expert-a` | Useful baseline; not exact-phrase selective. |
| Historical MoE milestone | `expert-a + expert-b2` | Sub-1 FAPH milestone, but recall/selectivity still block deployment claims. |
| v18/checkpoint diagnostics | `v18*`, `checkpoint-faph*` | Show label purity and FAPH optimization are not sufficient. |
| Single-word ablation | `v19a-kratt-only` | Separate target policy; not a replacement for `Kuule/Kule Kratt`. |
| Framework diagnostic | OWW 50k runs | Completed; not an active replacement path. |

### openWakeWord completed branch

- ✅ OWW ONNX models copied locally:
  - `wake-word/models/openwakeword/oww-v4-50k/`
  - `wake-word/models/openwakeword/oww-v6-50k/`
  - `wake-word/models/openwakeword/oww-v17-official-50k/`
  - `wake-word/models/openwakeword/oww-v18d-clean96-cap128-50k/`
- ✅ Supervisor-style OWW CSVs copied locally:
  - `wake-word/evaluation/openwakeword-supervisor-full-20260515/`
- ✅ Combined mWW+OWW report generated:
  - `docs/research/artifacts/openwakeword-comparison-2026-05-15/supervisor_report_plus_openwakeword.html`
- ⚠️ Interpretation: lower FAPH at strict OWW thresholds is possible, but recall/confusable rejection does not meet the thesis target.
- 🧊 No more OWW training before submission unless explicitly reopened.

### Frozen/deferred model work

- 🧊 No new architecture searches or training branches before thesis submission.
- 🧊 If future work resumes after submission: collect more clean/diverse real positives; add explicit phrase-structure hard negatives (`kuule` only, `kratt` only, reversed order, `kuule/kule <confusable>`); keep held-out evaluation disjoint.
- 🧊 Do not train on user-test audio before final evaluation unless the thesis explicitly separates training and held-out data.

---

## 3. User testing / pilot evidence

Current stance: **do not let user testing block thesis closeout unless usable data already exists**.

- ⚠️ Use only consent-safe evidence.
- ⚠️ If protocol-complete participant sessions are absent, do not claim a full user study.
- ⚠️ Limited demo/pilot logs may support prototype/UX observations only, not general wake-word recall/FPR claims.
- ⏳ If any pilot/session data is included, report exactly what was measured: participant/session count, positive recall, hard-negative FPR, task success/latency, and questionnaire results if present.
- ⏳ If no sufficient data is included, write this as a limitation/future-work item rather than leaving empty result sections.

Known reference artifact:

- `output/user-test-analysis/demo-log-analysis-20260513/README.md` — limited demo/pilot log analysis for `m01`, `f02`, `m03`; use cautiously.

---

## 4. Home Assistant / deployment / demo

### Completed

- ✅ ESP32-S3-Korvo-2 recorder and wake-word-logger firmware exist.
- ✅ ESPHome integration path exists.
- ✅ Android false-trigger logger exists.
- ✅ Demo pipeline tooling exists.
- ✅ Modular HA add-on/public packaging committed in `ee0d414`:
  - add-on repository metadata;
  - `kratt-kiirkirjutaja-stt/` local STT;
  - `kratt-neurokone-tts/` local TartuNLP TTS wrapper using `text-to-speech-worker` v3.1.0;
  - `docker/kratt-stack.yml`;
  - public ESPHome `v16c` manifest;
  - quickstart/validation docs.

### Pending validation / correction

- ✅ **Replace/reframe TTS around local TartuNLP worker**:
  1. cites upstream `https://github.com/TartuNLP/text-to-speech-worker`, pinned local checkout `v3.1.0` / `14d47bf9af4e562829ccafcc757d93abb2a6412f`;
  2. downloads `multispeaker.zip` from the TartuNLP release, not the public API endpoint;
  3. adds a local Wyoming wrapper around `tts_worker.synthesizer.Synthesizer` (demo precedent: `tools/tts-server/server.py`);
  4. removes the API wrapper from the active add-on path.
- ⏳ **Validate Home Assistant path end-to-end** before using it as final demo evidence:
  1. add repository/install path visible in HA;
  2. STT add-on build/install/start succeeds;
  3. local TartuNLP TTS path starts and is reachable via Wyoming/Assist;
  4. ESPHome voice-satellite firmware with `v16c` connects;
  5. one-bulb command works through the intended pipeline;
  6. logs captured for failures/success.
- ⏳ **Wake-word install UX:** build and publish a ready ESPHome firmware image for the supported target board(s), starting with ESP32-S3-Korvo-2. YAML/package remains the developer/reproducibility path, but normal-user docs should point to firmware flashing, not manual model YAML.
- ⏳ Verify demo configs point to the intended active model (`v16c`) and threshold.
- ⏳ Document deployment limitations concisely in thesis: prototype packaging exists; validation status determines how strong the claim can be.

---

## 5. Documentation / artifact sync

Keep these synchronized if material facts change:

- `docs/PROJECT_TODO.md`
- `docs/research/source-of-truth-apr-2026.md`
- `docs/research/openwakeword-framework-comparison-2026-05-15.md`
- `wake-word/docs/MODEL_LINEAGE.md`
- `wake-word/evaluation/training_data_manifest.md` if training data/manifests change

### Recent decisions log

- **2026-05-13:** Modular Home Assistant add-on stack committed (`ee0d414`). Treat as packaging evidence until end-to-end validation exists.
- **2026-05-15:** TTS add-on path corrected from external Neurokõne API wrapper to local TartuNLP `text-to-speech-worker` wrapper; wake-word install UX reframed as prebuilt ESPHome firmware image.
- **2026-05-15:** OWW diagnostic comparison completed. Conclusion: framework/capacity change did not remove recall–FAPH–confusable tradeoff; no OWW model replaces `v16c` for demo/user-test.

---

## 6. After-submission / future work bucket

These are explicitly **not** submission blockers:

- More OWW training variants.
- More `Kratt`-only variants.
- Broad negative-pool expansion.
- New ASR verifier experiments.
- Translation MT benchmark polishing.
- Intent regression harness polishing.
- Questionnaire server / Google Forms tooling unless actually used.
- Airfryer/MCP side quests.
