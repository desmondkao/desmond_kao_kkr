"""The rules for one car at one tick, shared by the engine and by forecasts.

Keeping this in one place means a forecast can never disagree with the real
simulation about how a car behaves.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

from .models import Car, Direction, Passenger

Decide = Callable[[Car, int], Direction]


def service(car: Car, now: int, decide: Decide, dwell: int) -> None:
    """At the car's floor: riders get off, a direction is chosen, passengers board."""
    exiting = [p for p in car.riders if p.dest == car.floor]
    for p in exiting:
        p.dropoff_time = now
    car.riders = [p for p in car.riders if p.dropoff_time is None]

    car.direction = decide(car, now)

    # `waiting` is in request order, so this is first come, first served.
    # An IDLE car matches no passenger's direction, so nobody boards it.
    boarding = [p for p in car.waiting
                if p.source == car.floor and p.direction == car.direction][:car.free_slots]
    for p in boarding:
        p.board_time = now
    car.waiting = [p for p in car.waiting if p.board_time is None]
    car.riders += boarding

    if (exiting or boarding) and dwell:
        car.held_until = now + dwell


def advance(car: Car, now: int) -> None:
    """Move one floor in the current direction, unless the doors are held open."""
    if now >= car.held_until:
        car.floor += car.direction


def forecast(car: Car, now: int, decide: Decide, dwell: int, limit: int = 100_000) -> list[Passenger]:
    """Play one car forward with no new arrivals; return copies of its passengers
    with predicted board/drop-off times. The real car is not touched.

    Assumes drop-offs at the current floor have already happened this tick.
    """
    car = replace(car, riders=[replace(p) for p in car.riders], waiting=[replace(p) for p in car.waiting])
    passengers = car.riders + car.waiting
    for t in range(now, now + limit):
        service(car, t, decide, dwell)
        if not (car.riders or car.waiting):
            return passengers
        advance(car, t)
    raise RuntimeError(f"forecast for car {car.id} did not finish in {limit} ticks")
