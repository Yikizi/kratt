# Standalone engineering guide: thesis automation system

Last updated: 2026-05-09

This is a self-contained rebuild guide for the thesis automation used in the Kratt project. It describes the design, dependencies, file layout, prompts, scheduling, state formats, and operational rules closely enough to recreate the same automation in another repository without needing access to the original source tree.

The original implementation is project-specific, but the architecture is reusable: **isolated agent worktrees produce small lane commits; a daily consolidation gate decides what reaches `main`; rejected work is compressed into future guidance.**

---

## 1. What the automation does

The system continuously improves a LaTeX thesis with coding-agent assistance while avoiding uncontrolled autonomous edits.

It runs three recurring loops:

```text
hourly   choose one editing lane
         -> reviewer agent proposes one small issue
         -> writer agent edits only one target file
         -> writer creates at most one commit on that lane branch

daily    collect lane commits
         -> consolidator agent accepts / rejects / defers each commit
         -> accepted commits are cherry-picked onto main
         -> rejected commits become short lane-guidance memory
         -> lane branches/worktrees reset to fresh main

weekly   rerun a thesis quality review
         -> compare against previous reviews
         -> summarize lane signal and next emphasis
```

Optional support tools:

- dashboard: local HTML/JSON view over logs;
- thesis style audit: grep-like guard for language/style regressions;
- thesis final check: project-specific consistency assertions;
- thesis watch: LaTeX auto-build loop;
- thesis voice dispatch: speech-to-agent correction workflow.

---

## 2. Design principles

Use these rules unchanged if you recreate the system:

1. **No direct hourly edits on `main`.** Hourly agents work only inside lane worktrees.
2. **One lane, one file, one issue, one commit max.** This prevents broad rewrites.
3. **Daily consolidation is the trust boundary.** Only accepted lane commits reach `main`.
4. **Rejected work is distilled, not preserved.** Keep short guidance, not bad branches.
5. **Compression-first closeout.** Prefer shorter, clearer, more defensible prose over additive drafting.
6. **Evidence discipline.** Agents must not invent numbers, citations, user-study results, or claims.
7. **Dirty user work is protected.** Daily consolidation stashes local WIP before cherry-picking and restores it afterwards.
8. **Scheduler is serial.** Never run hourly/daily/weekly jobs concurrently.

---

## 3. Dependency checklist

### Required for core automation

| Dependency | Purpose |
|---|---|
| `git` | branches, worktrees, cherry-picks, stashes |
| `bash` | shell wrappers |
| `python3` | runner, scheduler, dashboard, audits |
| `jq` | parse `lanes.json` in bootstrap script |
| Claude Code CLI `claude` | reviewer/writer/consolidator/fixer/reconciler agents |
| authenticated Claude Code OAuth session | scheduled calls use Claude Code auth |
| `tmux` **or** macOS `launchd` | persistent background scheduling |

### Optional but useful

| Dependency | Purpose |
|---|---|
| `latexmk`, TeX Live/MacTeX, `biber` | thesis PDF builds |
| `zathura` or macOS `open` | PDF viewer reload loop |
| `uv` | project Python env / figure generation |
| Docker | voice dispatch STT runtime |
| `ffmpeg` | microphone capture |
| Codex CLI `codex` | optional voice-dispatched worker profile |

Example macOS setup:

```bash
brew install git jq tmux python ffmpeg uv
brew install --cask docker
# Install MacTeX separately if PDF compilation is needed.
# Install Claude Code CLI and authenticate it interactively.
```

Claude smoke test:

```bash
claude --print --permission-mode default --tools "" --max-budget-usd 0.05 <<<'Reply OK only.'
```

If Claude is not on `PATH`, set:

```bash
export CLAUDE_BIN=/absolute/path/to/claude
```

Unset stale provider variables if they break OAuth:

```bash
unset CLAUDE_API_KEY CLAUDE_CODE_USE_OPENAI
```

---

## 4. Directory layout to create

Create this structure in the repository root:

```text
.hermes/thesis-automation/
├── bin/
│   ├── runner.py
│   ├── scheduler.py
│   └── dashboard.py
├── lanes/
│   └── lanes.json
├── prompts/
│   ├── reviewer.md
│   ├── writer.md
│   ├── consolidator.md
│   ├── fixer.md
│   ├── reconciler.md
│   └── weekly.md
├── launchd/                         # optional macOS plists
├── memory/                          # local ignored runtime memory
├── state/                           # local ignored runtime state
│   └── .gitignore
├── logs/                            # local ignored logs
├── bootstrap-worktrees.sh
├── run-hourly.sh
├── run-daily-consolidation.sh
├── run-weekly-review.sh
├── run-scheduler.sh
├── start-scheduler-tmux.sh
└── stop-scheduler-tmux.sh
```

Add to `.gitignore`:

```gitignore
# Agent worktrees and runtime state
.claude/
.hermes/thesis-automation/memory/
.hermes/thesis-automation/logs/
.hermes/thesis-automation/state/*
!.hermes/thesis-automation/state/.gitignore

# Optional local voice-dispatch config
cli/tools/thesis_voice_dispatch.config.json
```

`state/.gitignore` should contain:

```gitignore
scheduler.json
scheduler.lock
rotation.json
```

---

## 5. Lane model

A **lane** is one autonomous editing workflow with:

- stable ID;
- branch name;
- worktree path;
- target-file rotation;
- focus;
- reviewer/writer extra instructions;
- optional dependency on another lane.

Each lane branch is named `cron/<lane-id>`. Each worktree is stored under `.claude/worktrees/cron-<lane-id>`.

### Recommended lanes

For a thesis closeout workflow, use these lanes:

| Lane | Purpose |
|---|---|
| `terminology` | replace mixed English/local-language terms with proper thesis language |
| `chapter-readiness` | remove repeated claims and overlong transitions |
| `committee-questions` | sharpen existing answers to likely defense questions |
| `claim-evidence` | soften unsupported claims and attach existing evidence only when needed |
| `literature-gap` | compress prior-art positioning and avoid duplicated comparisons |
| `formal-compliance-writer` | citations, captions, quotes, dashes, units, cross-refs |
| `summary-tightening` | make summary concise and self-contained |
| `methodology-tightening` | compress reproducibility details; remove log-like parameter dumps |
| `intro-builder` | tighten problem, scope, contribution, limits |
| `implementation-narrative` | compress implementation detail into design-relevant prose |
| `evaluation-closeout` | keep benchmark, field, and user-study evidence separated |
| `alternatives-comparison` | shorten comparisons against alternatives |
| `research-note` | optional research collection lane; disable in closeout mode |
| `distill-sentence` | optional follow-up lane; disable unless `research-note` is active |

