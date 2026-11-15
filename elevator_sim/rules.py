"""What one car does in one tick. Shared by the engine and by ETD's forecasts,
so a forecast follows exactly the same rules as the real simulation.
"""

from __future__ import annotations

from dataclasses import replace

from .models import Car, Passenger
from .routing import look


def service(car: Car, now: int) -> None:
    """At the car's floor: riders get off, LOOK picks a direction, passengers going that way board."""
    exiting = [p for p in car.riders if p.dest == car.floor]
    for p in exiting:
        p.dropoff_time = now
    car.riders = [p for p in car.riders if p.dropoff_time is None]

    car.direction = look(car, now)

    # First come, first served (`waiting` is in request order, oldest first).
    # While someone is overdue, keep a seat free for them; LOOK is heading their way.
    here = [p for p in car.waiting if p.source == car.floor and p.direction == car.direction]
    seats = car.free_slots
    overdue = car.overdue(now)
    if overdue and overdue not in here:
        seats -= 1
    boarding = here[:max(seats, 0)]
    for p in boarding:
        p.board_time = now
    car.waiting = [p for p in car.waiting if p.board_time is None]
    car.riders += boarding

    if (exiting or boarding) and car.dwell:
        car.held_until = now + car.dwell


def move(car: Car, now: int) -> None:
    """One floor in the car's direction, unless its doors are held open."""
    if now >= car.held_until:
        car.floor += car.direction


def forecast(car: Car, now: int, limit: int = 100_000) -> list[Passenger]:
    """Play a copy of the car forward with no new arrivals; return copies of its
    passengers with predicted board and drop-off times."""
    car = replace(car, riders=[replace(p) for p in car.riders], waiting=[replace(p) for p in car.waiting])
    passengers = car.riders + car.waiting
    for t in range(now, now + limit):
        service(car, t)
        if not (car.riders or car.waiting):
            return passengers
        move(car, t)
    raise RuntimeError(f"forecast for car {car.id} did not finish in {limit} ticks")
