# Results chapter topic inventory and compression plan — 2026-05-11

Current thesis: `docs/thesis/thesis-tex-estonian/`  
Current compiled main body after formal fixes: **58 pages**  
Current results chapter: **35 pages** (`pp. 24--58`)

Goal: make the results chapter easier and more interesting for a human reviewer. The reviewer should see the main discovery arc quickly:

1. first evaluation was misleading;
2. data leakage forced independent hold-outs and FAPH;
3. positive data quality forced phrase-completeness tests;
4. FAPH-only checkpointing produced a new shortcut;
5. therefore the real contribution is a multidimensional evaluation protocol, not a final production model.

## Current topic inventory from the results chapter

Approximate page ranges from current TOC.

| Topic | Current location | Approx. pages | Narrative role | Recommendation |
|---|---:|---:|---|---|
| Training/evaluation pipeline reconstruction | 3.1 | <1 | Establishes reproducibility | **Keep short**. Essential, but no need for long tool detail. |
| Public `marvin` control experiment | 3.2 | ~1 | Shows pipeline sanity check | **Keep**. Strong reviewer-friendly evidence. |
| Current state / transition to Estonian | 3.3 | <1 | Bridge | **Merge** into surrounding prose. |
| v1--v8 model version table | 3.4.1 | ~1 | Experiment diary / lineage | **Compress heavily**. Keep only versions that teach a methodological lesson. Full lineage belongs in repo, not thesis body. |
| Initial misleading result | 3.4.2 | ~1 | Hook / problem | **Keep**. This is interesting and motivates the thesis. |
| Fair comparison with identical test sets | 3.4.3 | ~1 | Method correction | **Keep but compact**. |
| Degradation valley | 3.4.4 | ~1 | Secondary interpretation | **Mention in passing** unless tied directly to main claim. |
| Iterative v4--v6 improvement | 3.4.5 | ~1 | Historical model diary | **Compress/merge** with initial misleading result. |
| Data leakage + corrected holdout evaluation | 3.4.6 | ~2 | Core methodological finding | **Keep**. This is one of the thesis’s best parts. |
| Cross-microphone H2 test | 3.4.7 | ~1 | Diagnostic aside | **Mention in passing** or merge with asymmetry. |
| Cross-microphone generalisation asymmetry | 3.4.8 | ~1 | Useful insight | **Keep compact**; can be one paragraph in discussion. |
| Cross-language FAPH | 3.4.9 | ~1 | Interesting but side-branch | **Mention in passing**. Good sentence/table footnote, not full subsection. |
| Dataset scaling possibilities | 3.4.10 | ~1 | Future-work/resource context | **Move to discussion/future work or compress to one paragraph**. |
| Expert-model consensus | 3.4.11 | ~6 | Major result, but overlong | **Keep result, cut architecture/history.** Aim 2 pages. |
| Residual-connection ablation | 3.4.12 | ~1 | Architecture side result | **Mention in passing** or one row in ablation summary table. |
| SpecAugment ablation | 3.4.13 | ~2 | Architecture/training side result | **Mention in passing** unless needed for core narrative. |
| Positive-data pollution audit | 3.5.1 | ~2 | Core methodological finding | **Keep**, but make it crisp and story-like. |
| Training pipeline quality controls | 3.5.2 | ~1 | Implementation detail | **Compress** to bullets or one paragraph. |
| New phrase-completeness test sets | 3.5.3 | ~1 | Core protocol contribution | **Keep**. |
| v18 cleaned-positive results | 3.5.4 | ~2 | Shows cleaning alone not enough | **Keep but compact**. |
| Iterative metric expansion conclusion | 3.5.5 | ~1 | Good synthesis | **Keep, maybe move to discussion**. |
| Checkpoint-FAPH setup | 3.6 | ~1 | Third audit setup | **Keep short**. |
| Checkpoint experiment results | 3.6.1 | ~2 | Core negative result | **Keep but cut table/prose density**. |
| Checkpoint consensus combinations | 3.6.2 | ~1 | Interesting but can distract | **Mention in passing** unless needed for sub-1 FAPH caveat. |
| Manual listening + acoustic shortcut | 3.6.3 | <1 | Reviewer-friendly concrete evidence | **Keep**. Human-readable and memorable. |
| Metric/objective divergence conclusion | 3.6.4 | ~2 | Core methodological synthesis | **Keep but make concise**. |
| User-test status | 3.7 | ~1 | Honesty / limitation | **Keep short**. |

