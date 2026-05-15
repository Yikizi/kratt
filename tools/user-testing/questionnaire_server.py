#!/usr/bin/env python3
"""Local Kratt pilot-questionnaire web form.

Runs a tiny localhost HTTP server, serves a single self-contained HTML form, and
stores submitted responses as JSONL/JSON/CSV under output/user-tests/questionnaires.
No external network or JavaScript dependencies are used.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import threading
import uuid
import webbrowser
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "user-tests" / "questionnaires"

REQUIRED_FIELDS = {
    "participant_id",
    "date",
    "consent_level",
    "language_level",
    "voice_assistant_usage",
    "smart_home_usage",
    "umux_capabilities",
    "umux_ease",
    "seq_ease",
    "reliability",
    "speed",
    "natural_phrasing",
    "home_use",
}

CSV_COLUMNS = [
    "submitted_at",
    "response_id",
    "participant_id",
    "date",
    "session_id",
    "consent_level",
    "language_level",
    "language_level_other",
    "voice_assistant_usage",
    "smart_home_usage",
    "umux_capabilities",
    "umux_ease",
    "umux_lite_normalized",
    "seq_ease",
    "reliability",
    "speed",
    "natural_phrasing",
    "home_use",
    "open_comment",
]

STORE_LOCK = threading.Lock()


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return cleaned[:60] or "participant"


def _int_field(data: dict[str, Any], key: str, lo: int, hi: int) -> int:
    try:
        value = int(data.get(key))
    except (TypeError, ValueError):
        raise ValueError(f"{key} must be an integer")
    if value < lo or value > hi:
        raise ValueError(f"{key} must be between {lo} and {hi}")
    return value


def normalize_submission(raw: dict[str, Any]) -> dict[str, Any]:
    data = {str(k): (str(v).strip() if v is not None else "") for k, v in raw.items()}
    missing = sorted(key for key in REQUIRED_FIELDS if not data.get(key))
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))

    for key in ("umux_capabilities", "umux_ease", "seq_ease"):
        data[key] = _int_field(data, key, 1, 7)
    for key in ("reliability", "speed", "natural_phrasing", "home_use"):
        data[key] = _int_field(data, key, 1, 5)

    mean_umux = (data["umux_capabilities"] + data["umux_ease"]) / 2
    data["umux_lite_normalized"] = round(((mean_umux - 1) / 6) * 100, 2)
    data["participant_id"] = data["participant_id"][:80]
    data["session_id"] = data.get("session_id", "")[:120]
    data["language_level_other"] = data.get("language_level_other", "")[:80]
    data["open_comment"] = data.get("open_comment", "")[:4000]
    data["submitted_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    data["response_id"] = uuid.uuid4().hex[:12]
    return data


def store_submission(output_dir: Path, raw: dict[str, Any]) -> dict[str, Any]:
    record = normalize_submission(raw)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_dir = output_dir / "responses"
    json_dir.mkdir(parents=True, exist_ok=True)

    participant = _safe_name(str(record["participant_id"]))
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = json_dir / f"{stamp}_{participant}_{record['response_id']}.json"
    jsonl_path = output_dir / "responses.jsonl"
    csv_path = output_dir / "responses.csv"

    with STORE_LOCK:
        json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        with jsonl_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        write_header = not csv_path.exists() or csv_path.stat().st_size == 0
        with csv_path.open("a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            if write_header:
                writer.writeheader()
            writer.writerow({key: record.get(key, "") for key in CSV_COLUMNS})

    return {"ok": True, "response_id": record["response_id"], "json_path": str(json_path)}


def page_html(
    *,
    participant_id: str = "",
    session_id: str = "",
    consent_level: str = "",
    today: str | None = None,
) -> str:
    if today is None:
        today = datetime.now().strftime("%Y-%m-%d")
    return (
        _PAGE_TEMPLATE
        .replace("__PARTICIPANT__", json.dumps(participant_id))
        .replace("__SESSION__", json.dumps(session_id))
        .replace("__CONSENT__", json.dumps(consent_level))
        .replace("__DATE__", json.dumps(today))
    )


_PAGE_TEMPLATE = r"""<!doctype html>
<html lang="et">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Kratt · kasutajatesti küsimustik</title>
  <style>
    :root {
      --bg: oklch(0.985 0.005 75);
      --paper: oklch(1 0.002 75);
      --ink: oklch(0.20 0.012 50);
      --ink-soft: oklch(0.38 0.014 50);
      --muted: oklch(0.55 0.012 50);
      --rule: oklch(0.90 0.006 60);
      --rule-strong: oklch(0.78 0.008 60);
      --accent: oklch(0.44 0.13 25);
      --accent-deep: oklch(0.34 0.13 25);
      --accent-tint: oklch(0.96 0.020 30);
      --ok: oklch(0.42 0.10 150);
      --bad: oklch(0.48 0.18 25);
      --serif: "Charter", "Iowan Old Style", "Source Serif Pro", "Cambria", Georgia, serif;
      --sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
      --mono: "JetBrains Mono", "SF Mono", ui-monospace, "Menlo", monospace;
      --ease: cubic-bezier(0.22, 1, 0.36, 1);
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; }
    body {
      min-height: 100vh; color: var(--ink); background: var(--bg);
      font-family: var(--sans); font-size: 16px; line-height: 1.5;
      -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
      overflow-x: hidden;
    }

    .app {
      min-height: 100vh; display: grid;
      grid-template-rows: auto 1fr auto;
    }

    /* ── Top bar ───────────────────────────────────────────── */
    .topbar {
      position: sticky; top: 0; z-index: 10; background: var(--bg);
    }
    .progress {
      height: 2px; background: transparent; overflow: hidden;
    }
    .progress .bar {
      height: 100%; width: 100%; background: var(--accent);
      transform: scaleX(0); transform-origin: left center;
      transition: transform 380ms var(--ease); will-change: transform;
    }
    .topbar-row {
      display: flex; justify-content: space-between; align-items: center;
      padding: 14px 28px 12px;
      font-family: var(--mono); font-size: 11px; letter-spacing: 0.18em;
      color: var(--muted); text-transform: uppercase;
    }
    .topbar-row .brand { display: inline-flex; gap: 10px; align-items: center; }
    .topbar-row .brand .dot { width: 6px; height: 6px; background: var(--accent); border-radius: 50%; }
    .counter .of { color: oklch(0.72 0.010 60); margin: 0 4px; }
    @media (max-width: 600px) { .topbar-row { padding: 12px 18px 10px; } }

    /* ── Stage (centered) ──────────────────────────────────── */
    .stage {
      display: grid; place-items: center; padding: 20px 28px 60px;
      position: relative;
    }
    .step {
      width: 100%; max-width: 600px;
      opacity: 0; transform: translateY(14px);
      transition: opacity 280ms var(--ease), transform 280ms var(--ease);
    }
    .step.in { opacity: 1; transform: translateY(0); }
    .step.out-up { opacity: 0; transform: translateY(-14px); }
    .step.out-down { opacity: 0; transform: translateY(14px); }

    .step.shake { animation: shake 320ms var(--ease); }
    @keyframes shake {
      0%, 100% { transform: translateX(0); }
      20% { transform: translateX(-6px); }
      40% { transform: translateX(6px); }
      60% { transform: translateX(-4px); }
      80% { transform: translateX(4px); }
    }

    .step .num {
      font-family: var(--mono); font-size: 12px; letter-spacing: 0.18em;
      color: var(--muted); text-transform: uppercase; margin-bottom: 18px;
      display: flex; align-items: center; gap: 10px;
    }
    .step .num .arrow { color: var(--accent); }
    .step .q {
      font-family: var(--serif); font-weight: 400; font-size: clamp(26px, 3.4vw, 34px);
      line-height: 1.22; letter-spacing: -0.01em; color: var(--ink);
      margin: 0 0 14px; max-width: 28ch;
    }
    .step .hint {
      font-family: var(--serif); font-style: italic; font-size: 16px;
      color: var(--muted); margin: 0 0 32px; max-width: 48ch;
    }
    .step .err {
      font-family: var(--sans); font-size: 13px; color: var(--bad);
      margin-top: 12px; min-height: 18px; font-weight: 500;
    }

    /* Text & date inputs */
    .text-input, .date-input {
      width: 100%; font-family: var(--serif); font-size: 24px; color: var(--ink);
      background: transparent; border: 0;
      border-bottom: 2px solid var(--rule-strong);
      padding: 8px 2px 12px; outline: none;
      transition: border-color 180ms var(--ease);
    }
    .text-input::placeholder { color: oklch(0.74 0.010 60); }
    .text-input:focus, .date-input:focus { border-bottom-color: var(--accent); }
    .date-input { color-scheme: light; font-family: var(--serif); }

    /* Textarea */
    .textarea-input {
      width: 100%; font-family: var(--serif); font-size: 18px; line-height: 1.55;
      color: var(--ink); background: var(--paper);
      border: 1px solid var(--rule-strong); border-radius: 2px;
      padding: 14px 16px; min-height: 140px; resize: vertical; outline: none;
      transition: border-color 180ms var(--ease), box-shadow 180ms var(--ease);
    }
    .textarea-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-tint); }

    /* Choice list */
    .options { list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; }
    .option {
      width: 100%; display: grid; grid-template-columns: 28px 1fr; align-items: center;
      gap: 14px; padding: 13px 16px;
      font-family: var(--serif); font-size: 17px; color: var(--ink);
      background: var(--paper); border: 1px solid var(--rule-strong);
      border-radius: 2px; cursor: pointer; text-align: left;
      transition: border-color 140ms var(--ease), background 140ms var(--ease), transform 140ms var(--ease);
    }
    .option:hover { border-color: var(--ink-soft); }
    .option .key {
      font-family: var(--mono); font-size: 11px; font-weight: 500;
      background: var(--paper); border: 1px solid var(--rule-strong);
      border-bottom-width: 2px; border-radius: 3px;
      padding: 2px 6px; color: var(--ink-soft); text-align: center;
      letter-spacing: 0;
    }
    .option.selected {
      background: var(--accent); border-color: var(--accent); color: var(--paper);
    }
    .option.selected .key { background: var(--paper); color: var(--accent); border-color: transparent; }

    /* Likert */
    .likert { display: grid; gap: 10px; }
    .likert .scale {
      display: grid; grid-template-columns: repeat(var(--cols), 1fr);
      border: 1px solid var(--rule-strong); border-radius: 2px; overflow: hidden;
      background: var(--paper);
    }
    .likert .cell {
      min-height: 64px; display: grid; place-items: center;
      font-family: var(--mono); font-size: 17px; font-weight: 500;
      color: var(--ink-soft); cursor: pointer; background: transparent;
      border: 0; border-right: 1px solid var(--rule);
      transition: background 140ms var(--ease), color 140ms var(--ease);
      font-variant-numeric: tabular-nums;
    }
    .likert .cell:last-child { border-right: 0; }
    .likert .cell:hover { background: var(--accent-tint); color: var(--ink); }
    .likert .cell.selected { background: var(--accent); color: var(--paper); font-weight: 600; }
    .likert .anchors {
      display: flex; justify-content: space-between; gap: 16px;
      font-family: var(--sans); font-style: italic; font-size: 13px; color: var(--muted);
    }

    /* Actions row */
    .actions {
      display: flex; align-items: center; gap: 16px; margin-top: 28px; flex-wrap: wrap;
    }
    .actions .press {
      font-family: var(--mono); font-size: 11px; letter-spacing: 0.10em;
      color: var(--muted); text-transform: uppercase;
    }
    kbd {
      font-family: var(--mono); font-size: 11px; font-weight: 500;
      background: var(--paper); border: 1px solid var(--rule-strong);
      border-bottom-width: 2px; border-radius: 3px;
      padding: 1px 6px; color: var(--ink); text-transform: none;
    }
    button.btn, button.skip {
      font-family: var(--sans); font-size: 14px; font-weight: 600;
      letter-spacing: 0.01em; padding: 12px 22px; cursor: pointer;
      border-radius: 2px; transition: background 140ms var(--ease), border-color 140ms var(--ease);
    }
    button.btn {
      border: 1px solid var(--accent); background: var(--accent); color: var(--paper);
      display: inline-flex; align-items: center; gap: 10px;
    }
    button.btn .ret { font-family: var(--mono); font-size: 12px; opacity: 0.85; }
    button.btn:hover { background: var(--accent-deep); border-color: var(--accent-deep); }
    button.btn:disabled { opacity: 0.5; cursor: wait; }
    button.skip {
      background: transparent; border: 1px solid var(--rule-strong); color: var(--ink-soft);
    }
    button.skip:hover { border-color: var(--ink-soft); }

    /* Intro & thanks */
    .step.intro .q, .step.thanks .q {
      font-size: clamp(36px, 5vw, 52px); max-width: 18ch;
    }
    .tutorial {
      list-style: none; margin: 26px 0 0; padding: 0;
      display: grid; gap: 12px; max-width: 58ch;
    }
    .tutorial li {
      display: grid; grid-template-columns: 28px 1fr; gap: 12px; align-items: start;
      font-family: var(--serif); font-size: 17px; color: var(--ink-soft);
    }
    .tutorial .key {
      font-family: var(--mono); font-size: 12px; color: var(--accent);
      padding-top: 3px; font-variant-numeric: tabular-nums;
    }
    .step.thanks .rid {
      font-family: var(--mono); font-size: 12px; color: var(--muted);
      letter-spacing: 0.10em; text-transform: uppercase; margin-top: 6px;
      display: inline-block;
    }

    /* ── Bottom bar ────────────────────────────────────────── */
    .bottombar {
      display: flex; justify-content: space-between; align-items: center;
      padding: 16px 28px 22px; gap: 16px;
      font-family: var(--mono); font-size: 11px; letter-spacing: 0.10em;
      color: var(--muted); text-transform: uppercase;
    }
    .nav-arrows { display: flex; gap: 6px; }
    .nav-arrows button {
      width: 32px; height: 32px; display: grid; place-items: center;
      background: var(--paper); border: 1px solid var(--rule-strong);
      color: var(--ink-soft); cursor: pointer; border-radius: 2px;
      transition: border-color 140ms var(--ease), color 140ms var(--ease);
      font-family: var(--sans); font-size: 14px;
    }
    .nav-arrows button:hover:not(:disabled) { border-color: var(--ink-soft); color: var(--ink); }
    .nav-arrows button:disabled { opacity: 0.35; cursor: not-allowed; }
    .footer-meta { display: flex; gap: 16px; flex-wrap: wrap; }
    @media (max-width: 600px) { .bottombar { padding: 14px 18px 18px; } }

    /* Toast */
    .toast {
      position: fixed; top: 16px; left: 50%; transform: translate(-50%, -16px);
      background: var(--ink); color: var(--paper);
      padding: 12px 18px; font-family: var(--sans); font-size: 14px;
      border-radius: 2px; opacity: 0; pointer-events: none;
      transition: opacity 240ms var(--ease), transform 240ms var(--ease);
      max-width: min(520px, calc(100vw - 32px));
      box-shadow: 0 4px 24px oklch(0.20 0.012 50 / 0.18);
      z-index: 20;
    }
    .toast.show { opacity: 1; transform: translate(-50%, 0); }
    .toast.bad { background: var(--bad); }

    /* Focus rings: container never shows one; controls use focus-visible only */
    .step:focus { outline: none; }
    .step[tabindex]:focus { outline: none; }
    button:focus { outline: none; }
    .option:focus, .cell:focus, button.btn:focus, button.skip:focus,
    .nav-arrows button:focus { outline: none; }
    .text-input:focus-visible, .date-input:focus-visible {
      outline: none; border-bottom-color: var(--accent);
    }
    .textarea-input:focus-visible {
      outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-tint);
    }
    .option:focus-visible, .cell:focus-visible {
      outline: 2px solid var(--accent); outline-offset: 2px;
    }
    button.btn:focus-visible, button.skip:focus-visible, .nav-arrows button:focus-visible {
      outline: 2px solid var(--accent); outline-offset: 3px;
    }

    /* Setup screen (researcher view between participants) */
    .setup .badge {
      font-family: var(--mono); font-size: 11px; letter-spacing: 0.18em;
      text-transform: uppercase; color: var(--accent); margin-bottom: 14px;
      display: inline-flex; gap: 10px; align-items: center;
    }
    .setup .badge .dot { width: 6px; height: 6px; background: var(--accent); border-radius: 50%; }
    .setup .fields { display: grid; gap: 22px; margin-top: 8px; }
    .setup .field { display: grid; gap: 8px; }
    .setup .field .label {
      font-family: var(--mono); font-size: 11px; letter-spacing: 0.10em;
      color: var(--muted); text-transform: uppercase;
    }
    .setup .field .req { color: var(--accent); margin-left: 4px; font-style: normal; }
    .setup .consent {
      display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
    }
    .setup .consent .option {
      grid-template-columns: 28px 1fr; padding: 14px 16px;
    }
    .setup .field-hint {
      font-family: var(--sans); font-style: italic; font-size: 12px; color: var(--muted);
    }
    @media (max-width: 520px) { .setup .consent { grid-template-columns: 1fr; } }

    /* Prefers reduced motion */
    @media (prefers-reduced-motion: reduce) {
      .step, .progress .bar, .toast, .text-input, .textarea-input, .option, .likert .cell {
        transition: none !important;
      }
      .step.shake { animation: none; }
    }
  </style>
