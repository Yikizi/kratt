# Kratt thesis closeout plan

> For Hermes: planning only. Do not implement from this file unless explicitly asked.

Goal
- Close the Kratt bachelor thesis cleanly without uncontrolled scope creep, while still using agentic engineering to accelerate high-value polishing, synthesis, and validation work.

Current context / assumptions
- Strongest contribution is not just “trained an Estonian wake word”, but “built and corrected a realistic evaluation methodology for low-resource Estonian wake-word detection under deployment constraints”.
- Repo contains substantial real work, but working tree is noisy: many modified and untracked files.
- Thesis text has real substance but still shows draft markers, terminology drift, uneven chapter maturity, and a too-wide story.
- User testing appears to be critical-path if it is a hard thesis requirement. If it cannot be completed credibly in time, the thesis narrative must be narrowed now rather than hoping to “fit everything in”.
- Goal is not maximal feature expansion. Goal is a strong, defensible submission.

Recommended strategic stance
- Default rule for all new work: only do work that strengthens one of these four things:
  1. thesis claim clarity
  2. evidence quality
  3. document completion/polish
  4. submission hygiene / reproducibility
- Everything else is optional.
- New engineering work is allowed only when it directly closes an evidence gap or simplifies the story.

Primary thesis story to lock now
- Recommended main claim:
  - This thesis studies how to build and realistically evaluate an Estonian wake-word detector for constrained smart-home hardware, with emphasis on avoiding misleading results from weak evaluation setups.
- Supporting but secondary threads:
  - Android false-trigger logger as measurement instrument
  - ESP32 deployment as target platform / realism anchor
  - model iteration history as empirical path
  - agentic engineering as process accelerator, not central scientific contribution
- Demote unless fully evidenced soon:
  - broad “best framework” claims
  - ambitious multi-model system story if it is not central to the final measured result
  - large new feature branches unrelated to evaluation or thesis completion

Decision framework for scope control
- Before starting any task, ask:
  1. Does this directly improve the thesis argument or evidence?
  2. Will this likely appear in the final document?
  3. Can this be finished and integrated in 1 day or less?
  4. Is it more valuable than polishing a weak chapter or cleaning evidence presentation?
- If fewer than 3 answers are “yes”, do not do it now.

Priority stack

## Priority 0 — Make the thesis finishable this week
Objective
- Remove ambiguity about what “done” means.

Actions
1. Write a one-paragraph thesis claim statement and pin it at the top of your own notes.
2. Decide today whether user testing is:
   - mandatory and feasible in time,
   - mandatory but must be reframed as pilot/partial,
   - or optional for the final claim.
3. Freeze which comparison threads are definitely in scope for the written thesis.
4. Explicitly mark all non-essential work as backlog.

Deliverable
- One locked problem statement
- One locked chapter outline
- One locked “not doing now” list

Why this is critical
- This prevents the last-week death spiral where engineering expands while writing lags.

## Priority 1 — Finish the document skeleton before improving the system further
Objective
- Get every chapter to “complete but rough” before doing more ambitious experiments.

Actions
1. Convert all chapters from fragment state into full draft state.
2. Remove visible draft markers:
   - placeholders like §2.X
   - “lisatakse hiljem” wording
   - empty/underweight summary
3. Make chapter boundaries strict:
   - Introduction = question + scope + contribution framing
   - Methodology = datasets, splits, metrics, setup, protocol
   - Implementation = system and tooling
   - Results = measured outcomes only
   - Discussion = interpretation, limits, implications
   - Summary = concise answer to research question
4. Add one explicit subsection on limitations and scope boundaries.

Deliverable
- A complete readable full thesis draft, even if still ugly.

Why this is critical
- An imperfect full thesis is much safer than a strong but partial one.

## Priority 2 — Lock the evidence and tables
Objective
- Ensure every strong claim in the document maps to a stable figure/table/result.

Actions
1. Make a “claim -> evidence” matrix:
   - claim
   - supporting table/figure
   - source script / source file
   - current confidence level
2. Freeze the final evaluation subsets that will actually be cited.
3. Re-run only the minimum high-value evaluations needed for final tables.
4. Save outputs in one stable location for citation.
5. Prefer fewer clean tables over many partially trustworthy results.

Deliverable
- Final thesis tables/figures list
- Reproducible source paths for each

Why this is critical
- Your thesis strength depends on credible evaluation, not the number of model versions trained.

## Priority 3 — Handle the biggest risk item explicitly: user testing
Objective
- Prevent user testing from becoming a vague looming blocker.

Actions
1. Decide if user testing is truly required for acceptance or just highly desirable.
2. If required, immediately reduce ambition:
   - prefer a smaller, well-described pilot over a half-chaotic 20–30 person plan that never stabilizes
   - define exact protocol, recruitment path, consent handling, and analysis output