### Complete `lanes.json` template

Adjust target paths to your thesis source files.

```json
{
  "version": 2,
  "worktree_root": ".claude/worktrees",
  "branch_prefix": "cron/",
  "chapters_root": "docs/thesis/thesis-tex/chapters",
  "lanes": [
    {
      "id": "terminology",
      "title": "Terminology cleanup",
      "active": true,
      "branch": "cron/terminology",
      "worktree": ".claude/worktrees/cron-terminology",
      "rotation": [
        "docs/thesis/thesis-tex/chapters/introduction.tex",
        "docs/thesis/thesis-tex/chapters/background.tex",
        "docs/thesis/thesis-tex/chapters/methodology.tex",
        "docs/thesis/thesis-tex/chapters/results.tex",
        "docs/thesis/thesis-tex/chapters/summary.tex"
      ],
      "focus": "Replace mixed-language technical prose with idiomatic thesis-language terminology while preserving code/model names.",
      "reviewer_extra": "Identify one Englishism, unnecessary English gloss, or inconsistent term that can be replaced with a shorter local-language form.",
      "writer_extra": "Replace the term or sentence idiomatically. Preserve code/model names. Prefer net-shorter wording."
    },
    {
      "id": "chapter-readiness",
      "title": "Redundancy pruning",
      "active": true,
      "branch": "cron/chapter-readiness",
      "worktree": ".claude/worktrees/cron-chapter-readiness",
      "rotation": [
        "docs/thesis/thesis-tex/chapters/introduction.tex",
        "docs/thesis/thesis-tex/chapters/background.tex",
        "docs/thesis/thesis-tex/chapters/methodology.tex",
        "docs/thesis/thesis-tex/chapters/results.tex",
        "docs/thesis/thesis-tex/chapters/summary.tex"
      ],
      "focus": "Remove repeated claims, duplicated caveats, and over-explained transitions inside one chapter while preserving the argument.",
      "reviewer_extra": "Identify the single clearest repetition or overlong transition in the target chapter.",
      "writer_extra": "Delete, merge, or shorten that passage. Do not add new signposting unless it replaces a longer unclear sentence."
    },
    {
      "id": "committee-questions",
      "title": "Committee-facing compression",
      "active": true,
      "branch": "cron/committee-questions",
      "worktree": ".claude/worktrees/cron-committee-questions",
      "rotation": [
        "docs/thesis/thesis-tex/chapters/introduction.tex",
        "docs/thesis/thesis-tex/chapters/discussion.tex",
        "docs/thesis/thesis-tex/chapters/summary.tex"
      ],
      "focus": "Pre-empt likely defense questions by sharpening existing explanations, not by adding new caveat lists.",
      "reviewer_extra": "Pose one committee-style concern and identify the existing sentence/paragraph that can answer it more tightly.",
      "writer_extra": "Tighten the existing passage so it is more defensible and shorter or same length. Do not add new claims."
    },
    {
      "id": "claim-evidence",
      "title": "Claim-evidence calibration",
      "active": true,
      "branch": "cron/claim-evidence",
      "worktree": ".claude/worktrees/cron-claim-evidence",
      "rotation": [
        "docs/thesis/thesis-tex/chapters/results.tex",
        "docs/thesis/thesis-tex/chapters/discussion.tex",
        "docs/thesis/thesis-tex/chapters/introduction.tex"
      ],
      "focus": "Make existing claims match existing evidence; prefer softening or shortening unsupported claims over adding more prose.",
      "reviewer_extra": "Find one claim whose evidence is vague, repeated, or stronger than the cited/table-backed result.",
      "writer_extra": "Attach existing evidence only if needed; otherwise shorten or soften the claim. No fabricated numbers and no new side discussion."
    },
    {
      "id": "literature-gap",
      "title": "Literature gap compression",
      "active": true,
      "branch": "cron/literature-gap",
      "worktree": ".claude/worktrees/cron-literature-gap",
      "rotation": [
        "docs/thesis/thesis-tex/chapters/background.tex",
        "docs/thesis/thesis-tex/chapters/introduction.tex"
      ],
      "focus": "Keep prior-art positioning concise, citation-backed, and free of source footnotes or duplicated comparisons.",
      "reviewer_extra": "Identify one prior-art passage that can be shortened, deduplicated, or converted from footnote-style prose into citation style.",
      "writer_extra": "Tighten existing positioning using citations already present. Do not add new sources, subsections, or long comparisons."
    },
    {
      "id": "formal-compliance-writer",
      "title": "Citation and formal hygiene",
      "active": true,
      "branch": "cron/formal-compliance-writer",
      "worktree": ".claude/worktrees/cron-formal-compliance-writer",
      "rotation": [
        "docs/thesis/thesis-tex/chapters/introduction.tex",
        "docs/thesis/thesis-tex/chapters/background.tex",
        "docs/thesis/thesis-tex/chapters/methodology.tex",
        "docs/thesis/thesis-tex/chapters/results.tex",
        "docs/thesis/thesis-tex/chapters/summary.tex"
      ],
      "focus": "Thesis style: bibliography citations instead of source footnotes, clean captions, quotes, dashes, units, and references.",
      "reviewer_extra": "Identify one concrete formal issue: source footnote, overlong caption, straight quotes, broken reference, unit spacing, or mixed citation style.",
      "writer_extra": "Fix only that one issue. Prefer shortening captions/notes and converting source footnotes to bibliography citations when safe."
    },
    {
      "id": "summary-tightening",
      "title": "Summary compression",
      "active": true,
      "branch": "cron/summary-tightening",
      "worktree": ".claude/worktrees/cron-summary-tightening",
      "rotation": ["docs/thesis/thesis-tex/chapters/summary.tex"],
      "focus": "Keep summary crisp, self-contained, and no longer than necessary.",
      "reviewer_extra": "Find the single summary sentence that can be shortened, made more accurate, or deduplicated from earlier chapters.",
      "writer_extra": "Rewrite that one sentence only; net-shorter unless correcting a factual ambiguity."
    },
    {
      "id": "methodology-tightening",
      "title": "Methodology compression",
      "active": true,
      "branch": "cron/methodology-tightening",
      "worktree": ".claude/worktrees/cron-methodology-tightening",
      "rotation": ["docs/thesis/thesis-tex/chapters/methodology.tex"],
      "focus": "Compress reproducibility prose: keep details needed to interpret results, remove low-level configuration logs.",
      "reviewer_extra": "Identify one methodology detail block that is too log-like or too low-level for the main text.",
      "writer_extra": "Replace that detail block with a shorter thesis-level description. Do not add new parameters."
    },
    {
      "id": "intro-builder",
      "title": "Introduction compressor",
      "active": true,
      "branch": "cron/intro-builder",
      "worktree": ".claude/worktrees/cron-intro-builder",
      "rotation": ["docs/thesis/thesis-tex/chapters/introduction.tex"],
      "focus": "Tighten problem, scope, research question, contribution, and limits in fewer words.",
      "reviewer_extra": "Identify one introduction sentence or paragraph that is redundant, overlong, or mixed-language.",
      "writer_extra": "Shorten or rewrite at most one paragraph. Do not add new motivation or literature unless replacing longer existing text."
    },
    {
      "id": "implementation-narrative",
      "title": "Implementation detail compressor",
      "active": true,
      "branch": "cron/implementation-narrative",
      "worktree": ".claude/worktrees/cron-implementation-narrative",
      "rotation": ["docs/thesis/thesis-tex/chapters/implementation.tex"],
      "focus": "Compress implementation prose; keep thesis-relevant design facts and remove repo-log-level detail.",
      "reviewer_extra": "Identify one implementation passage that reads like a repository log or configuration dump.",
      "writer_extra": "Shorten the passage to the design-relevant point. Do not add implementation details."
    },
    {
      "id": "evaluation-closeout",
      "title": "Evaluation compression and closeout",
      "active": true,
      "branch": "cron/evaluation-closeout",
      "worktree": ".claude/worktrees/cron-evaluation-closeout",
      "rotation": [
        "docs/thesis/thesis-tex/chapters/results.tex",
        "docs/thesis/thesis-tex/chapters/discussion.tex"
      ],
      "focus": "Compress evaluation history and keep benchmark, field, and user-test evidence clearly separated.",
      "reviewer_extra": "Identify one result-history passage, limitation, or bridge that can be shortened or deduplicated without losing evidence.",
      "writer_extra": "Tighten at most one short result/limitation passage. Add prose only for final data already present in tracked outputs."
    },
    {
      "id": "alternatives-comparison",
      "title": "Alternatives comparison compression",
      "active": true,
      "branch": "cron/alternatives-comparison",
      "worktree": ".claude/worktrees/cron-alternatives-comparison",
      "rotation": [
        "docs/thesis/thesis-tex/chapters/background.tex",
        "docs/thesis/thesis-tex/chapters/introduction.tex"
      ],
      "focus": "Keep comparison against alternatives concise and non-duplicative.",
      "reviewer_extra": "Identify one comparison point that is duplicated, too broad, or longer than needed.",
      "writer_extra": "Shorten or merge the comparison sentence/paragraph using existing citations only. Do not introduce new alternatives."
    },
    {
      "id": "research-note",
      "title": "Research note (paused in compression mode)",
      "active": false,
      "branch": "cron/research-note",
      "worktree": ".claude/worktrees/cron-research-note",
      "rotation": ["docs/research/thesis-writing-research-queue.md"],
      "focus": "Paused during compression-first closeout; reactivate only when a mandatory missing source/evidence gap is approved.",
      "reviewer_extra": "Paused: push back unless the user explicitly asks to collect a missing source.",
      "writer_extra": "Paused: do not append research notes during compression mode."
    },
    {
      "id": "distill-sentence",
      "title": "Distill sentence (paused in compression mode)",
      "active": false,
      "branch": "cron/distill-sentence",
      "worktree": ".claude/worktrees/cron-distill-sentence",
      "depends_on": {"lane": "research-note"},
      "rotation": [
        "docs/thesis/thesis-tex/chapters/introduction.tex",
        "docs/thesis/thesis-tex/chapters/background.tex",
        "docs/thesis/thesis-tex/chapters/results.tex"
      ],
      "focus": "Paused during compression-first closeout; reactivate only to insert approved mandatory evidence.",
      "reviewer_extra": "Paused: push back unless the latest approved research note maps to a mandatory thesis gap.",
      "writer_extra": "Paused: do not add thesis prose during compression mode."
    }
  ]
}
```

