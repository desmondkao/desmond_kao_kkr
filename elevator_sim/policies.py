"""Scheduling policies.

The controller makes two independent decisions, each behind a small interface:

* Dispatcher: which car serves a new passenger. Decided once, at request time.
* Router: which way a car heads next. Re-decided every tick.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from .models import Car, Direction, Request


class Dispatcher(Protocol):
    def assign(self, request: Request, cars: Sequence[Car], now: int) -> int:
        """Return the id of the car that will serve `request`. Must not mutate cars."""


class Router(Protocol):
    def decide(self, car: Car, now: int) -> Direction:
        """Direction for `car`, called after drop-offs and before boarding."""


class RoundRobinDispatcher:
    """Baseline: cycle through the cars, ignoring where they are."""

    def __init__(self) -> None:
        self._count = 0

    def assign(self, request: Request, cars: Sequence[Car], now: int) -> int:
        self._count += 1
        return cars[(self._count - 1) % len(cars)].id


class LookRouter:
    """LOOK, the classic elevator (and disk-arm) sweep.

    Keep going while there is work ahead; reverse when there is none.
    Every stop is reached within one round trip, so nobody waits forever.
    """

    def decide(self, car: Car, now: int) -> Direction:
        if car.riders:
            return car.riders[0].direction  # boarding rule keeps all riders going one way
        if not car.waiting:
            return Direction.IDLE

        here = [p for p in car.waiting if p.source == car.floor]
        if car.direction is Direction.IDLE:  # starting from rest: serve the oldest here, else the nearest
            if here:
                return here[0].direction
            nearest = min(car.waiting, key=lambda p: abs(p.source - car.floor))
            return Direction.UP if nearest.source > car.floor else Direction.DOWN

        work_ahead = any((p.source - car.floor) * car.direction > 0 for p in car.waiting)
        boarding_here = any(p.direction == car.direction for p in here)
        return car.direction if work_ahead or boarding_here else Direction(-car.direction)