</head>
<body>
  <div class="app">
    <div class="topbar">
      <div class="progress"><div class="bar" id="bar"></div></div>
      <div class="topbar-row">
        <span class="brand"><span class="dot"></span><span>Kratt · tagasiside</span></span>
        <span class="counter"><span id="counterNow">00</span><span class="of">/</span><span id="counterTotal">00</span></span>
      </div>
    </div>

    <main class="stage">
      <div id="stage" aria-live="polite"></div>
    </main>

    <div class="bottombar">
      <div class="nav-arrows">
        <button type="button" id="prevBtn" title="Tagasi (Shift+Tab)">↑</button>
        <button type="button" id="nextBtn" title="Edasi (Enter)">↓</button>
      </div>
      <div class="footer-meta">
        <span>Lokaalne · ei lahku arvutist</span>
        <span>Kratt · 2026</span>
      </div>
    </div>
  </div>

  <div class="toast" id="toast"></div>

  <script>
    const PARTICIPANT = __PARTICIPANT__;
    const SESSION = __SESSION__;
    const CONSENT = __CONSENT__;
    const DATE = __DATE__;

    const steps = [
      {
        kind: 'setup', name: '_setup',
      },
      {
        kind: 'intro', name: '_intro',
        q: 'Mida tasub Kratiga päriselt proovida?',
        hint: 'See demo hindab ühe WiZ lambi hääljuhtimist ja väikseid info-oskusi. Proovi toetatud piire, mitte ainult kõige lihtsamat käsku.',
        tips: [
          'Valgus: pane põlema või kustu; ütle värviks sinine, punane, roosa, soe valge, külm valge või neutraalne.',
          'Heledus: proovi loomulikke lauseid nagu liiga hele, tee hämaramaks, tee valgemaks või suurenda heledust.',
          'Efektid ja olek: ütle tee diskot, käi värvid läbi, vilguta roosalt või küsi kas tuli põleb / mis värvi tuli on.',
          'Info: küsi kellaaega, kuupäeva või ilma teise päeva ja linna kohta, näiteks mis ilm homme Tartus on või kas ülehomme sajab.',
          'Täpsustus: anna poolik käsk nagu pane tuli teist värvi ja vasta Krati küsimusele ilma uut äratussõna ütlemata.',
          'Üldküsimus: küsi lühikest retsepti, nõu või seletust; see läheb abimudelile ja võib olla aeglasem kui lambikäsk.',
          'Piirid: taimerid, muusika, uksed ja muud seadmed ei ole selles demos toetatud.',
        ],
      },
      {
        kind: 'choice', name: 'language_level', required: true,
        q: 'Milline on sinu eesti keele tase?',
        options: ['emakeel', 'C1–C2', 'B1–B2', 'A1–A2', 'muu', 'ei soovi öelda'],
      },
      {
        kind: 'text', name: 'language_level_other', required: true,
        q: 'Täpsusta keeletaset.',
        hint: 'Kirjelda lühidalt, nt "vene emakeel, eesti keelt valdav".',
        placeholder: 'sinu sõnastus',
        showIf: (s) => s.language_level === 'muu',
      },
      {
        kind: 'choice', name: 'voice_assistant_usage', required: true,
        q: 'Kui tihti oled varem kasutanud häälassistenti?',
        options: ['mitte kunagi', 'harva', 'iganädalaselt', 'iga päev'],
      },
      {
        kind: 'choice', name: 'smart_home_usage', required: true,
        q: 'Kui tihti kasutad nutikodu seadmeid?',
        options: ['ei kasuta', 'aeg-ajalt', 'regulaarselt'],
      },
      {
        kind: 'likert', name: 'umux_capabilities', required: true, max: 7,
        q: 'Selle süsteemi võimekused vastavad mu nõudmistele.',
        left: 'ei nõustu üldse', right: 'nõustun täielikult',
      },
      {
        kind: 'likert', name: 'umux_ease', required: true, max: 7,
        q: 'Seda süsteemi on lihtne kasutada.',
        left: 'ei nõustu üldse', right: 'nõustun täielikult',
      },
      {
        kind: 'likert', name: 'seq_ease', required: true, max: 7,
        q: 'Kui lihtne oli Kratiga etteantud ülesandeid lõpule viia?',
        left: 'väga raske', right: 'väga lihtne',
      },
      {
        kind: 'likert', name: 'reliability', required: true, max: 5,
        q: 'Süsteem reageeris piisavalt usaldusväärselt.',
        left: 'üldse ei nõustu', right: 'nõustun täielikult',
      },
      {
        kind: 'likert', name: 'speed', required: true, max: 5,
        q: 'Süsteem reageeris piisavalt kiiresti.',
        left: 'üldse ei nõustu', right: 'nõustun täielikult',
      },
      {
        kind: 'likert', name: 'natural_phrasing', required: true, max: 5,
        q: 'Käskude sõnastamine tundus loomulik.',
        left: 'üldse ei nõustu', right: 'nõustun täielikult',
      },
      {
        kind: 'likert', name: 'home_use', required: true, max: 5,
        q: 'Kasutaksin sellist süsteemi kodus.',
        left: 'üldse ei nõustu', right: 'nõustun täielikult',
      },
      {
        kind: 'textarea', name: 'open_comment', required: false,
        q: 'Kui midagi häiris või üllatas, pane kirja.',
        hint: 'Valikuline. Paar lauset piisab. Enter salvestab; Shift+Enter teeb reavahetuse.',
        placeholder: 'Mis jäi meelde…',
      },
    ];

    const stage = document.getElementById('stage');
    const bar = document.getElementById('bar');
    const counterNow = document.getElementById('counterNow');
    const counterTotal = document.getElementById('counterTotal');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const toast = document.getElementById('toast');

    const state = {
      participant_id: PARTICIPANT || '',
      date: DATE || new Date().toLocaleDateString('en-CA'),
      session_id: SESSION || '',
      consent_level: CONSENT || '',
    };
    let idx = 0;
    let busy = false;
    let submitting = false;
    let submittedId = null;

    function isVisible(step) {
      if (!step) return false;
      if (typeof step.showIf === 'function') return step.showIf(state);
      return true;
    }
    function isCounted(step) {
      return step && step.kind !== 'setup' && step.kind !== 'intro' && step.kind !== 'thanks';
    }
    function visibleSteps() { return steps.filter(isVisible); }
    function countedTotal() {
      return steps.filter(s => isVisible(s) && isCounted(s)).length;
    }
    function countedIndex(i) {
      let n = 0;
      for (let k = 0; k <= i; k++) if (isVisible(steps[k]) && isCounted(steps[k])) n++;
      return n;
    }
    function nextIdx(from) {
      for (let k = from + 1; k < steps.length; k++) if (isVisible(steps[k])) return k;
      return steps.length; // submit
    }
    function prevIdx(from) {
      // never let the participant step back into the researcher's setup screen
      const limit = (steps[from] && (steps[from].kind === 'setup' || steps[from].kind === 'intro')) ? -1 : 1;
      for (let k = from - 1; k >= 0; k--) {
        if (steps[k].kind === 'setup') return -1;
        if (isVisible(steps[k])) return k;
      }
      return -1;
    }

    const pad2 = n => String(n).padStart(2, '0');
    const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

    function isComplete(step) {
      if (!step.required) return true;
      const v = state[step.name];
      if (step.kind === 'likert') return Number.isInteger(v);
      return typeof v === 'string' ? v.trim().length > 0 : !!v;
    }

    function updateProgress() {
      const total = countedTotal();
      counterTotal.textContent = pad2(total);
      const step = steps[idx];
      if (idx >= steps.length) {
        bar.style.transform = 'scaleX(1)';
        counterNow.textContent = pad2(total);
      } else if (step && (step.kind === 'setup' || step.kind === 'intro' || step.kind === 'thanks')) {
        bar.style.transform = step.kind === 'thanks' ? 'scaleX(1)' : 'scaleX(0)';
        counterNow.textContent = '··';
      } else {
        const visIdx = countedIndex(idx);
        bar.style.transform = 'scaleX(' + (visIdx / Math.max(1, total)) + ')';
        counterNow.textContent = pad2(visIdx);
      }
      prevBtn.disabled = prevIdx(idx) < 0;
      nextBtn.disabled = false;
    }

    function showToast(msg, ok = true) {
      toast.textContent = msg;
      toast.classList.toggle('bad', !ok);
      toast.classList.add('show');
      clearTimeout(showToast._t);
      showToast._t = setTimeout(() => toast.classList.remove('show'), 3200);
    }

    function renderStep(i) {
      const step = steps[i];
      const total = countedTotal();
      const number = isCounted(step) ? pad2(countedIndex(i)) : '';
      const totalLabel = pad2(total);
      let body = '';

      if (step.kind === 'setup') {
        const consents = ['ainult mõõdikud', 'audio opt-in'];
        const consentBtns = consents.map((c, j) => {
          const isSel = state.consent_level === c ? ' selected' : '';
          return `<button type="button" class="option${isSel}" data-consent="${esc(c)}" data-key="${j+1}">
            <span class="key">${j+1}</span><span>${esc(c)}</span>
          </button>`;
        }).join('');
        body = `
          <div class="setup">
            <div class="badge"><span class="dot"></span><span>Läbiviija seadistus</span></div>
            <h2 class="q">Uue osaleja andmed</h2>
            <p class="hint">Sisesta enne kui annad arvuti osalejale. Server jääb jooksma; iga osaleja järel naase siia, et järgmise omaga jätkata.</p>
            <div class="fields">
              <label class="field">
                <span class="label">Osaleja tähis<span class="req">*</span></span>
                <input class="text-input" data-setup="participant_id" type="text" autocomplete="off"
                       spellcheck="false" value="${esc(state.participant_id || '')}" placeholder="P01" />
              </label>
              <div class="field">
                <span class="label">Nõusoleku tase<span class="req">*</span></span>
                <div class="consent" data-setup-consent>${consentBtns}</div>
                <span class="field-hint">Vali klahviga <kbd>1</kbd>/<kbd>2</kbd> või klõpsa.</span>
              </div>
              <label class="field">
                <span class="label">Sessiooni ID</span>
                <input class="text-input" data-setup="session_id" type="text" autocomplete="off"
                       spellcheck="false" value="${esc(state.session_id || '')}" placeholder="valikuline, nt session.json-ist" />
                <span class="field-hint">Vajaduse korral. Tühjaks jätta on okei.</span>
              </label>
            </div>
            <div class="err" data-err></div>
            <div class="actions">
              <button type="button" class="btn" data-action="begin-participant">Anna osalejale <span class="ret">↵</span></button>
              <span class="press">vajuta <kbd>↵</kbd></span>
            </div>
          </div>
        `;
        const el = document.createElement('div');
        el.className = 'step';
        el.dataset.kind = step.kind;
        el.dataset.idx = i;
        el.innerHTML = body;
        return el;
      }

      if (step.kind === 'intro') {
        const tips = (step.tips || []).map((tip, j) => `
          <li><span class="key">${pad2(j + 1)}</span><span>${esc(tip)}</span></li>
        `).join('');
        body = `
          <div class="num"><span>Algus</span></div>
          <h1 class="q">${esc(step.q)}</h1>
          <p class="hint">${esc(step.hint)}</p>
          ${tips ? `<ul class="tutorial">${tips}</ul>` : ''}
          <div class="actions">
            <button type="button" class="btn" data-action="begin">Alusta <span class="ret">↵</span></button>
          </div>
        `;
      } else if (step.kind === 'text') {
        const val = state[step.name] || '';
        body = `
          <div class="num"><span class="arrow">→</span><span>${number} / ${totalLabel}</span></div>
          <h2 class="q">${esc(step.q)}</h2>
          ${step.hint ? `<p class="hint">${esc(step.hint)}</p>` : ''}
          <input class="text-input" type="text" autocomplete="off" spellcheck="false"
                 value="${esc(val)}" placeholder="${esc(step.placeholder || '')}" />
          <div class="err" data-err></div>
          <div class="actions">
            <button type="button" class="btn" data-action="ok">${step.skippable ? 'Edasi' : 'OK'} <span class="ret">↵</span></button>
            ${step.skippable ? `<button type="button" class="skip" data-action="skip">Jäta vahele</button>` : ''}
            <span class="press">vajuta <kbd style="font-family:var(--mono)">↵</kbd></span>
          </div>
        `;
      } else if (step.kind === 'date') {
        const val = state[step.name] || today();
        body = `
          <div class="num"><span class="arrow">→</span><span>${number} / ${totalLabel}</span></div>
          <h2 class="q">${esc(step.q)}</h2>
          ${step.hint ? `<p class="hint">${esc(step.hint)}</p>` : ''}
          <input class="date-input" type="date" value="${esc(val)}" />
          <div class="err" data-err></div>
          <div class="actions">
            <button type="button" class="btn" data-action="ok">OK <span class="ret">↵</span></button>
            <span class="press">vajuta <kbd>↵</kbd></span>
          </div>
        `;
      } else if (step.kind === 'choice') {
        const sel = state[step.name];
        const opts = step.options.map((o, j) => {
          const k = j + 1;
          const isSel = sel === o ? ' selected' : '';
          return `<li><button type="button" class="option${isSel}" data-value="${esc(o)}" data-key="${k}">
            <span class="key">${k}</span><span>${esc(o)}</span>
          </button></li>`;
        }).join('');
        body = `
          <div class="num"><span class="arrow">→</span><span>${number} / ${totalLabel}</span></div>
          <h2 class="q">${esc(step.q)}</h2>
          <ul class="options">${opts}</ul>
          <div class="err" data-err></div>
          <div class="actions">
            <span class="press">vali klahviga <kbd>1</kbd>–<kbd>${step.options.length}</kbd> või klõpsa</span>
          </div>
        `;
      } else if (step.kind === 'likert') {
        const sel = state[step.name];
        const cells = Array.from({length: step.max}, (_, j) => {
          const v = j + 1;
          const isSel = sel === v ? ' selected' : '';
          return `<button type="button" class="cell${isSel}" data-value="${v}">${v}</button>`;
        }).join('');
        body = `
          <div class="num"><span class="arrow">→</span><span>${number} / ${totalLabel}</span></div>
          <h2 class="q">${esc(step.q)}</h2>
          <div class="likert" style="--cols:${step.max}">
            <div class="scale">${cells}</div>
            <div class="anchors"><span>← ${esc(step.left)}</span><span>${esc(step.right)} →</span></div>
          </div>
          <div class="err" data-err></div>
          <div class="actions">
            <span class="press">vali klahviga <kbd>1</kbd>–<kbd>${step.max}</kbd></span>
          </div>
        `;
      } else if (step.kind === 'textarea') {
        const val = state[step.name] || '';
        body = `
          <div class="num"><span class="arrow">→</span><span>${number} / ${totalLabel}</span></div>
          <h2 class="q">${esc(step.q)}</h2>
          ${step.hint ? `<p class="hint">${esc(step.hint)}</p>` : ''}
          <textarea class="textarea-input" placeholder="${esc(step.placeholder || '')}">${esc(val)}</textarea>
          <div class="err" data-err></div>
          <div class="actions">
            <button type="button" class="btn" data-action="submit">Salvesta vastus <span class="ret">↵</span></button>
            <span class="press"><kbd>↵</kbd> salvesta · <kbd>Shift+↵</kbd> reavahetus</span>
          </div>
        `;
      }

      const el = document.createElement('div');
      el.className = 'step ' + (step.kind === 'intro' ? 'intro' : '');
      el.dataset.kind = step.kind;
      el.dataset.idx = i;
      el.innerHTML = body;
      return el;
    }

    function renderThanks(rid) {
      const el = document.createElement('div');
      el.className = 'step thanks in';
      el.innerHTML = `
        <div class="num"><span>Valmis</span></div>
        <h2 class="q">Aitäh. Vastus on salvestatud.</h2>
        <div class="rid">ID: ${esc(rid)}</div>
        <div class="actions" style="margin-top:32px">
          <button type="button" class="btn" data-action="next-participant">Järgmine osaleja <span class="ret">↵</span></button>
        </div>
      `;
      return el;
    }

    function transitionTo(buildEl, direction = 'forward') {
      if (busy) return;
      busy = true;
      const current = stage.querySelector('.step');
      const outClass = direction === 'forward' ? 'out-up' : 'out-down';
      if (current) {
        current.classList.remove('in');
        current.classList.add(outClass);
      }
      const next = buildEl();
      // start state: opposite side
      next.style.transform = direction === 'forward' ? 'translateY(14px)' : 'translateY(-14px)';
      next.style.opacity = '0';
      const swap = () => {
        if (current && current.parentNode) current.parentNode.removeChild(current);
        stage.appendChild(next);
        // force reflow then animate in
        // eslint-disable-next-line no-unused-expressions
        next.offsetHeight;
        next.style.transform = '';
        next.style.opacity = '';
        next.classList.add('in');
        attachStepHandlers(next);
        focusStep(next);
        busy = false;
      };
      setTimeout(swap, current ? 240 : 0);
    }

    function focusStep(el) {
      const step = steps[idx];
      if (step && step.kind === 'setup') {
        let target;
        if (!String(state.participant_id || '').trim()) {
          target = el.querySelector('input[data-setup="participant_id"]');
        } else if (!state.consent_level) {
          target = el.querySelector('[data-setup-consent] .option');
        } else {
          target = el.querySelector('button.btn');
        }
        if (target) target.focus({preventScroll: true});
        return;
      }
      const input = el.querySelector('input, textarea');
      if (input) {
        input.focus({preventScroll: true});
        if (input.type === 'text' || input.tagName === 'TEXTAREA') {
          try { input.setSelectionRange(input.value.length, input.value.length); } catch (_) {}
        }
        return;
      }
      // No native input on this step (choice/likert/intro/thanks).
      // Don't put a focus ring on the .step container; focus the primary
      // button so keyboard users have a meaningful focus target.
      const btn = el.querySelector('button.btn, .option, .cell');
      if (btn) btn.focus({preventScroll: true});
    }

    function attachStepHandlers(el) {
      const step = steps[idx]; // may be undefined on the thanks screen
      const errEl = el.querySelector('[data-err]');
      const clearErr = () => { if (errEl) errEl.textContent = ''; el.classList.remove('shake'); };

      // Wire data-action buttons regardless of step kind so the setup, intro,
      // textarea-submit and thanks-next-participant buttons all work.
      el.querySelectorAll('[data-action]').forEach(btn => {
        btn.addEventListener('click', () => handleAction(btn.dataset.action));
      });
      if (!step) return; // thanks screen has no step descriptor; data-action above suffices

      if (step.kind === 'setup') {
        el.querySelectorAll('input[data-setup]').forEach(inp => {
          inp.addEventListener('input', () => { state[inp.dataset.setup] = inp.value; clearErr(); });
        });
        const consentWrap = el.querySelector('[data-setup-consent]');
        if (consentWrap) {
          consentWrap.querySelectorAll('.option').forEach(btn => {
            btn.addEventListener('click', () => {
              state.consent_level = btn.dataset.consent;
              consentWrap.querySelectorAll('.option').forEach(b => b.classList.toggle('selected', b === btn));
              clearErr();
              // Move focus to the primary advance button so Enter immediately continues.
              const primary = el.querySelector('button.btn');
              if (primary) primary.focus({preventScroll: true});
            });
          });
        }
      }

      if (step.kind === 'text') {
        const input = el.querySelector('input');
        input.addEventListener('input', () => { state[step.name] = input.value; clearErr(); });
      }
      if (step.kind === 'date') {
        const input = el.querySelector('input');
        input.addEventListener('input', () => { state[step.name] = input.value; clearErr(); });
      }
      if (step.kind === 'textarea') {
        const input = el.querySelector('textarea');
        input.addEventListener('input', () => { state[step.name] = input.value; clearErr(); });
      }
      if (step.kind === 'choice') {
        el.querySelectorAll('.option').forEach(btn => {
          btn.addEventListener('click', () => {
            state[step.name] = btn.dataset.value;
            if (step.name === 'language_level' && btn.dataset.value !== 'muu') {
              state.language_level_other = '';
            }
            el.querySelectorAll('.option').forEach(b => b.classList.toggle('selected', b === btn));
            clearErr();
            setTimeout(() => advance(), 200);
          });
        });
      }
      if (step.kind === 'likert') {
        el.querySelectorAll('.cell').forEach(btn => {
          btn.addEventListener('click', () => {
            state[step.name] = parseInt(btn.dataset.value, 10);
            el.querySelectorAll('.cell').forEach(b => b.classList.toggle('selected', b === btn));
            clearErr();
            setTimeout(() => advance(), 200);
          });
        });
      }
    }

    function handleAction(action) {
      if (action === 'begin' || action === 'begin-participant') { advance(); return; }
      if (action === 'ok') { advance(); return; }
      if (action === 'skip') { state[steps[idx].name] = ''; advance(); return; }
      if (action === 'submit') { advance(); return; }
      if (action === 'next-participant') { resetForNext(); return; }
    }

    function flagMissing(msg) {
      const el = stage.querySelector('.step');
      if (!el) return;
      el.classList.add('shake');
      const errEl = el.querySelector('[data-err]');
      if (errEl) errEl.textContent = msg || 'Palun täida see väli.';
      setTimeout(() => el.classList.remove('shake'), 360);
    }

    function advance() {
      if (busy || submitting) return;
      if (idx >= steps.length) return; // already on thanks
      const step = steps[idx];
      if (step && step.kind === 'setup') {
        const missing = [];
        if (!String(state.participant_id || '').trim()) missing.push('osaleja tähis');
        if (!state.consent_level) missing.push('nõusoleku tase');
        if (missing.length) {
          flagMissing('Palun täida: ' + missing.join(', ') + '.');
          return;
        }
      } else if (step && step.required && !isComplete(step)) {
        flagMissing(step.kind === 'likert' || step.kind === 'choice'
          ? 'Palun tee valik.'
          : 'Palun täida see väli.');
        return;
      }
      const ni = nextIdx(idx);
      if (ni >= steps.length) { submit(); return; }
      idx = ni;
      updateProgress();
      transitionTo(() => renderStep(idx), 'forward');
    }

    function back() {
      if (busy || submitting) return;
      const pi = prevIdx(idx);
      if (pi < 0) return;
      idx = pi;
      updateProgress();
      transitionTo(() => renderStep(idx), 'backward');
    }

    async function submit() {
      if (submitting) return;
      submitting = true;
      const payload = {
        participant_id: state.participant_id || '',
        date: state.date || '',
        session_id: state.session_id || '',
        consent_level: state.consent_level || '',
      };
      for (const s of steps) {
        if (s.name.startsWith('_')) continue;
        let v = state[s.name];
        if (v === undefined || v === null) v = '';
        payload[s.name] = v;
      }
      try {
        const res = await fetch('/api/submit', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok || !data.ok) throw new Error(data.error || 'Salvestamine ebaõnnestus');
        submittedId = data.response_id;
        // Move past last index to drive progress to 100%
        idx = steps.length;
        updateProgress();
        transitionTo(() => renderThanks(submittedId), 'forward');
      } catch (err) {
        showToast(err.message || String(err), false);
      } finally {
        submitting = false;
      }
    }

    function incrementParticipant(id) {
      const m = String(id || '').match(/^(.*?)(\d+)$/);
      if (!m) return id;
      const prefix = m[1];
      const num = String(parseInt(m[2], 10) + 1).padStart(m[2].length, '0');
      return prefix + num;
    }

    function resetForNext() {
      const nextPid = incrementParticipant(state.participant_id) || state.participant_id;
      const sessId = state.session_id;
      const consent = state.consent_level;
      for (const s of steps) {
        if (s.name.startsWith('_')) continue;
        if (s.kind === 'likert') delete state[s.name];
        else state[s.name] = '';
      }
      state.participant_id = nextPid;
      state.date = DATE || new Date().toLocaleDateString('en-CA');
      state.session_id = sessId;
      state.consent_level = consent;
      // Back to the researcher setup screen so PID/consent can be confirmed for the next person.
      idx = 0;
      updateProgress();
      transitionTo(() => renderStep(idx), 'backward');
    }

    // Global keys
    document.addEventListener('keydown', (e) => {
      if (busy || submitting) return;
      const active = document.activeElement;
      const inTextarea = active && active.tagName === 'TEXTAREA';
      const inText = active && (active.tagName === 'INPUT' && (active.type === 'text' || active.type === 'date'));

      // Shift+Enter inside textarea: newline. Plain Enter advances (or moves to next participant on thanks).
      // If focus is on a button, let the browser fire its native click (consent select, etc.) rather than skipping past it.
      if (e.key === 'Enter') {
        if (inTextarea && e.shiftKey) return;
        if (active && active.tagName === 'BUTTON' && active.dataset && (active.dataset.consent || active.classList.contains('option') || active.classList.contains('cell'))) {
          return; // let the click fire
        }
        e.preventDefault();
        if (idx >= steps.length) { resetForNext(); return; }
        advance();
        return;
      }
      // Cmd/Ctrl+Enter always advances
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault();
        advance();
        return;
      }
      // Escape: back (Shift+Tab is left to natural focus traversal inside a step).
      if (e.key === 'Escape') { e.preventDefault(); back(); return; }
      // Digit keys for choice / likert / setup-consent. Skip when typing into text fields.
      if (inText || inTextarea) return;
      const step = steps[idx];
      if (!step) return;
      if (step.kind === 'likert' && /^[1-9]$/.test(e.key)) {
        const v = parseInt(e.key, 10);
        if (v >= 1 && v <= step.max) {
          const btn = stage.querySelector(`.cell[data-value="${v}"]`);
          if (btn) btn.click();
        }
      } else if (step.kind === 'choice' && /^[1-9]$/.test(e.key)) {
        const v = parseInt(e.key, 10);
        if (v >= 1 && v <= step.options.length) {
          const btn = stage.querySelector(`.option[data-key="${v}"]`);
          if (btn) btn.click();
        }
      } else if (step.kind === 'setup' && /^[1-2]$/.test(e.key)) {
        const btn = stage.querySelector(`[data-setup-consent] .option[data-key="${e.key}"]`);
        if (btn) { btn.click(); btn.focus({preventScroll: true}); }
      }

      // Arrow-left / -right move between consent options when one is focused.
      if (step.kind === 'setup' && active && active.classList && active.classList.contains('option') && active.dataset.consent) {
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
          e.preventDefault();
          const opts = Array.from(stage.querySelectorAll('[data-setup-consent] .option'));
          const i = opts.indexOf(active);
          const j = e.key === 'ArrowRight' ? (i + 1) % opts.length : (i - 1 + opts.length) % opts.length;
          opts[j].focus({preventScroll: true});
          opts[j].click();
        }
      }
    });

    prevBtn.addEventListener('click', back);
    nextBtn.addEventListener('click', advance);

    // Start: setup screen if metadata not all prefilled, otherwise straight to intro.
    if (state.participant_id && state.consent_level) {
      idx = nextIdx(0); // skip setup
    }
    updateProgress();
    transitionTo(() => renderStep(idx), 'forward');
  </script>
