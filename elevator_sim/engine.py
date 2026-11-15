"""Discrete-time simulation engine.

Each call to `step()` advances exactly one tick and runs these phases in order:

1. Assign  - requests whose time has come are given to a car, permanently.
2. Service - at each car's floor: riders get off, the router picks a direction,
             then waiting passengers going that way get on (first come, first served).
3. Log     - every car's floor is recorded for this tick.
4. Move    - each car moves one floor in its direction, unless its doors are held.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .feed import RequestFeed
from .models import Car, Passenger, Request, validate
from .policies import Dispatcher, Router
from .rules import advance, service


@dataclass(frozen=True)
class Config:
    floors: int
    cars: int
    capacity: int
    start_floor: int = 1
    dwell: int = 0  # extra ticks a car stays put after anyone boards or exits

    def __post_init__(self) -> None:
        if self.floors < 2 or self.cars < 1 or self.capacity < 1 or self.dwell < 0:
            raise ValueError(f"invalid config: {self}")
        if not 1 <= self.start_floor <= self.floors:
            raise ValueError(f"start_floor {self.start_floor} outside 1..{self.floors}")


@dataclass
class Result:
    config: Config
    passengers: list[Passenger]
    positions: list[tuple[int, ...]]  # positions[t][car_id] = floor at tick t

    @property
    def end_time(self) -> int:
        return len(self.positions) - 1


class Simulation:
    def __init__(self, config: Config, requests: Iterable[Request], dispatcher: Dispatcher,
                 router: Router, max_ticks: int = 1_000_000):
        requests = list(requests)
        validate(requests, config.floors)
        self.config, self.dispatcher, self.router, self.max_ticks = config, dispatcher, router, max_ticks
        self.feed = RequestFeed(requests)
        self.cars = [Car(i, config.capacity, config.start_floor) for i in range(config.cars)]
        self.passengers: list[Passenger] = []
        self.positions: list[tuple[int, ...]] = []
        self.now = 0

    @property
    def done(self) -> bool:
        return self.feed.empty and all(p.dropoff_time is not None for p in self.passengers)

    def run(self) -> Result:
        self.step()
        while not self.done:
            if self.now > self.max_ticks:
                raise RuntimeError(f"no finish after {self.max_ticks} ticks; likely a scheduler bug")
            self.step()
        return Result(self.config, self.passengers, self.positions)

    def step(self) -> None:
        for request in self.feed.release(self.now):
            self._assign(request)
        for car in self.cars:
            service(car, self.now, self.router.decide, self.config.dwell)
        self.positions.append(tuple(car.floor for car in self.cars))
        for car in self.cars:
            self._move(car)
        self.now += 1

    def _assign(self, request: Request) -> None:
        car = self.cars[self.dispatcher.assign(request, self.cars, self.now)]
        passenger = Passenger(request, car.id)
        self.passengers.append(passenger)
        car.waiting.append(passenger)

    def _move(self, car: Car) -> None:
        advance(car, self.now)
        if not 1 <= car.floor <= self.config.floors:
            raise RuntimeError(f"router sent car {car.id} off the building (floor {car.floor})")
