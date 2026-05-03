"""Wilson score 95% CIs for proportions.

Used to annotate small-N recall and FPR cells in the thesis Results chapter
(`docs/thesis/thesis-tex-estonian/chapters/second_chapter.tex`). The Wilson
interval is preferred over the normal approximation because the small recall
denominators in this work (Isa XTTS N=48, Ode N=11, Mac hard-neg N=15) push
the proportion close to 0 or 1, where the normal approximation breaks down.
"""

from __future__ import annotations

import math
import sys


def wilson_ci(successes: int, trials: int, confidence: float = 0.95) -> tuple[float, float]:
    """Return (lower, upper) Wilson score interval as proportions in [0, 1].

    Raises ValueError if `trials` is not strictly positive.
    """
    if trials <= 0:
        raise ValueError("trials must be > 0")
    if successes < 0 or successes > trials:
        raise ValueError(f"successes={successes} out of [0, trials={trials}]")
    # z is the inverse CDF of the standard normal at (1 + confidence) / 2.
    # We avoid scipy here so the helper has no heavy dep.
    if abs(confidence - 0.95) < 1e-9:
        z = 1.959963984540054
    elif abs(confidence - 0.99) < 1e-9:
        z = 2.5758293035489004
    elif abs(confidence - 0.90) < 1e-9:
        z = 1.6448536269514722
    else:
        # Fall back to scipy for non-standard confidences.
        from scipy.stats import norm  # type: ignore
        z = float(norm.ppf((1 + confidence) / 2))

    p = successes / trials
    denom = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denom
    margin = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denom
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    return (lower, upper)


def format_recall_with_ci(
    successes: int,
    trials: int,
    *,
    percent: bool = True,
    decimals: int = 1,
    confidence: float = 0.95,
    locale: str = "en",
) -> str:
    """Return a LaTeX-paste string with the point estimate and Wilson CI.

    locale="en" (default) uses the dot decimal and comma separator, matching
    earlier callers: ``91.7\\% [80.5, 96.7]``.

    locale="et" uses the Estonian comma decimal and an en-dash separator,
    matching the thesis convention: ``91,7\\% [80,5--96,7]``.
    """
    if locale not in {"en", "et"}:
        raise ValueError(f"locale must be 'en' or 'et', got {locale!r}")

    lo, hi = wilson_ci(successes, trials, confidence=confidence)
    if percent:
        point = successes / trials * 100 if trials else 0.0
        point_s = f"{point:.{decimals}f}"
        lo_s = f"{lo*100:.{decimals}f}"
        hi_s = f"{hi*100:.{decimals}f}"
    else:
        point = successes / trials if trials else 0.0
        point_s = f"{point:.{decimals+2}f}"
        lo_s = f"{lo:.{decimals+2}f}"
        hi_s = f"{hi:.{decimals+2}f}"

    if locale == "et":
        point_s = point_s.replace(".", ",")
        lo_s = lo_s.replace(".", ",")
        hi_s = hi_s.replace(".", ",")
        sep = "--"
    else:
        sep = ", "

    if percent:
        return f"{point_s}\\% [{lo_s}{sep}{hi_s}]"
    return f"{point_s} [{lo_s}{sep}{hi_s}]"


def _main(argv: list[str]) -> int:
    # Parse from sys.argv directly (no argparse), per thesis CLI conventions.
    args = list(argv[1:])
    locale = "en"
    filtered: list[str] = []
    for a in args:
        if a in {"-h", "--help"}:
            prog = argv[0] if argv else "wilson_ci"
            print(
                f"usage: {prog} <successes> <trials> [confidence] [--locale=et|en]",
                file=sys.stderr,
            )
            return 2
        if a.startswith("--locale="):
            locale = a.split("=", 1)[1]
        else:
            filtered.append(a)

    if len(filtered) < 2:
        prog = argv[0] if argv else "wilson_ci"
        print(
            f"usage: {prog} <successes> <trials> [confidence] [--locale=et|en]",
            file=sys.stderr,
        )
        return 2
    successes = int(filtered[0])
    trials = int(filtered[1])
    confidence = float(filtered[2]) if len(filtered) >= 3 else 0.95
    print(format_recall_with_ci(successes, trials, confidence=confidence, locale=locale))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
