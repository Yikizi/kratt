# Thesis automation MVP

A lean, writable automation that now acts as a **compression-first thesis editor**:
it shortens existing prose, removes repetition, normalizes Estonian terminology,
cleans citation/caption style, and only adds text for mandatory final evidence.
It still uses Claude Code, persistent git worktrees, chapter-scoped lanes, and
daily consolidation.

Source of truth: `.hermes/thesis-automation/`.

## Architecture at a glance

```
hourly  ─── pick next lane ─── reviewer ─── writer ─── ≤1 compression commit (lane branch only)
daily   ─── triage lane commits ─── accept tightening / reject additive drift
            └── then reset all lane branches/worktrees to fresh main
weekly  ─── rerun thesis-quality-review ─── meta summary (compression signal + guidance tweaks)
```

Main rules:

- Hourly runs write only inside a lane worktree — **never** to `main`.
- Daily consolidation is the only thing that moves changes onto `main`.
- Rejected work is distilled into 1–3 short positive lane-guidance lines, then its
  branch is reset. Lessons survive, clutter does not.
- One scoped improvement per run. One commit max per run.
- Thesis prose changes should be net-shorter by default: delete, merge, translate
  into clearer Estonian, or calibrate claims instead of adding more explanation.
- Additive drafting is paused except for mandatory final evidence such as real
  user-test results already present in tracked artifacts.

## The 14 lanes

Defined in `.hermes/thesis-automation/lanes/lanes.json`. Most lane IDs are kept
stable for branch/worktree compatibility, but their focus has shifted from
additive drafting to thesis closeout editing.

| id                           | target files                              | compression-mode focus                                                  |
|------------------------------|-------------------------------------------|-------------------------------------------------------------------------|
| terminology                  | all chapters (rotating)                   | idiomatic Estonian terminology; remove unnecessary English glosses       |
| chapter-readiness            | all chapters (rotating)                   | prune repeated claims and over-explained transitions                     |
| committee-questions          | intro, third, summary                     | sharpen existing answers to likely defense questions                     |
| claim-evidence               | third, second, intro                      | calibrate claims to existing evidence; soften instead of expanding       |
| literature-gap               | second, intro                             | concise prior-art positioning with bibliography citations                |
| formal-compliance-writer     | all chapters (rotating)                   | citation hygiene, short captions, quotes, dashes, units, refs            |
| summary-tightening           | summary.tex                               | compressed, self-contained summary                                      |
| methodology-tightening       | third_chapter.tex                         | compress reproducibility detail; remove log-like parameter dumps         |
| intro-builder                | introduction.tex                          | introduction compression, not new motivation                             |
| implementation-narrative     | third_chapter.tex                         | compress Android/ESP32/ESPHome implementation detail                     |
| evaluation-closeout          | second, third                             | compress result history; add only final user-test results when present   |
| alternatives-comparison      | first, intro                              | concise non-duplicative alternatives comparison                          |
| research-note                | docs/research/thesis-writing-research-queue.md | **paused** unless a missing source is explicitly approved       |
| distill-sentence             | intro, first, second, third               | **paused** unless an approved mandatory evidence note must be inserted   |

`research-note` and `distill-sentence` are inactive during compression mode.
Reactivate them only when a specific missing source/evidence gap is approved by
the author.

## Ordered two-phase lane cycle

`run-research-distill-cycle.sh` is retained for compatibility, but in compression
mode it exits successfully without work when `research-note` / `distill-sentence`
are inactive. The two-phase additive research-to-sentence cycle should remain
paused until the author explicitly approves a missing source/evidence gap.

Each lane has a persistent branch `cron/<lane>` and persistent worktree
`.claude/worktrees/cron-<lane>`.

## Hourly flow

`.hermes/thesis-automation/run-hourly.sh` (delegates to `bin/runner.py hourly`).

1. Pick the next lane in a deterministic rotation (`state/rotation.json`).
2. Pick the next target file in that lane's rotation.
3. Run a **reviewer** call (`claude --print`) — proposes exactly one
   compression/style/citation improvement.
4. Run a **writer** call (`claude --print --dangerously-skip-permissions` inside
   the lane worktree) — either applies a surgical net-shorter edit + commits on
   the lane branch, or prints `PUSHBACK: …` and does nothing.
