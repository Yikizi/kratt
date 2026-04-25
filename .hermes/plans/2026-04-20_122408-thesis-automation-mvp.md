# Kratt thesis automation MVP — consolidated implementation plan

Goal
- Build a lean, writable thesis-improvement automation system for the Kratt repository using Claude Code, persistent worktrees, chapter-scoped workflow pairs, daily consolidation, distilled workflow memory, and weekly meta-review.
- The system must deliver small, real improvements without letting the thesis drift apart.

Core philosophy
- Keep it lean. No overengineered orchestration, no big lock manager, no giant metrics stack.
- One hourly run should produce at most one small, scoped commit in one workflow worktree.
- Daily consolidation is the main stabilizer.
- Learning from rejected work must be preserved in distilled guidance, not by keeping bad branches alive.

Constraints
- Use Claude Code as the execution engine.
- Use persistent git worktrees, one per workflow.
- Use workflow-specific branches tied to those worktrees.
- Use daily consolidation to decide what reaches `main`.
- After consolidation, refresh workflow branches/worktrees to the latest accepted `main`.
- Add a lightweight learning layer so rejected ideas do not keep recurring.
- Prefer chapter-scoped operations.
- Keep prompts, files, and logs simple and inspectable.

Non-goals
- No complex locking subsystem unless real collisions appear later.
- No patch-only workflow as the default.
- No direct autonomous writing on `main`.
- No huge KPI dashboard in MVP.

## MVP architecture

### 1. Persistent workflow lanes
Create 8 persistent workflow lanes, each with:
- one branch
- one worktree
- one workflow memory file
- one run log stream

Suggested lane IDs:
1. terminology
2. chapter-readiness
3. committee-questions
4. claim-evidence
5. literature-gap
6. formal-compliance-writer
7. summary-tightening
8. methodology-tightening

Suggested worktree naming:
- `.claude/worktrees/cron-<lane>`

Suggested branch naming:
- `cron/<lane>`

### 2. Hourly execution model
Each hourly slot runs exactly one lane.
Each lane run is a pair flow:
1. reviewer/suggester agent
2. writer/pushback agent

Hard boundaries for hourly runs:
- one lane only
- one chapter/file focus only
- one problem only
- one small commit max

The writer may write real files in the lane worktree and commit, but never to `main` directly.

### 3. Daily consolidation
Once per day, run a consolidation pass that:
1. reviews all lane commits created since the previous consolidation
2. marks each result as `accept`, `reject`, or `defer`
3. integrates accepted changes into `main`
4. runs a rejected-work distillation step
5. refreshes all lane branches/worktrees to the newly accepted `main`

For MVP, simple refresh is enough:
- update `main`
- for each lane branch: reset hard to `main`
- keep the worktree paths persistent

### 4. Learning layer
Rejected or dropped work should not disappear completely.
Before lane reset, distill rejected work into tiny, positive, workflow-specific guidance.

Important rule:
- do not store long negative histories in prompts
- store at most 1–3 short active guidance lines per lane
- phrasing should be positive and steering-oriented, not “DO NOT DO X” style

Examples of good guidance:
- “Prefer tightening an existing claim with local evidence rather than opening a new side thread.”
- “Keep edits chapter-local and avoid reframing the thesis contribution at lane level.”
- “Favor terminology normalization that preserves meaning over broad stylistic rewriting.”

Also maintain a tiny global guidance file with 1–3 thesis-wide north-star reminders.

### 5. Weekly meta-review
Once per week:
- run the thesis-quality-review skill/process again
- compare against the latest saved review
- inspect which lanes are producing accepted value versus churn
- refresh lane guidance if needed

## Required deliverables

Implement the following inside the repo.

### A. Documentation
Create a concise docs page that explains:
- what the automation system is
- the 8 lanes
- hourly flow
- daily consolidation flow
- workflow memory concept
- weekly meta-review concept
- how to inspect logs
- how to manually pause or repair a lane if needed

Suggested path:
- `docs/automation/thesis-automation-mvp.md`

### B. State directories
Create a small internal automation area, for example:
- `.hermes/thesis-automation/lanes/`
- `.hermes/thesis-automation/logs/`
- `.hermes/thesis-automation/memory/`
- `.hermes/thesis-automation/state/`

### C. Lane definitions
Create one structured file describing all 8 lanes.
Each lane definition should include at minimum:
- lane id
- chapter/file target rotation
- reviewer prompt path or text reference
- writer prompt path or text reference
- worktree path
- branch name
- active/inactive flag