---

## 6. Runtime state formats

### Rotation state

Create/read `.hermes/thesis-automation/state/rotation.json` lazily. Example:

```json
{
  "lane_cursor": 0,
  "file_cursor": {
    "terminology": 1,
    "claim-evidence": 0
  },
  "last_consolidation": "2026-05-09T03:13:27",
  "last_weekly_review": "2026-05-04T21:05:47",
  "lane_progress": {
    "terminology": "<last-lane-commit-sha>"
  },
  "lane_dependency_consumed": {
    "distill-sentence": "<research-note-sha-consumed>"
  }
}
```

### Lane memory

File: `.hermes/thesis-automation/memory/<lane>.json`

```json
{
  "lane": "terminology",
  "updated": "2026-05-09T08:00:00",
  "guidance": [
    "Replace mixed English/local-language phrases with idiomatic thesis-language terms while preserving code and dataset names."
  ],
  "rejected_refs": [
    {
      "sha": "<rejected-commit-sha>",
      "reason": "additive drift",
      "distilled": "Prefer shortening existing claims over adding caveat lists."
    }
  ]
}
```

Rules:

- max 3 active `guidance` lines per lane;
- max 20 `rejected_refs` per lane;
- newest guidance first;
- guidance should be positive steering, not long negative history.

### Global memory

File: `.hermes/thesis-automation/memory/global.json`

```json
{
  "updated": "2026-05-09T08:00:00",
  "guidance": [
    "Primary thesis claim is the evaluation protocol/prototype; soften product-readiness claims unless frozen evidence supports them.",
    "User-study results may be added only from tracked sessions; otherwise describe user testing as planned or as a limitation."
  ]
}
```

Max 5 lines.

### Scheduler state

File: `.hermes/thesis-automation/state/scheduler.json`

```json
{
  "jobs": {
    "hourly": {
      "next_run": "2026-05-09T09:07:00",
      "runs": 108,
      "last_run": "2026-05-09T08:08:17",
      "last_rc": 0,
      "last_scheduled_run": "2026-05-09T08:07:00",
      "last_timed_out": false
    },
    "daily": {
      "next_run": "2026-05-10T03:11:00",
      "runs": 7,
      "last_run": "2026-05-09T03:13:27",
      "last_rc": 0
    },
    "weekly": {
      "next_run": "2026-05-11T04:17:00",
      "runs": 0,
      "last_run": null,
      "last_rc": null
    }
  },
  "updated": "2026-05-09T08:40:00"
}
```

