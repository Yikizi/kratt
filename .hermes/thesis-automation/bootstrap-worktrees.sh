#!/usr/bin/env bash
# Bootstrap / repair all active lane branches and their persistent worktrees.
# Idempotent. Safe to re-run.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$HERE" rev-parse --show-toplevel)"
cd "$REPO"

LANES_JSON="$REPO/.hermes/thesis-automation/lanes/lanes.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "bootstrap: jq is required" >&2
  exit 1
fi

# Ensure main is clean enough (warn-only).
if ! git rev-parse --verify main >/dev/null 2>&1; then
  echo "bootstrap: no 'main' branch in $REPO" >&2
  exit 1
fi

MAIN_SHA="$(git rev-parse main)"

LANE_IDS_STR="$(jq -r '.lanes[] | select(.active==true) | .id' "$LANES_JSON")"

for lane in $LANE_IDS_STR; do
  branch="cron/${lane}"
  wt_rel="$(jq -r --arg id "$lane" '.lanes[] | select(.id==$id) | .worktree' "$LANES_JSON")"
  wt_abs="$REPO/$wt_rel"

  # Ensure branch exists.
  if git rev-parse --verify "$branch" >/dev/null 2>&1; then
    :
  else
    git branch "$branch" "$MAIN_SHA"
    echo "bootstrap: created branch $branch at $MAIN_SHA"
  fi

  # Ensure worktree is registered at the expected path with the expected branch.
  existing_path="$(git worktree list --porcelain | awk -v b="refs/heads/${branch}" '
    $1=="worktree" {p=$2}
    $1=="branch" && $2==b {print p; exit}
  ' || true)"

  if [[ -n "${existing_path:-}" && "$existing_path" != "$wt_abs" ]]; then
    echo "bootstrap: moving worktree for $branch from $existing_path -> $wt_abs"
    git worktree remove --force "$existing_path" || true
    existing_path=""
  fi

  if [[ -z "${existing_path:-}" || ! -d "$wt_abs" ]]; then
    mkdir -p "$(dirname "$wt_abs")"
    git worktree add "$wt_abs" "$branch"
    echo "bootstrap: added worktree $wt_abs on $branch"
  fi
done

echo "bootstrap: done."
git worktree list | grep -E "cron-|/kratt$" || true
