# Thesis feedback action plan — 2026-05-14

Source: `thesis-feedback.txt` (full pass through p62; first half focused on pp13–48, second half adds pp48–62 discussion/summary/future-work feedback).

## Operating rule

Deadline is close, so every worker should prefer **compression, consistency, and defensible claims** over new material. Do not add experiments or large explanations unless they replace longer weaker prose. User feedback says the thesis is drifting into a work diary around pp. 37–48 and then repeats results in chapter 4; the highest-value fixes are therefore structural compression, terminology cleanup, and turning chapter 4 into concise implications/future work rather than another results chapter.

## Decisions from the feedback

- Standard false-trigger term in the thesis: **valevallandumine** / **valevallandumised tunnis** for FAPH. Avoid `valehäire`, `valeaktiveering`, and `valetrigger` except when quoting an external term.
- `inference` should usually be described as **mudeli käitamine**, **mudel töötab**, or **otsuse tegemine**, not `järeldamine`, unless the mathematical/statistical meaning is intended.
- User-test target should be **kuni 10 osalejat**, framed as a pilot/UX check for the complete voice-assistant loop, not as a full 20–30 participant wake-word validation study.
- `openWakeWord` is a background/technology comparison, not a fully measured comparison unless there are actual matching measurements.
- TalTech 2025 IT guide: lists of figures/tables are optional “if needed”; if included, every figure/table must be numbered, referenced before appearing, and caption/title must be on same page.
- Chapter 4 must not re-read chapter 3. Keep only implications, limitations, methodological lessons, and future work.
- Do not start new openWakeWord experiments before submission unless the user explicitly asks. Soften comparison claims instead.
- The Android false-trigger logger is worth preserving as a methodological insight: long-term, privacy-preserving trigger logging without storing audio, but with the limitation that it is not replayable.
- Make the synthetic-data thread explicit: limited real speakers were mitigated with synthetic positives, but evaluation must use real speakers and independent held-out sets.

## Already applied in this session

- Updated `misc/terms_abbreviations.tex` with missing acronyms (ASR, FPR, HN, HPC, MCP, RMS, RNG, SLURM, SSML, UMUX-Lite, VAD, XTTS, etc.) and aligned FAPH with `valevallandumised tunnis`.
- Cleaned `first_chapter.tex` methodology intro, `openWakeWord` framing, `järeldamine`, `speech-negative`, `audio opt-in`, FAPH variant wording, 20–30 participant claim, and some LaTeX `~sekund` rendering risks.
- Compressed `second_chapter.tex` around v17 positive-data quality controls: removed log-like script-by-script subsection and replaced it with a thesis-level guardrail paragraph.
- Began terminology cleanup in `second_chapter.tex`: removed visible `auditiring`, `voice-cloning`, `sub-1`, `disjoint`, `tripwire`, `unseen`, `scripted offline`, and many `valeaktiveering` occurrences from the page-37–48 region.
- Rebuilt `docs/thesis/thesis-tex-estonian/main.pdf`; LaTeX completed successfully, `thesis-lint` now has no `error` severity findings, and the `šekund` rendering bug no longer appears in extracted PDF text.

## Backlog queue

Status legend: `todo`, `doing`, `done`, `defer`.

