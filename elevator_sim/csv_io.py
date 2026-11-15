"""CSV input and output."""

from __future__ import annotations

import csv
from pathlib import Path

from .engine import Result
from .models import Request


def load_requests(path: str | Path) -> list[Request]:
    """Read `time,id,source,dest` rows; errors name the offending line."""
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f, skipinitialspace=True))
    requests = []
    for line, row in enumerate(rows, start=2):
        try:
            requests.append(Request(int(row["time"]), row["id"].strip(), int(row["source"]), int(row["dest"])))
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            raise ValueError(f"{path}:{line}: bad row {row} ({e})") from None
    return requests


def write_requests(requests: list[Request], path: str | Path) -> None:
    _write(path, ["time", "id", "source", "dest"], ([r.time, r.id, r.source, r.dest] for r in requests))


def write_positions(result: Result, path: str | Path) -> None:
    """The required log: one row per tick with every car's floor."""
    header = ["time"] + [f"car_{i}" for i in range(result.config.num_cars)]
    _write(path, header, ([t, *floors] for t, floors in enumerate(result.positions)))


def write_passengers(result: Result, path: str | Path) -> None:
    header = ["id", "car", "request_time", "source", "dest", "board_time", "dropoff_time",
              "wait", "travel", "total", "ideal"]
    _write(path, header, ([p.request.id, p.car_id, p.request.time, p.source, p.dest, p.board_time, p.dropoff_time,
                           p.wait_time, p.travel_time, p.total_time, p.request.distance] for p in result.passengers))


def _write(path, header, rows) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
