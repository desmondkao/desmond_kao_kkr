"""Routing: which way a car heads next. Re-decided every tick.

LOOK: keep going while there is work ahead, reverse when there is none.
An overdue passenger (see Car.overdue) becomes the car's next target, so
nobody waits forever.
"""

from __future__ import annotations

from .models import Car, Direction, Passenger


def look(car: Car, now: int) -> Direction:
    """Called after riders get off at the current floor and before anyone boards."""
    if car.riders:
        return car.riders[0].direction  # boarding rule keeps all riders going one way
    if overdue := car.overdue(now):
        return _toward(car, overdue)
    if not car.waiting:
        return Direction.IDLE
    if car.direction is Direction.IDLE:  # starting from rest: go to the nearest (oldest on ties)
        return _toward(car, min(car.waiting, key=lambda p: abs(p.source - car.floor)))

    work_ahead = any((p.source - car.floor) * car.direction > 0 for p in car.waiting)
    boarding_here = any(p.source == car.floor and p.direction == car.direction for p in car.waiting)
    return car.direction if work_ahead or boarding_here else Direction(-car.direction)


def _toward(car: Car, p: Passenger) -> Direction:
    """Head to p's floor; once there, go p's way so they can board."""
    if p.source == car.floor:
        return p.direction
    return Direction.UP if p.source > car.floor else Direction.DOWN
