# Thesis anti-slop rewrite tracker — 2026-05-16

Purpose: keep the valid critique intent from recent thesis-review commits, but rewrite or compress the resulting prose so the Estonian thesis does not grow through additive caveats, awkward calques, or glossary bloat.

## Done criteria for each checkbox

Tick a commit only when all are true:

1. The commit's critique intent has been read from `git show <hash>`.
2. Affected thesis text has been reviewed in the current manuscript.
3. Any needed fix is rewritten in natural Estonian, not merely patched around.
4. Net text length is the same or shorter unless a concrete missing fact/citation is essential.
5. No glossary entry is kept for ordinary words or one-off abbreviations.
6. Quick checks pass for the touched area (`thesis_lint` relevant checks and LaTeX smoke when practical).

## Anti-slop style rules

Prefer plain Estonian:

- `juurutuskiht`, `juurutusahel` → `seadmel käitamine`, `paigaldus`, `ESPHome'i kaudu kasutamine`, or delete.
- `tulemusväide` → `töö järeldus`, `väide`, or delete.
- `süsteemitaseme kasutusvalmidus` → `kas süsteem sobib päriselt kasutamiseks`.
- `operatsioonipunkt` → `valitud lävi`, `lävepaar`, `seadistus` unless discussing an actual threshold operating point.
- `eesmärgivektor`, `mõõdiku-monokultuur`, `disainiloogika`, `skoobist` → rewrite from scratch.
- `tööahel` only when it really means the whole process; otherwise name the concrete thing (`treening`, `hindamine`, `salvestus`, `seadmel käitamine`).
- Glossary: keep only recurring acronyms/terms useful to the reader. Remove ordinary Estonian words (`lävi`, `taustaheli`, `valeaktiveering`, etc.).

## Audit boundary

- First terminology/glossary slop boundary: `92b4f1b`.
- Main critique-rewrite wave boundary: around `2026-05-15 20:06`, starting with `0a9ec42`/`301791b`/`e2d512b` and continuing through the page-by-page fixes.
- Large consolidation pass requiring special care: `547f601`.

## Commit-by-commit tracker

### Phase 1 — terminology and glossary

- [x] `92b4f1b` — `fix(thesis): clarify inference terminology`
  - Intent: distinguish model inference/käitamine terminology and define needed abbreviations.
  - Risk: glossary bloat; awkward `mudeli käitamine`; ordinary words treated as terms.
  - Files: `first_chapter.tex`, `terms_abbreviations.tex`.
  - Fix committed 2026-05-16 as `b773e9e`: removed ordinary/one-off glossary entries from this area, kept relevant `FRR` and `RMS`, rewrote `mudeli käitamine`/`käitus*` phrasing in `first_chapter.tex`, and kept the intent with shorter prose. Checks: terminology+abbreviations lint = 0 findings; `latexmk` OK.
- [x] `180f789` — `fix(thesis): correct glossary page 5 — DiPCo, DET, ESP32-S3, CV, BC-ResNet, 1K-FPR`
  - Intent: factual glossary corrections.
  - Risk: overly long definitions and entries for low-value terms.
  - Files: `terms_abbreviations.tex`.
  - Fix committed 2026-05-16 as `560d42d`: preserved factual corrections for `1K-FPR`, `BC-ResNet`, `CV`, `DiPCo`, `ESP32-S3`, and `FA/h` in compact form; did not re-add unused `DET-kõver`. Checks: terminology+abbreviations lint = 0 findings; `latexmk` OK.
- [x] `547f601` — glossary part of `docs(thesis): broad critique pass — glossary, structure, narrative softening`
  - Intent: unify `valeaktiveering`, add genuinely needed terms, clean estonglish.
  - Risk: glossary over-expansion and mechanical terminology.
  - Files: `terms_abbreviations.tex`, all chapters.
  - Glossary fix committed 2026-05-16 as `69df25e`: kept the `valeaktiveering` vocabulary already present, refined `HN`, added compact recurring ML term `Lühitee`, and did not re-add ordinary/unused terms. Checks: terminology+abbreviations lint = 0 findings; `latexmk` OK.

### Phase 2 — introduction and scope framing

- [x] `17fa1d1` — `fix(thesis): tighten Sissejuhatus (lk 11) — FAPH target rationale, openWakeWord claim, operational main question`
  - Intent: make FAPH target and research question defensible.
  - Risk: bureaucratic wording.
  - Files: `introduction.tex`.
  - Resolved by later introduction rewrite (`cc4dde4`): current intro keeps the openWakeWord/ready-Estonian-starting-point correction, frames FAPH and recall as guiding targets, and compresses the research-question framing. No new thesis edit needed. Checks: terminology lint = 0 findings; `latexmk` OK.
