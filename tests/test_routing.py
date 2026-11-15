"""LOOK routing, and the forecast that ETD relies on."""

from __future__ import annotations

from elevator_sim import Car, Config, Direction, Passenger, Request, Simulation
from elevator_sim.dispatch import RoundRobinDispatcher
from elevator_sim.routing import look
from elevator_sim.rules import forecast
from helpers import random_requests


def waiting_at(*sources):
    return [Passenger(Request(0, f"p{s}", s, s + 1), car_id=0) for s in sources]


def test_look_keeps_going_while_work_is_ahead():
    car = Car(0, 8, floor=5, direction=Direction.UP, waiting=waiting_at(2, 9))
    assert look(car, now=0) is Direction.UP


def test_look_reverses_when_nothing_is_ahead():
    car = Car(0, 8, floor=5, direction=Direction.UP, waiting=waiting_at(2))
    assert look(car, now=0) is Direction.DOWN


def test_look_rests_with_no_work():
    assert look(Car(0, 8, floor=5, direction=Direction.UP), now=0) is Direction.IDLE


def test_forecast_matches_real_run_when_no_new_arrivals():
    # The forecast and the engine share rules.py, so with no surprises they must agree.
    requests = [Request(0, r.id, r.source, r.dest) for r in random_requests(10, 15, 0, seed=3)]
    sim = Simulation(Config(15, 1, 4), requests, RoundRobinDispatcher())
    sim.step()
    predicted = {p.request.id: p.dropoff_time for p in forecast(sim.cars[0], sim.now)}
    actual = {p.request.id: p.dropoff_time for p in sim.run().passengers}
    assert {k: actual[k] for k in predicted} == predicted


def test_forecast_does_not_touch_the_real_car():
    car = Car(0, 4, floor=3, waiting=waiting_at(5))
    forecast(car, now=0)
    assert car.floor == 3 and car.waiting[0].board_time is None
