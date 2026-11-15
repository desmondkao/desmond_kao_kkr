"""Summary statistics for a finished run."""

from __future__ import annotations

import math

from .engine import Result

STATS = ("min", "mean", "p50", "p95", "max")


def percentile(values: list[int], q: float) -> int:
    """Nearest-rank percentile (always an actual observed value)."""
    s = sorted(values)
    return s[max(0, math.ceil(q / 100 * len(s)) - 1)]


def describe(values: list[int]) -> dict[str, float]:
    return dict(zip(STATS, (min(values), sum(values) / len(values),
                            percentile(values, 50), percentile(values, 95), max(values))))


def summarize(result: Result) -> dict:
    ps = result.passengers
    totals = [p.total_time for p in ps]
    ideal = [p.req.distance for p in ps]
    return {
        "passengers": len(ps),
        "end_time": result.end_time,
        "wait": describe([p.wait_time for p in ps]),
        "travel": describe([p.travel_time for p in ps]),
        "total": describe(totals),
        # No scheduler can beat |dest - source| for anyone, so this ratio is >= 1.
        "total_vs_ideal": sum(totals) / sum(ideal),
    }


def format_summary(s: dict) -> str:
    lines = [f"{s['passengers']} passengers, finished at t={s['end_time']}",
             f"{'':>8}" + "".join(f"{k:>8}" for k in STATS)]
    for key in ("wait", "travel", "total"):
        lines.append(f"{key:>8}" + "".join(f"{s[key][k]:>8.1f}" for k in STATS))
    lines.append(f"total time / ideal time = {s['total_vs_ideal']:.3f}  (1.000 is perfect)")
    return "\n".join(lines)