- [x] `547f601` — introduction part of broad critique pass
  - Intent: soften readiness claims, define H1/H2, make FAPH/recall targets non-promissory.
  - Risk: additive caveats and `süsteemitaseme kasutusvalmidus` prose.
  - Files: `introduction.tex`.
  - Resolved by later introduction rewrite (`cc4dde4`): current intro keeps H1/H2 and non-promissory FAPH/recall targets while removing additive caveats and awkward readiness prose. No new thesis edit needed. Checks: no `valevallandum`/`vallandu*` residue in intro area; `latexmk` OK/up-to-date.

### Phase 3 — methodology chapter (`first_chapter.tex`)

- [x] `7627586` — `fix(thesis): page 14 §2.2 axes split + §2.3 hard-negatives data type`
  - Intent: clarify comparison axes and data types.
  - Risk: overexplaining simple structure.
  - Files: `first_chapter.tex`.
  - Fix committed 2026-05-16 as `0236552`: clarified Picovoice exclusion, compressed comparison axes into prose, added HN/fraasilähedased negatiivid as a fourth data type, and avoided the long five-axis bullet list. Checks: terminology+abbreviations lint = 0 findings; `latexmk` OK. Note: accepted slight local word increase because the missing data type was substantive; compensate in later cuts.
- [ ] `a8e89c7` — `fix(thesis): page 13 §2.1 methodology — component count, scope, Wyoming/HPC`
  - Intent: clarify components, local-vs-HPC scope, Wyoming role.
  - Risk: `juurutus*`, `tulemusväide`, component-count prose.
  - Files: `first_chapter.tex`.
- [ ] `06b0be3` — `fix(thesis): §2.1 — mWW selection criteria, deploy/training privacy split, Python pin`
  - Intent: justify microWakeWord choice and split training vs on-device privacy.
  - Risk: `juurutusahel`, excessive tooling detail.
  - Files: `first_chapter.tex`.
- [ ] `2aa5af8` — `fix(thesis): page 15 corrections — VOiCES scope, §2.5 features/splits, §2.6 metrics`
  - Intent: fix VOiCES scope, feature/split definitions, FAPH convention.
  - Risk: long metric definitions, acronym glossary pressure.
  - Files: `first_chapter.tex`, `references.bib`.
- [ ] `5c5fe14` — `fix(thesis): page 17 §2.7 architecture — SVDF/MixConv bridge, IPA fixes, streaming clarification`
  - Intent: clarify architecture and streaming behavior.
  - Risk: too much architecture exposition.
  - Files: `first_chapter.tex`, `references.bib`, `thesis.sty`.
- [ ] `ae62639` — `fix(thesis): §2.7.3 and §2.7.4 — qualify BC-ResNet, expand v6-residual reporting, tie context window to streaming cost`
  - Intent: avoid overclaiming BC-ResNet/residuals and connect context window to cost.
  - Risk: additive caveats.
  - Files: `first_chapter.tex`.
- [ ] `66f6a57` — `fix(thesis): page 19 §2.7 critique fixes — context window, SpecAugment, quantization`
  - Intent: qualify SpecAugment/window/quantization claims.
  - Risk: defensive long paragraphs.
  - Files: `first_chapter.tex`.
- [ ] `15d8033` — `fix(thesis): page 20 §2.7 tail and §2.8 opening critique fixes`
  - Intent: clarify quantization tail and user-test opening.
  - Risk: `operatsioonipunkt`, user-test caveat bloat.
  - Files: `first_chapter.tex`.
- [ ] `deb3d96` — `fix(thesis): page 21 §3.x user-test methodology clarity and citations`
  - Intent: strengthen user-test methodology and citations.
  - Risk: too much protocol detail in thesis body.
  - Files: `first_chapter.tex`, `references.bib`.

### Phase 4 — results chapter (`second_chapter.tex`)

- [ ] `953fce7` — `fix(thesis): strengthen §3.4.6 data-leakage narrative and test-set descriptions`
  - Intent: make data leakage and hold-out construction defensible.
  - Risk: overexplained narrative and long bullets.
  - Files: `second_chapter.tex`.
- [ ] `993e7e8` — `fix(thesis): page 31 §3.4 v1-v8 fair-comparison critique fixes`
  - Intent: clarify fair comparison and uncertainty.
  - Risk: long caveats after table.
  - Files: `second_chapter.tex`.
- [ ] `c6fc2b7` — `fix(thesis): page 36 §3.4.11–§3.4.12 critique fixes`
  - Intent: qualify consensus/residual findings.
  - Risk: `operatsioonipunkt`, generic defensiveness.
  - Files: `second_chapter.tex`.
- [ ] `36c66b9` — `fix(thesis): page 37 §3.4.12-13 residual & SpecAugment ablation clarity`
  - Intent: make ablation logic clear.
  - Risk: technical over-detail.
  - Files: `second_chapter.tex`.
- [ ] `dc08a7b` / `8ce46e1` — consensus notation and caveats
  - Intent: explain two-model AND/consensus and uncertainty.
  - Risk: `AND-reegel`, `operatsioonipunkt`, `juurutusseadistus`.
  - Files: `second_chapter.tex`.
