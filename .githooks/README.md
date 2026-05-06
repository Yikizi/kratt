# Time-tracking git hooks

Captures commit metadata and proposes Clockify+GitLab time entries via LLM,
to avoid 8-day backfills like the one on 2026-05-04.

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
| `lib/propose_commit.py` | Tier 1 proposer | async, fire-and-forget | 1 codex call |
| `pre-push` | orchestrator | every push | shell only |
| `lib/review_proposals.py` | Tier 2 reviewer | sync | shell summary today; LLM-aggregator plumbed for later |

## Storage (`~/.kratt-time-log/`)

| Path | Purpose |
|------|---------|
| `commits.jsonl` | Source of truth — every commit, with `gap_sec` from previous |
| `proposals/YYYY-MM-DD.jsonl` | LLM-proposed Clockify entries per commit |
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

## Disable temporarily

```sh
KRATT_TIME_HOOKS=0 git commit -m "..."
```

## Apply proposals

Not yet automated. Read `~/.kratt-time-log/review-pending.md` and feed
relevant entries to `clockify-cli manual` + `glab issue note <N> -m "/spend Xh"`.
A `kratt time apply` CLI wrapper is on the roadmap.

## Diagnostics

```sh
# Last few captured commits
tail -3 ~/.kratt-time-log/commits.jsonl

# Today's proposals
cat ~/.kratt-time-log/proposals/$(date +%Y-%m-%d).jsonl | jq .

# Agent errors
tail -20 ~/.kratt-time-log/logs/propose-errors.log
```
