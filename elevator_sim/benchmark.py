"""Reproduce every experiment in the README: python -m elevator_sim.benchmark [names...]

Each experiment runs building x scenario x load x seed x dispatcher. All
dispatchers see identical request lists (same seeds), so differences come from
the algorithms alone. Writes results/<name>.md: means over seeds, with a 95%
confidence interval on the mean total time (and the same rows as <name>.csv).
"""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from dataclasses import dataclass, replace
from pathlib import Path

from .dispatch import make_dispatcher
from .engine import Config, Simulation
from .metrics import summarize
from .scenarios import SCENARIOS, generate

STANDARD = Config(floors=30, num_cars=4, capacity=10)
UPPER_EXPRESS = frozenset({1, *range(16, 31)})
EXPRESS = replace(STANDARD, express={2: UPPER_EXPRESS, 3: UPPER_EXPRESS})


@dataclass(frozen=True)
class Experiment:
    question: str
    buildings: dict[str, Config]
    dispatchers: tuple[str, ...]
    scenarios: tuple[str, ...] = tuple(SCENARIOS)
    rates: tuple[float, ...] = (0.4, 0.8)  # passengers per tick; up-peak saturates near 1.0

    def with_dwell(self, dwell: int) -> Experiment:
        return replace(self, buildings={k: replace(c, dwell=dwell) for k, c in self.buildings.items()})


BASE = {
    "algorithms": Experiment("Which dispatcher works best?",
                             {"standard": STANDARD}, ("round-robin", "nearest", "directional", "zone", "etd")),
    "fairness": Experiment("How does ETD's cost exponent trade average time against the worst case?",
                           {"standard": STANDARD}, ("etd-p1", "etd-p2", "etd-p4"), rates=(0.8,)),
    "express": Experiment("Do express cars (2 of 4 serve only the lobby and floors 16-30) help?",
                          {"standard": STANDARD, "express": EXPRESS}, ("zone", "etd"),
                          scenarios=("up-peak", "lunch")),
}
EXPERIMENTS = {f"{name}_dwell{dwell}": exp.with_dwell(dwell) for dwell in (0, 1) for name, exp in BASE.items()}

COLUMNS = ("wait_mean", "total_mean", "total_ci95", "total_p95", "total_max", "vs_ideal")


def run(exp: Experiment, seeds: int, duration: int) -> list[dict]:
    """One row per (building, scenario, rate, dispatcher), averaged over seeds."""
    runs: dict[tuple, list[dict]] = defaultdict(list)
    for building, config in exp.buildings.items():
        for scenario in exp.scenarios:
            for rate in exp.rates:
                for seed in range(seeds):
                    requests = generate(scenario, config.floors, rate, duration, seed)
                    for name in exp.dispatchers:
                        result = Simulation(config, requests, make_dispatcher(name, config.floors)).run()
                        runs[(building, scenario, rate, name)].append(summarize(result))
    rows = []
    for (building, scenario, rate, name), summaries in runs.items():
        means = [s["total"]["mean"] for s in summaries]
        rows.append({
            "building": building, "scenario": scenario, "rate": rate, "dispatcher": name,
            "wait_mean": statistics.mean(s["wait"]["mean"] for s in summaries),
            "total_mean": statistics.mean(means),
            "total_ci95": 1.96 * statistics.stdev(means) / len(means) ** 0.5 if len(means) > 1 else 0.0,
            "total_p95": statistics.mean(s["total"]["p95"] for s in summaries),
            "total_max": statistics.mean(s["total"]["max"] for s in summaries),
            "vs_ideal": statistics.mean(s["total_vs_ideal"] for s in summaries),
        })
    return rows


def to_markdown(rows: list[dict]) -> str:
    keys = [k for k in rows[0] if k not in COLUMNS]
    lines = ["| " + " | ".join(keys + list(COLUMNS)) + " |", "|" + "---|" * len(rows[0])]
    for row in rows:
        cells = [str(row[k]) for k in keys]
        for c in COLUMNS:
            fmt = ".2f" if c == "vs_ideal" else ".1f"
            cells.append(f"±{row[c]:{fmt}}" if c == "total_ci95" else f"{row[c]:{fmt}}")
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="elevator_sim.benchmark", description=__doc__)
    ap.add_argument("names", nargs="*", help=f"experiments to run (default: all): {', '.join(EXPERIMENTS)}")
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--duration", type=int, default=1200, help="ticks of arrivals per run")
    ap.add_argument("--out", type=Path, default=Path("results"))
    args = ap.parse_args(argv)
    if unknown := set(args.names) - set(EXPERIMENTS):
        ap.error(f"unknown experiments: {sorted(unknown)}")

    args.out.mkdir(parents=True, exist_ok=True)
    for name in args.names or EXPERIMENTS:
        exp = EXPERIMENTS[name]
        rows = run(exp, args.seeds, args.duration)
        with open(args.out / f"{name}.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        table = to_markdown(rows)
        (args.out / f"{name}.md").write_text(
            f"# {name}\n\n{exp.question}\n\n{args.seeds} seeds x {args.duration} ticks of arrivals. "
            "Times in ticks.\n\n" + table + "\n")
        print(f"wrote {args.out / name}.md")


if __name__ == "__main__":
    main()