5. Append a structured JSON line to `logs/hourly/<date>.jsonl`.

Pushback is a first-class outcome and counted separately from `no_change` / `committed`.

### Prompts

- `prompts/reviewer.md` — narrow, one-finding-only compression/style review
- `prompts/writer.md` — surgical writer with explicit additive-drift pushback
- `prompts/consolidator.md` — strict-JSON consolidation output; rejects additive drift
- `prompts/weekly.md` — short markdown meta summary focused on compression signal

Each lane contributes `reviewer_extra` / `writer_extra` lines and its own
memory (`memory/<lane>.json`).

## Daily consolidation

`.hermes/thesis-automation/run-daily-consolidation.sh` →
`bin/runner.py daily`.

1. Stash non-automation WIP if needed, run `git pull --ff-only origin main`,
   then restore/reconcile the stashed WIP. Set `KRATT_THESIS_AUTOMATION_PULL=0`
   to disable. Diverged histories stop the daily run rather than creating merges.
2. For every active lane, list commits in `main..cron/<lane>` since the last
   consolidation.
3. Show full diffs to a consolidator Claude call; require strict-JSON output with
   `accept | reject | defer` per commit + positive guidance lines.
4. Accept only tightening, Estonianization, citation/caption hygiene, or mandatory
   evidence insertions; reject additive drift.
5. Stash non-automation WIP if needed, cherry-pick accepted commits onto `main`,
   then restore/reconcile the stashed WIP.
6. Distill rejected commits into ≤ 3 short positive guidance lines per lane
   (rolling window). Optionally 1 global line.
7. Refresh every lane worktree/branch to the new `main`.
8. Push `main` once per daily run with `git push origin main:main` unless conflict
   recovery left the repository unsafe. Set `KRATT_THESIS_AUTOMATION_PUSH=0` to disable.
9. Write `logs/daily/<timestamp>.json` and update `state/rotation.json`.

Rejected commits disappear from branch history on refresh, but their rejection
reason + distilled line live on in `memory/<lane>.json.rejected_refs` (rolling last 20).

## Weekly meta-review

`.hermes/thesis-automation/run-weekly-review.sh` →
`bin/runner.py weekly`.

1. Re-run the thesis-quality-review skill via `claude --print`.
2. Collect the latest and previous review, all lane memory, last-7-days hourly
   stats, last-7-days daily-consolidation logs.
3. Produce a short Markdown meta summary in `logs/weekly/<timestamp>-meta.md`
   (readiness delta, lane signal, guidance updates, next-week emphasis).

## Runner model and budget

`runner.py` calls `claude --print` with:

- `--max-budget-usd` set per lane/task (0.5 reviewer, 1.0 writer and reconciler/fixer,
  1.5/2.0 consolidation/meta, 3.0 weekly rerun),
- `--tools default` (all built-in Claude tools),
- `--model` only when `CLAUDE_MODEL` is set in environment.

If `CLAUDE_MODEL` is not set, Claude uses its local default model.

## Layout

```
.hermes/thesis-automation/
├── bin/runner.py                     # hourly | daily | weekly implementation
├── lanes/lanes.json                  # lane definitions
├── memory/
│   ├── global.json                   # 1–5 north-star lines
│   └── <lane>.json                   # ≤3 active guidance lines + rejected_refs log
├── prompts/                          # reviewer, writer, consolidator, weekly
├── state/rotation.json               # cursors + last consolidation/weekly
├── logs/
│   ├── hourly/<YYYY-MM-DD>.jsonl
│   ├── daily/<timestamp>.json
│   └── weekly/<timestamp>-meta.md
├── bootstrap-worktrees.sh            # idempotent lane branch + worktree setup
├── run-hourly.sh                     # cron/launchd entrypoints
├── run-daily-consolidation.sh
└── run-weekly-review.sh
```

Worktrees themselves live at `.claude/worktrees/cron-<lane>` and are git-ignored
as part of `.claude/`.

## Setup / bootstrap

```bash
./.hermes/thesis-automation/bootstrap-worktrees.sh
```

Idempotent. Creates missing `cron/<lane>` branches at current `main` and missing
worktrees at the expected paths. Safe to re-run any time.

## Running manually