---

## 7. Prompt templates

The exact words can vary, but the contracts below should be preserved.

### `prompts/reviewer.md`

```markdown
# Reviewer prompt

You are the REVIEWER for a single automated thesis-editing lane.

The thesis is in compression-first closeout mode. Your default job is not to grow the document; it is to make existing prose shorter, cleaner, less repetitive, and more defensible.

## Hard scope
- Lane: {{LANE_ID}} — {{LANE_TITLE}}
- Target file only: `{{TARGET_FILE}}`
- Lane focus: {{LANE_FOCUS}}

## Rules
- Read only the target file plus minimal adjacent files if strictly needed for duplication/citation checks.
- Propose exactly ONE concrete edit that fits the lane focus and stays inside the target file.
- If the target file contains TODO/FIXME/TBD/placeholder result scaffolding, removing or converting it into final prose is highest priority.
- Prefer edits that remove repetition, replace mixed-language wording, shorten captions, remove unnecessary glosses, or collapse log-like prose.
- Do not suggest cross-chapter restructuring, new subsections, or new background material.
- Do not propose adding evidence unless the current sentence is unsafe without an already-present number/table/citation.
- If the only useful change would be additive, set confidence to low and say skip.
- Lane reviewer extra: {{REVIEWER_EXTRA}}

## Active lane guidance
{{LANE_GUIDANCE}}

## Active global guidance
{{GLOBAL_GUIDANCE}}

## Output exactly
### Finding
One sentence naming the single problem.

### Evidence
Quote at most 3 short snippets from the target file, with line hints.

### Proposed fix
Concrete, minimal, surgical. State whether effect is shorter, same length but cleaner, or skip.

### Confidence
low | medium | high. If low, say skip.

Do not edit files.
```

### `prompts/writer.md`

```markdown
# Writer prompt

You are the WRITER for a single automated thesis-editing lane.

## Hard scope
- Lane: {{LANE_ID}} — {{LANE_TITLE}}
- Target file only: `{{TARGET_FILE}}`
- Lane focus: {{LANE_FOCUS}}
- Lane writer extra: {{WRITER_EXTRA}}

## Reviewer finding
{{REVIEWER_OUTPUT}}

## Active lane guidance
{{LANE_GUIDANCE}}

## Active global guidance
{{GLOBAL_GUIDANCE}}

## Rules
- Edit only `{{TARGET_FILE}}`.
- Push back and make no edits if reviewer confidence was low/skip, the fix is larger than about 25 changed lines, requires missing evidence, drifts from lane focus, mainly adds explanatory prose, introduces a new source footnote, adds new unnecessary English glosses, repeats a point already made clearly, or introduces placeholders.
- If evidence is absent, write a concise limitation sentence only when replacing placeholder text; otherwise do not add.
- Prefer deleting, shortening, merging overlapping sentences, shortening captions, or replacing mixed-language terms.
- Ordinary prose should be net-shorter. Neutral length is allowed for citation hygiene, typo fixes, or terminology cleanup.
- Preserve LaTeX structure, labels, citations, tables, and numeric claims unless the reviewer identified a safe correction.
- Stage only `{{TARGET_FILE}}`.
- Create one commit with message: `docs(thesis): <lane-id> — <short reason>`.
- Print `DONE: <summary>` after committing, or `PUSHBACK: <reason>` if not.
```

### `prompts/consolidator.md`

```markdown
# Daily consolidation prompt

You are the CONSOLIDATOR. Triage lane commits produced since the previous consolidation and decide what reaches main.

The thesis is in compression-first closeout mode. Accepted commits should reduce length, remove repetition, improve language/style, fix formal hygiene, or make an existing claim more defensible without expanding the document.

For each commit choose exactly one:
- accept
- reject
- defer

Decision rules:
- Favor small chapter-local edits that are net-shorter or formally cleaner.
- Accept terminology cleanup, repetition removal, caption shortening, citation hygiene, and evidence-backed claim softening.
- Reject additive prose unless it supplies mandatory final evidence already present in tracked artifacts.
- Reject placeholders in active thesis chapter sources.
- Reject unsupported reframing, fabricated citations/numbers, edits outside lane scope, new source footnotes, mixed-language prose, or undoing previous tightening.

For each reject, produce one short positive steering line, max 140 chars.

Output strict JSON only:
{
  "decisions": [
    {"lane": "<lane-id>", "sha": "<hash>", "action": "accept|reject|defer", "reason": "<short>"}
  ],
  "lane_guidance_additions": [
    {"lane": "<lane-id>", "line": "<short positive steering line>"}
  ],
  "global_guidance_additions": [
    "<optional short global steering line>"
  ]
}
```

### `prompts/fixer.md`

```markdown
# Cherry-pick conflict fixer

A cherry-pick of lane commit `{{SHA}}` onto main hit a conflict.

Scope:
- You are in the main worktree with a cherry-pick in progress.
- Touch only unmerged files.
- Preserve the accepted lane commit's intent.
- Resolve conflict markers manually.
- Stage resolved files and run `git cherry-pick --continue`.
- If not safely resolvable, run `git cherry-pick --abort` and print `ABORT: <reason>`.
- On success print `FIXED: <summary>`.

Unmerged files:
{{UNMERGED_FILES}}

Status:
{{STATUS}}
```

### `prompts/reconciler.md`

```markdown
# Stash-pop reconciler

After daily consolidation cherry-picked accepted lane commits onto main, `git stash pop` of the user's prior WIP conflicted.

Scope:
- Touch only unmerged files.
- Do not create commits.
- Preserve both accepted main state and user's original WIP where possible.
- If accepted commit subsumed user's local change in same region, keep accepted version.
- If local change is orthogonal, keep local change.
- If ambiguous, keep user's local WIP rather than silently dropping it.
- Resolve files so final `git status --porcelain` has no unmerged rows and no conflict markers.
- Leave restored WIP uncommitted.
- Print `RECONCILED: <summary>` or `UNRESOLVED: <reason>`.

Status:
{{STATUS}}

Unmerged files:
{{UNMERGED_FILES}}
```

### `prompts/weekly.md`