Suggested path:
- `.hermes/thesis-automation/lanes/lanes.json`

### D. Workflow memory format
Implement simple per-lane memory files, plus a tiny global guidance file.
Suggested paths:
- `.hermes/thesis-automation/memory/global.json`
- `.hermes/thesis-automation/memory/<lane>.json`

Each lane memory file should contain:
- lane name
- updated timestamp
- up to 3 active guidance lines
- source references to rejected commits or rejection reasons

### E. Hourly runner
Implement one runner that:
- determines the current lane based on deterministic rotation
- checks out the correct worktree/lane
- invokes reviewer then writer in sequence
- produces at most one small commit
- logs the run outcome as structured JSON

Suggested path:
- `.hermes/thesis-automation/run-hourly.sh`
- or a small Python wrapper if that is cleaner

### F. Daily consolidation runner
Implement a runner that:
- scans lane commits since last consolidation
- reviews them
- integrates accepted changes into `main`
- distills rejected work into lane guidance
- refreshes lane branches/worktrees to `main`
- logs what was accepted/rejected and why

Suggested path:
- `.hermes/thesis-automation/run-daily-consolidation.sh`

### G. Weekly meta-review runner
Implement a runner that:
- reruns the thesis-quality-review baseline/follow-up process
- logs deltas and lane-level observations in a simple summary file

Suggested path:
- `.hermes/thesis-automation/run-weekly-review.sh`

### H. Worktree bootstrap / repair utility
Implement a simple bootstrap command that:
- creates the 8 lane branches if missing
- creates/repairs the 8 persistent worktrees
- ensures they point to the expected paths

Suggested path:
- `.hermes/thesis-automation/bootstrap-worktrees.sh`

## Git policy

MVP policy:
- lane writers commit only inside their own worktree branch
- consolidation is the only step that updates `main`
- accepted changes should be integrated in the simplest robust way available
- rejected changes should not survive as lane history after refresh; instead, their lesson is distilled into lane memory

Use simple, inspectable commit messages.
Examples:
- `docs(thesis): normalize terminology in methodology chapter`
- `docs(thesis): tighten committee-facing explanation in discussion`
- `docs(thesis): align claim with evidence in results chapter`

## Logging policy

Keep logs structured and lightweight.

Per hourly run, log at least:
- timestamp
- lane
- target chapter/file
- reviewer summary
- writer summary
- commit sha or no-op status
- result classification (`committed`, `no_change`, `failed`)

Per consolidation run, log at least:
- timestamp
- reviewed lane commits
- accepted commit refs
- rejected commit refs
- rejection reasons
- lane memory updates
- refreshed branches/worktrees

## Prompting policy

Reviewer prompts should:
- stay narrow
- focus on one chapter/file
- identify one highest-value improvement only

Writer prompts should:
- either implement a small subset of suggestions
- or push back and keep the text unchanged if the suggestions are not worth applying
- avoid broad rewrites
- avoid changing the thesis’s top-level framing

## Quality guardrails for MVP

Keep these as process rules, not giant infra:
- one lane per hour
- one scoped improvement per run
- one commit max per run
- chapter-local edits preferred
- no direct main writes from hourly flows
- daily consolidation decides what survives
- rejected work becomes distilled guidance, not branch clutter

## Practical expectations

This MVP does not need to be perfect.
It needs to be:
- understandable
- restartable
- inspectable
- cheap to operate
- good enough to begin generating disciplined progress

## Build instructions for Claude Code

Please implement the system now in the Kratt repository.
Specific expectations:
- create the docs
- create the directory structure
- create lane definitions and memory formats
- implement bootstrap, hourly, daily consolidation, and weekly review scripts
- keep everything lean and readable
- prefer simple shell/Python glue over a large framework
- if Claude Code cron configuration is practical from the current environment, wire it up; otherwise document the exact final command(s) needed and implement all supporting machinery
- make the system runnable after implementation
- leave a concise final summary in the terminal of what was built and how to start/verify it

Success criteria
- repo contains a coherent automation MVP
- 8 lanes are defined
- persistent worktree strategy is implemented
- hourly runner exists
- daily consolidation exists
- learning layer exists
- weekly review runner exists
- logs/state layout exists
- docs explain the system clearly
- the implementation is ready to run or already running if environment permits
