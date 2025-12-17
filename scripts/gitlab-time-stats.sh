#!/bin/bash
# GitLab time tracking statistics
# Usage: ./scripts/gitlab-time-stats.sh

PROJECT="malinh%2Fiaib"

echo "=== GitLab Time Tracking Statistics ==="
echo

# Get all issues with time tracking
glab api "projects/${PROJECT}/issues" --paginate | jq '
  [.[] | {
    id: .id,
    iid: .iid,
    title: .title,
    time_estimate: .time_stats.time_estimate,
    time_spent: .time_stats.total_time_spent
  }] | {
    total_estimate: (map(.time_estimate) | add),
    total_spent: (map(.time_spent) | add),
    issues: .
  }
' | jq '
  {
    total_estimate_hours: (.total_estimate / 3600 | floor),
    total_estimate_minutes: ((.total_estimate % 3600) / 60 | floor),
    total_spent_hours: (.total_spent / 3600 | floor),
    total_spent_minutes: ((.total_spent % 3600) / 60 | floor),
    remaining_hours: ((.total_estimate - .total_spent) / 3600 | floor),
    remaining_minutes: (((.total_estimate - .total_spent) % 3600) / 60 | floor),
    progress_percent: ((.total_spent / .total_estimate) * 100 | floor)
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
