"""Scheduling policies.

The controller makes two independent decisions, each behind a small interface:

* Dispatcher: which car serves a new passenger. Decided once, at request time.
* Router: which way a car heads next. Re-decided every tick.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Protocol

from .models import Car, Direction, Request
from .rules import forecast


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


def squared(total_time: int) -> float:
    return float(total_time * total_time)


class RolloutRouter:
    """LOOK plus one step of look-ahead ("rollout").

    The only real routing choice is which way an *empty* car heads; with riders
    aboard the direction is fixed by the rules. At that choice, simulate the
    car's known passengers forward for each direction (then LOOK) and take the
    cheaper plan.

    Because LOOK's own choice is always one of the options, the plan can only
    match or beat LOOK on the passengers already known (the classic rollout
    improvement property; tested in test_routing.py).

    `cost` maps a passenger's total time to a penalty. Squared (default) weighs
    long waits more, which acts as aging; plain linear minimises the average but
    in testing it let worst-case times grow.
    `max_wait` is a starvation backstop: if this car's oldest waiting passenger
    has waited that long, defer to LOOK, which reaches them within a round trip.
    """

    def __init__(self, dwell: int = 0, cost: Callable[[int], float] = squared, max_wait: int | None = None):
        self.look = LookRouter()
        self.dwell, self.cost, self.max_wait = dwell, cost, max_wait

    def decide(self, car: Car, now: int) -> Direction:
        default = self.look.decide(car, now)
        if car.riders or not car.waiting:
            return default
        if self.max_wait is not None and now - car.waiting[0].req.time >= self.max_wait:
            return default
        options = [d for d in (Direction.UP, Direction.DOWN) if _has_work(car, d)]
        if len(options) < 2:
            return default
        return min(options, key=lambda d: (self.plan_cost(car, now, d), d != default))

    def plan_cost(self, car: Car, now: int, first: Direction) -> float:
        def decide(c: Car, t: int) -> Direction:
            return first if t == now else self.look.decide(c, t)
        return sum(self.cost(p.total_time) for p in forecast(car, now, decide, self.dwell))


def _has_work(car: Car, d: Direction) -> bool:
    """Is any waiting passenger ahead in direction d, or here and going d?"""
    return any((p.source - car.floor) * d > 0 or (p.source == car.floor and p.direction == d)
               for p in car.waiting)
