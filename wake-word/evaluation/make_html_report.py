#!/usr/bin/env python3
"""Render a single self-contained interactive HTML report from benchmark CSV.

Input:  benchmark_results_*.csv (all thresholds, all test sets, all models)
Output: supervisor_report.html — single file, no CDN deps, minimalist style,
        sortable table, hoverable cells, DET-style threshold-sweep curves.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

MODEL_ORDER = [
    "v1", "v2", "v3", "v4", "v5",
    "v6", "v6-specaug", "v6-residual",
    "v7", "v8", "v9", "v10", "v11", "v12",
    "v13a", "v13b", "v14", "v15",
    "v16a", "v16b", "v16c", "v17a", "v17b",
    "oww-v17-smoke2",
    "v18a-clean48", "v18b-clean48-sa", "v18c-clean48-hn",
    "v18d-clean96", "v18e-clean48-tts-hn", "v18f-clean48-tts-hn-fast",
    "checkpoint-faph-v18d-clean96-pw96x4",
    "checkpoint-faph10-v18d-clean96-pw96x4",
    "checkpoint-faph20-v18d-clean96-pw96x4",
    "v19a-kratt-only",
    "ex2a", "ex3a", "ex3b",
    "expert-a", "expert-b", "expert-b2",
    "v14 + expert-b",
    "v6-residual + expert-a",
    "ex3a + expert-a",
    "ex3a + expert-b2",
    "ex3a + expert-a + expert-b2",
    "ex3a + expert-a + expert-b",
    "ex3a + expert-b + expert-b2",
    "ex3b + expert-b2",
    "v17a + v17b",
    "v17a + expert-a",
    "v17b + expert-a",
    "v18a-clean48 + expert-a",
    "v18a-clean48 + v16c",
    "v18a-clean48 + v18b-clean48-sa",
    "v18b-clean48-sa + expert-a",
    "v18b-clean48-sa + v16c",
    "v18c-clean48-hn + expert-a",
    "v18c-clean48-hn + v16c",
    "v18d-clean96 + expert-a",
    "v18d-clean96 + v16c",
    "v18e-clean48-tts-hn + expert-a",
    "v18e-clean48-tts-hn + v16c",
    "v18e-clean48-tts-hn + v18f-clean48-tts-hn-fast",
    "v18f-clean48-tts-hn-fast + expert-a",
    "v18f-clean48-tts-hn-fast + v16c",
    "checkpoint-faph10-v18d-clean96-pw96x4 + v16c",
    "checkpoint-faph10-v18d-clean96-pw96x4 + expert-a",
    "checkpoint-faph10-v18d-clean96-pw96x4 + v6-residual",
    "checkpoint-faph20-v18d-clean96-pw96x4 + v16c",
    "checkpoint-faph20-v18d-clean96-pw96x4 + expert-a",
    "checkpoint-faph20-v18d-clean96-pw96x4 + v6-residual",
    "checkpoint-faph20-v18d-clean96-pw96x4 + checkpoint-faph10-v18d-clean96-pw96x4",
]

# Default threshold for the main table view
DEFAULT_THR = 0.97

# Notes/descriptions for test sets (shown on hover)
SET_INFO = {
    "pos_isa_xtts":
        "48 'Kuule Kratt' XTTS-klooni isa hääl. "
        "Primary cross-version unseen-speaker recall benchmark. "
        "Held out from every model.",
    "pos_mattias_short":
        "135 'Kuule Kratt' Mac-mikrofonil salvestatud Mattias klippi "
        "(50 originaal + 85 laiendus 2026-04-14, noise floor −67 dBFS). "
        "Cross-device recall. Eelnev n=50 mõõtmine säilitatud pos_mattias_short_n50.",
    "pos_mattias_short_n50":
        "50 originaal Mattias klippi (2026-04-14 hommikune salvestus). "
        "Säilitatud provenance'i jaoks.",
    "pos_ode":
        "11 päris õe salvestust. Unseen speaker, ainult eval'iks.",
    "pos_friend1":
        "145 'Kuule Kratt' klippi sõbralt (friend1), 2026-04-14. "
        "16 kHz, 1.5s per klipp. Unseen speaker, ainult eval'iks. "
        "Laiendatud set — eelnev mõõtmine n=37 säilitatud test-setina pos_friend1_n37.",
    "pos_friend1_n37":
        "37 'Kuule Kratt' klippi sõbralt — esimene partii (2026-04-14 19:47). "
        "Säilitatud CSV'is provenance/võrdluse jaoks.",
    "hard_neg_mac_holdout":
        "15 päris hard-negative klippi Mac-mikrofonil "
        "('Kuule kraam', 'Kuule rott' jm confusables).",
    "hard_neg_isa_xtts":
        "60 XTTS-klooni hard-negative klippi isa hääl.",
    "hard_neg_canary":
        "5 päris v10 false-accept kanaariklippi — mined live testingust.",
    "faph_cv_et":
        "Common Voice eesti, 2000 klippi (indeksid 5000–7000, seed=42). "
        "3.65h raw / 3.82h streaming track with 300 ms gaps. Primary in-domain FAPH benchmark.",
    "faph_librispeech":
        "LibriSpeech test-clean, 2620 klippi, 5.62h. "
        "Standard cross-language FAPH (inglise kõne).",
    "faph_dipco":
        "DiPCo dinner-party corpus, 6 sessiooni, 3.32h. "
        "Far-field multi-speaker — openWakeWord-i primary.",
    "faph_macbook_bg":
        "Same-device MacBook ambient, 1.17h. Oma-seadme sanity.",
}

MAIN_COLS = [
    ("pos_isa_xtts", "recall", "Isa", 48),
    ("pos_mattias_short", "recall", "Mat", 135),
    ("pos_ode", "recall", "Õde", 11),
    ("pos_friend1", "recall", "Friend1", 145),
    ("hard_neg_mac_holdout", "fpr", "HN-Mac", 15),
    ("hard_neg_isa_xtts", "fpr", "HN-Isa", 60),
    ("hard_neg_canary", "fpr", "HN-Can", 5),
    ("faph_cv_et", "faph", "CV-ET", 2000),
    ("faph_librispeech", "faph", "LibSp", 2620),
    ("faph_dipco", "faph", "DiPCo", 6),
    ("faph_macbook_bg", "faph", "MacBG", 14),
]

# Fixed real-world Android field measurement from the long Session 4 deployment.
# Not threshold-swept in the benchmark CSV: it was measured at runtime threshold 0.90
# over a 98.97h Pixel 8a deployment (2026-04-14 .. 2026-04-19).
ANDROID_FIELD = {
    "label": "Android99h",
    "metric": "faph",
    "threshold": 0.90,
    "hours": 98.97,
    "models": {
        "v6-residual": 0.58,
        "ex3a": 2.71,
        "expert-a": 2.79,
        "v10": 3.08,
        "v16c": 4.06,
        "v6": 4.48,
        "v11": 10.49,
        "v14": 12.83,
    },
    "info": (
        "Android false-trigger logger field run, Session 4 on Pixel 8a. "
        "98.97h listening, runtime threshold 0.90. Fixed real-world FAPH column; "
        "not linked to the threshold selector because it was measured separately from the offline benchmark sweep."
    ),
}


def load_rows(path: Path) -> list[dict]:
    with open(path) as f:
        return list(csv.DictReader(f))


def sort_models(models: list[str]) -> list[str]:
    known = [m for m in MODEL_ORDER if m in models]
    extra = sorted(set(models) - set(known))
    return known + extra


def build_data(rows: list[dict]) -> dict:
    by_model: dict[str, dict] = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        m = r["model"]
        s = r.get("test_set") or r.get("set")
        if not s:
            continue
        t = float(r["threshold"])
        metric = r["metric"]
        value = float(r["value"])
        by_model[m][s][f"{metric}@{t:.3f}"] = value
        by_model[m][s]["_n"] = int(r["n"])
        hours_raw = r.get("duration_h", r.get("hours", ""))
        by_model[m][s]["_hours"] = float(hours_raw) if hours_raw else None
        by_model[m][s]["_kind"] = r["kind"]
    return dict(by_model)


HTML = r"""<!DOCTYPE html>
<html lang="et">
<head>
<meta charset="utf-8">
<title>Kuule Kratt — mudelite benchmark</title>
<style>
:root {
  --bg: #fafaf7;
  --panel: #ffffff;
  --ink: #181818;
  --muted: #6b6b6b;
  --line: #e6e3dd;
  --accent: #b5451a;
  --good: #a9d4a9;
  --okay: #f2e8b8;
  --bad: #e8b5b5;
  --moe: #c4e0ea;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: var(--bg); color: var(--ink); }
body {
  font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  max-width: 1380px; margin: 0 auto; padding: 2rem 2.5rem 4rem;
  font-feature-settings: "tnum" 1, "cv11" 1;
}
h1 { font-weight: 600; font-size: 1.6rem; letter-spacing: -0.01em; }
h2 { font-weight: 500; font-size: 1.15rem; margin: 2rem 0 0.5rem; }
h3 { font-weight: 500; font-size: 1rem; margin: 1rem 0 0.5rem; color: var(--muted); }
.sub { color: var(--muted); font-size: 0.88rem; margin: 0.3rem 0 2rem; }
.section {
  background: var(--panel); border: 1px solid var(--line); border-radius: 6px;
  padding: 1.5rem; margin: 1.5rem 0;
}
.controls { display: flex; gap: 1rem; flex-wrap: wrap; align-items: center; margin-bottom: 1rem; font-size: 13px; color: var(--muted); }
.controls select, .controls input[type=checkbox] { cursor: pointer; }
.controls label { cursor: pointer; }

table { border-collapse: collapse; width: 100%; font-size: 12.5px; font-variant-numeric: tabular-nums; }
th, td { padding: 0.38rem 0.55rem; text-align: right; border-bottom: 1px solid var(--line); white-space: nowrap; }
th {
  font-weight: 500; text-align: right; background: #f0ede7; color: #333;
  cursor: pointer; user-select: none; position: sticky; top: 0; font-size: 11.5px;
  text-transform: uppercase; letter-spacing: 0.03em;
}
th.sortable:hover { background: #e7e3da; }
th.sorted { background: #e2ddd0; }
.sort-badge {
  display: inline-flex; align-items: center; gap: 0.15rem;
  margin-left: 0.28rem; padding: 0.02rem 0.28rem; border-radius: 999px;
  background: #fff9ee; border: 1px solid #d8c7a6; color: var(--accent);
  font-size: 10px; font-weight: 600; text-transform: none; letter-spacing: 0;
  vertical-align: middle;
}
.sort-badge .ord { color: #7b6b53; }
.sort-badge.desc { background: #f7e8df; border-color: #d6ac98; }
th.model, td.model { text-align: left; font-weight: 500; padding-left: 0.25rem; }
tbody tr:hover td { background: #f4f2ec; }
tbody tr.moe td { background: #f3f8fc; }
tbody tr.moe:hover td { background: #e3f0f7; }
td.cell { position: relative; cursor: help; }
td.cell:hover .tip { display: block; }
.tip {
  display: none; position: absolute; top: 100%; right: 0;
  background: #222; color: #fff; padding: 0.55rem 0.7rem; border-radius: 4px;
  font-size: 11px; font-weight: 400; z-index: 20; white-space: nowrap;
  margin-top: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  line-height: 1.4; max-width: 360px; white-space: normal; text-align: left;
}
.tip .hint { color: #bbb; font-size: 10px; margin-top: 0.25rem; }

/* heat classes */
.good { background: #e2f1dd; }
.okay { background: #faf3d4; }
.bad { background: #f6dcd8; }
.excellent { background: #c8e9c0; }
.highlight-row td { box-shadow: inset 3px 0 0 var(--accent); }

.legend {
  display: flex; gap: 1rem; font-size: 11.5px; color: var(--muted);
  margin-top: 0.75rem; flex-wrap: wrap;
}
.legend-item { display: flex; align-items: center; gap: 0.3rem; }
.sw { display: inline-block; width: 14px; height: 14px; border-radius: 2px; border: 1px solid rgba(0,0,0,0.1); }
.sw.good { background: #c8e9c0; }
.sw.okay { background: #faf3d4; }
.sw.bad { background: #f6dcd8; }
.sw.moe { background: #f3f8fc; }

/* chart */
svg.chart { width: 100%; height: auto; display: block; }
svg text { font-family: -apple-system, BlinkMacSystemFont, sans-serif; fill: var(--ink); }
.axis line, .axis path { stroke: #bbb; fill: none; }
.axis text { fill: var(--muted); font-size: 10px; }
.gridline { stroke: #eee; }
.curve { fill: none; stroke-width: 1.8; opacity: 0.85; cursor: pointer; }
.curve:hover { stroke-width: 3; opacity: 1; }
.curve.fade { opacity: 0.12; }
.dot { cursor: pointer; }
.target { stroke: #b5451a; stroke-dasharray: 3,3; stroke-width: 1; fill: none; }
.target-label { fill: #b5451a; font-size: 10px; font-weight: 500; }

.chart-legend { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.3rem 1.5rem; font-size: 12px; margin-top: 0.75rem; }
.chart-legend-item { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; padding: 2px 4px; border-radius: 3px; }
.chart-legend-item:hover { background: #f0ede7; }
.chart-legend-item.muted { opacity: 0.3; }
.chart-legend-item .bar { width: 18px; height: 3px; border-radius: 2px; }
.chart-legend-item .name { font-weight: 500; }
.chart-legend-item .pt { color: var(--muted); font-size: 11px; }

.kpi { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin: 1rem 0; }
.kpi .card {
  padding: 1rem; border: 1px solid var(--line); border-radius: 5px; background: #fdfcf9;
}
.kpi .card .v { font-size: 1.5rem; font-weight: 500; color: var(--accent); }
.kpi .card .k { font-size: 0.78rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.2rem; }
.kpi .card .ctx { font-size: 0.75rem; color: var(--muted); margin-top: 0.2rem; }

code { font: 12px/1.4 "SF Mono", Monaco, Consolas, monospace; background: #f0ede7; padding: 1px 4px; border-radius: 2px; }
.proto { font-size: 12px; color: var(--muted); background: #faf8f3; padding: 0.75rem 1rem; border-left: 3px solid var(--accent); border-radius: 0 3px 3px 0; }
footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--line); color: var(--muted); font-size: 11px; text-align: right; }

/* threshold sweep details */
.sweep-rows { display: none; }
.sweep-rows.open { display: table-row-group; }
.sweep-row td { font-size: 11.5px; background: #fbf9f5 !important; color: #555; }
.sweep-row td.model { padding-left: 1.5rem; font-weight: 400; font-style: italic; }
.expand { cursor: pointer; color: var(--accent); user-select: none; margin-right: 3px; }
</style>
</head>
<body>

<h1>Kuule Kratt — mudelite benchmark</h1>
<div class="sub">
  Generated from <code>__SOURCE__</code> at <code>__TIMESTAMP__</code>.
  __MODEL_COUNT__ mudelit × __SET_COUNT__ test-seti × threshold-sweep = __ROWS__ mõõdet.
</div>

<div class="section">
  <h2>Protokoll</h2>
  <div class="proto">
    Canonical streaming FAPH: <code>microwakeword.test.compute_false_accepts_per_hour</code>
    — 50 ms moving average (5 slaidi @ 10 ms samm), 250 ms refractory cooldown,
    single concatenated track per FAPH set. Iga test-set on registreeritud
    <code>evaluation/test_sets.py</code>'is ja disjoint-kontroll jookseb enne eval'i.
  </div>
</div>

<div class="section">
  <h2>Peamised tulemused @ threshold = __DEFAULT_THR__</h2>
  <div class="controls">
    <label>Threshold:
      <select id="thr-select"></select>
    </label>
    <label><input type="checkbox" id="show-moe" checked> Näita MoE-konsensusi</label>
    <label><input type="checkbox" id="color-heat" checked> Värvikodeering</label>
    <span style="margin-left: auto; color: var(--muted);">Kliki veerul → min → max → väljas. Mitu veergu = mitmeastmeline sort.</span>
  </div>
  <div style="overflow-x: auto;">
    <table id="main-table">
      <thead id="main-thead"></thead>
      <tbody id="main-tbody"></tbody>
    </table>
  </div>
  <div class="legend">
    <div class="legend-item"><span class="sw good"></span>hea</div>
    <div class="legend-item"><span class="sw okay"></span>keskmine</div>
    <div class="legend-item"><span class="sw bad"></span>halb</div>
    <div class="legend-item"><span class="sw moe"></span>MoE-konsensus (mitme mudeli AND)</div>
    <div class="legend-item" style="margin-left: auto;"><em>recall = suurem parem; FPR / FAPH = väiksem parem</em></div>
  </div>
</div>

<div class="section">
  <h2>DET-kõver — Isa recall vs. CV-ET FAPH</h2>
  <div class="sub">
    X-telg: FAPH eestikeelsel Common Voice setil (log). Y-telg: miss-rate
    (1 − recall) Isa XTTS positive setil. Alumine vasak nurk = parim.
    Hover mudelit → tõsta esile.
  </div>
  <svg class="chart" id="det-chart" viewBox="0 0 780 460" preserveAspectRatio="xMidYMid meet"></svg>
  <div class="chart-legend" id="det-legend"></div>
</div>

<div class="section">
  <h2>Tööstusstandarditega võrdlus (CV-ET @ 0.97)</h2>
  <div class="kpi" id="kpi-cards"></div>
  <div class="sub" style="margin-top: 0.5rem;">
    Viitetasemed: Apple Siri production ~0.006/h · openWakeWord target &lt;0.5/h ·
    Picovoice target &lt;0.5/h · Hey Jarvis DiPCo 0.187/h.
  </div>
</div>

<footer>
  Kratt wake-word thesis · TalTech BSc · 2026 · Mattias
</footer>

<script>
const DATA = __DATA__;
const META = __META__;
const MAIN_COLS = __MAIN_COLS__;
const ANDROID_FIELD = __ANDROID_FIELD__;
const THRESHOLDS = __THRESHOLDS__;
const SET_INFO = __SET_INFO__;
const MODEL_ORDER = __MODEL_ORDER__;
const MOE_SET = new Set(MODEL_ORDER.filter(m => m.includes('+')));

const state = {
  threshold: __DEFAULT_THR__,
  showMoe: true,
  heat: true,
  sorts: [],
  hiddenCurves: new Set(),
};

// ── Table ──
function bandClass(metric, value) {
  if (!state.heat || value == null) return '';
  if (metric === 'recall') {
    if (value >= 0.95) return 'excellent';
    if (value >= 0.80) return 'good';
    if (value >= 0.60) return 'okay';
    return 'bad';
  }
  if (metric === 'fpr') {
    if (value <= 0.20) return 'excellent';
    if (value <= 0.50) return 'good';
    if (value <= 0.80) return 'okay';
    return 'bad';
  }
  if (metric === 'faph') {
    if (value <= 1.0) return 'excellent';
    if (value <= 5.0) return 'good';
    if (value <= 50.0) return 'okay';
    return 'bad';
  }
  return '';
}

function fmt(metric, v) {
  if (v == null) return '—';
  if (metric === 'recall' || metric === 'fpr') return (v * 100).toFixed(0) + '%';
  if (v >= 100) return v.toFixed(0);
  if (v >= 10) return v.toFixed(1);
  return v.toFixed(2);
}

function getValue(model, testSet, metric, threshold) {
  const entry = (DATA[model] || {})[testSet];
  if (!entry) return null;
  return entry[metric + '@' + threshold.toFixed(3)];
}

function getAndroidFieldValue(model) {
  return ANDROID_FIELD.models[model] ?? null;
}

function modelRank(model) {
  const idx = MODEL_ORDER.indexOf(model);
  return idx >= 0 ? idx : Number.MAX_SAFE_INTEGER;
}

function compareModelOrder(a, b, dir = 'asc') {
  const factor = dir === 'asc' ? 1 : -1;
  const ar = modelRank(a);
  const br = modelRank(b);
  if (ar !== br) return (ar - br) * factor;
  return a.localeCompare(b) * factor;
}

function compareNullableNumber(va, vb, dir) {
  if (va == null && vb == null) return 0;
  if (va == null) return 1;
  if (vb == null) return -1;
  const factor = dir === 'asc' ? 1 : -1;
  return (va - vb) * factor;
}

function compareBySort(a, b, sort) {
  if (sort.col === 'model') return compareModelOrder(a, b, sort.dir);
  const col = MAIN_COLS.find(c => c[2] === sort.col);
  if (col) {
    const [set, metric] = col;
    return compareNullableNumber(
      getValue(a, set, metric, state.threshold),
      getValue(b, set, metric, state.threshold),
      sort.dir
    );
  }
  if (sort.col === ANDROID_FIELD.label) {
    return compareNullableNumber(getAndroidFieldValue(a), getAndroidFieldValue(b), sort.dir);
  }
  return 0;
}

function sortBadge(col) {
  const idx = state.sorts.findIndex(s => s.col === col);
  if (idx < 0) return '';
  const dir = state.sorts[idx].dir;
  const label = dir === 'asc' ? 'min' : 'max';
  return `<span class="sort-badge ${dir}"><span class="ord">${idx + 1}</span>${label}</span>`;
}

function renderTable() {
  const thead = document.getElementById('main-thead');
  const tbody = document.getElementById('main-tbody');

  const headCells = [`<th class="model sortable" data-col="model">Mudel${sortBadge('model')}</th>`];
  for (const [set, metric, label, n] of MAIN_COLS) {
    const info = SET_INFO[set] || '';
    headCells.push(
      `<th class="sortable" data-col="${label}" title="${info.replace(/"/g, '&quot;')}">${label}${sortBadge(label)}<br><small style="color:#888;font-weight:400;text-transform:none;letter-spacing:0">n=${n}</small></th>`
    );
  }
  headCells.push(
    `<th class="sortable" data-col="${ANDROID_FIELD.label}" title="${ANDROID_FIELD.info.replace(/"/g, '&quot;')}">${ANDROID_FIELD.label}${sortBadge(ANDROID_FIELD.label)}<br><small style="color:#888;font-weight:400;text-transform:none;letter-spacing:0">${ANDROID_FIELD.hours.toFixed(2)}h @ ${ANDROID_FIELD.threshold.toFixed(2)}</small></th>`
  );
  thead.innerHTML = '<tr>' + headCells.join('') + '</tr>';

  // Sort
  let models = Object.keys(DATA);
  if (!state.showMoe) models = models.filter(m => !MOE_SET.has(m));

  models.sort((a, b) => {
    for (const sort of state.sorts) {
      const cmp = compareBySort(a, b, sort);
      if (cmp !== 0) return cmp;
    }
    return compareModelOrder(a, b);
  });

  const rows = models.map(m => {
    const isMoe = MOE_SET.has(m);
    const cells = [`<td class="model">${m}</td>`];
    for (const [set, metric, label, n] of MAIN_COLS) {
      const v = getValue(m, set, metric, state.threshold);
      const band = bandClass(metric, v);
      const entry = (DATA[m] || {})[set] || {};
      const hours = entry._hours;
      const hint = SET_INFO[set] || '';
      const suffix = metric === 'faph' && hours ? ` · ${hours.toFixed(2)}h audio` : '';
      const tipHtml = `<div class="tip"><strong>${label}</strong> (${set})<br>` +
        `${hint}${suffix}<br><span class="hint">väärtus: ${fmt(metric, v)} · metric: ${metric} · thr: ${state.threshold}</span></div>`;
      cells.push(`<td class="cell ${band}">${fmt(metric, v)}${tipHtml}</td>`);
    }
    const androidV = getAndroidFieldValue(m);
    const androidBand = bandClass(ANDROID_FIELD.metric, androidV);
    const androidTip = `<div class="tip"><strong>${ANDROID_FIELD.label}</strong><br>${ANDROID_FIELD.info}<br>` +
      `<span class="hint">väärtus: ${fmt(ANDROID_FIELD.metric, androidV)} · metric: ${ANDROID_FIELD.metric} · thr: fixed ${ANDROID_FIELD.threshold.toFixed(2)}</span></div>`;
    cells.push(`<td class="cell ${androidBand}">${fmt(ANDROID_FIELD.metric, androidV)}${androidTip}</td>`);
    return `<tr class="${isMoe ? 'moe' : ''}">${cells.join('')}</tr>`;
  });
  tbody.innerHTML = rows.join('');

  // Mark sorted columns
  thead.querySelectorAll('th').forEach(th => {
    th.classList.remove('sorted', 'asc', 'desc');
    const sort = state.sorts.find(s => s.col === th.dataset.col);
    if (sort) {
      th.classList.add('sorted', sort.dir);
    }
  });
}

function toggleSort(col) {
  const idx = state.sorts.findIndex(s => s.col === col);
  if (idx < 0) {
    state.sorts.push({ col, dir: 'asc' });
  } else if (state.sorts[idx].dir === 'asc') {
    state.sorts[idx].dir = 'desc';
  } else {
    state.sorts.splice(idx, 1);
  }
}

document.addEventListener('click', (e) => {
  const th = e.target.closest('th.sortable');
  if (th) {
    toggleSort(th.dataset.col);
    renderTable();
  }
});

// ── Controls ──
const thrSelect = document.getElementById('thr-select');
THRESHOLDS.forEach(t => {
  const opt = document.createElement('option');
  opt.value = t;
  opt.textContent = t.toFixed(3);
  if (Math.abs(t - state.threshold) < 1e-6) opt.selected = true;
  thrSelect.appendChild(opt);
});
thrSelect.addEventListener('change', () => {
  state.threshold = parseFloat(thrSelect.value);
  renderTable();
  renderKpi();
});
document.getElementById('show-moe').addEventListener('change', (e) => {
  state.showMoe = e.target.checked;
  renderTable();
});
document.getElementById('color-heat').addEventListener('change', (e) => {
  state.heat = e.target.checked;
  renderTable();
});

// ── DET chart ──
const DET_MODELS = [
  'v6-residual', 'v11', 'v16a', 'v16b', 'oww-v17-smoke2',
  'ex3a', 'expert-a',
  'v6-residual + expert-a', 'ex3a + expert-a',
  'ex3a + expert-a + expert-b2', 'ex3a + expert-a + expert-b',
];
const COLORS = {
  'v6-residual': '#888',
  'v11': '#d4a64a',
  'v16a': '#3f7fbf',
  'v16b': '#2c5aa0',
  'oww-v17-smoke2': '#111111',
  'ex3a': '#5fa84b',
  'expert-a': '#b5451a',
  'v6-residual + expert-a': '#7a4ea0',
  'ex3a + expert-a': '#b14a99',
  'ex3a + expert-a + expert-b2': '#a62d1f',
  'ex3a + expert-a + expert-b': '#d4683a',
};

function renderDET() {
  const svg = document.getElementById('det-chart');
  const W = 780, H = 460, ML = 60, MR = 20, MT = 20, MB = 50;
  const plotW = W - ML - MR, plotH = H - MT - MB;

  // axes: x = log10(FAPH) from 0.05 to 2000; y = miss rate 0..1
  const xMin = -1.3, xMax = 3.3; // log10
  const yMin = 0, yMax = 1;
  const xScale = v => ML + (Math.log10(Math.max(v, 0.05)) - xMin) / (xMax - xMin) * plotW;
  const yScale = v => MT + (v - yMin) / (yMax - yMin) * plotH;

  let s = '';

  // gridlines and axes
  const xTicks = [0.1, 0.5, 1, 5, 10, 50, 100, 500, 1000];
  const yTicks = [0, 0.1, 0.25, 0.5, 0.75, 1];

  for (const t of xTicks) {
    const x = xScale(t);
    s += `<line class="gridline" x1="${x}" x2="${x}" y1="${MT}" y2="${MT + plotH}" />`;
    s += `<text x="${x}" y="${MT + plotH + 16}" text-anchor="middle" class="axis-label">${t}</text>`;
  }
  for (const t of yTicks) {
    const y = yScale(t);
    s += `<line class="gridline" x1="${ML}" x2="${ML + plotW}" y1="${y}" y2="${y}" />`;
    s += `<text x="${ML - 6}" y="${y + 3}" text-anchor="end" class="axis-label">${(t*100).toFixed(0)}%</text>`;
  }

  // axis frame
  s += `<g class="axis"><line x1="${ML}" x2="${ML + plotW}" y1="${MT + plotH}" y2="${MT + plotH}" />`;
  s += `<line x1="${ML}" x2="${ML}" y1="${MT}" y2="${MT + plotH}" /></g>`;
  s += `<text x="${ML + plotW/2}" y="${H - 10}" text-anchor="middle" class="axis-label">FAPH — CV-ET ambient (events / hour, log skaala)</text>`;
  s += `<text transform="translate(14, ${MT + plotH/2}) rotate(-90)" text-anchor="middle" class="axis-label">Miss rate = 1 − recall (Isa XTTS)</text>`;

  // target lines
  s += `<line class="target" x1="${xScale(0.5)}" x2="${xScale(0.5)}" y1="${MT}" y2="${MT+plotH}" />`;
  s += `<text class="target-label" x="${xScale(0.5)+4}" y="${MT+12}">oWW/Picovoice target</text>`;

  // curves
  for (const m of DET_MODELS) {
    if (state.hiddenCurves.has(m)) continue;
    const entry = DATA[m];
    if (!entry) continue;
    const pts = [];
    for (const t of THRESHOLDS) {
      const faph = (entry['faph_cv_et'] || {})['faph@' + t.toFixed(3)];
      const rec = (entry['pos_isa_xtts'] || {})['recall@' + t.toFixed(3)];
      if (faph == null || rec == null) continue;
      pts.push({ t, faph, miss: 1 - rec });
    }
    if (pts.length < 2) continue;
    const path = pts.map((p, i) =>
      (i === 0 ? 'M' : 'L') + xScale(p.faph).toFixed(1) + ',' + yScale(p.miss).toFixed(1)
    ).join(' ');
    const color = COLORS[m] || '#555';
    s += `<path class="curve" d="${path}" stroke="${color}" data-model="${m}" />`;
    for (const p of pts) {
      s += `<circle class="dot" cx="${xScale(p.faph).toFixed(1)}" cy="${yScale(p.miss).toFixed(1)}" r="3" fill="${color}" data-model="${m}" data-info="thr=${p.t}, FAPH=${p.faph.toFixed(2)}, recall=${((1-p.miss)*100).toFixed(0)}%"><title>${m}: thr=${p.t}, FAPH=${p.faph.toFixed(2)}/h, miss=${(p.miss*100).toFixed(0)}%</title></circle>`;
    }
  }
  svg.innerHTML = s;
}

function renderLegend() {
  const el = document.getElementById('det-legend');
  el.innerHTML = DET_MODELS.map(m => {
    const entry = DATA[m] || {};
    const faph = (entry['faph_cv_et'] || {})['faph@0.970'];
    const rec = (entry['pos_isa_xtts'] || {})['recall@0.970'];
    const pt = faph != null && rec != null
      ? `FAPH ${faph.toFixed(faph < 10 ? 2 : 1)} / Isa ${(rec*100).toFixed(0)}%`
      : '—';
    const muted = state.hiddenCurves.has(m) ? 'muted' : '';
    return `<div class="chart-legend-item ${muted}" data-model="${m}">
      <span class="bar" style="background:${COLORS[m] || '#555'}"></span>
      <span class="name">${m}</span>
      <span class="pt">${pt}</span>
    </div>`;
  }).join('');

  el.querySelectorAll('.chart-legend-item').forEach(item => {
    item.addEventListener('click', () => {
      const m = item.dataset.model;
      if (state.hiddenCurves.has(m)) state.hiddenCurves.delete(m);
      else state.hiddenCurves.add(m);
      renderDET();
      renderLegend();
    });
  });
}

// ── KPI cards ──
function renderKpi() {
  const el = document.getElementById('kpi-cards');
  const picks = [
    { label: 'Parim üksikmudel (DiPCo)', pick: () => {
        let best = null, bestV = Infinity, bestRec = 0;
        for (const m of Object.keys(DATA)) {
          if (MOE_SET.has(m)) continue;
          const v = (DATA[m].faph_dipco || {})['faph@0.970'];
          const r = (DATA[m].pos_isa_xtts || {})['recall@0.970'];
          if (v != null && r >= 0.95 && v < bestV) { best = m; bestV = v; bestRec = r; }
        }
        return { model: best, value: bestV.toFixed(2) + ' /h', ctx: `DiPCo FAPH · ${(bestRec*100).toFixed(0)}% Isa recall` };
    }},
    { label: 'Parim üksikmudel (CV-ET)', pick: () => {
        let best = null, bestV = Infinity, bestRec = 0;
        for (const m of Object.keys(DATA)) {
          if (MOE_SET.has(m)) continue;
          const v = (DATA[m].faph_cv_et || {})['faph@0.970'];
          const r = (DATA[m].pos_isa_xtts || {})['recall@0.970'];
          if (v != null && r >= 0.95 && v < bestV) { best = m; bestV = v; bestRec = r; }
        }
        return { model: best, value: bestV.toFixed(1) + ' /h', ctx: `CV-ET FAPH · ${(bestRec*100).toFixed(0)}% Isa recall` };
    }},
    { label: 'Parim MoE (balanss)', pick: () => {
        const cand = 'ex3a + expert-a';
        const v = (DATA[cand].faph_cv_et || {})['faph@0.970'];
        const r = (DATA[cand].pos_isa_xtts || {})['recall@0.970'];
        return { model: cand, value: v.toFixed(2) + ' /h', ctx: `CV-ET · ${(r*100).toFixed(0)}% Isa recall` };
    }},
    { label: 'Parim MoE (FAPH)', pick: () => {
        const cand = 'ex3a + expert-a + expert-b2';
        const v = (DATA[cand].faph_cv_et || {})['faph@0.970'];
        const r = (DATA[cand].pos_isa_xtts || {})['recall@0.970'];
        return { model: cand, value: v.toFixed(2) + ' /h', ctx: `CV-ET · ${(r*100).toFixed(0)}% Isa recall (LOW)` };
    }},
    { label: "Deploy'tud (v11)", pick: () => {
        const v = (DATA.v11.faph_cv_et || {})['faph@0.970'];
        const r = (DATA.v11.pos_isa_xtts || {})['recall@0.970'];
        return { model: 'v11', value: v.toFixed(0) + ' /h', ctx: `CV-ET · ${(r*100).toFixed(0)}% Isa recall` };
    }},
  ];
  el.innerHTML = picks.map(p => {
    const r = p.pick();
    return `<div class="card">
      <div class="k">${p.label}</div>
      <div class="v">${r.value}</div>
      <div class="ctx"><strong>${r.model}</strong> — ${r.ctx}</div>
    </div>`;
  }).join('');
}

renderTable();
renderDET();
renderLegend();
renderKpi();
</script>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", required=True, help="benchmark_results_*.csv")
    ap.add_argument("--output", "-o", default=None, help="HTML output path")
    args = ap.parse_args()

    inp = Path(args.input)
    rows = load_rows(inp)
    thresholds = sorted({float(r["threshold"]) for r in rows})
    data = build_data(rows)
    timestamps = [r.get("timestamp", "") for r in rows if r.get("timestamp")]
    latest_ts = max(timestamps) if timestamps else ""
    meta = {
        "source": inp.name,
        "timestamp": latest_ts,
        "rows": len(rows),
    }

    html = (
        HTML
        .replace("__DATA__", json.dumps(data, separators=(",", ":")))
        .replace("__META__", json.dumps(meta))
        .replace("__MAIN_COLS__", json.dumps(MAIN_COLS))
        .replace("__ANDROID_FIELD__", json.dumps(ANDROID_FIELD, ensure_ascii=False, separators=(",", ":")))
        .replace("__THRESHOLDS__", json.dumps(thresholds))
        .replace("__SET_INFO__", json.dumps(SET_INFO, ensure_ascii=False))
        .replace("__MODEL_ORDER__", json.dumps(MODEL_ORDER))
        .replace("__DEFAULT_THR__", f"{DEFAULT_THR}")
        .replace("__SOURCE__", inp.name)
        .replace("__TIMESTAMP__", latest_ts)
        .replace("__ROWS__", str(len(rows)))
        .replace("__MODEL_COUNT__", str(len(data)))
        .replace("__SET_COUNT__", str(len({r.get("test_set") or r.get("set") for r in rows})))
    )

    out = Path(args.output) if args.output else inp.parent / "supervisor_report.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}  ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
