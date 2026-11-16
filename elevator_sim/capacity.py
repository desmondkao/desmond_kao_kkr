"""How do the dispatchers compare across building sizes?

    python -m elevator_sim.capacity    # -> results/capacity_dwell{0,1}.md and .csv (about 30 min)

A fixed arrival rate can't be compared across buildings: 0.8 passengers per
tick swamps 2 cars in 30 floors but barely loads 8. So, for each building:

1. Handling capacity: the highest arrival rate each dispatcher sustains before
   its queue grows (found by bisection). This is the number elevator
   engineers size buildings by.
2. Trip times at half of that building's capacity (the best capacity any
   dispatcher reached), so every building is equally busy.
"""

from __future__ import annotations

import argparse
import csv
import statistics
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

from .benchmark import Experiment, run
from .dispatch import make_dispatcher
from .engine import Config, Simulation
from .scenarios import generate

BUILDINGS = {
    "10 floors, 4 cars": Config(10, 4, 10),
    "30 floors, 2 cars": Config(30, 2, 10),
    "30 floors, 4 cars": Config(30, 4, 10),
    "30 floors, 8 cars": Config(30, 8, 10),
    "60 floors, 4 cars": Config(60, 4, 10),
    "60 floors, 8 cars": Config(60, 8, 10),
}
DISPATCHERS = ("round-robin", "nearest", "directional", "zone", "etd")
SCENARIOS = ("up-peak", "lunch")
FRACTION = 0.5  # an ordinary busy day; the capacity table covers heavy load


def keeps_up(config: Config, scenario: str, dispatcher: str, rate: float, seeds: int, duration: int) -> bool:
    """True if the number of people in the building (waiting or riding) is not growing.

    Compares the average over the last third of the arrival period with the middle
    third. The first third is skipped: cars start empty at the lobby.
    """
    middle = last = 0.0
    for seed in range(seeds):
        result = Simulation(config, generate(scenario, config.floors, rate, duration, seed),
                            make_dispatcher(dispatcher, config.floors)).run()
        in_system = [0] * (duration + 1)
        for p in result.passengers:
            for t in range(p.request.time, min(p.dropoff_time, duration + 1)):
                in_system[t] += 1
        third = duration // 3
        middle += statistics.mean(in_system[third:2 * third])
        last += statistics.mean(in_system[2 * third:3 * third])
    return last <= 1.2 * middle + seeds  # +1 person per seed: slack for nearly empty buildings


def handling_capacity(config: Config, scenario: str, dispatcher: str, seeds: int = 3, duration: int = 1200,
                      steps: int = 4) -> float:
    """Highest sustainable arrival rate, to within about 1.5%.

    Steps up by 25% until the queue grows, then bisects. Small steps matter:
    a heavily overloaded run is slow, because ETD forecasts get long.
    """
    lo, hi = 0.0, 0.05
    while keeps_up(config, scenario, dispatcher, hi, seeds, duration):
        lo, hi = hi, hi * 1.25
    for _ in range(steps):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if keeps_up(config, scenario, dispatcher, mid, seeds, duration) else (lo, mid)
    return lo


def _capacity_task(task):
    building, scenario, dispatcher, dwell = task
    config = replace(BUILDINGS[building], dwell=dwell)
    return task, handling_capacity(config, scenario, dispatcher)


def report(dwell: int, seeds: int, duration: int, pool: ProcessPoolExecutor, out: Path) -> None:
    tasks = [(b, s, d, dwell) for b in BUILDINGS for s in SCENARIOS for d in DISPATCHERS]
    cap = {task[:3]: value for task, value in pool.map(_capacity_task, tasks)}
    with open(out / f"capacity_dwell{dwell}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["building", "scenario", "dispatcher", "capacity"])
        writer.writerows([*key, round(value, 4)] for key, value in cap.items())

    lines = [f"# capacity_dwell{dwell}", "", "\n\n".join(__doc__.split("\n\n")[2:4]).strip(), "",
             f"Dwell {dwell}. Capacity in passengers per tick (3 seeds x {duration} ticks per test).", "",
             "| building | scenario | " + " | ".join(DISPATCHERS) + " | ETD vs best other |",
             "|---|---|" + "---|" * (len(DISPATCHERS) + 1)]
    for b in BUILDINGS:
        for s in SCENARIOS:
            values = [cap[(b, s, d)] for d in DISPATCHERS]
            best_other = max(cap[(b, s, d)] for d in DISPATCHERS if d != "etd")
            lines.append(f"| {b} | {s} | " + " | ".join(f"{v:.2f}" for v in values)
                         + f" | {cap[(b, s, 'etd')] / best_other - 1:+.0%} |")

    lines += ["", f"Mean total time in ticks at half of the building's capacity "
                  f"({seeds} seeds x {duration} ticks, ± 95% CI).", "",
              "| building | scenario | arrivals | " + " | ".join(DISPATCHERS) + " |",
              "|---|---|---|" + "---|" * len(DISPATCHERS)]
    jobs = []
    for b in BUILDINGS:
        for s in SCENARIOS:
            best = max(cap[(b, s, d)] for d in DISPATCHERS)
            exp = Experiment("", {b: replace(BUILDINGS[b], dwell=dwell)}, DISPATCHERS, scenarios=(s,),
                             rates=(round(FRACTION * best, 3),))
            jobs.append((b, s, pool.submit(run, exp, seeds, duration)))
    for b, s, job in jobs:
        rows = job.result()
        by = {r["dispatcher"]: r for r in rows}
        win = min(DISPATCHERS, key=lambda d: by[d]["total_mean"])
        cells = [(f"**{by[d]['total_mean']:.1f}**" if d == win else f"{by[d]['total_mean']:.1f}")
                 + f" ±{by[d]['total_ci95']:.1f}" for d in DISPATCHERS]
        lines.append(f"| {b} | {s} | {rows[0]['rate']:.2f}/tick | " + " | ".join(cells) + " |")
    (out / f"capacity_dwell{dwell}.md").write_text("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="elevator_sim.capacity", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--duration", type=int, default=1200)
    ap.add_argument("--out", type=Path, default=Path("results"))
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor() as pool:
        for dwell in (0, 1):
            report(dwell, args.seeds, args.duration, pool, args.out)
            print(f"wrote {args.out}/capacity_dwell{dwell}.md")


if __name__ == "__main__":
    main()
