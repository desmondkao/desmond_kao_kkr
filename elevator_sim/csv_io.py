"""CSV input and output."""

from __future__ import annotations

import csv
from pathlib import Path

from .engine import Result
from .models import Request

COLUMNS = ("time", "id", "source", "dest")


def load_requests(path: str | Path) -> list[Request]:
    """Read `time,id,source,dest` rows. The header line is optional; errors name the line."""
    with open(path, newline="") as f:
        rows = [(n, [cell.strip() for cell in row]) for n, row in enumerate(csv.reader(f), start=1)
                if any(cell.strip() for cell in row)]
    columns = list(COLUMNS)
    if rows and not _is_int(rows[0][1][0]):  # first cell isn't a time, so it's a header
        _, columns = rows.pop(0)
        if sorted(columns) != sorted(COLUMNS):
            raise ValueError(f"{path}: header must be {','.join(COLUMNS)}, got {','.join(columns)}")
    requests = []
    for line, row in rows:
        if len(row) != len(COLUMNS):
            raise ValueError(f"{path}:{line}: expected {len(COLUMNS)} fields, got {row}")
        f = dict(zip(columns, row))
        if not all(_is_int(f[c]) for c in ("time", "source", "dest")):
            raise ValueError(f"{path}:{line}: time, source and dest must be whole numbers, got {row}")
        requests.append(Request(int(f["time"]), f["id"], int(f["source"]), int(f["dest"])))
    return requests


def _is_int(text: str) -> bool:
    return text.lstrip("-").isdigit()


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
