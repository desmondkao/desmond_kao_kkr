"""CSV input and output."""

from __future__ import annotations

import csv
from pathlib import Path

from .engine import Result
from .models import Request

COLUMNS = ("time", "id", "source", "dest")


def load_requests(path: str | Path) -> list[Request]:
    """Read a CSV whose first line is `time,id,source,dest`. Errors name the line."""
    with open(path, newline="") as f:
        reader = csv.reader(f, skipinitialspace=True)
        if next(reader, None) != list(COLUMNS):
            raise ValueError(f"{path}: the first line must be {','.join(COLUMNS)}")
        requests = []
        for line, row in enumerate(reader, start=2):
            if not row:
                continue
            try:
                time, id_, source, dest = row
                requests.append(Request(int(time), id_, int(source), int(dest)))
            except ValueError:
                raise ValueError(f"{path}:{line}: expected time,id,source,dest as numbers, got {row}") from None
    return requests


def write_requests(requests: list[Request], path: str | Path) -> None:
    _write(path, COLUMNS, ([r.time, r.id, r.source, r.dest] for r in requests))


def write_positions(result: Result, path: str | Path) -> None:
    """The required log: one row per tick, with every car's floor."""
    header = ["time"] + [f"car_{i}" for i in range(result.config.num_cars)]
    _write(path, header, ([t, *floors] for t, floors in enumerate(result.positions)))


def write_passengers(result: Result, path: str | Path) -> None:
    header = ["id", "car", "request_time", "source", "dest", "board_time", "dropoff_time",
              "wait", "travel", "total", "ideal"]
    _write(path, header, ([p.request.id, p.car_id, p.request.time, p.source, p.dest, p.board_time,
                           p.dropoff_time, p.wait_time, p.travel_time, p.total_time, p.request.distance]
                          for p in result.passengers))


def _write(path, header, rows) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
