# Review-derived thesis deficiencies for automation agents — 2026-05-07

Source reviews:
- `notes/agent-reviews-2026-05-07/35-Faktivead_ja_loogikavead.md`
- `notes/agent-reviews-2026-05-07/38-Kontrolli_tulemusi.md`
- `notes/agent-reviews-2026-05-07/39-Kontrolli_uurimiskusimusi.md`
- `notes/agent-reviews-2026-05-07/40-Kontrolli_uurimiskusimuste_vastuseid.md`
- `notes/agent-reviews-2026-05-07/41-Kontrolli_valideerimist.md`
- `notes/agent-reviews-2026-05-07/50-Eelkaitsmine_poordprojekteeritud.md`
- `notes/agent-reviews-2026-05-07/52-Hindamine_IT_kolledzi_maatriks.md`
- `notes/agent-reviews-2026-05-07/59-Retsensent_karm.md`
- `notes/agent-reviews-2026-05-07/61-Soovitused_hinde_max.md`
- `notes/agent-reviews-2026-05-07/70-Retsensiooni_paranduste_soovitamine.md`
- `notes/agent-reviews-2026-05-07/74-Teadusartikli_retsenseerimine.md`
- `notes/agent-reviews-2026-05-07/76-Eesti_keel.md`
- `.hermes/thesis-quality-reviews/2026-05-07_222644-review.md`

Canonical tracked copy for thesis-automation reviewer/writer lanes. Runtime steering copy is also stored in `.hermes/thesis-automation/memory/review-deficiencies-2026-05-07.md`. The thesis is in **compression-first closeout mode**: prefer shorter, sharper rewrites over new sections. Add new prose only when it closes a major evidence gap using evidence already present in the repo.

## Current readiness diagnosis

- Eelkaitsmiseks: defensible as a **methodology/prototype thesis**.
- Not defensible as: a completed production-quality wake-word system or completed user-study thesis.
- Central safe claim: Kratt demonstrates a reproducible, multidimensional wake-word evaluation protocol for a low-resource language through an ESP32-S3-oriented prototype.
- Central unsafe claim: any current model is production-ready or satisfies FAPH < 1, recall >= 0.95, phrase selectivity, prefix/confusable rejection, and broad-user validity simultaneously.

## P0 — claim/evidence blockers

1. **Reframe the main contribution.**
   - Fix target: introduction, abstract alignment, summary.
   - Required direction: methodology/evaluation protocol first; model and ESP32/Home Assistant integration as supporting artefacts.
   - Avoid: wording that implies a final deployable Estonian wake-word model.

2. **Close the research-question loop explicitly.**
   - Add or tighten a compact mapping: research question -> answer -> evidence -> status.
   - The FAPH < 1 and recall >= 0.95 target must be answered as conditional/partial/negative: sub-1 FAPH was reached only in narrow operating points and not together with all other requirements.

3. **Handle user-test evidence honestly.**
   - If frozen participant data is absent, every user-test reference must be planned/future/limitation.
   - If data appears, add only factual results from tracked `kratt user-test`, `validate-user-test`, `replay-user-test`, and `summarize-user-test` outputs.
   - Do not imply broad-user validation from author/self/demo tests.

4. **Fix the statistical-reporting contract.**
   - `first_chapter.tex` promises intervals broadly; several diagnostic FPR/FAPH values are point estimates.
   - Either add Wilson/Poisson intervals where data is available, or narrow captions/method wording: primary recall/FAPH tables get CIs; diagnostic regression-set FPR rows may be point estimates.

5. **Finalize or quarantine threshold-freeze language.**
   - If user-test results are used, `docs/user-testing/frozen-threshold-policy.md` needs date/commit/session fields filled before analysis.
   - If not finalized, threshold freeze remains a limitation/policy candidate, not claimed evidence.

## P1 — structure and readability improvements

