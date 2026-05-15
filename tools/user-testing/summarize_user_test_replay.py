#!/usr/bin/env python3
"""Aggregate Kratt user-test replay results across sessions.

Input may be one or more replay output roots, session replay directories, or
`replay_scores.jsonl` files created by `kratt replay-user-test`. The summary is
intended for fast thesis-table iteration after pilots/full collection.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


def wilson_ci(successes: int, trials: int, confidence: float = 0.95) -> tuple[float, float]:
    if trials <= 0:
        return (0.0, 0.0)
    if successes < 0 or successes > trials:
        raise ValueError(f"successes={successes} outside [0,{trials}]")
    if abs(confidence - 0.95) < 1e-9:
        z = 1.959963984540054
    elif abs(confidence - 0.90) < 1e-9:
        z = 1.6448536269514722
    elif abs(confidence - 0.99) < 1e-9:
        z = 2.5758293035489004
    else:
        raise ValueError("only 0.90, 0.95, and 0.99 confidence are supported without scipy")
    p = successes / trials
    denom = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denom
    margin = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{100 * value:.1f}%"


def pct_ci(successes: int, total: int, confidence: float) -> str:
    if total <= 0:
        return "n/a"
    lo, hi = wilson_ci(successes, total, confidence=confidence)
    return f"{100 * successes / total:.1f}% [{100 * lo:.1f}--{100 * hi:.1f}]"


def discover_score_files(paths: Iterable[str]) -> list[Path]:
    files: set[Path] = set()
    for raw in paths:
        path = Path(raw).expanduser()
        if path.is_file():
            if path.name == "replay_scores.jsonl":
                files.add(path.resolve())
            else:
                raise SystemExit(f"not a replay_scores.jsonl file: {path}")
        elif path.is_dir():
            direct = path / "replay_scores.jsonl"
            if direct.exists():
                files.add(direct.resolve())
            else:
                for candidate in path.rglob("replay_scores.jsonl"):
                    files.add(candidate.resolve())
        else:
            raise SystemExit(f"path not found: {path}")
    return sorted(files)


def read_scores(path: Path) -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            objects.append(json.loads(line))

    replay_start = next((row for row in objects if row.get("type") == "replay_start"), {})
    session_meta: dict[str, Any] = {}
    session_dir = replay_start.get("session_dir")
    if session_dir:
        session_path = Path(str(session_dir)) / "session.json"
        try:
            session_meta = json.loads(session_path.read_text(encoding="utf-8"))
        except Exception:
            session_meta = {}

    rows: list[dict[str, Any]] = []
    for row in objects:
        if row.get("type") == "replay_score":
            row["_source_file"] = str(path)
            row["_replay_session_dir"] = str(session_dir or "")
            row.setdefault("session_dry_run", session_meta.get("dry_run"))
            row.setdefault("session_audio_fixture_dir", session_meta.get("audio_fixture_dir"))
            rows.append(row)
    return rows


def is_smoke_row(row: dict[str, Any]) -> bool:
    """Return True for dry-run/synthetic fixture rows that must not enter thesis tables.

    Current replay rows carry explicit dry-run/fixture metadata. Older smoke
    artifacts did not, so also exclude clearly synthetic participant IDs and
    temporary smoke-session paths when summarizing an existing output tree.
    """
    if row.get("session_dry_run") is True:
        return True
    if row.get("audio_source") in {"dry_run", "fixture"}:
        return True
    if row.get("session_audio_fixture_dir"):
        return True

    participant = str(row.get("participant_id") or "").upper()
    if participant.startswith(("TEST", "SYNTH", "SMOKE")):
        return True

    session_dir = str(row.get("_replay_session_dir") or "")
    if "/kratt-fixture" in session_dir or "/kratt-user-test-smoke" in session_dir:
        return True
    return False


def aggregate(rows: list[dict[str, Any]], confidence: float) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        model = str(row.get("model_name"))
        # Main thesis view: expected_wake=True vs False. Keep per-trial-type rows
        # as diagnostics below the ALL row.
        grouped[(model, "ALL")].append(row)
        grouped[(model, str(row.get("trial_type")))].append(row)

    summary: list[dict[str, Any]] = []
    for (model, slice_name), group_rows in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1] != "ALL", item[0][1])):
        positives = [row for row in group_rows if row.get("expected_wake") is True]
        negatives = [row for row in group_rows if row.get("expected_wake") is False]
        pos_hits = sum(1 for row in positives if row.get("triggered"))
        neg_hits = sum(1 for row in negatives if row.get("triggered"))
        latencies = [int(row["trigger_time_ms"]) for row in positives if row.get("triggered") and row.get("trigger_time_ms") is not None]
        median_latency = None
        if latencies:
            latencies_sorted = sorted(latencies)
            mid = len(latencies_sorted) // 2
            if len(latencies_sorted) % 2:
                median_latency = latencies_sorted[mid]
            else:
                median_latency = int(round((latencies_sorted[mid - 1] + latencies_sorted[mid]) / 2))
        summary.append(
            {
                "model_name": model,
                "slice": slice_name,
                "positive_hits": pos_hits,
                "positive_total": len(positives),
                "positive_recall": pos_hits / len(positives) if positives else None,
                "positive_recall_wilson": pct_ci(pos_hits, len(positives), confidence) if positives else "n/a",
                "negative_false_accepts": neg_hits,
                "negative_total": len(negatives),
                "negative_fpr": neg_hits / len(negatives) if negatives else None,
                "negative_fpr_wilson": pct_ci(neg_hits, len(negatives), confidence) if negatives else "n/a",
                "median_trigger_latency_ms": median_latency,
            }
        )
    return summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, Any]], *, score_files: list[Path], confidence: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Kratt user-test replay aggregate")
    lines.append("")
    lines.append(f"Input replay files: {len(score_files)}")
    lines.append(f"Wilson confidence: {confidence:.2f}")
    lines.append("")
    lines.append("## Main ALL slice")
    lines.append("")
    lines.append("| Model | Recall | Hard-neg FPR | Median trigger latency |")
    lines.append("|---|---:|---:|---:|")
    for row in rows:
        if row["slice"] != "ALL":
            continue
        latency = "n/a" if row["median_trigger_latency_ms"] is None else f"{row['median_trigger_latency_ms']} ms"
        lines.append(
            f"| `{row['model_name']}` | {row['positive_recall_wilson']} "
            f"({row['positive_hits']}/{row['positive_total']}) | "
            f"{row['negative_fpr_wilson']} ({row['negative_false_accepts']}/{row['negative_total']}) | "
            f"{latency} |"
        )
    lines.append("")
    lines.append("## Diagnostic slices")
    lines.append("")
    lines.append("| Model | Slice | Recall | FPR |")
    lines.append("|---|---|---:|---:|")
    for row in rows:
        if row["slice"] == "ALL":
            continue
        lines.append(
            f"| `{row['model_name']}` | `{row['slice']}` | "
            f"{row['positive_recall_wilson']} ({row['positive_hits']}/{row['positive_total']}) | "
            f"{row['negative_fpr_wilson']} ({row['negative_false_accepts']}/{row['negative_total']}) |"
        )
    lines.append("")
    lines.append("## Sources")
    lines.append("")
    for score_file in score_files:
        lines.append(f"- `{score_file}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate Kratt user-test replay outputs")
    parser.add_argument("paths", nargs="+", help="Replay output root/session dir or replay_scores.jsonl file")
    parser.add_argument("--output-dir", default="output/user-test-analysis")
    parser.add_argument("--prefix", default="user_test_replay_summary")
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--include-smoke", action="store_true", help="Include dry-run/synthetic fixture replay rows (never for thesis main tables)")
    return parser.parse_args(list(argv))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    score_files = discover_score_files(args.paths)
    if not score_files:
        raise SystemExit("no replay_scores.jsonl files found")

    rows: list[dict[str, Any]] = []
    for score_file in score_files:
        rows.extend(read_scores(score_file))
    total_rows = len(rows)
    smoke_rows = [row for row in rows if is_smoke_row(row)]
    if not args.include_smoke:
        rows = [row for row in rows if not is_smoke_row(row)]
    summary = aggregate(rows, confidence=args.confidence)

    output_dir = Path(args.output_dir).expanduser().resolve()
    csv_path = output_dir / f"{args.prefix}.csv"
    md_path = output_dir / f"{args.prefix}.md"
    write_csv(csv_path, summary)
    write_markdown(md_path, summary, score_files=score_files, confidence=args.confidence)

    print(f"Replay files: {len(score_files)}")
    print(f"Score rows:   {len(rows)} used / {total_rows} total")
    if smoke_rows and not args.include_smoke:
        print(f"Excluded smoke rows: {len(smoke_rows)} (use --include-smoke only for infrastructure debugging)")
    print(f"CSV:          {csv_path}")
    print(f"Markdown:     {md_path}")
    for row in summary:
        if row["slice"] == "ALL":
            print(
                f"{row['model_name']:<28} recall={row['positive_recall_wilson']:<22} "
                f"FPR={row['negative_fpr_wilson']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
