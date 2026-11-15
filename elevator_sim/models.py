"""Core data types. Floors are numbered 1..n; one tick = one floor of travel."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class Direction(IntEnum):
    """Travel direction; the value is the floor change per tick."""

    DOWN = -1
    IDLE = 0
    UP = 1


@dataclass(frozen=True, slots=True)
class Request:
    """One input row: passenger `id` asks at `time` to go from `source` to `dest`."""

    time: int
    id: str
    source: int
    dest: int

    @property
    def direction(self) -> Direction:
        return Direction.UP if self.dest > self.source else Direction.DOWN

    @property
    def distance(self) -> int:
        """Ideal trip time: no waiting, direct ride. A lower bound for any scheduler."""
        return abs(self.dest - self.source)


@dataclass(slots=True)
class Passenger:
    """A request bound to the car that will serve it. `car_id` never changes."""

    req: Request
    car_id: int
    board_time: int | None = None
    dropoff_time: int | None = None

    # Shortcuts so scheduling code reads naturally (p.source, not p.req.source).
    source = property(lambda self: self.req.source)
    dest = property(lambda self: self.req.dest)
    direction = property(lambda self: self.req.direction)

    @property
    def wait_time(self) -> int:
        return self.board_time - self.req.time

    @property
    def travel_time(self) -> int:
        return self.dropoff_time - self.board_time

    @property
    def total_time(self) -> int:
        return self.dropoff_time - self.req.time


@dataclass(slots=True)
class Car:
    """An elevator car. `waiting`: assigned but not yet aboard. `riders`: aboard."""

    id: int
    capacity: int
    floor: int
    direction: Direction = Direction.IDLE
    riders: list[Passenger] = field(default_factory=list)
    waiting: list[Passenger] = field(default_factory=list)
    held_until: int = 0  # doors stay open (no movement) while now < held_until

    @property
    def free_slots(self) -> int:
        return self.capacity - len(self.riders)


def validate(requests: list[Request], floors: int) -> None:
    """Reject bad input up front, naming the offending passenger."""
    seen: set[str] = set()
    for r in requests:
        problem = (
            "duplicate id" if r.id in seen
            else "negative time" if r.time < 0
            else "floor out of range" if not (1 <= r.source <= floors and 1 <= r.dest <= floors)
            else "source equals dest" if r.source == r.dest
            else None
        )
        if problem:
            raise ValueError(f"{r.id}: {problem} ({r})")
        seen.add(r.id)
