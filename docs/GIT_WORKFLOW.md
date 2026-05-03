# Git Workflow

Last updated: 2026-04-29

This file describes the current low-drama git workflow for the Kratt monorepo.
It replaces older setup-era notes about remotes, milestones, and repo topology.

## Current Reality

- Active branch is usually `main`.
- The repo often contains large, long-lived ML worktrees and generated artifacts.
- Documentation, Android code, training scripts, and model metadata should not be
  committed as one giant blob unless they truly belong to the same change.
- `.claude/`, `.hermes/`, local venvs, pulled audio, and bulky generated outputs
  are tooling context, not the core product history.

## Quiet Cleanup First

When the worktree is noisy, prefer a calm cleanup pass before feature work:

```bash
git status --short --branch
git diff --stat
git diff --cached --stat
```

Then split changes into small, explainable batches.

Recommended commit slices in this repo:

1. docs/process updates
2. Android app changes
3. wake-word training/evaluation code
4. model metadata / benchmark artifacts
5. large binaries or pulled outputs only if they are intentionally versioned

## Staging Rules

- Do not use `git add .` in a dirty monorepo unless you already verified the full
  diff and want everything.
- Prefer path-scoped staging:

```bash
git add docs/documentation-maintenance.md scripts/docs_freshness_audit.py
git add wake-word/README.md
```

- Keep user-authored unrelated changes in place; do not revert them as part of a
  cleanup pass.
- If a file is both important and unstable, inspect it before staging rather than
  assuming it belongs in the current commit.

## Commit Style

Use small conventional commits when possible:

```text
docs: refresh wake-word README
docs: add repo documentation maintenance guide
fix(android): switch false logger to multi-detector runner
feat(eval): add Android field-run analysis
```

Good commit properties:

- one coherent topic
- clear reason for the change
- easy to revert independently

## Documentation Hygiene

Before or after a meaningful docs-heavy change:

```bash
python3 scripts/docs_freshness_audit.py
```

Priority order for docs refresh:

1. `docs/PROJECT_TODO.md`
2. `docs/research/source-of-truth-apr-2026.md`
3. entry docs such as `README.md`, `wake-word/README.md`, `wake-word/CLAUDE.md`

For the maintenance policy itself, see
`docs/documentation-maintenance.md`.

## Large Artifact Caution

The repo contains:

- model binaries (`.tflite`, `.onnx`)
- Android capture outputs
- benchmark CSV/JSON/HTML artifacts

Before committing them, answer:

- is this artifact part of the actual reproducible record?
- does it belong with the code/docs change in the same commit?
- is a smaller metadata summary enough instead?

If the answer is unclear, leave the artifact unstaged and commit the smaller
code or docs change first.

## Helpful Commands

```bash
git status --short --branch
git diff --stat
git diff --cached --stat
git log --oneline --decorate -n 12
git restore --staged <path>
```

Avoid destructive history cleanup in a dirty tree unless that is the explicit
task.
