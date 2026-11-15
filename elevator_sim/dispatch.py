"""Dispatching: which car serves a new passenger. Decided once, at request time."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from .models import Car, Request


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


def make_dispatcher(name: str, floors: int) -> Dispatcher:
    if name != "round-robin":
        raise ValueError(f"unknown dispatcher {name!r}")
    return RoundRobinDispatcher()
