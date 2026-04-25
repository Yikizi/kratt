#!/usr/bin/env python3
"""Pivot benchmark CSV into a clean supervisor-ready markdown + CSV table.

Input:  benchmark_results_*.csv with columns
        timestamp, model, test_set, kind, threshold, metric, value, n, duration_h, combo
Output: supervisor_table.md (pretty markdown)
        supervisor_table.csv (flat pivot)
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


# Canonical ordering — matches training chronology, then MoE
MODEL_ORDER = [
    "v1", "v2", "v3", "v4", "v5",
    "v6", "v6-specaug", "v6-residual",
    "v7", "v8", "v9", "v10", "v11", "v12",
    "v13a", "v13b", "v14", "v15",
    "v16a", "v16b", "v16c",
    "ex2a", "ex3a", "ex3b",
    "expert-a", "expert-b", "expert-b2",
]

# Combos appended after singles, alphabetical
COMBO_PRIORITY = [
    "v14 + expert-b",
    "v6-residual + expert-a",
    "ex3a + expert-a",
    "ex3a + expert-b2",
    "ex3a + expert-a + expert-b2",
    "ex3a + expert-a + expert-b",
    "ex3a + expert-b + expert-b2",
    "ex3b + expert-b2",
]

# Columns shown in the main @0.97 table
MAIN_COLS = [
    ("pos_isa_xtts", "recall", "Isa(48)"),
    ("pos_mattias_short", "recall", "Mat(135)"),
    ("pos_ode", "recall", "Ode(11)"),
    ("pos_friend1", "recall", "Friend1(145)"),
    ("hard_neg_mac_holdout", "fpr", "HN-Mac(15)"),
    ("hard_neg_isa_xtts", "fpr", "HN-Isa(60)"),
    ("hard_neg_canary", "fpr", "HN-Can(5)"),
    ("faph_cv_et", "faph", "CV-ET 3.82h"),
    ("faph_librispeech", "faph", "LibSp 5.62h"),
    ("faph_dipco", "faph", "DiPCo 3.32h"),
    ("faph_macbook_bg", "faph", "MacBG 1.17h"),
]


def load_rows(path: Path) -> list[dict]:
    with open(path) as f:
        return list(csv.DictReader(f))


def fmt(metric: str, value: float) -> str:
    if metric in ("recall", "fpr"):
        return f"{value*100:4.0f}%"
    if metric == "faph":
        if value >= 100:
            return f"{value:6.0f}"
        if value >= 10:
            return f"{value:6.1f}"
        return f"{value:6.2f}"
    return f"{value:.2f}"


def pivot(rows: list[dict], threshold: float) -> dict[str, dict[tuple[str, str], float]]:
    out: dict[str, dict[tuple[str, str], float]] = defaultdict(dict)
    for r in rows:
        if abs(float(r["threshold"]) - threshold) > 1e-6:
            continue
        out[r["model"]][(r["test_set"], r["metric"])] = float(r["value"])
    return out


def sort_models(models: list[str]) -> list[str]:
    known = [m for m in MODEL_ORDER if m in models]
    known += [m for m in COMBO_PRIORITY if m in models]
    extra = sorted(set(models) - set(known))
    return known + extra


def build_markdown_table(pivot_data: dict, threshold: float, models: list[str]) -> str:
    headers = ["Model"] + [c[2] for c in MAIN_COLS]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for m in models:
        row = [m]
        for test_set, metric, _label in MAIN_COLS:
            v = pivot_data.get(m, {}).get((test_set, metric))
            row.append(fmt(metric, v) if v is not None else "—")
        lines.append("| " + " | ".join(row) + " |")
    title = f"### Koondtabel @ threshold = {threshold}\n"
    legend = (
        "\n*Veerud: pos=recall% (suurem parem), HN=hard-neg FPR% (väiksem parem), "
        "FAPH=false accepts/hour (väiksem parem). n=klippe / h=tunde.*\n"
    )
    return title + "\n".join(lines) + legend


def build_threshold_sweep(
    rows: list[dict], model: str, thresholds: list[float]
) -> str:
    header_sets = [
        ("pos_isa_xtts", "recall", "Isa rec"),
        ("pos_ode", "recall", "Õde rec"),
        ("hard_neg_mac_holdout", "fpr", "HN Mac"),
        ("hard_neg_isa_xtts", "fpr", "HN Isa"),
        ("faph_cv_et", "faph", "CV-ET"),
        ("faph_librispeech", "faph", "LibSp"),
        ("faph_dipco", "faph", "DiPCo"),
    ]
    by_t = {}
    for r in rows:
        if r["model"] != model:
            continue
        t = float(r["threshold"])
        by_t.setdefault(t, {})[(r["test_set"], r["metric"])] = float(r["value"])
    headers = ["Thr"] + [h[2] for h in header_sets]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for t in thresholds:
        if t not in by_t:
            continue
        row = [f"{t:.3f}"]
        for ts, metric, _ in header_sets:
            v = by_t[t].get((ts, metric))
            row.append(fmt(metric, v) if v is not None else "—")
        lines.append("| " + " | ".join(row) + " |")
    return f"### Threshold sweep — {model}\n" + "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", required=True, help="benchmark_results CSV")
    ap.add_argument("--out-md", default=None, help="Markdown output (default: next to input)")
    ap.add_argument("--out-csv", default=None, help="Flat pivot CSV output")
    ap.add_argument("--threshold", type=float, default=0.97)
    ap.add_argument(
        "--sweep-models", nargs="*",
        default=["v11", "ex3a", "expert-a", "ex3a + expert-a", "ex3a + expert-a + expert-b2"],
    )
    args = ap.parse_args()

    inp = Path(args.input)
    rows = load_rows(inp)
    if not rows:
        raise SystemExit("No rows in input")

    data = pivot(rows, args.threshold)
    models = sort_models(list(data.keys()))

    md_parts: list[str] = []
    md_parts.append(f"# Kuule Kratt — mudelite benchmark (supervisor view)\n")
    md_parts.append(f"*Generated from `{inp.name}` ({rows[0]['timestamp']})*\n")
    md_parts.append(
        "**Protokoll**: canonical streaming FAPH via "
        "`microwakeword.test.compute_false_accepts_per_hour`, "
        "50ms moving average (5 slices @10ms), 250ms refractory, "
        "single concatenated track per FAPH set.\n"
    )
    md_parts.append(build_markdown_table(data, args.threshold, models))
    for m in args.sweep_models:
        if m in data:
            md_parts.append("")
            md_parts.append(build_threshold_sweep(rows, m, [0.5, 0.7, 0.9, 0.95, 0.97, 0.99, 0.995, 0.996, 0.999]))

    md = "\n".join(md_parts) + "\n"
    out_md = Path(args.out_md) if args.out_md else inp.parent / "supervisor_table.md"
    out_md.write_text(md)
    print(f"Wrote {out_md}")

    # Flat pivot CSV
    out_csv = Path(args.out_csv) if args.out_csv else inp.parent / "supervisor_table.csv"
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["model"] + [c[2] for c in MAIN_COLS])
        for m in models:
            row = [m]
            for ts, metric, _ in MAIN_COLS:
                v = data.get(m, {}).get((ts, metric))
                row.append(f"{v:.4f}" if v is not None else "")
            writer.writerow(row)
    print(f"Wrote {out_csv}")


if __name__ == "__main__":
    main()
