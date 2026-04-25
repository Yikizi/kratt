# Thesis automation MVP

A lean, writable automation that nudges the thesis forward in small,
inspectable steps using Claude Code, persistent git worktrees, chapter-scoped
lanes, and daily consolidation.

Source of truth: `.hermes/thesis-automation/`.

## Architecture at a glance

```
hourly  ─── pick next lane ─── reviewer ─── writer ─── ≤1 commit (lane branch only)
daily   ─── triage lane commits ─── accept to main / reject with distilled guidance
            └── then reset all lane branches/worktrees to fresh main
weekly  ─── rerun thesis-quality-review ─── meta summary (lane signal + guidance tweaks)
```

Main rules:

- Hourly runs write only inside a lane worktree — **never** to `main`.
- Daily consolidation is the only thing that moves changes onto `main`.
- Rejected work is distilled into 1–3 short positive lane-guidance lines, then its
  branch is reset. Lessons survive, clutter does not.
- One scoped improvement per run. One commit max per run.

## The 8 lanes

Defined in `.hermes/thesis-automation/lanes/lanes.json`.

| id                           | target files                              | focus                                                                  |
|------------------------------|-------------------------------------------|------------------------------------------------------------------------|
| terminology                  | all chapters (rotating)                   | normalize Estonian technical vocabulary / acronyms                     |
| chapter-readiness            | all chapters (rotating)                   | flow, signposting, paragraph coherence                                 |
| committee-questions          | intro, third, summary                     | anticipate one defense committee question and tighten the passage       |
| claim-evidence               | third, second, intro                      | each claim backed by number / table / cited source                     |
| literature-gap               | second, intro                             | positioning vs existing Estonian NLP / wake-word literature            |
| formal-compliance-writer     | all chapters (rotating)                   | TalTech formal style: quotes, dashes, refs, captions                   |
| summary-tightening           | summary.tex                               | crisp self-contained summary aligned to contributions                  |
| methodology-tightening       | third_chapter.tex                         | reproducibility of wake-word methodology                               |

Each lane has a persistent branch `cron/<lane>` and persistent worktree
`.claude/worktrees/cron-<lane>`.

## Hourly flow

`.hermes/thesis-automation/run-hourly.sh` (delegates to `bin/runner.py hourly`).

1. Pick the next lane in a deterministic rotation (`state/rotation.json`).
2. Pick the next target file in that lane's rotation.
3. Run a **reviewer** call (`claude --print`, read-only tools) — proposes exactly one
   highest-value improvement.
4. Run a **writer** call (`claude --print --dangerously-skip-permissions` inside
   the lane worktree) — either applies a surgical edit + commits on the lane
   branch, or prints `PUSHBACK: …` and does nothing.
5. Append a structured JSON line to `logs/hourly/<date>.jsonl`.

Pushback is a first-class outcome and counted separately from `no_change` / `committed`.

### Prompts

- `prompts/reviewer.md` — narrow, one-finding-only format
- `prompts/writer.md` — surgical writer with explicit pushback rule
- `prompts/consolidator.md` — strict-JSON consolidation output
- `prompts/weekly.md` — short markdown meta summary

Each lane contributes `reviewer_extra` / `writer_extra` lines and its own
memory (`memory/<lane>.json`).

## Daily consolidation

`.hermes/thesis-automation/run-daily-consolidation.sh` →
`bin/runner.py daily`.

1. For every active lane, list commits in `main..cron/<lane>` since the last
   consolidation.
2. Show full diffs to a consolidator Claude call; require strict-JSON output with
   `accept | reject | defer` per commit + positive guidance lines.
3. Cherry-pick accepted commits onto `main` (refuses if working tree dirty).
4. Distill rejected commits into ≤ 3 short positive guidance lines per lane
   (rolling window). Optionally 1 global line.
5. Refresh every lane worktree/branch to the new `main`.
6. Write `logs/daily/<timestamp>.json` and update `state/rotation.json`.

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

Install the three plists shipped in `.hermes/thesis-automation/launchd/` and
load them:

```bash
cp .hermes/thesis-automation/launchd/ee.taltech.kratt.*.plist ~/Library/LaunchAgents/
launchctl load -w ~/Library/LaunchAgents/ee.taltech.kratt.thesis-automation.hourly.plist
launchctl load -w ~/Library/LaunchAgents/ee.taltech.kratt.thesis-automation.daily.plist
launchctl load -w ~/Library/LaunchAgents/ee.taltech.kratt.thesis-automation.weekly.plist
```

Unload with `launchctl unload -w <plist>` to pause.

### Option B — Claude Code in-session cron (dev-loop only)

From an open `claude` REPL in this repo:

```
CronCreate cron="7 * * * *" prompt="Run ./.hermes/thesis-automation/run-hourly.sh and report the JSON line it prints." recurring=true durable=true
CronCreate cron="11 3 * * *" prompt="Run ./.hermes/thesis-automation/run-daily-consolidation.sh and report counts." recurring=true durable=true
CronCreate cron="17 4 * * 1" prompt="Run ./.hermes/thesis-automation/run-weekly-review.sh and print the meta path." recurring=true durable=true
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
The hourly runner will skip inactive lanes; the daily consolidator will still
refresh the branch/worktree.

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
- Reviewer is invoked with read-only tools (`Read Grep Glob`).
- Consolidator will not cherry-pick onto `main` if the working tree is dirty.
- Lane refresh uses a hard reset to the new `main`, with `git clean` that
  preserves `.claude/` so worktree machinery survives.
- Per-lane `rejected_refs` window is capped at 20 entries.
- Per-lane active guidance is capped at 3 lines. Global at 5.