| ID | Priority | Status | Worker lane | Target | Task | Acceptance check |
|---|---:|---|---|---|---|---|
| FB-001 | P0 | done | glossary-worker | `misc/terms_abbreviations.tex` | Expand and normalize abbreviations/mõisted table. | `rg "FAPH&|FRR&|FPR&|RMS&|RNG&|VAD&|KWS&|XTTS&|SSML&|HPC&|SLURM&|UMUX" misc/terms_abbreviations.tex` finds entries. |
| FB-002 | P0 | done | terminology-worker | all chapters | Standardize `valevallandumine`; remove `valehäire`, `valeaktiveering`, `valetrigger`. | `rg "valehäire|valeaktiveering|valetrigger" chapters misc` returns only intentional external/legacy notes. |
| FB-003 | P0 | doing | terminology-worker | all chapters | Replace visible Estonglish/slop: `auditiring`, `disjoint`, `tripwire`, `unseen`, `score`, `public`, `speech-negative`, `voice-cloning`, `benchmark`, `scripted offline`, `manuaalne`, `freim`, `kapatsiteet`, `pool`, `test-clean`, `komposiitne`, `eksplitsiit*`, `sekvents`, `ekstaktne`, `metoodikaline`, `tensor-arena`, `compile`, `flash`. | `rg` for those terms returns zero visible prose hits or only code identifiers / intentional English abstract. |
| FB-004 | P0 | done | methodology-worker | `first_chapter.tex` | Fix methodology opening and technology comparison: remove filler `sellist`, stop overclaiming openWakeWord comparison, mention Python/WiZ/mock MCP/Ollama briefly. | Page 13 no longer says full comparison was measured; Python/demo stack mentioned once. |
| FB-005 | P0 | done | user-test-worker | `first_chapter.tex` | Update user-test method from 20–30 full study to kuni 10 participant pilot/voice-assistant usefulness check; replace `audio opt-in`; align questionnaire with current mini questionnaire. | `rg "20--30|audio opt-in|planeeritav" first_chapter.tex` returns zero. |
| FB-006 | P0 | done | latex-worker | thesis source | Fix LaTeX rendering bugs from `~sekund` / `~s` and rebuild PDF. | `rg "~sekund" chapters` returns zero; `latexmk` succeeds; PDF no `šekund`. |
| FB-007 | P1 | todo | structure-worker | `second_chapter.tex` §§3.1–3.3 | Compress early model-history/data-leakage narrative; combine repeated “toru valideerimine + vead” into a concise arc. | Net shorter; section explains lesson, not diary; tables are interpreted, not read aloud. |
| FB-008 | P1 | doing | structure-worker | `second_chapter.tex` §§3.5–3.6 | Remove work-diary details from v17/v18/checkpoint sections, especially §3.6.2; keep insight: label purity/FAPH-only checkpointing necessary but insufficient. | No SLURM job IDs in prose; no “treeningujooks lõppes plaanipäraselt”; §3.6.2 is concise and not boastful; section stays evidence-led. |
| FB-009 | P1 | todo | table-worker | `second_chapter.tex` tables 10–12 | Redesign oversized tables: split, shrink columns semantically, or move full matrix to appendix and keep headline table in main text. | PDF table text readable at normal zoom; no `\scriptsize` wall of numbers in main flow unless unavoidable. |
| FB-010 | P1 | todo | visual-worker | figures | Add one high-value visual: model timeline / metric evolution plot that also explains version-number semantics, if it replaces prose. | Figure referenced before appearance; caption ends with full stop; no new unsupported claims; version lineage becomes easier to follow. |
| FB-011 | P1 | todo | evidence-worker | `first_chapter.tex` §Kontekstiaken; `third_chapter.tex` chapter 4 | Add/adjust citation support for context-window, KWS evaluation, TTS/synthetic-data, and scenario-validation claims; avoid unsupported memory/discrimination claims. | Strong claims have nearby citation or weaker wording. |
| FB-012 | P1 | todo | evidence-worker | `second_chapter.tex`; `third_chapter.tex` | Check DiPCo/openWakeWord/microWakeWord comparison references, make sure DiPCo is introduced before first use, and fix the claim that home/noise stimuli were not measured if DiPCo covers that role. | First DiPCo mention explains what it is and why used; openWakeWord is not framed as a fully measured comparison. |
| FB-013 | P1 | todo | terminology-worker | all chapters | Replace remaining `peal` where it means “on/with/in” and clean colloquial phrases like `sisuliselt vait`. | `rg "\bpeal\b|sisuliselt vait" chapters` reviewed; only natural uses remain. |
| FB-014 | P1 | todo | formal-worker | thesis source | Replace em-dash-heavy prose (`---`) with ordinary Estonian punctuation where not table missing-value markers. | No dense dash chains in paragraphs; missing-value `---` in tables untouched. |
| FB-015 | P2 | todo | questionnaire-visual-worker | methodology/figures | Optional: add a small questionnaire/protocol screenshot or compact form figure only if it breaks up empty space without adding fluff. | Figure is readable and cited; no terminal screenshots unless they directly support demo instrumentation. |
| FB-016 | P0 | todo | discussion-restructure-worker | `third_chapter.tex` §§4.6–4.7 | Remove or merge repetitive “what can be claimed” / “three rounds” discussion that re-states results; keep only new implications and limitations. | Net shorter; no “kaitstavus” as a metric; no “lugeja ei tohi”; no audit-ring/ring narrative; chapter 4 adds interpretation, not another results pass. |
| FB-017 | P0 | todo | future-work-worker | `third_chapter.tex` future-work section | Replace narrow cascade-only ending with concise “future work” section: scenario-based validation, speaker/data diversity, and optional cascade/second-stage detector. | Future work has 2–3 concrete directions; cascade remains one subsection/paragraph, not the whole ending. |
| FB-018 | P0 | todo | summary-worker | `summary.tex` and introduction research questions | Align research questions/summary with actual thesis framing: pipeline + evaluation protocol + limited-speaker/TTS mitigation + prototype integration. | Summary questions no longer feel out of context; claims match evidence; no over-repeated “not production-grade” disclaimers. |
| FB-019 | P1 | todo | android-logger-worker | `third_chapter.tex` §4.4/§4.7 or `second_chapter.tex` | Integrate Android live false-trigger logger as a methodological contribution: long-term on-device parallel model logging, no audio storage, target phrase absent, privacy advantage, non-replayable limitation. | One concise paragraph; no novelty overclaim; explains why this helped find/mitigate real false triggers. |
| FB-020 | P1 | todo | hard-negative-worker | `second_chapter.tex`; `third_chapter.tex` | Check logs/docs for table-hit/keyboard/non-speech false triggers and whether collected false triggers were added as negatives; if evidenced, summarize as a methodological lesson. | Evidence found before writing; if not found, defer rather than invent. |
| FB-021 | P1 | todo | agentic-dev-worker | `third_chapter.tex` §Agentpõhine arendus | Rewrite agentic-development discussion: agents do not replace methodology; they increase iteration speed and evidence gathering, but also make wrong directions faster; mention blast-radius minimization and repeated small scoped tasks. | No token/USD/log bragging; no triple repetition of “does not replace real speakers”; concrete software-engineering lesson remains. |
| FB-022 | P1 | todo | synthetic-data-worker | `first_chapter.tex`; `third_chapter.tex` | Make the limited-speaker/synthetic-data hypothesis explicit: why TTS was used, what real-speaker eval sets tested, and gender/speaker-balance caveat. | Method/discussion mention author/friend/held-out speaker eval roles; cited synthetic-data/KWS reference if available; no claim that TTS replaces real speakers. |
| FB-023 | P1 | todo | home-assistant-worker | `summary.tex`; maybe `third_chapter.tex` | Mention Home Assistant integration as experimental prototype and personal continuation path, without implying stable production readiness. | Uses “experimental/prototüüp” framing once; notes remaining false triggers if discussed; avoids repeated defensive disclaimers. |
| FB-024 | P1 | todo | style-worker | all chapters | Remove `juur*`/deployment slop (`juurotsus`, `juurutuskandidaat`, “juur” as core) and overused “sellepärast X, mitte Y” patterns. | `rg "juurotsus|juurutuskandidaat|\bjuur\b|sellepärast" chapters` reviewed; only natural deployment uses remain. |
| FB-025 | P1 | todo | language-worker | all chapters | Audit weak subjective evidence phrasing: “käsitsi kuulamine näitas”, “kuulmiskontrolli tulemusena näis”, “autor ei leidnud”. Reframe as documented/subjektiivne inspection or remove. | Subjective listening is clearly marked as exploratory/diagnostic; strong claims rely on measured numbers. |
| FB-026 | P1 | todo | formal-worker | all chapters | Remove unnecessary English glosses and ugly parenthetical/source patterns: `(allikas ...)`, `(shortcut)`, `(ground truth)`, overused parentheses, ordinary words translated into English. | `rg "\(allikas|shortcut|ground truth|lyhitee|lühitee" chapters` reviewed; only necessary domain glosses remain. |
| FB-027 | P1 | todo | compound-language-worker | all chapters | Audit unnatural sidekriips compounds (`treeningu-domeeni`, `klipi-taseme`, `mitme-mõõdikuline`, etc.) and replace with natural Estonian phrasing. | Hyphen-heavy technical prose is reduced without breaking established terms like `FAPH-i`. |
| FB-028 | P1 | todo | hypotheses-worker | `second_chapter.tex`; intro/method if needed | Resolve unexplained labels such as `H2`, `Q1`, and table abbreviations (`UV`, `HN`) where they appear before definition. | Every H/Q label is defined or removed; table captions explain abbreviations or glossary covers them. |
| FB-029 | P2 | defer | experiment-worker | openWakeWord experiments | Optional idea from feedback: extra openWakeWord comparison with Estonian negative corpora. Defer until after submission unless user explicitly asks. | No new training/evaluation scope added before thesis deadline. |

