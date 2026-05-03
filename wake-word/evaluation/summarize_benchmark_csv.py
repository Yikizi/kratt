#!/usr/bin/env python3
"""Create a compact Markdown summary from benchmark_all_models.py CSV output."""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

KEY_SETS = [
    "pos_isa_xtts",
    "pos_ode",
    "pos_mattias_short",
    "pos_friend1",
    "hard_neg_mac_holdout",
    "hard_neg_isa_xtts",
    "hard_neg_canary",
    "neg_prefix_only_mattias_short",
    "neg_single_kratt_neurokone",
    "neg_reversed_kratt_kuule",
    "neg_kuule_kule_confusables",
    "faph_cv_et",
    "faph_librispeech",
    "faph_macbook_bg",
    "faph_dipco",
]

DISPLAY = {
    "pos_isa_xtts": "recall isa XTTS",
    "pos_ode": "recall Ode",
    "pos_mattias_short": "recall Mattias short",
    "pos_friend1": "recall friend1",
    "hard_neg_mac_holdout": "HN Mac FPR",
    "hard_neg_isa_xtts": "HN Isa FPR",
    "hard_neg_canary": "HN canary FPR",
    "neg_prefix_only_mattias_short": "prefix-only FPR",
    "neg_single_kratt_neurokone": "single Kratt FPR",
    "neg_reversed_kratt_kuule": "reversed Kratt-kuule FPR",
    "neg_kuule_kule_confusables": "kuule/kule confusable FPR",
    "faph_cv_et": "FAPH CV ET",
    "faph_librispeech": "FAPH LibriSpeech",
    "faph_macbook_bg": "FAPH Mac bg",
    "faph_dipco": "FAPH DiPCo",
}


def fmt(test_set: str, value: str | None) -> str:
    if value is None:
        return ""
    v = float(value)
    if test_set.startswith("faph_"):
        return f"{v:.2f}"
    return f"{100.0 * v:.1f}%"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv_path", type=Path)
    ap.add_argument("--threshold", type=float, default=0.995)
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()

    rows = list(csv.DictReader(args.csv_path.open()))
    # Preserve CSV model order for the chosen threshold.
    models: list[str] = []
    values: dict[tuple[str, str], str] = {}
    ns: dict[str, str] = {}
    durations: dict[str, str] = {}
    target_t = f"{args.threshold:.3f}".rstrip("0").rstrip(".")
    for r in rows:
        if abs(float(r["threshold"]) - args.threshold) > 1e-9:
            continue
        model = r["model"]
        if model not in models:
            models.append(model)
        test_set = r["test_set"]
        values[(model, test_set)] = r["value"]
        ns[test_set] = r.get("n", "")
        durations[test_set] = r.get("duration_h", "")

    out = args.output or args.csv_path.with_suffix(".md")
    lines: list[str] = []
    lines.append(f"# v18 clean benchmark summary")
    lines.append("")
    lines.append(f"Source CSV: `{args.csv_path.name}`")
    lines.append(f"Threshold: `{args.threshold}`")
    lines.append("")
    lines.append("Lower is better for FPR/FAPH; higher is better for recall.")
    lines.append("")

    header = ["model"] + [DISPLAY[s] for s in KEY_SETS]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    for model in models:
        cells = [model]
        for s in KEY_SETS:
            cells.append(fmt(s, values.get((model, s))))
        lines.append("| " + " | ".join(cells) + " |")

    lines.append("")
    lines.append("## Test-set sizes")
    lines.append("")
    lines.append("| test_set | n | duration_h |")
    lines.append("|---|---:|---:|")
    for s in KEY_SETS:
        if s in ns:
            lines.append(f"| {s} | {ns.get(s, '')} | {durations.get(s, '')} |")

    out.write_text("\n".join(lines) + "\n")
    print(out)


if __name__ == "__main__":
    main()
