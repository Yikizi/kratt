"""Generate thesis Results-chapter figures.

Each figure backs a specific thesis subsection in
`docs/thesis/thesis-tex-estonian/chapters/second_chapter.tex`:

- `model_lineage_timeline.pdf` -> `\\subsection{Mudeliversioonid}`. Compact
  visual summary of the main model-lineage milestones so the Results chapter
  does not read like a chronological experiment diary.
- `faph_recall_pareto.pdf` -> `\\subsection{Õiglane võrdlus identsete
  hindamiskomplektidega}`. Single-threshold operating-point scatter of (FAPH on
  faph_cv_et, recall on pos_isa_xtts) at threshold 0.995 across all benchmarked
  single models, with the lower-left envelope highlighted. Note: the highlighted
  curve is the lower-left envelope at this single threshold — NOT a
  threshold-independent Pareto frontier.
- `det_v6_v15_v16c_expertA.pdf` -> `\\subsection{Sihipäraselt projekteeritud
  ekspertmudelite konsensus}`. DET-style FRR vs FA/h on log-log axes for the
  four model families that motivated the consensus argument. FRR is pooled over
  the verifiably-disjoint unseen-positive sets (`pos_isa_xtts` + `pos_ode`).

The script is idempotent — running it overwrites the PDFs.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from test_sets import TEST_SETS, assert_disjoint_from_training  # noqa: E402

# Repo-relative paths. This file lives at wake-word/evaluation/.
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[2]
ARTIFACTS_DIR = REPO_ROOT / "docs" / "research" / "artifacts" / "wake-word-evaluation-2026-04"
EVAL_DIR = REPO_ROOT / "wake-word" / "evaluation"
FIG_DIR = REPO_ROOT / "docs" / "thesis" / "thesis-tex-estonian" / "figures"

# A5-friendly width: 12 cm at 300 DPI.
CM_TO_INCH = 1 / 2.54
FIG_WIDTH_IN = 12 * CM_TO_INCH

THRESHOLD = 0.995
SUPERVISOR_CSV = ARTIFACTS_DIR / "benchmark_results_supervisor.csv"
DET_POOLED_JSON = EVAL_DIR / "det_curves_20260423_pooled.json"

# Models whose DET curves are shown in the figure; each must be verifiably
# disjoint from BOTH unseen-positive sets used to pool FRR.
DET_MODELS = ("v6-residual", "v15", "v16c", "expert-a")
DET_POSITIVE_SETS = ("pos_isa_xtts", "pos_ode_real")

# Clip the Pareto x-axis so outliers (e.g. expert-b ~ 8766 FAPH) do not drag
# the frame; documented in the caption.
PARETO_FAPH_MAX = 1000.0


def _plot_timeline() -> Path:
    """Render a compact, thesis-facing model lineage timeline.

    The timeline is intentionally milestone-based rather than proportional to
    calendar time: several decisive events happened within a few April days and
    would overlap on a strict date axis.
    """
    milestones = [
        {
            "date": "19.03",
            "title": "v1–v2",
            "body": "esimene\näratussõna mudel",
            "color": "#6c757d",
        },
        {
            "date": "21.03",
            "title": "v3–v6",
            "body": "sama-seadme negatiivid\nja TTS-laiendus",
            "color": "#1f77b4",
        },
        {
            "date": "12.–14.04",
            "title": "v6-res. / v16c",
            "body": "residuaalühendused;\nstabiilne üksikmudel",
            "color": "#2ca02c",
        },
        {
            "date": "21.04",
            "title": "ühtne hindamine",
            "body": "kõrvalejäetud komplektid\nja voogedastus-FAPH",
            "color": "#9467bd",
        },
        {
            "date": "22.–24.04",
            "title": "expert A+B2",
            "body": "madal FAPH\nkonsensusena",
            "color": "#17a2b8",
        },
        {
            "date": "26.–28.04",
            "title": "v17 → v18",
            "body": "positiivse klassi\nkvaliteedikontroll",
            "color": "#d62728",
        },
        {
            "date": "28.–29.04",
            "title": "checkpoint-FAPH",
            "body": "ühe mõõdiku siht\nei säilita recall'i",
            "color": "#ff7f0e",
        },
    ]

    fig, ax = plt.subplots(figsize=(FIG_WIDTH_IN, FIG_WIDTH_IN * 0.58), dpi=300)
    ax.set_xlim(-0.35, len(milestones) - 0.65)
    ax.set_ylim(-1.2, 1.25)
    ax.axis("off")

    xs = list(range(len(milestones)))
    ax.hlines(0, xs[0], xs[-1], color="#adb5bd", linewidth=1.2, zorder=1)

    for idx, item in enumerate(milestones):
        x = xs[idx]
        y = 0.66 if idx % 2 == 0 else -0.66
        va = "bottom" if y > 0 else "top"
        ax.vlines(x, 0, y * 0.72, color=item["color"], linewidth=1.0, zorder=2)
        ax.scatter([x], [0], s=42, color=item["color"], edgecolor="white", linewidth=0.8, zorder=3)
        ax.text(
            x,
            y,
            f"{item['title']}\n{item['body']}",
            ha="center",
            va=va,
            fontsize=6.8,
            linespacing=1.1,
            color="#212529",
        )
        ax.text(
            x,
            -0.18 if y > 0 else 0.18,
            item["date"],
            ha="center",
            va="top" if y > 0 else "bottom",
            fontsize=6.2,
            color="#6c757d",
        )

    ax.text(
        xs[0],
        1.1,
        "Mudelipõlvkondade põhiverstapostid",
        ha="left",
        va="center",
        fontsize=9,
        weight="bold",
        color="#212529",
    )
    ax.text(
        xs[-1],
        -1.05,
        "Joonis koondab metoodiliselt olulised pöördekohad; see ei ole täielik mudeliregister.",
        ha="right",
        va="center",
        fontsize=6.2,
        color="#6c757d",
    )

    out = FIG_DIR / "model_lineage_timeline.pdf"
    fig.tight_layout(pad=0.2)
    fig.savefig(out, format="pdf")
    plt.close(fig)
    return out


def _ensure_input(path: Path) -> Path:
    if not path.exists():
        raise RuntimeError(
            f"Required input file is missing: {path}. Generate it before "
            f"running this script (see docs/research/wake-word-evaluation-methodology.md)."
        )
    return path


def _load_supervisor_pairs() -> dict[str, dict[str, float]]:
    """Return {model: {'faph': x, 'recall': y}} for threshold 0.995, single models only."""
    _ensure_input(SUPERVISOR_CSV)
    by_model: dict[str, dict[str, float]] = defaultdict(dict)
    with SUPERVISOR_CSV.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["threshold"] != str(THRESHOLD):
                continue
            model = row["model"]
            # Skip multi-model consensus rows for the single-model scatter.
            if "+" in model:
                continue
            metric = row["metric"]
            test_set = row["test_set"]
            value = float(row["value"])
            if metric == "faph" and test_set == "faph_cv_et":
                by_model[model]["faph"] = value
            elif metric == "recall" and test_set == "pos_isa_xtts":
                by_model[model]["recall"] = value
    return {m: d for m, d in by_model.items() if "faph" in d and "recall" in d}


def _lower_left_envelope(
    points: list[tuple[float, float, str]],
) -> list[tuple[float, float, str]]:
    """Return the lower-left envelope: minimise x (FAPH), maximise y (recall).

    NOT a threshold-independent Pareto frontier — these are operating points at
    a single threshold (theta=0.995). The envelope depends on threshold choice.
    """
    sorted_pts = sorted(points, key=lambda p: (p[0], -p[1]))
    envelope: list[tuple[float, float, str]] = []
    best_y = -1.0
    for x, y, label in sorted_pts:
        if y > best_y:
            envelope.append((x, y, label))
            best_y = y
    return envelope


def _plot_pareto() -> Path:
    pairs = _load_supervisor_pairs()
    points = [(d["faph"], d["recall"], m) for m, d in pairs.items()]
    if not points:
        raise RuntimeError(
            f"No (faph, recall) pairs at threshold {THRESHOLD} in {SUPERVISOR_CSV}."
        )
    # Clip outliers to keep the frame readable; caption documents the cutoff.
    visible_points = [(x, y, lab) for x, y, lab in points if x < PARETO_FAPH_MAX]
    envelope = _lower_left_envelope(visible_points)

    highlight_models = {"v6", "v6-residual", "v7", "v15", "v16c", "expert-a"}

    fig, ax = plt.subplots(figsize=(FIG_WIDTH_IN, FIG_WIDTH_IN * 0.75), dpi=300)
    xs, ys = zip(*[(x, y * 100) for x, y, _ in visible_points])
    ax.scatter(xs, ys, s=22, color="#888888", alpha=0.7, label="Üksikmudelid")

    env_xs, env_ys, _env_labels = zip(*[(x, y * 100, lab) for x, y, lab in envelope])
    ax.plot(
        env_xs,
        env_ys,
        "-o",
        color="#c0392b",
        markersize=5,
        linewidth=1.2,
        label="Alumise-vasakpoolne mähis",
    )

    for x, y, lab in visible_points:
        if lab in highlight_models:
            ax.annotate(lab, (x, y * 100), xytext=(4, 4), textcoords="offset points", fontsize=7)

    ax.set_xscale("log")
    ax.set_xlim(right=PARETO_FAPH_MAX)
    ax.set_xlabel("Streaming-FAPH (CV ET hold-out, 3,82 h koos vahedega)")
    ax.set_ylabel("Recall, Isa XTTS (%, N=48)")
    ax.set_title(
        f"FAPH-recall'i operatsioonipunktid lävel {str(THRESHOLD).replace('.', ',')}"
    )
    ax.grid(True, which="both", linestyle=":", linewidth=0.5)
    ax.legend(loc="lower right", fontsize=8, frameon=False)

    out = FIG_DIR / "faph_recall_pareto.pdf"
    fig.tight_layout()
    fig.savefig(out, format="pdf")
    plt.close(fig)
    return out


def _verify_det_disjointness() -> None:
    """Tripwire: each DET model must be verifiably disjoint from each pooled
    positive set. Raise RuntimeError naming the offending model + set on failure.
    """
    for model in DET_MODELS:
        for set_name in DET_POSITIVE_SETS:
            try:
                ts = TEST_SETS[set_name]
            except KeyError as exc:
                raise RuntimeError(
                    f"DET disjointness check: unknown test set {set_name!r}."
                ) from exc
            try:
                assert_disjoint_from_training(ts, model)
            except AssertionError as exc:
                raise RuntimeError(
                    f"DET disjointness check failed: model={model!r} is not "
                    f"verifiably disjoint from positive set {set_name!r}: {exc}"
                ) from exc


def _plot_det() -> Path:
    _ensure_input(DET_POOLED_JSON)
    _verify_det_disjointness()
    with DET_POOLED_JSON.open() as f:
        data = json.load(f)
    targets = list(DET_MODELS)
    missing = [t for t in targets if t not in data]
    if missing:
        raise RuntimeError(
            f"DET pooled JSON {DET_POOLED_JSON} is missing required models: {missing}. "
            f"Run a pooled threshold sweep that covers them before generating this figure."
        )

    fig, ax = plt.subplots(figsize=(FIG_WIDTH_IN, FIG_WIDTH_IN * 0.75), dpi=300)
    palette = {"v6-residual": "#1f77b4", "v15": "#2ca02c", "v16c": "#d62728", "expert-a": "#9467bd"}

    for model in targets:
        rec = data[model]
        faph = rec["faph"]
        # Pooled FRR over pos_isa_xtts (N=48) + pos_ode_real (N=11) only.
        # If the JSON carries the precomputed disjoint-pool key, use it.
        # Otherwise compute the weighted pool on-the-fly from frr_per_set so
        # the rendered curve matches the caption's N=59 claim.
        # The contaminated 421-clip "frr_pooled" pool is NEVER used here.
        if "frr_pooled_isa_ode" in rec:
            frr = rec["frr_pooled_isa_ode"]
        elif (
            "frr_per_set" in rec
            and "isa_xtts" in rec["frr_per_set"]
            and "ode_real" in rec["frr_per_set"]
        ):
            isa = rec["frr_per_set"]["isa_xtts"]
            ode = rec["frr_per_set"]["ode_real"]
            n_isa, n_ode = 48, 11
            n_total = n_isa + n_ode  # 59
            if len(isa) != len(ode):
                raise RuntimeError(
                    f"DET pool requires aligned per-set FRR arrays for {model}; "
                    f"got len(isa_xtts)={len(isa)} vs len(ode_real)={len(ode)}."
                )
            frr = [(n_isa * a + n_ode * b) / n_total for a, b in zip(isa, ode)]
        else:
            raise RuntimeError(
                f"DET pool requires disjoint per-set FRR for {model}; "
                f"regenerate det_curves_*.json with frr_per_set populated for "
                f"pos_isa_xtts and pos_ode_real"
            )
        # Drop entries with FAPH or FRR == 0 since log scale cannot show them.
        xy = [(fa, fr * 100) for fa, fr in zip(faph, frr) if fa > 0 and fr > 0]
        if not xy:
            continue
        xs, ys = zip(*xy)
        ax.plot(xs, ys, label=model, color=palette[model], linewidth=1.4)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Valeaktiveeringud tunnis (FA/h, CV ET)")
    ax.set_ylabel("FRR (%) — pos\\_isa\\_xtts ja pos\\_ode agregeeritult")
    ax.set_title("DET-tüüpi kõverad nelja mudeliperekonna kohta")
    ax.grid(True, which="both", linestyle=":", linewidth=0.5)
    ax.legend(loc="lower left", fontsize=8, frameon=False)

    out = FIG_DIR / "det_v6_v15_v16c_expertA.pdf"
    fig.tight_layout()
    fig.savefig(out, format="pdf")
    plt.close(fig)
    return out


def main() -> int:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    produced: list[Path] = []
    errors: list[str] = []
    for fn, name in [
        (_plot_timeline, "timeline"),
        (_plot_pareto, "pareto"),
        (_plot_det, "DET"),
    ]:
        try:
            produced.append(fn())
        except RuntimeError as exc:
            errors.append(f"[{name}] {exc}")

    for p in produced:
        print(f"wrote {p}")
    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