- [ ] `86910c2` — `docs(thesis): tighten §3.5 phrase-completeness narrative and add v16c/v17 table`
  - Intent: explain phrase-completeness failure.
  - Risk: table/caveat duplication.
  - Files: `second_chapter.tex`.
- [ ] `7c204c5` — `fix(thesis): page 42 §3.5.2-3.5.3 critique fixes — protocol, Wilson UVs, V18 totals`
  - Intent: define phrase metrics protocol, Wilson limits, v18 totals.
  - Risk: excessive per-set caveats; acronym bloat.
  - Files: `second_chapter.tex`.
- [ ] `9f97589` / `45fa0c5` — v18-family critique fixes
  - Intent: clarify v18 family interpretation.
  - Risk: repeated “not enough evidence” phrasing.
  - Files: `second_chapter.tex`.
- [ ] `802b44f` — `fix(thesis): page 45 §3.5.4-3.6 critique-driven sharpening`
  - Intent: sharpen metric iteration and transition to checkpoint-FAPH.
  - Risk: `mõõdikute komplekt`, `riskiklass`, abstract method-talk.
  - Files: `second_chapter.tex`.
- [ ] `e707acc` / `d67cc7b` — checkpoint-FAPH hypothesis and claims
  - Intent: make checkpoint-FAPH limitations explicit.
  - Risk: `eesmärgivektor`, `juurutuskriteerium`, inflated conclusions.
  - Files: `second_chapter.tex`.
- [ ] `8191533` / `17e1297` / `2cc6aa1` — checkpoint/consensus softening and table critique
  - Intent: avoid overclaiming checkpoint and consensus results.
  - Risk: layered caveats after every result.
  - Files: `second_chapter.tex`.
- [ ] `2090f00` — `docs(thesis): TOC cleanup — neutralize discussion section titles, consolidate ablations`
  - Intent: reduce rhetorical headings and duplicate ablation structure.
  - Risk: check that consolidation did not create dense, long sections.
  - Files: `second_chapter.tex`, `third_chapter.tex`.

### Phase 5 — discussion chapter (`third_chapter.tex`)

- [ ] `0a9ec42` — `fix(thesis): expand §4.8 cascade direction, resolve page 62 orphan`
  - Intent: clarify cascade direction.
  - Risk: inflated future-work prose.
  - Files: `third_chapter.tex`.
- [ ] `301791b` — `fix(thesis): clean up §4.6.1 three-validation-layer prose`
  - Intent: clarify validation layers.
  - Risk: abstract “layer” language.
  - Files: `third_chapter.tex`.
- [ ] `d6976a6` — `fix(thesis): tighten §4.7 claims and supporting paragraph on page 61`
  - Intent: make claims defensible.
  - Risk: `süsteemitaseme`, `metoodiline panus`, `kasutusvalmidus`.
  - Files: `third_chapter.tex`.
- [ ] `6ff206a` / `ac04f42` / `3f3fff8` — page 56–60 readability/front-load rewrites
  - Intent: make discussion clearer.
  - Risk: Claude-ish section claims and abstract nouns.
  - Files: `third_chapter.tex`.
- [ ] `984b687` — `fix(thesis): restructure §3.7 user-test caveat and add scope paragraph`
  - Intent: prevent empty user-test result overclaim.
  - Risk: overly legalistic caveat wording.
  - Files: `second_chapter.tex`, `introduction.tex`.
- [ ] `547f601` — discussion part of broad critique pass
  - Intent: restructure future directions and Android logger privacy trade-off.
  - Risk: `disainiloogika`, `süsteemitaseme`, `rakendatavus`, `MISP-tüüpi`, etc.
  - Files: `third_chapter.tex`.

### Phase 6 — summary and final framing

- [ ] `e2d512b` — `docs(thesis): restructure summary to lead with contribution`
  - Intent: stronger summary opener.
  - Risk: over-broad contribution language.
  - Files: `summary.tex`.
- [ ] `d022766` — `fix(thesis): strengthen conclusion framing and concretize RQ answers`
  - Intent: answer research questions concretely.
  - Risk: long RQ answers and `tulemusväide`/`süsteemitaseme` caveats.
  - Files: `summary.tex`.
- [ ] `547f601` — summary part of broad critique pass
  - Intent: soften novelty/readiness claims and remove future promises.
  - Risk: bureaucratic ending and repeated limitations.
  - Files: `summary.tex`.
- [ ] `43eb54a` / later summary-tightening commits if present in current branch
  - Intent: remove duplicate scope caveats.
  - Risk: ensure no important limitation got lost.
  - Files: `summary.tex`.

## Current working notes

- 2026-05-16: started manual anti-slop edits before this tracker was created:
  - trimmed `terms_abbreviations.tex` from glossary-bloat direction;
  - compressed `introduction.tex` scope/H1/H2 framing;
  - started replacing obvious calques in `first_chapter.tex`, `second_chapter.tex`, `third_chapter.tex`.
- Do not tick any commit above until its full affected area has been re-read and checked against the done criteria.
