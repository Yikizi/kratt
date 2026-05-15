#!/usr/bin/env python3
"""Regression-test the demo lightweight intent protocol against Ollama."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PIPELINE_PATH = PROJECT_ROOT / "tools/demo-pipeline/pipeline.py"
DEFAULT_CASES = PROJECT_ROOT / "tools/demo-pipeline/intent-regression-cases.json"


def load_pipeline():
    spec = importlib.util.spec_from_file_location("kratt_demo_pipeline", PIPELINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import {PIPELINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_protocol(value: str) -> str:
    raw = (value or "").strip().strip("` ")
    raw = raw.splitlines()[0].strip() if raw else "NONE"
    if "->" in raw:
        raw = raw.split("->", 1)[1].strip()
    parts = raw.split(maxsplit=1)
    cmd = parts[0].upper() if parts else "NONE"
    arg = parts[1].strip() if len(parts) > 1 else ""
    if cmd == "DIM":
        return "BRIGHT 80"
    if cmd == "BRIGHTEN":
        return "BRIGHT 200"
    if cmd == "BRIGHTNESS":
        cmd = "BRIGHT"
    if cmd == "STATUS":
        cmd = "STATE"
    if cmd == "COLOR":
        arg = arg.lower().replace("oranz", "oranž")
    if cmd == "WEATHER" and arg:
        place_aliases = {
            "tallinnas": "tallinn",
            "tartus": "tartu",
            "pärnus": "pärnu",
            "parnus": "pärnu",
            "parnu": "pärnu",
        }
        arg_norm = place_aliases.get(arg.lower(), arg.lower())
        return f"{cmd} {arg_norm}"
    if cmd == "COLOR" and arg:
        return f"{cmd} {arg}"
    if cmd in ("TIME", "DATE", "BRIGHT") and arg:
        # Keep the first numeric offset/value only. This makes comparison robust
        # against extra words after the protocol token.
        import re

        match = re.search(r"[-+]?\d+", arg)
        return f"{cmd} {match.group(0)}" if match else cmd
    return cmd


def matches(expected: str, actual: str) -> bool:
    exp = normalize_protocol(expected)
    got = normalize_protocol(actual)
    if exp in ("WEATHER", "COLOR", "BRIGHT", "TIME", "DATE"):
        return got == exp or got.startswith(exp + " ")
    return got == exp


def call_protocol(pipeline, text: str) -> tuple[str, float]:
    payload = {
        "model": pipeline.LLM_MODEL,
        "stream": False,
        "keep_alive": pipeline.OLLAMA_KEEP_ALIVE,
        "options": pipeline.OLLAMA_PROTOCOL_OPTIONS,
        "messages": [
            {"role": "system", "content": pipeline.SYSTEM_PROMPT_WIZ_PROTOCOL},
            {"role": "user", "content": text},
        ],
    }
    fmt = getattr(pipeline, "OLLAMA_PROTOCOL_FORMAT", None)
    if fmt is not None:
        payload["format"] = fmt
    t0 = time.monotonic()
    resp = pipeline.OLLAMA_SESSION.post(pipeline.OLLAMA_URL, json=payload, timeout=60)
    dt = time.monotonic() - t0
    resp.raise_for_status()
    raw = resp.json()["message"]["content"].strip()
    if fmt is not None:
        try:
            parsed = json.loads(raw)
            cmd = (parsed.get("cmd") or "NONE").strip().upper()
            arg = (parsed.get("arg") or "").strip()
            if cmd == "COLOR" and arg:
                raw = f"COLOR {arg.lower()}"
            elif cmd in ("WEATHER", "TIME", "DATE", "BRIGHT") and arg:
                raw = f"{cmd} {arg}"
            else:
                raw = cmd
        except (json.JSONDecodeError, AttributeError):
            pass
    return raw, dt


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Kratt demo intent routing")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--model", default=None, help="Ollama model (default: pipeline default)")
    parser.add_argument("--prompt-file", type=Path, default=None, help="Override SYSTEM_PROMPT_WIZ_PROTOCOL with file contents")
    parser.add_argument("--prompt-tag", default="default", help="Label included in JSON summary")
    parser.add_argument("--category", action="append", help="Run only category (can repeat)")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--show-pass", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable summary")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-row FAIL lines (clean stdout for --json)")
    args = parser.parse_args()

    pipeline = load_pipeline()
    pipeline.USE_CLAUDE_CODE = False
    pipeline.USE_PI_CLI = False
    if args.model:
        pipeline.LLM_MODEL = args.model
    if args.prompt_file:
        pipeline.SYSTEM_PROMPT_WIZ_PROTOCOL = args.prompt_file.read_text(encoding="utf-8")

    cases: list[dict[str, Any]] = json.loads(args.cases.read_text(encoding="utf-8"))
    if args.category:
        wanted = set(args.category)
        cases = [case for case in cases if case.get("category") in wanted]
    if args.limit is not None:
        cases = cases[: args.limit]

    results = []
    failures = []
    by_category: dict[str, dict[str, int]] = {}
    total_time = 0.0

    # Warm model.
    try:
        call_protocol(pipeline, "tere")
    except Exception as exc:
        print(f"Warmup failed: {exc}", file=sys.stderr)
        return 2

    for i, case in enumerate(cases, start=1):
        text = case["text"]
        expected = case["expect"]
        category = case.get("category", "uncategorized")
        try:
            actual, dt = call_protocol(pipeline, text)
            ok = matches(expected, actual)
            error = None
        except Exception as exc:
            actual = "<error>"
            dt = 0.0
            ok = False
            error = str(exc)
        total_time += dt

        stats = by_category.setdefault(category, {"ok": 0, "total": 0})
        stats["total"] += 1
        stats["ok"] += int(ok)

        row = {
            "i": i,
            "category": category,
            "text": text,
            "expected": expected,
            "actual": actual,
            "actual_norm": normalize_protocol(actual),
            "ok": ok,
            "latency_ms": int(dt * 1000),
            "error": error,
        }
        results.append(row)
        if not ok:
            failures.append(row)
        if (args.show_pass or not ok) and not args.quiet:
            mark = "OK" if ok else "FAIL"
            print(
                f"{mark:4} {i:03d} [{category:<16}] {dt:5.2f}s "
                f"{text!r} expected={expected!r} got={actual!r}"
            )
        if args.fail_fast and not ok:
            break

    total = len(results)
    ok_count = sum(1 for row in results if row["ok"])
    summary = {
        "model": pipeline.LLM_MODEL,
        "prompt_tag": args.prompt_tag,
        "ok": ok_count,
        "total": total,
        "accuracy": ok_count / total if total else 0,
        "avg_latency_ms": int((total_time / total) * 1000) if total else 0,
        "by_category": by_category,
        "failures": failures,
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print()
        print(
            f"Summary: {ok_count}/{total} ok "
            f"({summary['accuracy'] * 100:.1f}%), avg={summary['avg_latency_ms']}ms, model={pipeline.LLM_MODEL}"
        )
        for category, stats in sorted(by_category.items()):
            pct = (stats["ok"] / stats["total"] * 100) if stats["total"] else 0
            print(f"  {category:<16} {stats['ok']:>3}/{stats['total']:<3} {pct:5.1f}%")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
