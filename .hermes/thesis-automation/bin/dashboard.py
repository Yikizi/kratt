#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from collections import Counter, defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[3]
AUTO = REPO / ".hermes" / "thesis-automation"
LOGS = AUTO / "logs"
LANES_JSON = AUTO / "lanes" / "lanes.json"
REVIEWS_INDEX = REPO / ".hermes" / "thesis-quality-reviews" / "index.json"


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    with path.open() as f:
        return json.load(f)


def iter_hourly_entries():
    hourly_dir = LOGS / "hourly"
    if not hourly_dir.exists():
        return
    for path in sorted(hourly_dir.glob("*.jsonl")):
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except Exception:
                continue
            data["_log_file"] = str(path.relative_to(REPO))
            yield data


def iter_daily_entries():
    daily_dir = LOGS / "daily"
    if not daily_dir.exists():
        return
    for path in sorted(daily_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        data["_log_file"] = str(path.relative_to(REPO))
        yield data


def iter_weekly_entries():
    weekly_dir = LOGS / "weekly"
    if not weekly_dir.exists():
        return
    for path in sorted(weekly_dir.glob("*.md")):
        yield {"path": str(path.relative_to(REPO)), "name": path.name}


def parse_ts(ts: str | None):
    if not ts:
        return None
    try:
        return dt.datetime.fromisoformat(ts)
    except Exception:
        return None


def load_lanes():
    data = read_json(LANES_JSON, default={"lanes": []})
    return data.get("lanes", [])


def empty_lane_stats(lane_ids):
    out = {}
    for lane_id in lane_ids:
        out[lane_id] = {
            "runs": 0,
            "committed": 0,
            "pushback": 0,
            "no_change": 0,
            "reviewer_failed": 0,
            "writer_failed": 0,
            "accepted": 0,
            "rejected": 0,
            "deferred": 0,
            "last_run": None,
            "last_file": None,
            "last_commit": None,
            "last_result": None,
        }
    return out


def build_stats():
    lanes = load_lanes()
    lane_ids = [lane["id"] for lane in lanes]
    lane_titles = {lane["id"]: lane.get("title", lane["id"]) for lane in lanes}

    hourly_entries = list(iter_hourly_entries() or [])
    daily_entries = list(iter_daily_entries() or [])
    weekly_entries = list(iter_weekly_entries() or [])
    reviews_index = read_json(REVIEWS_INDEX, default={"reviews": []})
    reviews = reviews_index.get("reviews", [])

    result_counts = Counter()
    lane_stats = empty_lane_stats(lane_ids)
    hourly_runs_by_day = Counter()
    commit_subjects = {}
    unique_hourly_commit_shas = set()
    latest_hourly = None

    for entry in hourly_entries:
        result = entry.get("result", "unknown")
        lane = entry.get("lane", "unknown")
        ts = parse_ts(entry.get("ts"))
        if ts:
            hourly_runs_by_day[ts.date().isoformat()] += 1
            if latest_hourly is None or ts > parse_ts(latest_hourly.get("ts")):
                latest_hourly = entry
        result_counts[result] += 1
        lane_stats.setdefault(lane, {
            "runs": 0, "committed": 0, "pushback": 0, "no_change": 0,
            "reviewer_failed": 0, "writer_failed": 0, "accepted": 0,
            "rejected": 0, "deferred": 0, "last_run": None,
            "last_file": None, "last_commit": None, "last_result": None,
        })
        lane_stats[lane]["runs"] += 1
        lane_stats[lane]["last_file"] = entry.get("target_file")
        lane_stats[lane]["last_result"] = result
        lane_stats[lane]["last_run"] = entry.get("ts")
        if result in lane_stats[lane]:
            lane_stats[lane][result] += 1
        elif result == "committed":
            lane_stats[lane]["committed"] += 1
        elif result == "pushback":
            lane_stats[lane]["pushback"] += 1
        elif result == "no_change":
            lane_stats[lane]["no_change"] += 1
        elif result == "reviewer_failed":
            lane_stats[lane]["reviewer_failed"] += 1
        else:
            lane_stats[lane]["writer_failed"] += 1

        commit = entry.get("commit") or {}
        sha = commit.get("sha")
        if sha:
            unique_hourly_commit_shas.add(sha)
            commit_subjects[sha] = commit.get("subject")
            lane_stats[lane]["last_commit"] = {
                "sha": sha,
                "subject": commit.get("subject"),
            }

    daily_status_counts = Counter()
    daily_errors = 0
    degraded_daily = 0
    daily_runs_by_day = Counter()
    accepted_total = rejected_total = deferred_total = 0
    accepted_shas = set()
    recent_accepts = []
    recent_rejects = []
    latest_daily = None

    for entry in daily_entries:
        ts = parse_ts(entry.get("ts"))
        if ts:
            daily_runs_by_day[ts.date().isoformat()] += 1
            if latest_daily is None or ts > parse_ts(latest_daily.get("ts")):
                latest_daily = entry
        status = entry.get("status", "unknown")
        daily_status_counts[status] += 1
        if status == "degraded":
            degraded_daily += 1
        if entry.get("errors"):
            daily_errors += 1

        for item in entry.get("accepted", []):
            lane = item.get("lane", "unknown")
            lane_stats.setdefault(lane, empty_lane_stats([]))
            lane_stats[lane]["accepted"] += 1
            accepted_total += 1
            sha = item.get("sha")
            if sha:
                accepted_shas.add(sha)
            recent_accepts.append({
                "ts": entry.get("ts"),
                "lane": lane,
                "sha": sha,
                "reason": item.get("reason", ""),
                "subject": commit_subjects.get(sha, "") if sha else "",
            })
        for item in entry.get("rejected", []):
            lane = item.get("lane", "unknown")
            lane_stats.setdefault(lane, empty_lane_stats([]))
            lane_stats[lane]["rejected"] += 1
            rejected_total += 1
            recent_rejects.append({
                "ts": entry.get("ts"),
                "lane": lane,
                "sha": item.get("sha"),
                "reason": item.get("reason", ""),
                "subject": commit_subjects.get(item.get("sha"), "") if item.get("sha") else "",
            })
        for item in entry.get("deferred", []):
            lane = item.get("lane", "unknown")
            lane_stats.setdefault(lane, empty_lane_stats([]))
            lane_stats[lane]["deferred"] += 1
            deferred_total += 1

    acceptance_rate = round((accepted_total / max(1, accepted_total + rejected_total + deferred_total)) * 100, 1)
    hourly_commit_rate = round((result_counts.get("committed", 0) / max(1, len(hourly_entries))) * 100, 1)

    review_summary = None
    if reviews:
        latest_review = sorted(reviews, key=lambda r: r.get("timestamp", ""))[-1]
        review_summary = {
            "timestamp": latest_review.get("timestamp"),
            "readiness": latest_review.get("overall_readiness_0_to_10"),
            "kind": latest_review.get("kind"),
            "markdown_path": latest_review.get("markdown_path"),
        }

    recent_days = sorted(set(hourly_runs_by_day) | set(daily_runs_by_day))[-14:]
    series = []
    for day in recent_days:
        series.append({
            "day": day,
            "hourly_runs": hourly_runs_by_day.get(day, 0),
            "daily_runs": daily_runs_by_day.get(day, 0),
        })

    lane_rows = []
    for lane_id in lane_ids:
        row = lane_stats[lane_id]
        runs = max(1, row["runs"])
        commit_efficiency = round((row["committed"] / runs) * 100, 1)
        issue_count = row["rejected"] + row["reviewer_failed"] + row["writer_failed"] + row["no_change"]
        lane_rows.append({
            "lane": lane_id,
            "title": lane_titles.get(lane_id, lane_id),
            "commit_efficiency_pct": commit_efficiency,
            "issue_count": issue_count,
            **row,
        })

    lane_rows.sort(key=lambda r: (-r["runs"], r["lane"]))
    problematic_lanes = sorted(
        lane_rows,
        key=lambda r: (-r["issue_count"], r["commit_efficiency_pct"], -r["runs"], r["lane"])
    )[:5]

    warnings = []
    if degraded_daily:
        warnings.append(f"{degraded_daily} daily consolidation run(s) ended degraded.")
    if daily_errors:
        warnings.append(f"{daily_errors} daily run(s) recorded errors or invalid consolidator output.")
    if result_counts.get("reviewer_failed", 0):
        warnings.append(f"{result_counts.get('reviewer_failed', 0)} hourly run(s) failed at reviewer stage.")
    if not weekly_entries:
        warnings.append("No weekly meta-review logs found yet.")
    if reviews and review_summary and (review_summary.get("readiness") or 0) < 7:
        warnings.append(f"Latest thesis readiness review is {review_summary.get('readiness')}/10; thesis still reads as unfinished.")

    recent_accepts = sorted(recent_accepts, key=lambda x: x.get("ts") or "", reverse=True)[:12]
    recent_rejects = sorted(recent_rejects, key=lambda x: x.get("ts") or "", reverse=True)[:12]

    return {
        "generated_at": dt.datetime.now().replace(microsecond=0).isoformat(),
        "repo": str(REPO),
        "paths": {
            "hourly": str((LOGS / 'hourly').relative_to(REPO)),
            "daily": str((LOGS / 'daily').relative_to(REPO)),
            "weekly": str((LOGS / 'weekly').relative_to(REPO)),
        },
        "summary": {
            "hourly_runs": len(hourly_entries),
            "hourly_log_files": len(list((LOGS / 'hourly').glob('*.jsonl'))) if (LOGS / 'hourly').exists() else 0,
            "hourly_commits": result_counts.get("committed", 0),
            "unique_hourly_commit_shas": len(unique_hourly_commit_shas),
            "hourly_commit_rate_pct": hourly_commit_rate,
            "daily_runs": len(daily_entries),
            "weekly_runs": len(weekly_entries),
            "quality_reviews": len(reviews),
            "accepted_commits": accepted_total,
            "rejected_commits": rejected_total,
            "deferred_commits": deferred_total,
            "acceptance_rate_pct": acceptance_rate,
            "degraded_daily_runs": degraded_daily,
            "daily_runs_with_errors": daily_errors,
            "active_lanes": len(lane_ids),
        },
        "hourly_results": dict(result_counts),
        "daily_status_counts": dict(daily_status_counts),
        "series": series,
        "lane_rows": lane_rows,
        "latest": {
            "hourly": latest_hourly,
            "daily": latest_daily,
            "review": review_summary,
        },
        "weekly_entries": weekly_entries,
        "accepted_shas": sorted(accepted_shas),
        "commit_subjects": commit_subjects,
        "recent_accepts": recent_accepts,
        "recent_rejects": recent_rejects,
        "problematic_lanes": problematic_lanes,
        "warnings": warnings,
    }


HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Kratt Thesis Automation Dashboard</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0b1020;
      --panel: #121935;
      --panel-2: #1a2347;
      --text: #eef3ff;
      --muted: #aab4d6;
      --good: #3ecf8e;
      --warn: #ffb020;
      --bad: #ff6b6b;
      --blue: #66b3ff;
      --border: rgba(255,255,255,0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font: 14px/1.45 Inter, ui-sans-serif, system-ui, -apple-system, sans-serif;
      background: linear-gradient(180deg, var(--bg), #0e1430 60%, #0b1020);
      color: var(--text);
    }
    .wrap {
      max-width: 1400px;
      margin: 0 auto;
      padding: 24px;
    }
    h1,h2,h3 { margin: 0 0 12px; }
    .muted { color: var(--muted); }
    .topbar {
      display: flex; justify-content: space-between; gap: 16px; align-items: flex-end;
      margin-bottom: 24px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }
    .panel {
      background: rgba(18,25,53,0.9);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 16px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.22);
      backdrop-filter: blur(6px);
    }
    .metric { font-size: 30px; font-weight: 700; margin: 6px 0; }
    .kicker { font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }
    .good { color: var(--good); }
    .warn { color: var(--warn); }
    .bad { color: var(--bad); }
    .blue { color: var(--blue); }
    .two-col {
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 14px;
      margin-bottom: 18px;
    }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 10px 8px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }
    th { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; }
    .pill {
      display: inline-block; border-radius: 999px; padding: 2px 8px; font-size: 12px;
      border: 1px solid var(--border); background: rgba(255,255,255,0.04);
    }
    .bars { display: grid; gap: 10px; }
    .bar-row { display: grid; grid-template-columns: 96px 1fr 60px; gap: 10px; align-items: center; }
    .bar-track { height: 10px; background: rgba(255,255,255,0.08); border-radius: 999px; overflow: hidden; }
    .bar-fill { height: 100%; background: linear-gradient(90deg, var(--blue), var(--good)); }
    .timeline { display: grid; gap: 10px; }
    .timeline-row { display: grid; grid-template-columns: 88px 1fr auto; gap: 10px; align-items: center; }
    .timeline-bars { display: flex; gap: 6px; align-items: center; }
    .spark { height: 10px; border-radius: 999px; background: var(--blue); opacity: 0.85; }
    .spark.daily { background: var(--warn); }
    code { color: #c8d5ff; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }
    .footer { margin-top: 18px; color: var(--muted); font-size: 12px; }
    .list { display: grid; gap: 10px; }
    .item { padding: 10px 12px; border: 1px solid var(--border); border-radius: 12px; background: rgba(255,255,255,0.03); }
    .item-title { font-weight: 600; margin-bottom: 4px; }
    .item-meta { color: var(--muted); font-size: 12px; }
    .warning { border-left: 4px solid var(--warn); padding-left: 10px; }
    @media (max-width: 1100px) {
      .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .two-col { grid-template-columns: 1fr; }
    }
    @media (max-width: 720px) {
      .grid { grid-template-columns: 1fr; }
      .topbar { flex-direction: column; align-items: flex-start; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <div>
        <h1>Kratt thesis automation dashboard</h1>
        <div class="muted">Live stats from <code>.hermes/thesis-automation/logs/</code> · auto-refresh every 10s</div>
      </div>
      <div class="muted" id="generatedAt">Loading…</div>
    </div>

    <div class="grid" id="summaryCards"></div>

    <div class="two-col">
      <div class="panel">
        <h2>Run volume by day</h2>
        <div class="timeline" id="timeline"></div>
      </div>
      <div class="panel">
        <h2>Hourly outcomes</h2>
        <div class="bars" id="hourlyBars"></div>
        <h3 style="margin-top:18px">Daily consolidation status</h3>
        <div class="bars" id="dailyBars"></div>
      </div>
    </div>

    <div class="two-col">
      <div class="panel">
        <h2>Latest activity</h2>
        <table>
          <tbody id="latestTable"></tbody>
        </table>
      </div>
      <div class="panel">
        <h2>Quality review</h2>
        <div id="reviewBox" class="muted">No review found.</div>
      </div>
    </div>

    <div class="two-col">
      <div class="panel">
        <h2>Health warnings</h2>
        <div id="warningsBox" class="list"></div>
      </div>
      <div class="panel">
        <h2>Problematic lanes</h2>
        <div id="problemLanes" class="list"></div>
      </div>
    </div>

    <div class="two-col">
      <div class="panel">
        <h2>Recent accepted commits</h2>
        <div id="recentAccepts" class="list"></div>
      </div>
      <div class="panel">
        <h2>Recent rejected commits</h2>
        <div id="recentRejects" class="list"></div>
      </div>
    </div>

    <div class="panel">
      <h2>Lane performance</h2>
      <table>
        <thead>
          <tr>
            <th>Lane</th>
            <th>Runs</th>
            <th>Committed</th>
            <th>Accepted</th>
            <th>Rejected</th>
            <th>Pushback</th>
            <th>Efficiency</th>
            <th>Last result</th>
            <th>Last file</th>
          </tr>
        </thead>
        <tbody id="laneTable"></tbody>
      </table>
    </div>

    <div class="footer" id="footer"></div>
  </div>
<script>
const refreshMs = 10000;

function esc(s) {
  return String(s ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
}

function metricCard(label, value, sub, klass='') {
  return `
    <div class="panel">
      <div class="kicker">${esc(label)}</div>
      <div class="metric ${klass}">${esc(value)}</div>
      <div class="muted">${esc(sub)}</div>
    </div>`;
}

function renderBars(el, data, total) {
  const keys = Object.keys(data || {});
  if (!keys.length) { el.innerHTML = '<div class="muted">No data.</div>'; return; }
  el.innerHTML = keys.map(k => {
    const v = data[k] || 0;
    const pct = Math.max(2, Math.round((v / Math.max(1,total)) * 100));
    return `<div class="bar-row"><div>${esc(k)}</div><div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div><div>${v}</div></div>`;
  }).join('');
}

function renderList(el, items, renderItem, emptyText='No data.') {
  if (!items || !items.length) {
    el.innerHTML = `<div class="muted">${esc(emptyText)}</div>`;
    return;
  }
  el.innerHTML = items.map(renderItem).join('');
}

function render(data) {
  document.getElementById('generatedAt').textContent = `Generated ${data.generated_at}`;
  const s = data.summary;
  document.getElementById('summaryCards').innerHTML = [
    metricCard('Hourly runs', s.hourly_runs, `${s.hourly_log_files} log files`),
    metricCard('Lane commits', s.hourly_commits, `${s.hourly_commit_rate_pct}% of hourly runs`, 'good'),
    metricCard('Daily consolidations', s.daily_runs, `${s.accepted_commits} accepted / ${s.rejected_commits} rejected`, 'blue'),
    metricCard('Health', `${s.degraded_daily_runs} degraded`, `${s.daily_runs_with_errors} daily runs with errors`, s.degraded_daily_runs ? 'warn' : 'good'),
    metricCard('Acceptance rate', `${s.acceptance_rate_pct}%`, `${s.deferred_commits} deferred commits`, 'good'),
    metricCard('Active lanes', s.active_lanes, `${s.weekly_runs} weekly meta runs`),
    metricCard('Quality reviews', s.quality_reviews, `latest readiness shown below`),
    metricCard('Unique commit SHAs', s.unique_hourly_commit_shas, 'from hourly writer runs')
  ].join('');

  const maxHourly = Math.max(1, ...data.series.map(d => d.hourly_runs));
  const maxDaily = Math.max(1, ...data.series.map(d => d.daily_runs));
  document.getElementById('timeline').innerHTML = data.series.map(d => {
    const hw = Math.max(6, Math.round((d.hourly_runs / maxHourly) * 240));
    const dw = d.daily_runs ? Math.max(6, Math.round((d.daily_runs / maxDaily) * 120)) : 0;
    return `<div class="timeline-row">
      <div><code>${esc(d.day)}</code></div>
      <div class="timeline-bars">
        <div class="spark" style="width:${hw}px"></div>
        ${dw ? `<div class="spark daily" style="width:${dw}px"></div>` : ''}
      </div>
      <div class="muted">H ${d.hourly_runs} · D ${d.daily_runs}</div>
    </div>`;
  }).join('') || '<div class="muted">No run history yet.</div>';

  renderBars(document.getElementById('hourlyBars'), data.hourly_results, s.hourly_runs);
  renderBars(document.getElementById('dailyBars'), data.daily_status_counts, s.daily_runs);

  const latest = data.latest || {};
  document.getElementById('latestTable').innerHTML = `
    <tr><th>Latest hourly</th><td>${latest.hourly ? `${esc(latest.hourly.ts)} · <span class="pill">${esc(latest.hourly.lane)}</span> · ${esc(latest.hourly.result)}` : '<span class="muted">none</span>'}</td></tr>
    <tr><th>Latest commit</th><td>${latest.hourly && latest.hourly.commit ? `<code>${esc(latest.hourly.commit.sha.slice(0,7))}</code> ${esc(latest.hourly.commit.subject || '')}` : '<span class="muted">none</span>'}</td></tr>
    <tr><th>Target file</th><td>${latest.hourly ? `<code>${esc(latest.hourly.target_file)}</code>` : ''}</td></tr>
    <tr><th>Latest daily</th><td>${latest.daily ? `${esc(latest.daily.ts)} · status ${esc(latest.daily.status || 'unknown')}` : '<span class="muted">none</span>'}</td></tr>
    <tr><th>Refresh source</th><td><code>${esc(data.paths.hourly)}</code> + <code>${esc(data.paths.daily)}</code></td></tr>
  `;

  const review = latest.review;
  document.getElementById('reviewBox').innerHTML = review
    ? `<div class="metric blue">${esc(review.readiness)}/10</div>
       <div class="muted">Latest review · ${esc(review.timestamp)} · ${esc(review.kind)}</div>
       <div style="margin-top:8px"><code>${esc(review.markdown_path)}</code></div>`
    : '<div class="muted">No review found.</div>';

  renderList(
    document.getElementById('warningsBox'),
    data.warnings || [],
    (w) => `<div class="item warning">${esc(w)}</div>`,
    'No active health warnings.'
  );

  renderList(
    document.getElementById('problemLanes'),
    data.problematic_lanes || [],
    (r) => `<div class="item"><div class="item-title">${esc(r.lane)} <span class="pill">${esc(r.issue_count)} issues</span></div><div class="item-meta">${esc(r.title)} · ${esc(r.commit_efficiency_pct)}% commit efficiency · ${esc(r.rejected)} rejected · ${esc(r.reviewer_failed)} reviewer failed · ${esc(r.no_change)} no-change</div></div>`,
    'No problematic lanes detected.'
  );

  renderList(
    document.getElementById('recentAccepts'),
    data.recent_accepts || [],
    (r) => `<div class="item"><div class="item-title">${esc(r.lane)} · <code>${esc((r.sha || '').slice(0,7))}</code></div><div>${esc(r.subject || '(subject unavailable)')}</div><div class="item-meta">${esc(r.ts || '')} · ${esc(r.reason || '')}</div></div>`,
    'No accepted commits yet.'
  );

  renderList(
    document.getElementById('recentRejects'),
    data.recent_rejects || [],
    (r) => `<div class="item"><div class="item-title">${esc(r.lane)} · <code>${esc((r.sha || '').slice(0,7))}</code></div><div>${esc(r.subject || '(subject unavailable)')}</div><div class="item-meta">${esc(r.ts || '')} · ${esc(r.reason || '')}</div></div>`,
    'No rejected commits yet.'
  );

  document.getElementById('laneTable').innerHTML = data.lane_rows.map(r => `
    <tr>
      <td><strong>${esc(r.lane)}</strong><div class="muted">${esc(r.title)}</div></td>
      <td>${r.runs}</td>
      <td>${r.committed}</td>
      <td>${r.accepted}</td>
      <td>${r.rejected}</td>
      <td>${r.pushback}</td>
      <td>${r.commit_efficiency_pct}%</td>
      <td><span class="pill">${esc(r.last_result || '—')}</span></td>
      <td><code>${esc(r.last_file || '—')}</code></td>
    </tr>`).join('');

  document.getElementById('footer').innerHTML = `Repo: <code>${esc(data.repo)}</code> · accepted commits shown: ${(data.recent_accepts || []).length} · rejected commits shown: ${(data.recent_rejects || []).length}`;
}

async function load() {
  try {
    const res = await fetch('/api/stats.json?_=' + Date.now(), { cache: 'no-store' });
    const data = await res.json();
    render(data);
  } catch (err) {
    document.getElementById('generatedAt').textContent = 'Failed to load dashboard data';
    console.error(err);
  }
}

load();
setInterval(load, refreshMs);
</script>
</body>
</html>
'''


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        if os.environ.get("KRATT_DASHBOARD_QUIET") == "1":
            return
        super().log_message(fmt, *args)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/api/stats.json":
            body = json.dumps(build_stats(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"not found")


def main():
    ap = argparse.ArgumentParser(description="Serve a live HTML dashboard for thesis-automation logs.")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--dump-json", action="store_true", help="Print one stats snapshot as JSON and exit")
    args = ap.parse_args()

    if args.dump_json:
        print(json.dumps(build_stats(), indent=2, ensure_ascii=False))
        return

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Dashboard: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