```markdown
# Weekly meta-review prompt

Compare latest thesis-quality review against previous review, then inspect lane memory and consolidation logs.

Judge lanes by whether they reduced redundancy, improved language, cleaned citations/captions, or safely tightened claims. Additive drafting is useful only for mandatory final evidence.

Produce Markdown with:

### Readiness delta
Score change and two-line interpretation.

### Lane signal
Max 8 bullets: accepted value, additive churn, quiet lanes.

### Guidance updates suggested
Up to 3 lane/global steering lines.

### Next week's emphasis
Max 3 concrete bullets.

Keep under about 40 lines.
```

---

## 8. Worktree bootstrap script

Create `.hermes/thesis-automation/bootstrap-worktrees.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$HERE" rev-parse --show-toplevel)"
cd "$REPO"
LANES_JSON="$REPO/.hermes/thesis-automation/lanes/lanes.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "bootstrap: jq is required" >&2
  exit 1
fi

if ! git rev-parse --verify main >/dev/null 2>&1; then
  echo "bootstrap: no main branch" >&2
  exit 1
fi

MAIN_SHA="$(git rev-parse main)"
LANE_IDS="$(jq -r '.lanes[] | select(.active==true) | .id' "$LANES_JSON")"

for lane in $LANE_IDS; do
  branch="cron/${lane}"
  wt_rel="$(jq -r --arg id "$lane" '.lanes[] | select(.id==$id) | .worktree' "$LANES_JSON")"
  wt_abs="$REPO/$wt_rel"

  if ! git rev-parse --verify "$branch" >/dev/null 2>&1; then
    git branch "$branch" "$MAIN_SHA"
    echo "created branch $branch"
  fi

  existing_path="$(git worktree list --porcelain | awk -v b="refs/heads/${branch}" '
    $1=="worktree" {p=$2}
    $1=="branch" && $2==b {print p; exit}
  ' || true)"

  if [[ -n "${existing_path:-}" && "$existing_path" != "$wt_abs" ]]; then
    git worktree remove --force "$existing_path" || true
    existing_path=""
  fi

  if [[ -z "${existing_path:-}" || ! -d "$wt_abs" ]]; then
    mkdir -p "$(dirname "$wt_abs")"
    git worktree add "$wt_abs" "$branch"
    echo "added worktree $wt_abs on $branch"
  fi
done

echo "bootstrap: done"
git worktree list | grep -E "cron-|/$(basename "$REPO")$" || true
```

Make executable:

```bash
chmod +x .hermes/thesis-automation/bootstrap-worktrees.sh
```

---

## 9. Runner implementation blueprint

The production runner is a Python script. This section gives the complete behavior needed to rebuild it.

### Required constants

```python
REPO = Path(__file__).resolve().parents[3]
AUTO = REPO / ".hermes" / "thesis-automation"
LANES_JSON = AUTO / "lanes" / "lanes.json"
MEMORY_DIR = AUTO / "memory"
LOGS_DIR = AUTO / "logs"
STATE_DIR = AUTO / "state"
PROMPTS_DIR = AUTO / "prompts"
REVIEWS_DIR = REPO / ".hermes" / "thesis-quality-reviews"
```

### Helper behavior

Implement helpers for:

- `read_json(path, default)`;
- `write_json(path, data)` with `indent=2`, `ensure_ascii=False`;
- `append_jsonl(path, data)`;
- `git(repo, *args)` returning stdout;
- `render_prompt(template, **vars)` replacing `{{NAME}}` tokens;
- `load_lanes()` returning active lanes;
- `lane_memory(lane_id)` with default `{lane, updated, guidance: [], rejected_refs: []}`;
- `global_memory()` with default `{updated, guidance: []}`;
- `state()` reading `state/rotation.json`.

### Claude binary resolution

Search in this order:

1. `$CLAUDE_BIN`;
2. `shutil.which("claude")`;
3. `~/.local/bin/claude`;
4. `/opt/homebrew/bin/claude`;
5. `/usr/local/bin/claude`;
6. fallback string `claude`.

### Claude call function

Pseudo-code:

```python
def run_claude(prompt, cwd, dangerously=False, permission_mode="default",
               model=None, tools="default", max_budget_usd=None,
               timeout=900, output_format="text"):
    cmd = [CLAUDE_BIN, "--print", "--output-format", output_format]
    if dangerously:
        cmd.append("--dangerously-skip-permissions")
    else:
        cmd += ["--permission-mode", permission_mode]
    if model or os.getenv("CLAUDE_MODEL"):
        cmd += ["--model", model or os.getenv("CLAUDE_MODEL")]
    if tools is not None:
        cmd += ["--tools", tools]
    if max_budget_usd is not None:
        cmd += ["--max-budget-usd", str(max_budget_usd)]

    env = os.environ.copy()
    if os.getenv("KRATT_CLAUDE_KEEP_API_ENV") != "1":
        env.pop("CLAUDE_API_KEY", None)
        env.pop("CLAUDE_CODE_USE_OPENAI", None)

    proc = subprocess.run(cmd, cwd=cwd, input=prompt, text=True,
                          capture_output=True, timeout=timeout, env=env)
    return {"returncode": proc.returncode,
            "stdout": proc.stdout or "",
            "stderr": proc.stderr or "",
            "text": proc.stdout or ""}
```

### Hourly algorithm

```python
def hourly_run(force_lane=None):
    lanes = load_lanes()
    st = state()

    if force_lane:
        lane = lane matching force_lane
    else:
        cursor = st.get("lane_cursor", 0) % len(lanes)
        lane = lanes[cursor]
        st["lane_cursor"] = (cursor + 1) % len(lanes)

    file_cursor = st.setdefault("file_cursor", {}).get(lane_id, 0) % len(lane["rotation"])
    target_file = lane["rotation"][file_cursor]
    st["file_cursor"][lane_id] = (file_cursor + 1) % len(lane["rotation"])
    save_state(st)

    worktree = REPO / lane["worktree"]
    head_before = git(worktree, "rev-parse", "HEAD")

    if lane has depends_on and dependency not ready:
        log pushback and return 0

    render reviewer prompt using lane data, target file, memory
    reviewer = run_claude(... max_budget_usd=0.5, timeout=600)
    if reviewer failed: log reviewer_failed and return

    render writer prompt with REVIEWER_OUTPUT
    writer = run_claude(... dangerously=True, max_budget_usd=1.0, timeout=900)

    head_after = git(worktree, "rev-parse", "HEAD")
    if head_after != head_before:
        result = "committed"
        store lane_progress[lane_id] = head_after
    elif writer text starts with PUSHBACK:
        result = "pushback"
    else:
        result = "no_change"

    append JSON line to logs/hourly/YYYY-MM-DD.jsonl
    print compact JSON {lane, result, file, commit}
```