```bash
# one hourly run on the next lane in rotation
./.hermes/thesis-automation/run-hourly.sh

# force a specific lane (bypasses rotation advance for that lane)
./.hermes/thesis-automation/bin/runner.py hourly --lane terminology

# daily consolidation
./.hermes/thesis-automation/run-daily-consolidation.sh

# weekly meta review
./.hermes/thesis-automation/run-weekly-review.sh
```

## Scheduling

Two options, in order of preference.

### Option A — macOS launchd (persistent, runs without Claude Code open)

Install the serial scheduler and dashboard plists. In compression mode the scheduler
runs hourly, daily, and weekly jobs through `bin/scheduler.py`, so automation jobs
do not overlap. The dashboard plist keeps `kratt thesis-dashboard` available at
`http://127.0.0.1:8765`.

```bash
cp .hermes/thesis-automation/launchd/ee.taltech.kratt.thesis-automation.scheduler.plist ~/Library/LaunchAgents/
cp .hermes/thesis-automation/launchd/ee.taltech.kratt.thesis-dashboard.plist ~/Library/LaunchAgents/
launchctl load -w ~/Library/LaunchAgents/ee.taltech.kratt.thesis-automation.scheduler.plist
launchctl load -w ~/Library/LaunchAgents/ee.taltech.kratt.thesis-dashboard.plist
```

Do **not** load the legacy per-job launchd plists (`hourly`, `daily`, `weekly`,
`research-distill`) at the same time as the serial scheduler, or jobs can overlap.
The research-distill plist is disabled in compression mode. Unload with
`launchctl unload -w <plist>` to pause.

### Option B — Claude Code in-session cron (dev-loop only)

From an open `claude` REPL in this repo:

```
CronCreate cron="7 * * * *" prompt="Run ./.hermes/thesis-automation/run-hourly.sh and report the JSON line it prints." recurring=true durable=true
CronCreate cron="11 3 * * *" prompt="Run ./.hermes/thesis-automation/run-daily-consolidation.sh and report counts." recurring=true durable=true
CronCreate cron="17 4 * * 1" prompt="Run ./.hermes/thesis-automation/run-weekly-review.sh and print the meta path." recurring=true durable=true
# Compression mode: do not schedule research-distill unless an additive evidence gap is explicitly approved.
```

Session jobs auto-expire after 7 days — launchd is what you want for actual
always-on operation.

## Inspecting logs / state

```bash
tail -n 20 .hermes/thesis-automation/logs/hourly/$(date +%F).jsonl | jq .
ls -t .hermes/thesis-automation/logs/daily/ | head
cat .hermes/thesis-automation/state/rotation.json | jq .
cat .hermes/thesis-automation/memory/global.json | jq .
for f in .hermes/thesis-automation/memory/*.json; do echo "== $f =="; jq '.lane, .guidance' "$f"; done
git log --oneline main..cron/terminology        # pending lane work
git log --oneline -5 main                        # what consolidation accepted
```

## Pausing or repairing a lane

Pause a lane without removing it — set `active: false` for it in `lanes/lanes.json`.
The hourly runner will skip inactive lanes. Reactivate and run bootstrap/refresh
before using a paused lane again.

Repair a broken worktree:

```bash
git worktree remove --force .claude/worktrees/cron-<lane>
./.hermes/thesis-automation/bootstrap-worktrees.sh
```

Reset one lane back to `main` without running consolidation:

```bash
git -C .claude/worktrees/cron-<lane> reset --hard origin/main 2>/dev/null \
  || git -C .claude/worktrees/cron-<lane> reset --hard main
```

Clear a lane's guidance memory: edit `memory/<lane>.json` and set
`"guidance": []`.

## Guardrails built into the system

- Hourly writer must stay inside `TARGET_FILE` and produce ≤ 1 commit.
- Hourly writer must push back on additive prose unless it replaces longer text
  or inserts mandatory final evidence.
- Consolidator will not cherry-pick onto `main` if the working tree is dirty.
- Lane refresh uses a hard reset to the new `main`, with `git clean` that
  preserves `.claude/` so worktree machinery survives.
- Per-lane `rejected_refs` window is capped at 20 entries.
- Per-lane active guidance is capped at 3 lines. Global at 5.
- Use `kratt thesis-style-audit` to spot chapter footnotes, English glosses,
  Englishisms, TODO artefacts, and overlong captions before consolidation.
