# AGENTS.md — Context for Coding Agents (Codex, Pi agent, etc.)

This file is the agent-tool-agnostic counterpart of `CLAUDE.md`. Read both before
making changes. If they ever disagree, `CLAUDE.md` is authoritative — please flag
the divergence so it can be reconciled.

## ⚠️ Hard deadline

**Thesis document submission: 2026-05-18 (TalTech BSc).**

- Non-negotiable cutoff. Missing it pushes graduation.
- After early May, treat thesis writing (chapters 3–5 still pending) as the
  critical path. Reject or defer scope additions, new experiments, and
  refactors that threaten the writing budget.
- When in doubt, prefer "good enough for thesis" over polish.

## Project at a glance

- **Project**: Kratt — Estonian wake word ("Kuule Kratt") + Home Assistant
  voice satellite system.
- **Type**: TalTech Informatics bachelor's thesis (Feb 2025 – Jun 2026).
- **Author**: Mattias.
- **Languages**: Estonian for thesis prose; English for code, comments, commits.

## What to read first

1. `CLAUDE.md` (repo root) — full project overview, structure, conventions.
2. `docs/PROJECT_TODO.md` — current task breakdown.
3. `docs/research/source-of-truth-apr-2026.md` — current model/eval/user-test framing.
4. `docs/research/agentic-thesis-positioning-and-shortcomings-2026-04-14.md`
   — required reading before any methodological or thesis-direction proposal.
4. Sub-package `CLAUDE.md` files for area-specific context (`wake-word/`,
   `home-assistant/`, `scripts/`, etc.).

## Conventions agents must follow

- Python: `snake_case.py`; configs: `kebab-case.yaml`; docs: `kebab-case.md`.
- Python packages are project-scoped and managed with `uv`. Do not invoke
  global `pip`.
- Every workflow script needs a `kratt <name>` CLI wrapper in
  `cli/commands/kratt-*`.
- Commit messages: English, conventional commits.
- For each new wake-word model version under `wake-word/models/kuule-kratt-*/`:
  add a `NOTES.md` in its directory **and** an entry in
  `wake-word/docs/MODEL_LINEAGE.md`.
- Privacy-first: always consider GDPR / opt-in for voice data.
- Don't reinvent STT/TTS — focus on the wake word.

## Operational notes for non-Claude agents

- The Pi agent runs on the Raspberry Pi 5 that is also the always-on compute
  node. Avoid long-running training jobs there; training belongs on TalTech
  HPC (SLURM).
- Treat the time-tracking budget as 312h total (12 EAP × 26h). The script
  `scripts/gitlab-time-stats.sh` reports progress against it.
- Don't bulk-delete data directories to "regenerate" them — generate
  alongside and let the user decide what to keep.
