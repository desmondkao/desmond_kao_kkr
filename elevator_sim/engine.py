"""The simulation clock.

Each `step()` advances exactly one tick, in this order:

1. Assign  - requests whose time has come are given to a car, permanently.
2. Service - at each car's floor: riders get off, LOOK picks a direction,
             then waiting passengers going that way get on (rules.py).
3. Log     - every car's floor is recorded for this tick.
4. Move    - each car moves one floor, unless its doors are held open.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .dispatch import Dispatcher, make_dispatcher
from .feed import RequestFeed
from .models import Car, Passenger, Request
from .rules import move, service

MAX_TICKS = 1_000_000  # safety net: a correct scheduler never gets near this


@dataclass(frozen=True)
class Config:
    floors: int
    num_cars: int
    capacity: int
    start_floor: int = 1
    dwell: int = 0  # extra ticks per stop; 0 means stopping is free
    max_wait: int | None = None  # ticks before a waiting passenger gets priority; None = 3 x floors

    def __post_init__(self) -> None:
        if self.floors < 2 or self.num_cars < 1 or self.capacity < 1 or self.dwell < 0:
            raise ValueError(f"invalid config: {self}")
        if not 1 <= self.start_floor <= self.floors:
            raise ValueError(f"start_floor {self.start_floor} is outside 1..{self.floors}")


@dataclass
class Result:
    config: Config
    passengers: list[Passenger]
    positions: list[tuple[int, ...]]  # positions[t][car_id] = floor at tick t

    @property
    def end_time(self) -> int:
        return len(self.positions) - 1


class Simulation:
    def __init__(self, config: Config, requests: Iterable[Request], dispatcher: Dispatcher):
        max_wait = config.max_wait if config.max_wait is not None else 3 * config.floors
        self.cars = [Car(i, config.capacity, config.start_floor, config.dwell, max_wait)
                     for i in range(config.num_cars)]
        requests = list(requests)
        self._check(requests, config)
        self.config, self.dispatcher = config, dispatcher
        self.feed = RequestFeed(requests)
        self.passengers: list[Passenger] = []
        self.positions: list[tuple[int, ...]] = []
        self.now = 0

    @property
    def done(self) -> bool:
        return self.feed.empty and all(p.dropoff_time is not None for p in self.passengers)

    def run(self) -> Result:
        while True:
            self.step()
            if self.done:
                return Result(self.config, self.passengers, self.positions)
            if self.now > MAX_TICKS:
                raise RuntimeError(f"not finished after {MAX_TICKS} ticks; likely a scheduler bug")

    def step(self) -> None:
        for request in self.feed.release(self.now):
            self._assign(request)
        for car in self.cars:
            service(car, self.now)
        self.positions.append(tuple(car.floor for car in self.cars))
        for car in self.cars:
            move(car, self.now)
            if not 1 <= car.floor <= self.config.floors:
                raise RuntimeError(f"car {car.id} was routed off the building (floor {car.floor})")
        self.now += 1

    def _assign(self, request: Request) -> None:
        car_id = self.dispatcher.assign(request, self.cars, self.now)
        passenger = Passenger(request, car_id)
        self.passengers.append(passenger)
        self.cars[car_id].waiting.append(passenger)

    def _check(self, requests: list[Request], config: Config) -> None:
        """Reject bad input up front, naming the passenger."""
        seen = set()
        for r in requests:
            if r.id in seen:
                raise ValueError(f"{r.id}: duplicate id")
            if r.time < 0:
                raise ValueError(f"{r.id}: negative time {r.time}")
            if not (1 <= r.source <= config.floors and 1 <= r.dest <= config.floors):
                raise ValueError(f"{r.id}: floor outside 1..{config.floors} ({r.source} -> {r.dest})")
            if r.source == r.dest:
                raise ValueError(f"{r.id}: source equals dest ({r.source})")
            seen.add(r.id)


def simulate(requests: Iterable[Request | tuple], floors: int, num_cars: int = 3, capacity: int = 10,
             dispatcher: str = "round-robin", **options) -> Result:
    """One-call entry point. `requests` are Request objects or (time, id, source, dest) tuples.

    >>> simulate([(0, "a", 1, 5), (0, "b", 1, 3)], floors=10).passengers[0].total_time
    4
    """
    requests = [r if isinstance(r, Request) else Request(int(r[0]), str(r[1]), int(r[2]), int(r[3]))
                for r in requests]
    config = Config(floors, num_cars, capacity, **options)
    return Simulation(config, requests, make_dispatcher(dispatcher, floors)).run()
