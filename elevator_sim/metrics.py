"""Summary statistics for a finished run."""

from __future__ import annotations

import math
from collections import Counter

from .engine import Result

STATS = ("min", "mean", "p50", "p95", "max")


def percentile(values: list[int], q: float) -> int:
    """Nearest-rank percentile (always an actual observed value)."""
    s = sorted(values)
    return s[max(0, math.ceil(q / 100 * len(s)) - 1)]


def describe(values: list[int]) -> dict[str, float]:
    return {
        "min": min(values),
        "mean": sum(values) / len(values),
        "p50": percentile(values, 50),
        "p95": percentile(values, 95),
        "max": max(values),
    }


def summarize(result: Result) -> dict:
    ps = result.passengers
    if not ps:
        return {"passengers": 0, "end_time": result.end_time}
    totals = [p.total_time for p in ps]
    slowest = max(ps, key=lambda p: p.total_time)
    return {
        "passengers": len(ps),
        "end_time": result.end_time,
        "wait": describe([p.wait_time for p in ps]),
        "travel": describe([p.travel_time for p in ps]),
        "total": describe(totals),
        # No scheduler can beat |dest - source| for anyone, so this ratio is >= 1.
        "total_vs_ideal": sum(totals) / sum(p.request.distance for p in ps),
        "per_car": dict(sorted(Counter(p.car_id for p in ps).items())),
        "slowest": {"id": slowest.request.id, "total": slowest.total_time, "wait": slowest.wait_time},
    }


def format_summary(s: dict) -> str:
    if not s["passengers"]:
        return "no passengers"
    lines = [f"{s['passengers']} passengers, finished at t={s['end_time']}",
             f"{'':>8}" + "".join(f"{k:>8}" for k in STATS)]
    for key in ("wait", "travel", "total"):
        lines.append(f"{key:>8}" + "".join(f"{s[key][k]:>8.1f}" for k in STATS))
    lines += [
        f"total time / ideal time: {s['total_vs_ideal']:.2f}  (1.00 = nobody waited and every ride was direct)",
        f"passengers per car: {s['per_car']}",
        f"slowest: {s['slowest']['id']} (total {s['slowest']['total']}, of which waiting {s['slowest']['wait']})",
    ]
    return "\n".join(lines)
