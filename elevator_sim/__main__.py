"""Run a simulation: python -m elevator_sim requests.csv --floors 60 [options]"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .csv_io import load_requests, write_passengers, write_positions
from .engine import Config, Simulation
from .metrics import format_summary, summarize
from .policies import LookRouter, RoundRobinDispatcher


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="elevator_sim", description=__doc__)
    ap.add_argument("requests", type=Path, help="CSV with columns time,id,source,dest")
    ap.add_argument("--floors", type=int, required=True)
    ap.add_argument("--cars", type=int, default=3)
    ap.add_argument("--capacity", type=int, default=10)
    ap.add_argument("--start-floor", type=int, default=1)
    ap.add_argument("--dwell", type=int, default=0, help="extra ticks per stop")
    ap.add_argument("--out", type=Path, default=Path("output"))
    args = ap.parse_args(argv)

    config = Config(args.floors, args.cars, args.capacity, args.start_floor, args.dwell)
    result = Simulation(config, load_requests(args.requests), RoundRobinDispatcher(), LookRouter()).run()

    args.out.mkdir(parents=True, exist_ok=True)
    write_positions(result, args.out / "positions.csv")
    write_passengers(result, args.out / "passengers.csv")
    summary = summarize(result)
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(format_summary(summary))


if __name__ == "__main__":
    main()