## Suggested reviewer-friendly structure

Instead of model chronology, use a discovery narrative:

### 3.1 Pipeline sanity check

- `marvin` control experiment.
- What it proved and what it did not prove.

### 3.2 First audit: clip-level scores were misleading

- Initial v1--v8 result in one compact table or paragraph.
- MacBook real-time false fires as the hook.
- Data leakage finding.
- Corrected holdout + FAPH result.
- Methodological conclusion.

### 3.3 Second audit: the positive class did not always mean the full phrase

- v17 looked good, then failed on prefix behaviour.
- Positive pollution categories.
- New phrase-completeness tests.
- v18 result: cleaning helps but does not solve full phrase selectivity.

### 3.4 Third audit: FAPH-only checkpointing learned to be silent

- Checkpoint-FAPH idea.
- Result: low FAPH but unacceptable recall.
- Manual listening/acoustic shortcut.
- Conclusion: checkpoint selection must be composite.

### 3.5 Best observed operating points and deployment status

- v16c as stable single-model pilot candidate.
- expert consensus as sub-1 FAPH diagnostic but recall-limited.
- user-test status and why not a production claim.

This would be easier to read than the current long run-by-run structure.

## What can become “passing mention”

These are valuable work, but they do not need full subsections in the thesis body:

- Full v1--v18 chronology.
- Degradation valley details.
- Cross-language FAPH table.
- Dataset scaling inventory of 8000+ hours.
- Residual connection ablation.
- SpecAugment ablation.
- Expert B v1/v2 training-composition mini-story.
- Long comparison to published systems.
- Flash-size feasibility details beyond one sentence.

Suggested phrasing pattern:

> Täiendavad diagnostilised katsed (ristkeelne FAPH, residuaalühenduste ja SpecAugmenti ablatsioonid ning ekspertmudelite komponentide võrdlus) kinnitasid sama üldist mustrit: üksik mõõdik paranes sageli teise arvelt. Kuna need katsed ei muutnud lõplikku järeldust, käsitletakse neid siin ainult kontrollidena, mitte eraldi põhiväitena.

## Possible compression targets

| Area | Current | Realistic target | Potential saving |
|---|---:|---:|---:|
| v1--v8 chronology and early model diary | ~10 pages | 3--4 pages | 6--7 pages |
| Expert consensus section | ~6 pages | 2 pages | 4 pages |
| Ablations (residual + SpecAugment) | ~3 pages | 0.5--1 page | 2 pages |
| v17/v18 phrase audit | ~7 pages | 4 pages | 3 pages |
| Checkpoint-FAPH section | ~7 pages | 3--4 pages | 3--4 pages |
| Total realistic saving | 35 pages | 18--22 pages | 13--17 pages |

A realistic closeout compression could reduce the main body from **58 pages to ~41--45 pages**. Reaching the formal usual range maximum of **35 pages** would require aggressive moves to appendix or removal of most diagnostic detail.

## Recommendation

Given the hard deadline, do **not** try to make the thesis a 35-page thesis unless the supervisor explicitly demands it. Instead:

1. Remove formal blockers (done: dummy appendices, fourth-level headings, summary Q/A, abstract compression).
2. Make the results chapter reviewer-friendly by cutting chronology and side-branches.
3. Aim for **~42 pages main body** if time allows.
4. If the body remains above 35 pages, explicitly justify: the work is an experimental ML/prototype thesis with many tables, but the main story has been compressed to the three-audit narrative.