## Worker design for hourly automation

Use the existing `.hermes/thesis-automation` scheduler as the execution shell, but steer it as a **backlog-first system**:

1. **Queue triage before every hourly edit**
   - Read this file.
   - Pick the highest-priority `todo/doing` item that matches the lane’s target file.
   - If the item is already fixed in the target file, skip to the next matching item.

2. **One worker = one small patch**
   - Edit one file only.
   - Prefer deletion/replacement over addition.
   - Avoid changing tables and prose in the same patch.
   - Do not invent numbers, sources, or user-test results.

3. **Worker roles**
   - `terminology-worker`: regex-driven cleanup and glossary alignment.
   - `methodology-worker`: first-chapter method/user-test/technology corrections.
   - `structure-worker`: compress diary-like result sections into insight-led paragraphs.
   - `discussion-restructure-worker`: remove repeated results prose from chapter 4 and keep implications.
   - `future-work-worker`: turn §4.7 into concrete future work rather than another conclusion.
   - `table-worker`: redesign dense tables or produce a concrete split/appendix plan.
   - `visual-worker`: add only one high-yield plot/figure that replaces prose.
   - `evidence-worker`: check citations, TalTech rules, DiPCo/openWakeWord framing.
   - `agentic-dev-worker`: keep the agentic-development lesson concrete, humble, and non-boastful.
   - `latex-worker`: build PDF and report errors/overfull boxes caused by edits.

