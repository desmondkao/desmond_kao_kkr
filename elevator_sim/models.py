"""Core data types. Floors are numbered 1..n, floor 1 is the lobby, one tick = one floor of travel."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum

LOBBY = 1


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
        """Trip time with no waiting: a lower bound no scheduler can beat."""
        return abs(self.dest - self.source)


@dataclass(slots=True)
class Passenger:
    """A request bound to the car that will serve it. `car_id` never changes."""

    request: Request
    car_id: int
    board_time: int | None = None
    dropoff_time: int | None = None

    @property
    def source(self) -> int:
        return self.request.source

    @property
    def dest(self) -> int:
        return self.request.dest

    @property
    def direction(self) -> Direction:
        return self.request.direction

    @property
    def wait_time(self) -> int:
        return self.board_time - self.request.time

    @property
    def travel_time(self) -> int:
        return self.dropoff_time - self.board_time

    @property
    def total_time(self) -> int:
        return self.dropoff_time - self.request.time


@dataclass(slots=True)
class Car:
    """An elevator car. `waiting`: assigned but not aboard, in request order. `riders`: aboard."""

    id: int
    capacity: int
    floor: int
    dwell: int = 0  # extra ticks the doors stay open after anyone boards or exits
    max_wait: int = 10**9  # a passenger waiting this long becomes overdue and gets priority
    serves: frozenset[int] | None = None  # express car: the only floors it stops at (None = all)
    direction: Direction = Direction.IDLE
    riders: list[Passenger] = field(default_factory=list)
    waiting: list[Passenger] = field(default_factory=list)
    held_until: int = 0  # the car cannot move while now < held_until

    @property
    def free_slots(self) -> int:
        return self.capacity - len(self.riders)

    def can_serve(self, request: Request) -> bool:
        return self.serves is None or (request.source in self.serves and request.dest in self.serves)

    def overdue(self, now: int) -> Passenger | None:
        """The oldest waiting passenger, if they have waited `max_wait` ticks or more."""
        if self.waiting and now - self.waiting[0].request.time >= self.max_wait:
            return self.waiting[0]
        return None