3. If not realistically finishable, re-scope the thesis wording now so the core contribution stands without overpromising user-study evidence.

Deliverable
- One written decision: full study, pilot study, or not core claim

Why this is critical
- This is the likeliest source of deadline panic if left fuzzy.

## Priority 4 — Clean repo and artifact boundaries
Objective
- Make the project look stable, intentional, and defensible.

Actions
1. Split current working tree into coherent buckets:
   - thesis text edits
   - Android/logger changes
   - wake-word evaluation changes
   - tooling/demo changes
   - local artifacts/logs/models not for git
2. Fix ignore policy for runtime/output artifacts.
3. Decide where final cited outputs live.
4. Make the repo navigable for a supervisor/examiner.

Deliverable
- Smaller, understandable git state
- Cleaner README/source-of-truth pointers

Why this matters
- Repo hygiene will not save a weak thesis, but bad hygiene can undermine confidence in a strong one.

## Priority 5 — Do only the highest-leverage engineering from here
Allowed engineering work
- Anything that directly improves final evidence or makes a chapter honest and complete.

Good examples
- fixing evaluation scripts that affect final tables
- generating one missing final figure/table
- cleaning a measurement instrument you actually cite
- writing one script that stabilizes result collection

Bad examples right now
- broad refactors for elegance
- major new demo features
- framework expansion without thesis payoff
- speculative model branches with weak chance of making the final document

Agentic engineering playbook

Use agents aggressively for these tasks
1. Text polishing passes
- terminology normalization
- chapter-level language cleanup
- finding placeholders/inconsistencies
- converting notes into draft prose

2. Evidence packaging
- build claim-evidence matrices
- trace numbers in thesis back to scripts and result files
- audit whether tables match source data

3. Repo and docs cleanup planning
- identify untracked artifact classes
- propose .gitignore / folder policy changes
- check README / CLAUDE / docs consistency

4. Focused code review
- sample critical scripts only
- verify no obvious bugs in final evaluation path
- review only files that affect final thesis outputs

5. Presentation synthesis
- create defense narrative
- turn thesis into slide outline
- produce “what changed after methodology fix” narrative

Do NOT use agents for these unless explicitly justified
- open-ended feature ideation
- wide refactors across the repo
- multiplying experiment branches just because agents make it easy

Suggested operating model for the next phase

Daily loop
1. Morning: choose one thesis bottleneck only.
2. Spawn 2–3 narrow agent tasks in parallel.
3. Manually review and merge results.
4. Spend a human block on the hardest judgment call yourself.
5. End day by updating source-of-truth docs and thesis TODO.

Weekly rule
- At least 60–70% of effort should now go to writing, synthesis, evidence packaging, and cleanup.
- No more than 30–40% should go to fresh engineering/experiments unless a result-critical blocker appears.

Concrete “stop doing” list
- Stop chasing broad new branches just because they are interesting.
- Stop expanding comparative claims you may not fully support.
- Stop treating every repo rough edge as equally urgent.
- Stop doing engineering that does not clearly enter the thesis.

Concrete “do now” list
1. Lock thesis claim and contribution wording.
2. Finish rough full draft across all chapters.
3. Decide user-testing scope concretely.
4. Freeze final evaluation outputs and tables.
5. Clean repo enough that final artifacts and source-of-truth docs are obvious.
6. Then do language polish and defense packaging.

Likely files to touch soon
- docs/PROJECT_TODO.md
- docs/research/agentic-thesis-positioning-and-shortcomings-2026-04-14.md
- docs/thesis/thesis-tex-estonian/chapters/introduction.tex
- docs/thesis/thesis-tex-estonian/chapters/first_chapter.tex
- docs/thesis/thesis-tex-estonian/chapters/second_chapter.tex
- docs/thesis/thesis-tex-estonian/chapters/third_chapter.tex
- docs/thesis/thesis-tex-estonian/chapters/summary.tex
- README.md
- .gitignore
- whichever evaluation scripts generate final cited metrics

Validation / done criteria
- You can describe the thesis in 3 sentences without apologizing or branching into side stories.
- Every major claim maps to a stable table/figure/result.
- No visible placeholders remain in the thesis source.
- Final chapter set reads like one argument, not a lab notebook.
- Repo has a clear source-of-truth path for results and docs.
- New work items are being rejected unless they clearly strengthen the final submission.

Final recommendation
- From this point, optimize for closure quality, not exploration rate.
- Agentic engineering should now make you faster at convergence: drafting, auditing, packaging, polishing, and selectively verifying.
- The winning move is not “do less interesting work forever”; it is “earn the right to do extra work only after the thesis is already finishable”.