</body>
</html>"""


class QuestionnaireHandler(BaseHTTPRequestHandler):
    output_dir: Path = DEFAULT_OUTPUT_DIR

    def log_message(self, fmt: str, *args: Any) -> None:  # quieter, but still useful
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.address_string()} {fmt % args}")

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, obj: dict[str, Any]) -> None:
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in {"/", "/index.html"}:
            self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not found"})
            return
        q = parse_qs(parsed.query)
        page = page_html(
            participant_id=(q.get("participant_id") or q.get("p") or [""])[0],
            session_id=(q.get("session_id") or q.get("s") or [""])[0],
            consent_level=(q.get("consent_level") or q.get("c") or [""])[0],
        )
        self._send(HTTPStatus.OK, page.encode("utf-8"), "text/html; charset=utf-8")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/submit":
            self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 256_000:
                raise ValueError("Request too large")
            raw = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError("Expected JSON object")
            result = store_submission(self.output_dir, payload)
            self._json(HTTPStatus.OK, result)
        except Exception as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local Kratt user-test questionnaire server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host. Default: 127.0.0.1")
    parser.add_argument("--port", type=int, default=8877, help="Bind port. Default: 8877. Use 0 for an auto-selected free port.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help=f"Output dir. Default: {DEFAULT_OUTPUT_DIR}")
    parser.add_argument("--participant-id", default="", help="Optional prefill for first participant; in-browser setup is the source of truth.")
    parser.add_argument("--session-id", default="", help="Optional session ID prefill")
    parser.add_argument("--consent-level", default="", choices=("", "ainult mõõdikud", "audio opt-in"),
                        help="Optional consent-level prefill: 'ainult mõõdikud' or 'audio opt-in'")
    parser.add_argument("--no-open", action="store_true", help="Do not open the browser automatically")
    args = parser.parse_args()

    QuestionnaireHandler.output_dir = args.output_dir
    try:
        server = ThreadingHTTPServer((args.host, args.port), QuestionnaireHandler)
    except OSError as exc:
        if args.port != 0:
            print(f"Port {args.port} is unavailable ({exc}). Falling back to a free local port.")
            server = ThreadingHTTPServer((args.host, 0), QuestionnaireHandler)
        else:
            raise
    actual_host, actual_port = server.server_address[:2]
    display_host = "127.0.0.1" if actual_host in ("0.0.0.0", "") else actual_host
    url = f"http://{display_host}:{actual_port}/"
    import urllib.parse as _u
    query = []
    if args.participant_id:
        query.append("p=" + _u.quote(args.participant_id))
    if args.session_id:
        query.append("s=" + _u.quote(args.session_id))
    if args.consent_level:
        query.append("c=" + _u.quote(args.consent_level))
    open_url = url + ("?" + "&".join(query) if query else "")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    print("Kratt questionnaire server")
    print(f"  URL: {open_url}")
    print(f"  Saving to: {args.output_dir}")
    print("  Ctrl+C to stop")
    if not args.no_open:
        webbrowser.open(open_url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
