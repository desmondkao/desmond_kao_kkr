"""Dispatching: which car serves a new passenger. Decided once, at request time.

The engine only offers cars that can serve the trip (express cars skip floors).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import replace
from typing import Protocol

from .models import LOBBY, Car, Passenger, Request
from .rules import forecast

Cost = Callable[[int], float]  # a passenger's total time -> penalty


def power_cost(p: float) -> Cost:
    """total_time ** p. p=1 minimises the average; larger p weighs long trips more."""
    return lambda total_time: float(total_time) ** p


class Dispatcher(Protocol):
    def assign(self, request: Request, cars: Sequence[Car], now: int) -> int:
        """Return the id of the car that will serve `request`. Must not mutate cars."""


class RoundRobinDispatcher:
    """Baseline: cycle through the cars, ignoring where they are."""

    def __init__(self) -> None:
        self._count = 0

    def assign(self, request: Request, cars: Sequence[Car], now: int) -> int:
        car = cars[self._count % len(cars)]
        self._count += 1
        return car.id


class NearestCarDispatcher:
    """Baseline: the car closest to the pickup floor, ignoring its direction and load."""

    def assign(self, request: Request, cars: Sequence[Car], now: int) -> int:
        return min(cars, key=lambda c: (abs(c.floor - request.source), c.id)).id


class ZoneDispatcher:
    """Baseline: split the floors above the lobby into one band per car.

    A trip belongs to the band of its non-lobby end: the upper floor for lobby
    trips, the pickup floor otherwise.
    """

    def __init__(self, floors: int):
        self.floors = floors

    def assign(self, request: Request, cars: Sequence[Car], now: int) -> int:
        key = request.dest if request.source == LOBBY else request.source
        band = (key - LOBBY - 1) * len(cars) // (self.floors - LOBBY)
        return cars[min(max(band, 0), len(cars) - 1)].id


class EtdDispatcher:
    """Estimated Time to Destination (ETD). The default dispatcher.

    For each car, forecast its passengers with and without the newcomer. The
    difference is the newcomer's own cost plus the delay they add for everyone
    already on that car. Pick the car where it is smallest.

    Cost is total_time**2 by default, so one very long trip counts for more than
    several short ones (see the fairness experiment).
    """

    def __init__(self, cost: Cost = power_cost(2)):
        self.cost = cost

    def assign(self, request: Request, cars: Sequence[Car], now: int) -> int:
        return min(cars, key=lambda c: (self.added_cost(c, request, now), c.id)).id

    def added_cost(self, car: Car, request: Request, now: int) -> float:
        with_new = replace(car, waiting=car.waiting + [Passenger(request, car.id)])
        return self._plan_cost(with_new, now) - self._plan_cost(car, now)

    def _plan_cost(self, car: Car, now: int) -> float:
        if not (car.riders or car.waiting):
            return 0.0
        return sum(self.cost(p.total_time) for p in forecast(car, now))


def make_dispatcher(name: str, floors: int) -> Dispatcher:
    """'etd', 'nearest', 'zone', 'round-robin', or 'etd-p<k>' (ETD with cost total_time**k)."""
    if name.startswith("etd-p"):
        return EtdDispatcher(power_cost(float(name.removeprefix("etd-p"))))
    makers = {"etd": EtdDispatcher, "nearest": NearestCarDispatcher,
              "zone": lambda: ZoneDispatcher(floors), "round-robin": RoundRobinDispatcher}
    if name not in makers:
        raise ValueError(f"unknown dispatcher {name!r}; choose from {list(makers)} or etd-p<k>")
    return makers[name]()