Hourly log entry should include:

```json
{
  "ts": "2026-05-09T08:08:17",
  "lane": "terminology",
  "target_file": "docs/thesis/.../chapter.tex",
  "worktree": "/repo/.claude/worktrees/cron-terminology",
  "branch": "cron/terminology",
  "head_before": "...",
  "reviewer": {"rc": 0, "stderr_tail": "", "text": "..."},
  "writer": {"rc": 0, "stderr_tail": "", "text": "..."},
  "commit": {"sha": "...", "subject": "..."},
  "result": "committed"
}
```

### Daily algorithm

```python
def daily_run():
    lanes = load_lanes()
    collect commits for each lane with: git log main..cron/<lane> --pretty=%H%x1f%an%x1f%s%x1f%ct
    if no commits: still refresh state/log and exit

    for each commit: include git show --stat -p <sha> in consolidator input, truncate huge diffs
    result = run_claude(consolidator prompt, max_budget_usd=2.0, timeout=1200)
    parse first JSON object in result text

    accepted = decisions where action == accept
    rejected = decisions where action == reject
    deferred = decisions where action == defer

    if main worktree dirty:
        git stash push -u -m "thesis-automation daily <timestamp>" -- ':(exclude,glob).hermes/**' ':/''

    git checkout main

    for accepted commit:
        try git cherry-pick -x <sha>
        if conflict:
            run fixer prompt dangerously
            if still conflict: git cherry-pick --abort; mark degraded/rejected

    if stash was used:
        git stash pop <stash-ref>
        if conflict:
            run reconciler prompt dangerously
            if unresolved: mark degraded; skip lane refresh

    update lane/global memory with guidance additions

    if safe:
        main_sha = git rev-parse main
        for lane:
            reset and clean lane worktree
            update refs/heads/cron/<lane> to main_sha
            checkout branch and reset hard main_sha

    write logs/daily/<timestamp>.json
```

Use these safety checks:

- detect unmerged files from `git status --porcelain` XY codes: `DD AU UD UA DU AA UU`;
- detect cherry-pick in progress from `.git/CHERRY_PICK_HEAD`;
- skip destructive lane refresh if stash-pop conflict remains unresolved.

### Weekly algorithm

```python
def weekly_run():
    run_claude("Use the thesis-quality-review skill...", dangerously=True, max_budget_usd=3.0, timeout=1800)
    read .hermes/thesis-quality-reviews/index.json
    latest = newest review entry
    previous = second-newest review entry
    read latest/previous markdown
    collect lane memories
    collect last-7-days hourly stats
    collect last-7-days daily logs
    run_claude(weekly prompt + collected data, max_budget_usd=1.5)
    write logs/weekly/<timestamp>-meta.md
    update state["last_weekly_review"]
```

The weekly quality-review skill can be replaced by any script that writes comparable review Markdown/JSON plus an `index.json`.

---

## 10. Shell wrappers

Create these executable wrappers.

`run-hourly.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec /usr/bin/env python3 "$HERE/bin/runner.py" hourly "$@"
```

`run-daily-consolidation.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec /usr/bin/env python3 "$HERE/bin/runner.py" daily "$@"
```

`run-weekly-review.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec /usr/bin/env python3 "$HERE/bin/runner.py" weekly "$@"
```

`run-scheduler.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(cd "$HERE/../.." && pwd)"
exec /usr/bin/env python3 "$HERE/bin/scheduler.py" "$@"
```

Make executable:

```bash
chmod +x .hermes/thesis-automation/*.sh
```

---

## 11. Scheduler design

The scheduler is a long-running Python process with a file lock. It runs due jobs serially.

### Jobs

| Job | Default time | Command | Timeout | Catch-up |
|---|---:|---|---:|---:|
| `hourly` | every hour at minute `07` | `run-hourly.sh` | 1h | 2h |
| `daily` | 03:11 daily | `run-daily-consolidation.sh` | 3h | 24h |
| `weekly` | Monday 04:17 | `run-weekly-review.sh` | 3h | 7d |
| `research-distill` | optional minute `15` | `run-research-distill-cycle.sh` | 2h | 2h |

### Scheduler implementation requirements

- Use `fcntl.flock` on `state/scheduler.lock`.
- Store job state in `state/scheduler.json`.
- Before each job, run a Claude auth smoke test:

```bash
claude --print --output-format text --permission-mode default \
  --model sonnet --tools "" --disable-slash-commands \
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --no-session-persistence --max-budget-usd 0.05
```

Prompt: `Reply OK only.`

- Strip `CLAUDE_API_KEY` and `CLAUDE_CODE_USE_OPENAI` from the job environment unless explicitly overridden.
- If auth fails, record `last_auth_failure`, append `logs/scheduler/auth-skips.jsonl`, and retry that job after 15 minutes.
- For every job run, write stdout/stderr to:

```text
logs/scheduler/YYYY-MM-DD/YYYYMMDD_HHMMSS_<job>.stdout.log
logs/scheduler/YYYY-MM-DD/YYYYMMDD_HHMMSS_<job>.stderr.log
```

- Append summary rows to `logs/scheduler/runs.jsonl`.
- On timeout, SIGTERM the process group, wait briefly, then SIGKILL.

### tmux scheduler wrapper

`start-scheduler-tmux.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SESSION="${KRATT_SCHEDULER_TMUX_SESSION:-thesis-scheduler}"

restart=0
if [[ "${1:-}" == "--restart" ]]; then restart=1; shift; fi

command -v tmux >/dev/null || { echo "tmux not found" >&2; exit 127; }

if [[ "$restart" == "1" ]] && tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux kill-session -t "$SESSION"
fi
if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "scheduler already running: $SESSION"
  exit 0
fi

cmd="cd '$REPO' && while true; do '$HERE/run-scheduler.sh' $*; rc=\$?; echo scheduler exited rc=\$rc; sleep 30; done"
tmux new-session -d -s "$SESSION" -n scheduler "$cmd"
echo "started scheduler: tmux attach -t $SESSION"
```

`stop-scheduler-tmux.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
SESSION="${KRATT_SCHEDULER_TMUX_SESSION:-thesis-scheduler}"
if tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux kill-session -t "$SESSION"
  echo "stopped scheduler: $SESSION"
else
  echo "scheduler not running: $SESSION"
fi
```

---

## 12. macOS launchd setup

Use launchd if you want the scheduler and dashboard to survive terminal sessions.

### Scheduler plist template

