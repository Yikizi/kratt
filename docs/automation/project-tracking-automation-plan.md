# Project tracking automation plan

Purpose: keep Kratt thesis work accounting and GitLab planning close to reality without spending a full session manually reconstructing progress.

Status on 2026-04-26: Clockify was backfilled through 2026-04-26 from git history and agent-session evidence. GitLab auth works, but issues need light triage.

## Scope

Track three things:

1. **Clockify time log** — thesis hours for the Kratt project.
2. **GitLab issues** — coarse roadmap / supervisor-visible planning.
3. **Progress digest** — short weekly summary from git commits, agent sessions, and docs changes.

This is bookkeeping automation, not a scientific evidence source. Exact research claims still come from measured artifacts, frozen test sets, and thesis documents.

## Manual source-of-truth commands

```bash
# Clockify project total for current thesis period
clockify-cli report 2026-04-01 today --duration-formatted -p "$KRATT_CLOCKIFY_PROJECT_ID"

# Missing recent entries check
clockify-cli report 2026-04-15 today --csv -p "$KRATT_CLOCKIFY_PROJECT_ID"

# GitLab issue overview
glab issue list -R malinh/iaib --per-page 50

# Commit timeline
git log --since='7 days ago' --date=short --pretty=format:'%ad %h %s' --first-parent
```

## Desired weekly automation

Run once per week, preferably before supervisor meeting prep.

1. Collect commits since the last report:
   - first-parent `main` commits;
   - accepted `cron/*` thesis-automation commits;
   - notable uncommitted work from `git status`.
2. Collect recent agent-session headings:
   - Pi sessions under `~/.pi/agent/sessions/--Users-mattias-kratt--/`;
   - Hermes sessions under `~/.hermes/sessions/`;
   - Codex sessions under `~/.codex/sessions/`;
   - Claude Code project sessions under `~/.claude/projects/-Users-mattias-kratt*`.
3. Produce a proposed Clockify backfill table:
   - date;
   - start/end or duration;
   - concise description;
   - evidence anchors: commit hashes / session filenames.
4. Ask for human confirmation before writing Clockify entries.
5. Produce a GitLab triage checklist:
   - issues to close;
   - issues to update;
   - new issues worth creating;
   - thesis-critical blockers.
6. Append a short digest to `docs/research/weekly-progress-digests.md` once reviewed.

## Guardrails

- Never create Clockify entries without explicit confirmation.
- Prefer conservative hours when reconstructing from evidence.
- Do not double-log days that already have detailed Clockify entries.
- Keep GitLab issues coarse; do not mirror every small task.
- Do not let tracking automation become a replacement for `docs/PROJECT_TODO.md`.

## Suggested future CLI wrappers

Add these when the workflow stabilizes:

```bash
kratt tracking status      # Clockify + GitLab + git status snapshot
kratt tracking propose     # generate proposed backfill / weekly digest only
kratt tracking clockify    # apply approved Clockify entries from a reviewed CSV/YAML
kratt tracking gitlab      # print issue triage commands / summaries
```

## 2026-04-26 backfill applied

Applied 8 Clockify entries for 2026-04-19..2026-04-26, total **28:30:00**.

Clockify totals after backfill:

- 2025-01-01..today: **193:46:33**
- 2026-01-01..today: **160:52:26**
- 2026-04-01..today: **103:15:00**

Backfilled themes:

- repo/context-window and source-of-truth process;
- Hermes thesis automation review;
- supervisor meeting prep and Android field benchmark planning;
- thesis methodology / claim-evidence / formal-compliance tightening;
- Android field data and model comparison;
- demo tooling, WiZ/Claude Code pipeline, user-testing plan;
- scope decision and project tracking audit.

## 2026-04-26 GitLab tracking update

Created two new GitLab issues:

- `#28` — Kasutajatestide pilot ja 20–30 osaleja täistest, estimate **35h**, spent **3h**.
- `#29` — Thesis automation ja project tracking automation, estimate **8h**, spent **5h**.

Distributed the same **28:30:00** recent backfill into GitLab issue time tracking:

- `#29` thesis/project tracking automation: **+5h**
- `#28` user-testing planning: **+3h**
- `#19` thesis drafting / scope / methodology: **+6h**
- `#18` wake-word pipeline / Android field data: **+5h**
- `#25` streaming FAPH methodology/artifacts: **+4h**
- `#27` MoE/consensus: **+2h30m**
- `#20` Home Assistant/demo pipeline: **+3h**

Ran `./scripts/gitlab-time-stats.sh` after updates:

- GitLab total estimate: **122h 30m**
- GitLab total spent: **209h 39m**
- GitLab progress vs issue estimates: **171%**

Issue notes were added on `#2`, `#9`, `#18`–`#29` where relevant to mark current scope, de-prioritized tracks, and next steps.
