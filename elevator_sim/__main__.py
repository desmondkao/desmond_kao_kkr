"""Run a simulation: python -m elevator_sim requests.csv --floors 60 [options]"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .csv_io import load_requests, write_passengers, write_positions
from .engine import simulate
from .metrics import format_summary, summarize


def parse_express(spec: str) -> dict[int, frozenset[int]]:
    """'2,3:1,16-30' -> cars 2 and 3 stop only at floor 1 and floors 16..30."""
    cars, floors = spec.split(":")
    served = set()
    for part in floors.split(","):
        lo, _, hi = part.partition("-")
        served.update(range(int(lo), int(hi or lo) + 1))
    return {int(c): frozenset(served) for c in cars.split(",")}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="elevator_sim", description=__doc__)
    ap.add_argument("requests", type=Path, help="CSV of time,id,source,dest (header optional)")
    ap.add_argument("--floors", type=int, required=True)
    ap.add_argument("--cars", type=int, default=3)
    ap.add_argument("--capacity", type=int, default=10)
    ap.add_argument("--dispatcher", default="etd", help="etd (default), nearest, directional, zone, round-robin, etd-p<k>")
    ap.add_argument("--dwell", type=int, default=0, help="extra ticks per stop (default 0)")
    ap.add_argument("--express", type=parse_express, default={}, metavar="CARS:FLOORS",
                    help="e.g. 2,3:1,16-30 = cars 2 and 3 stop only at floor 1 and floors 16-30")
    ap.add_argument("--start-floor", type=int, default=1)
    ap.add_argument("--out", type=Path, default=Path("output"))
    args = ap.parse_args(argv)

    try:
        result = simulate(load_requests(args.requests), floors=args.floors, num_cars=args.cars,
                          capacity=args.capacity, dispatcher=args.dispatcher, dwell=args.dwell,
                          express=args.express, start_floor=args.start_floor)
    except (OSError, ValueError) as e:
        ap.error(str(e))

    args.out.mkdir(parents=True, exist_ok=True)
    write_positions(result, args.out / "positions.csv")
    write_passengers(result, args.out / "passengers.csv")
    summary = summarize(result)
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(format_summary(summary))
    print(f"\nWrote {args.out}/positions.csv, passengers.csv, summary.json")


if __name__ == "__main__":
    main()
