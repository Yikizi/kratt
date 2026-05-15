# Current Kratt thesis vs TalTech IT faculty 2025 guide — post-fix compliance audit

Audit date: 2026-05-11/12  
Thesis path: `docs/thesis/thesis-tex-estonian/`  
Compiled with: `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`  
Current PDF: `docs/thesis/thesis-tex-estonian/main.pdf`

Primary formal source:

- `https://haldus.taltech.ee/sites/default/files/2025-08/IT-teaduskonna%20l%C3%B5put%C3%B6%C3%B6%20koostamise%20ja%20vormindamise%20juhend.pdf`

Supporting extraction:

- `docs/research/taltech-it-2025-formal-rules-extract.md`

## Executive result

The clearest formal blockers found in the first audit have now been fixed:

- Dummy appendices `Lisa 2 -- Something` and `Lisa 3 -- Something Else` are gone.
- No `\subsubsection` commands remain in chapter files.
- `tab:cross-language-faph` now has a textual reference before the table.
- The two one-paragraph discussion subsections (`Põhjus 3`, `Põhjus 4`) were merged.
- The summary now explicitly answers the four research subquestions.
- The Estonian abstract was shortened toward the ½ A4 requirement.

Main remaining issue:

- **Main body is still 58 pages**, while the 2025 IT faculty guide says a bachelor thesis main body is generally **25–35 pages**. This is the major remaining compliance/reader-load risk.

## Current page counts

Source: current compiled `main.aux`, `main.toc`, `main.pdf`.

| Scope | Pages | Status / note |
|---|---:|---|
| Full PDF | 77 | Includes title, declarations, abstracts, TOC, lists, body, bibliography, licence. |
| Main body / põhiosa | **58** | `lastpagetocount abspage 70 - firstpagetocount abspage 12 = 58`. |
| IT guide usual BSc range | 25–35 | Current thesis is **23 pages over max usual range**. |
| Bibliography | pp. 71–76 | 6 pages. |
| Licence | p. 77 | Present as Lisa 1. |
| Extra appendices | 0 | Dummy appendices removed. |

Chapter distribution from TOC:

| Chapter | Start page | End page | Pages | Share of main body |
|---|---:|---:|---:|---:|
| 1 Sissejuhatus | 13 | 14 | 2 | 3.4% |
| 2 Metoodika | 15 | 23 | 9 | 15.5% |
| 3 Tulemused | 24 | 58 | 35 | 60.3% |
| 4 Arutelu ja järeldused | 59 | 69 | 11 | 19.0% |
| 5 Kokkuvõte | 70 | 70 | 1 | 1.7% |

## Current compliance matrix

| Requirement from 2025 IT guide | Current state | Status | Next action |
|---|---|---|---|
| Bachelor main body generally 25–35 pages | 58 pages | **Risk / justify or compress** | Compress results chapter or get supervisor acceptance for overlength. |
| Main body includes intro, chapters, summary | Present | PASS | Keep. |
| Title page | Present | PASS | Keep. |
| Author declaration | Present | PASS | Keep. |
| Abstract in thesis main language | Present, shortened | PASS / visual check | Check if reviewer expects stricter ½ A4; currently much shorter than before. |
| Abstract in second language | Present, at least 1 page | PASS | Keep. |
| Required abstract final count sentence | Present | PASS | Recompile after all edits so count stays correct. |
| Translated thesis title before second-language abstract | Present | PASS | Keep. |
| Abbreviations/glossary if needed | Present | PASS / content check | Review glossary completeness separately. |
| TOC | Present | PASS | Keep. |
| List of figures/tables if applicable | Present | PASS | Keep. |
| Independent parts start new page | Template handles | PASS | Visual final check only. |
| Max three heading levels / avoid fourth | No `\subsubsection` remains | PASS | Keep source clean. |
| Avoid one-paragraph subsections | Clear Põhjus 3/4 cases fixed | PASS / spot check | Re-run after any restructuring. |
| Heading followed by text, not immediately object | Appears okay | PASS / spot check | Visual final check. |
| Figures/tables numbered and captioned | Present | PASS | Keep. |
| Figures/tables referenced before appearing | Known unreferenced table fixed | PASS / rerun scan | Re-run scan after compression. |
| Code listings captioned as figures | Dummy code appendix removed | PASS | Keep no extra code appendix unless needed. |
| Bibliography present | Present | PASS | Separate citation hygiene audit still useful. |
| Licence as Lisa 1 in same PDF | Present p. 77 | PASS | Keep. |
| Extra appendices numbered, titled, referenced | No extra appendices | PASS | Add none unless necessary. |
| Summary answers introduction questions | Explicit 4-item answer list | PASS | Keep concise. |
| AI use described when substantive | Agentic-development section exists | PARTIAL | Consider adding a short formal AI-use declaration if required/preferred. |
| Personal/audio data handling | Consent/audio opt-in described | PARTIAL | Add retention/publication-limit sentence if user audio remains in scope. |
| PDF compiles cleanly | `latexmk` successful | PASS | Recompile after all edits. |

## Remaining P0/P1 actions

### P0

1. Decide what to do about the **58-page main body**.
   - If compressing: target chapter 3 first.
   - If not compressing to 35 pages: ask/confirm supervisor acceptance and keep thesis tightly structured.

2. Run final citation hygiene audit.
   - Every printed bibliography entry should be cited.
   - Remove placeholder/example sources if they print.

3. Re-run final PDF check after any compression.

### P1

1. Make the results chapter more reviewer-friendly.
   - Use the three-audit narrative rather than chronological model diary.
   - See `docs/research/thesis-results-chapter-compression-plan-2026-05-11.md`.

2. Add or clarify formal AI-use statement.

3. Strengthen user-test/audio data-protection wording if real user audio remains part of the submitted thesis.

## New rules confirmed compared with earlier assumptions

- The current formal source is the **2025 IT faculty guide**, not older 2020 wording.
- BSc main body usual range is **25–35 pages**.
- Main-language abstract is **½ A4 page**; second-language abstract is **at least 1 A4 page**.
- The ½ A4 rule does **not** apply to the introduction.
- Licence must be **Lisa 1** in the same PDF.
- Fourth-level headings should be avoided.
