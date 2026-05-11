# Time-tracking git hooks

Captures commit metadata, proposes Clockify+GitLab time entries via LLM,
and auto-applies medium/high-confidence non-duplicate proposals by default.
This prevents the proposal queue from becoming another manual backlog.

## Activate

```sh
git config core.hooksPath .githooks
mkdir -p ~/.kratt-time-log/{proposals,logs}
chmod +x .githooks/post-commit .githooks/pre-push .githooks/lib/*.py
```

## Components

| File | Stage | When | Cost |
|------|-------|------|------|
| `post-commit` | orchestrator | every commit | shell only |
| `lib/log_commit.py` | Tier 0 logger | sync, ~50ms | none (no LLM) |
| `lib/propose_commit.py` | Tier 1 proposer + auto-applier | async, fire-and-forget | 1 codex call + Clockify/GitLab API |
| `lib/apply_proposals.py` | Backlog/manual applier | on demand | Clockify/GitLab API |
| `pre-push` | orchestrator | every push | shell only |
| `lib/review_proposals.py` | Tier 2 reviewer | sync | shell summary today; LLM-aggregator plumbed for later |

## Storage (`~/.kratt-time-log/`)

| Path | Purpose |
|------|---------|
| `commits.jsonl` | Source of truth — every commit, with `gap_sec` from previous |
| `proposals/YYYY-MM-DD.jsonl` | LLM-proposed entries plus `applied`/`skipped` backend status |
| `review-pending.md` | Human-readable pre-push summary |
| `logs/` | Agent stderr/stdout, parse-error log |

## Environment

| Var | Default | Purpose |
|-----|---------|---------|
| `KRATT_TIME_HOOKS` | `1` | Set `0` to skip all hooks for one command |
| `KRATT_TIME_AGENT_FAST` | `codex exec` | Tier 1 LLM (per commit, async) |
| `KRATT_TIME_AGENT_DEEP` | `claude --print` | Tier 2 LLM (pre-push, sync) |
| `KRATT_TIME_AGENT_TIMEOUT` | `180` | Tier 1 max seconds |
| `KRATT_TIME_REVIEW_TIMEOUT` | `240` | Tier 2 max seconds |
| `KRATT_TIME_AUTO_APPLY` | `1` | Auto-create Clockify entries and GitLab `/spend` notes after proposal |
| `KRATT_TIME_SKIP_CLOCKIFY` | `0` | Set `1` to only apply GitLab side |
| `KRATT_TIME_SKIP_GITLAB` | `0` | Set `1` to only apply Clockify side |
| `KRATT_GITLAB_REPO` | `malinh/iaib` | GitLab repo for issue notes |
| `KRATT_CLOCKIFY_PROJECT_ID` | required | Clockify project to write to |

## Disable temporarily

```sh
KRATT_TIME_HOOKS=0 git commit -m "..."
```

## Apply / clear proposals

Future proposals auto-apply by default. To clear or re-run a backlog manually:

```sh
# Dry-run recent unapplied proposals
.githooks/lib/apply_proposals.py --since 2026-05-08 --dry-run

# Apply them to Clockify + GitLab, skipping duplicate cherry-picks by patch-id
.githooks/lib/apply_proposals.py --since 2026-05-08

# Mark a covered backfill as skipped without external writes
.githooks/lib/apply_proposals.py --since 2026-05-04 --until 2026-05-07 \
  --mark-skipped 'covered by manual Clockify/GitLab backfill'
```

## Diagnostics

```sh
# Last few captured commits
tail -3 ~/.kratt-time-log/commits.jsonl

# Today's proposals and applied status
cat ~/.kratt-time-log/proposals/$(date +%Y-%m-%d).jsonl | jq .

# Agent errors
tail -20 ~/.kratt-time-log/logs/propose-errors.log
```