1. **Metric/threshold register.**
   - Create or tighten one compact table defining FAPH variants, recall, FPR, prefix/confusable FPR, thresholds, datasets, and comparability limits.
   - Explicitly say 0.97, 0.995, 0.996, and 0.997 are separate operating points and cannot be compared casually.

2. **Validation-ring table.**
   - Convert scattered narrative into a compact risk -> measurement shortcut -> audit finding -> correction table.
   - Keep the three-ring story: data leakage, missing phrase-selectivity/prefix tests, FAPH-only checkpoint shortcut.

3. **Reduce chronological model diary.**
   - Keep v1-v18/checkpoint history only where it supports the methodological lesson.
   - Prefer research-logic grouping over run-by-run prose.
   - Move or compress repository-log-level detail, file paths, and long parameter lists.

4. **Internal artefact references.**
   - Keep file names only when needed for reproducibility or direct evidence.
   - If an artefact is not public/checkable in the thesis, describe the audit method and result rather than using the path as proof.

## P2 — language, terminology, and formal hygiene

1. **Estonian terminology cleanup.**
   - Replace mixed wording such as `deploy-kandidaat`, `runtime-loogika`, `failure-režiim`, `baseline`, `score-jaotus`, `from-scratch`.
   - Prefer: `juurutuskandidaat`, `käitusloogika`, `tõrkerežiim`, `baasjoon`, `skoorijaotus`, `algusest peale`.

2. **Avoid colloquial `peal`.**
   - Replace `andmestiku/klippide/seadme/kõneleja peal` with `andmestikul`, `põhjal`, `korral`, `abil`, or `kaudu` as appropriate.

3. **Use consistent core terms.**
   - Prefer `valevallandumine` for false activation/false accept in prose.
   - Prefer `tuvastamismäär` for recall; avoid switching to `saagis` unless a table explicitly defines it.
   - Prefer `mittekattuvuse kontroll` over `disjointsuskontroll` in final prose.

4. **Glossary/abbreviation follow-up.**
   - Review notes flagged many missing terms and unused entries.
   - Remove unused CPU/DSP/IOT/ESP-style entries if not used, and add missing thesis-active terms (FAPH variants, threshold, recall/FPR, ESP32-S3, microWakeWord/openWakeWord, etc.) only where the glossary exists.

5. **Formal compliance.**
   - Prefer bibliography citations over source footnotes.
   - Keep captions short; move repeated method details to prose or appendix.
   - Fix stale wording (`käimasolev kasutajatest`, T-14/T-11 mismatch), overfull boxes, obvious typos such as `corpus'tel`.

## P3 — do not expand unless evidence appears

- Do not start new model-training branches for thesis polish.
- Do not add new literature-review sections unless a mandatory citation gap blocks a claim.
- Do not invent user-study, venue, review, or publication facts.
- Do not add TODO/FIXME/platsihoidja text into active thesis chapters; keep open tasks in `docs/PROJECT_TODO.md`.

## Lane mapping

| Automation lane | Primary review-derived task |
|---|---|
| `intro-builder` | Make intro contribution hierarchy match safe claim: protocol/prototype first, production readiness avoided. |
| `claim-evidence` | Soften unsupported product-readiness and metric-success claims; ensure every result claim names its evidence scope. |
| `committee-questions` | Pre-empt defense questions about user-test absence, FAPH/recall non-joint success, and threshold freeze. |
| `evaluation-closeout` | Keep user-test and threshold results separated from exploratory v17/v18/checkpoint diagnostics. |
| `methodology-tightening` | Compress metric definitions and reproducibility details; add/replace with compact register only if it shortens scattered prose. |
| `summary-tightening` | Close with conservative answer: feasible prototype + evaluation protocol + explicit remaining validation limits. |
| `terminology` | Remove English/Estonian hybrids and standardize false-trigger/recall wording. |
| `formal-compliance-writer` | Fix CI/caption/citation promises and stale formal issues without broad rewrites. |
