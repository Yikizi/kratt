# Documentation Maintenance

Lean process for keeping repo docs useful without turning maintenance into a
second project.

## Freshness Tiers

### Tier 1 — source of truth

These must reflect the current operating reality:

- `docs/PROJECT_TODO.md`
- `docs/research/source-of-truth-apr-2026.md`
- `docs/research/wake-word-evaluation-methodology.md`
- `wake-word/docs/MODEL_LINEAGE.md`
- `wake-word/evaluation/training_data_manifest.md`

Rule:
- update them in the same session when a decision, benchmark baseline, or model
  ranking materially changes.

### Tier 2 — operator entry docs

These are high-traffic orientation docs and should stay roughly aligned with the
current repo shape:

- `README.md`
- `wake-word/README.md`
- `wake-word/CLAUDE.md`
- `docs/CLAUDE.md`
- `docs/GIT_WORKFLOW.md`

Rule:
- if a doc describes setup, active directories, or current “best model”, it
  should be reviewed at least weekly.

### Tier 3 — dated snapshots

These are valuable but intentionally time-bound:

- `docs/research/*.md`
- `docs/notebooklm-pack/*`
- presentation/export packs and dated analysis notes

Rule:
- do not silently rewrite historical documents into “current state” docs.
- keep the date in the title or body and link back to Tier 1 docs when needed.

## Quiet Cleanup Workflow

1. Run the audit:

```bash
python3 scripts/docs_freshness_audit.py
```

2. Fix only the high-signal items first:
- missing or stale Tier 1 docs
- entry docs with obsolete setup instructions
- docs that still describe removed directories or workflows

3. For historical docs:
- keep them if they are still useful as dated evidence
- add context rather than force-rewriting them into evergreen docs

4. When a cleanup session finishes:
- refresh any affected Tier 1 doc
- add or update `Last updated: YYYY-MM-DD` on process docs

## What Counts As “Stale”

Examples:

- setup commands that no longer work
- references to removed directories such as `backend/` or `experiments/`
- model rankings or deployment recommendations that conflict with current
  source-of-truth docs
- process docs with old dates and old repo topology

Not automatically stale:

- dated research snapshots
- thesis notes tied to a specific checkpoint
- archived comparison material

## Suggested Cadence

- After major ML/eval change: same-day Tier 1 refresh
- Weekly: run the docs freshness audit and fix the top 1-3 findings
- Monthly: prune or clearly label historical docs that keep confusing navigation

## Automation

Recommended low-noise schedule:

- weekly thread heartbeat
- Monday morning, local time
- task: run `python3 scripts/docs_freshness_audit.py`, summarize findings, and
  suggest the next quiet cleanup batch

This keeps docs maintenance visible without mixing it into every coding session.