Save as `~/Library/LaunchAgents/ee.example.thesis-automation.scheduler.plist` after editing paths.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>ee.example.thesis-automation.scheduler</string>
  <key>ProgramArguments</key>
  <array>
    <string>/ABS/PATH/TO/REPO/.hermes/thesis-automation/run-scheduler.sh</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>WorkingDirectory</key>
  <string>/ABS/PATH/TO/REPO</string>
  <key>StandardOutPath</key>
  <string>/ABS/PATH/TO/REPO/.hermes/thesis-automation/logs/scheduler/launchd.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>/ABS/PATH/TO/REPO/.hermes/thesis-automation/logs/scheduler/launchd.stderr.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/Users/YOU/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    <key>CLAUDE_BIN</key>
    <string>/Users/YOU/.local/bin/claude</string>
  </dict>
</dict>
</plist>
```

Load/unload:

```bash
launchctl load -w ~/Library/LaunchAgents/ee.example.thesis-automation.scheduler.plist
launchctl unload -w ~/Library/LaunchAgents/ee.example.thesis-automation.scheduler.plist
```

Do not load separate hourly/daily/weekly plists at the same time as the serial scheduler.

---

## 13. Dashboard design

The dashboard is optional and read-only. It should:

- read `logs/hourly/*.jsonl`;
- read `logs/daily/*.json`;
- read `logs/weekly/*.md`;
- read `lanes/lanes.json`;
- read quality-review `index.json` if present;
- compute counts by lane/result;
- show recent accepted/rejected commits;
- expose JSON at `/api/stats.json`;
- serve a simple HTML page at `/`.

Minimum command:

```bash
python3 .hermes/thesis-automation/bin/dashboard.py --host 127.0.0.1 --port 8765
```

Useful `--dump-json` output shape:

```json
{
  "generated_at": "2026-05-09T08:00:00",
  "summary": {
    "hourly_runs": 264,
    "hourly_commits": 233,
    "daily_runs": 14,
    "weekly_runs": 1,
    "accepted_commits": 188,
    "rejected_commits": 22,
    "active_lanes": 14
  },
  "hourly_results": {"committed": 233, "pushback": 20},
  "lane_rows": [],
  "warnings": []
}
```

A dashboard can be rebuilt in under 200 lines with Python's `http.server.ThreadingHTTPServer`.

---

## 14. CLI wrappers

If your repo has a project CLI, add wrappers. Otherwise run scripts directly.

Example wrapper `cli/commands/project-thesis-dashboard`:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec /usr/bin/env python3 "$ROOT/.hermes/thesis-automation/bin/dashboard.py" "$@"
```

Example wrapper `cli/commands/project-thesis-style-audit`:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec python3 "$ROOT/scripts/thesis_style_audit.py" "$@"
```

Example wrapper `cli/commands/project-thesis-watch`:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
THESIS_DIR="$ROOT/docs/thesis/thesis-tex"
cd "$THESIS_DIR"
exec latexmk -pvc -pdf -interaction=nonstopmode -halt-on-error -file-line-error -view=none main.tex
```

---

## 15. Thesis style audit

A lightweight style audit catches regressions that agents often introduce.

Recommended checks:

- source footnotes inside chapter prose;
- English glosses such as `(ingl ...)`;
- common Englishisms (`pipeline`, `baseline`, `threshold`, `runtime`, etc.);
- TODO/FIXME/TBD/placeholders;
- overlong captions.

Minimal Python behavior:

```python
for each .tex file in chapters/ and selected misc files:
    ignore comments and common code-like LaTeX wrappers
    if "\\footnote{" -> finding "chapter-footnote"
    if regex for English gloss -> finding "english-gloss"
    if regex TODO/FIXME/TBD/placeholder -> finding "placeholder-artifact"
    if configured Englishism regex matches -> finding "englishism"
    parse simple \caption{...} blocks and count words
    if caption word count > 45 -> finding "long-caption"

print text summary or JSON
exit 1 only with --fail-on-findings
```

Example command:

```bash
python3 scripts/thesis_style_audit.py --root docs/thesis/thesis-tex --json --fail-on-findings
```

---

## 16. Quality review skill

The weekly loop expects a repeatable thesis-quality review. If you do not use Hermes skills, implement a local script or prompt with the same output contract.

Required output directory:

```text
.hermes/thesis-quality-reviews/
```

Required files per run:

```text
YYYY-MM-DD_HHMMSS-review.json
YYYY-MM-DD_HHMMSS-review.md
index.json
```

Recommended rubric dimensions, each scored 0-5:

1. problem framing
2. research questions and scope
3. related work and positioning
4. methodology rigor
5. implementation/artifact clarity
6. evaluation and evidence
7. discussion and limitations
8. ethics/privacy/reproducibility
9. structure and coherence
10. language and academic style
11. formal compliance
12. defense readiness

Also compute `overall_readiness_0_to_10`, adjusted downward for blockers.

Index format:

```json
{
  "project_name": "Project",
  "project_root": "/abs/path/to/repo",
  "reviews": [
    {
      "timestamp": "2026-05-09_120000",
      "kind": "follow_up",
      "overall_readiness_0_to_10": 7.0,
      "json_path": ".hermes/thesis-quality-reviews/2026-05-09_120000-review.json",
      "markdown_path": ".hermes/thesis-quality-reviews/2026-05-09_120000-review.md"
    }
  ]
}
```

Hard checks to include:

- placeholders;
- template leftovers;
- missing/empty conclusion;
- claim/evidence mismatch;
- missing limitations;
- missing ethics/privacy when human/user data is involved;
- traceability of tables/figures/results;
- formal language and citation problems.

---

## 17. Optional voice-dispatched corrections

This is separate from lane automation. It lets the author read the PDF, dictate one correction, and route the transcript into a tmux agent/worker.

Architecture:

```text
microphone
  -> ffmpeg 16 kHz mono PCM
  -> Docker Kiirkirjutaja / sherpa-onnx online recognizer
  -> final transcript
  -> tmux paste/type into agent pane or new worker window
```

Dependencies:

- `tmux`;
- `ffmpeg`;
- Docker;
- Python image with `numpy`, `sherpa-onnx`, `wyoming`;
- optional `claude`/`codex` profiles.

Essential commands:

```bash
# create blank target pane
project thesis-voice pane

# send already-typed transcript
project thesis-voice send "page 3 sentence is wrong; rewrite in thesis language"

# continuous dictation
project thesis-voice listen --device 1

# safer: create one worker tmux window per request
project thesis-voice listen --device 1 --mode worker-window --profile claude-yolo
```

Safety rules for the worker prompt:

- make exactly one small thesis correction;
- if a PDF page is named, map it to source `.tex` first;
- thesis prose uses the thesis language;
- inspect git status before editing;
- preserve unrelated user changes;
- do not regenerate PDFs unless needed;
- finish with changed files and verification.

Current limitation: without a wake-word gate, live dictation can dispatch accidental speech.

---

## 18. End-to-end setup procedure

### 1. Clone and enter repo

```bash
git clone <your-repo-url> thesis-project
cd thesis-project
git checkout main
```

### 2. Create the automation layout

Create the directory tree from section 4. Add `.gitignore` entries.

### 3. Add lane config and prompts

- Save the `lanes.json` template and adjust chapter paths.
- Save prompt templates from section 7.

### 4. Implement runner/scheduler/dashboard

Either:

- implement `runner.py` from the blueprint in section 9;
- implement `scheduler.py` from section 11;
- implement a small dashboard from section 13;

or copy equivalent code from an existing implementation.

### 5. Add wrappers and mark executable

```bash
chmod +x .hermes/thesis-automation/*.sh
chmod +x .hermes/thesis-automation/bootstrap-worktrees.sh
```

### 6. Authenticate Claude

```bash
claude --print --permission-mode default --tools "" --max-budget-usd 0.05 <<<'Reply OK only.'
```

### 7. Bootstrap worktrees

```bash
.hermes/thesis-automation/bootstrap-worktrees.sh
git worktree list | grep cron-
```

### 8. Smoke-test one lane

```bash
.hermes/thesis-automation/run-hourly.sh --lane terminology
```

Expected result: compact JSON like:

```json
{"lane":"terminology","result":"pushback","file":"docs/thesis/...","commit":null}
```

or a `committed` result on `cron/terminology`.

### 9. Smoke-test daily consolidation

```bash
.hermes/thesis-automation/run-daily-consolidation.sh
```

If a lane commit exists, this should create a daily log and either accept/reject/defer it. If no commits exist, it should exit cleanly.

### 10. Start persistent automation

Tmux:

```bash
.hermes/thesis-automation/start-scheduler-tmux.sh
```

Launchd on macOS:

```bash
# after editing plist paths
launchctl load -w ~/Library/LaunchAgents/ee.example.thesis-automation.scheduler.plist
```

### 11. Start dashboard

```bash
python3 .hermes/thesis-automation/bin/dashboard.py --host 127.0.0.1 --port 8765
```

Open:

```text
http://127.0.0.1:8765
```

---

## 19. Operational commands

```bash
# Current git state
git status --short --branch

# Worktrees
git worktree list | grep cron-

# Today's hourly logs
tail -n 20 .hermes/thesis-automation/logs/hourly/$(date +%F).jsonl | jq .

# Latest daily consolidation
latest=$(ls -t .hermes/thesis-automation/logs/daily/*.json | head -1)
jq . "$latest"

# Scheduler state
jq . .hermes/thesis-automation/state/scheduler.json

# Rotation state
jq . .hermes/thesis-automation/state/rotation.json

# Lane memory
for f in .hermes/thesis-automation/memory/*.json; do
  echo "== $f =="
  jq '.lane, .guidance' "$f"
done

# Pending commits on a lane
git log --oneline main..cron/terminology

# Manually force one lane
.hermes/thesis-automation/run-hourly.sh --lane claim-evidence

# Manually consolidate
.hermes/thesis-automation/run-daily-consolidation.sh

# Dashboard JSON
python3 .hermes/thesis-automation/bin/dashboard.py --dump-json | jq '.summary, .warnings'
```

---

## 20. Failure modes and repairs

| Symptom | Likely cause | Repair |
|---|---|---|
| `jq is required` | missing dependency | install `jq` |
| worktree missing | deleted/never bootstrapped | rerun `bootstrap-worktrees.sh` |
| Claude calls fail with auth/API errors | stale env or OAuth expired | run Claude interactively, unset stale API env, check `CLAUDE_BIN` |
| scheduler says lock held | another scheduler instance | stop tmux/launchd instance; remove lock only after verifying no process owns it |
| daily consolidation degraded | unresolved cherry-pick or stash-pop conflict | inspect latest daily JSON and `git status`; resolve manually |
| lane keeps bad commits | refresh skipped or daily not run | run daily when safe; otherwise reset lane manually |
| dashboard empty | logs missing or wrong working dir | check launchd paths and `logs/` |
| weekly review fails | quality-review skill/script absent | implement local review script or remove weekly job |
| launchd does nothing | hard-coded paths wrong | edit plist `WorkingDirectory`, `ProgramArguments`, `PATH`, `CLAUDE_BIN` |

Manual reset for one lane:

```bash
lane=terminology
git -C .claude/worktrees/cron-$lane reset --hard main
git -C .claude/worktrees/cron-$lane clean -fdx -- ':!.claude/'
git branch -f cron/$lane main
```

Remove/recreate a broken worktree:

```bash
git worktree remove --force .claude/worktrees/cron-terminology
.hermes/thesis-automation/bootstrap-worktrees.sh
```

Abort a stuck cherry-pick:

```bash
git cherry-pick --abort
```

Recover stash if daily left it behind:

```bash
git stash list
git stash show -p stash@{0}
git stash pop stash@{0}
```

---

## 21. Porting checklist

To adapt this automation to another thesis/project:

- [ ] Replace all chapter paths in `lanes.json`.
- [ ] Rewrite lane focus text for the target thesis language and risk profile.
- [ ] Add project-specific global guidance.
- [ ] Adjust style-audit Englishism/terminology patterns.
- [ ] Replace quality-review rubric if the degree/programme differs.
- [ ] Update launchd/tmux names and absolute paths.
- [ ] Decide whether optional voice dispatch is needed.
- [ ] Run one forced lane smoke test.
- [ ] Run one daily consolidation smoke test.
- [ ] Confirm dirty user work is preserved through daily consolidation.
- [ ] Confirm logs and dashboard update.

---

## 22. Why this works

The system is effective because it uses git as the safety mechanism:

- Worktrees isolate autonomous edits.
- Lane branches make every change reviewable.
- Strict prompts limit scope.
- Daily consolidation gives a human-like acceptance boundary.
- Rejected work becomes compact guidance, so the system learns without accumulating junk.
- Scheduler serialization prevents overlapping agent edits.
- Logs and dashboard provide observability without a database.

The core pattern is reusable for any long-form technical document where agents can help with polishing but must not be allowed to silently rewrite the source of truth.