4. **Validation commands**

```bash
rg "auditiring|valehäire|valeaktiveering|valetrigger|disjoint|tripwire|unseen|scripted offline|voice-cloning|speech-negative|audio opt-in|manuaalne|freim|kapatsiteet|komposiit|eksplitsiit|ekstakt|sekvents|metoodikaline|juurutuskandidaat|juurotsus|\\(allikas|ground truth|shortcut|~sekund" docs/thesis/thesis-tex-estonian/chapters docs/thesis/thesis-tex-estonian/misc
./cli/kratt thesis-lint --profile final --ranked --json
(cd docs/thesis/thesis-tex-estonian && latexmk -pdf -interaction=nonstopmode main.tex)
```

5. **Current highest-value order after full feedback pass**
   1. FB-016/FB-017: compress/rewrite chapter 4 §§4.6–4.7 so it stops repeating results and ends with useful future work.
   2. FB-008/FB-009: finish §3.6 compression and redesign tables 10–12.
   3. FB-003/FB-024/FB-025/FB-026: run the expanded terminology/style sweep from the second feedback half.
   4. FB-012/FB-011/FB-022: fix DiPCo/openWakeWord/TTS/synthetic-data evidence framing.
   5. FB-018/FB-023: align summary with the actual contribution and experimental Home Assistant integration.
   6. FB-010 only if it replaces prose: model timeline / metric evolution visual.
