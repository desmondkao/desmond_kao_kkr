"""Traffic generators for the four standard office-building patterns.

Arrivals are Poisson (exponential gaps at `rate` passengers per tick). Each
pattern is a mix of trip types:

    up-peak     morning: mostly lobby -> upper floors
    down-peak   evening: mostly upper floors -> lobby
    lunch       both directions through the lobby
    interfloor  between upper floors only

Usage: python -m elevator_sim.scenarios up-peak --floors 30 --rate 0.3 --out up.csv
"""

from __future__ import annotations

import argparse
import random

from .csv_io import write_requests
from .models import LOBBY, Request

TRIPS = {
    "up": lambda rng, floors: (LOBBY, rng.randint(2, floors)),
    "down": lambda rng, floors: (rng.randint(2, floors), LOBBY),
    "inter": lambda rng, floors: tuple(rng.sample(range(2, floors + 1), 2)),
}

SCENARIOS = {
    "up-peak": {"up": 0.85, "inter": 0.10, "down": 0.05},
    "down-peak": {"down": 0.85, "inter": 0.10, "up": 0.05},
    "lunch": {"up": 0.45, "down": 0.45, "inter": 0.10},
    "interfloor": {"inter": 1.0},
}


def generate(scenario: str, floors: int, rate: float, duration: int, seed: int) -> list[Request]:
    """Requests from t=0 to `duration`, reproducible from `seed`."""
    mix = SCENARIOS[scenario]
    rng = random.Random(seed)
    requests: list[Request] = []
    t = rng.expovariate(rate)
    while t < duration:
        kind = rng.choices(list(mix), weights=list(mix.values()))[0]
        source, dest = TRIPS[kind](rng, floors)
        requests.append(Request(int(t), f"p{len(requests)}", source, dest))
        t += rng.expovariate(rate)
    return requests


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="elevator_sim.scenarios", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenario", choices=SCENARIOS)
    ap.add_argument("--floors", type=int, default=30)
    ap.add_argument("--rate", type=float, default=0.3, help="passengers per tick")
    ap.add_argument("--duration", type=int, default=600)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    write_requests(generate(args.scenario, args.floors, args.rate, args.duration, args.seed), args.out)


if __name__ == "__main__":
    main()
