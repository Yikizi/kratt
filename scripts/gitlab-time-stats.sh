#!/bin/bash
# GitLab time tracking statistics
# Usage: ./scripts/gitlab-time-stats.sh

PROJECT="malinh%2Fiaib"
TARGET_HOURS="${TARGET_HOURS:-312}" # 12 EAP × 26h thesis budget; override via env

echo "=== GitLab Time Tracking Statistics ==="
echo "Target budget: ${TARGET_HOURS}h"
echo

# Get all issues with time tracking
glab api "projects/${PROJECT}/issues" --paginate | jq --argjson target "$TARGET_HOURS" '
  [.[] | {
    id: .id,
    iid: .iid,
    title: .title,
    time_estimate: .time_stats.time_estimate,
    time_spent: .time_stats.total_time_spent
  }] | {
    total_estimate: (map(.time_estimate) | add),
    total_spent: (map(.time_spent) | add),
    target_seconds: ($target * 3600),
    issues: .
  }
' | jq '
  {
    total_spent_hours: (.total_spent / 3600 | floor),
    total_spent_minutes: ((.total_spent % 3600) / 60 | floor),
    total_estimate_hours: (.total_estimate / 3600 | floor),
    total_estimate_minutes: ((.total_estimate % 3600) / 60 | floor),
    target_hours: (.target_seconds / 3600),
    remaining_to_target_hours: ((.target_seconds - .total_spent) / 3600 | floor),
    remaining_to_target_minutes: ((((.target_seconds - .total_spent) % 3600) + 3600) % 3600 / 60 | floor),
    progress_vs_target_percent: ((.total_spent / .target_seconds) * 100 | . * 10 | floor / 10),
    progress_vs_estimate_percent: (if .total_estimate > 0 then (.total_spent / .total_estimate) * 100 | floor else null end)
  }
'

echo
echo "Detailed breakdown:"
glab api "projects/${PROJECT}/issues" --paginate | jq -r '
  [.[] | {
    iid: .iid,
    title: .title,
    spent: .time_stats.total_time_spent,
    estimate: .time_stats.time_estimate
  }] |
  map(select(.spent > 0 or .estimate > 0)) |
  sort_by(.iid) |
  .[] |
  "#\(.iid): \(.title)\n  Spent: \(.spent / 3600 | floor)h \((.spent % 3600) / 60 | floor)m / Estimate: \(.estimate / 3600 | floor)h \((.estimate % 3600) / 60 | floor)m"
'
