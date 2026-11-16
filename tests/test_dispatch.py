"""Dispatchers: every one must obey the rules; ETD must make sensible choices."""

from __future__ import annotations

import pytest

from elevator_sim import Car, Config, Direction, Passenger, Request, Simulation
from elevator_sim.csv_io import load_requests
from elevator_sim.dispatch import (DirectionalDispatcher, EtdDispatcher, NearestCarDispatcher, RoundRobinDispatcher,
                                   make_dispatcher)
from helpers import random_requests

FLOORS = 20
DISPATCHERS = ("round-robin", "nearest", "directional", "zone", "etd", "etd-p1")


def run(requests, dispatcher, floors=FLOORS, cars=3, capacity=6):
    return Simulation(Config(floors, cars, capacity), requests, dispatcher).run()


@pytest.mark.parametrize("name", DISPATCHERS)
def test_every_dispatcher_delivers_everyone_and_keeps_rules(name):
    result = run(random_requests(400, FLOORS, 300, seed=11), make_dispatcher(name, FLOORS))
    for p in result.passengers:
        assert p.dropoff_time is not None
        path = [floors[p.car_id] for floors in result.positions[p.board_time:p.dropoff_time + 1]]
        assert all((b - a) * p.direction >= 0 for a, b in zip(path, path[1:]))


def test_etd_fixes_the_spec_example():
    # Round robin sends passenger3 to the busy car (71-tick wait); ETD uses the free one.
    requests = load_requests("examples/spec_example.csv")
    rr = {p.request.id: p.wait_time for p in run(requests, RoundRobinDispatcher(), floors=60, cars=2).passengers}
    etd = {p.request.id: p.wait_time for p in run(requests, EtdDispatcher(), floors=60, cars=2).passengers}
    assert rr["passenger3"] == 71
    assert etd["passenger3"] < 30


def test_etd_prefers_far_empty_car_over_near_busy_one():
    # Car 0 is 2 floors from the caller but carrying 5 people up to floor 30.
    # Car 1 is empty, 17 floors away. Nearest-car picks car 0; ETD picks car 1.
    riders = [Passenger(Request(0, f"r{i}", 1, 30), car_id=0, board_time=0) for i in range(5)]
    busy = Car(0, capacity=8, floor=5, direction=Direction.UP, riders=riders)
    empty = Car(1, capacity=8, floor=20)
    request = Request(10, "new", 3, 1)
    assert NearestCarDispatcher().assign(request, [busy, empty], now=10) == 0
    assert EtdDispatcher().assign(request, [busy, empty], now=10) == 1


def test_directional_skips_a_car_heading_away():
    # Caller at floor 3 going down. Car 0 is at floor 5 but carrying riders up to 30,
    # so it must reach 30 first: 25 + 27 = 52 floors. Car 1 is idle 17 floors away.
    riders = [Passenger(Request(0, "r", 1, 30), car_id=0, board_time=0)]
    busy = Car(0, capacity=8, floor=5, direction=Direction.UP, riders=riders)
    idle = Car(1, capacity=8, floor=20)
    request = Request(10, "new", 3, 1)
    assert DirectionalDispatcher.distance(busy, request) == 52
    assert DirectionalDispatcher().assign(request, [busy, idle], now=10) == 1


def test_directional_picks_a_car_coming_its_way():
    coming = Car(0, capacity=8, floor=2, direction=Direction.UP,
                 riders=[Passenger(Request(0, "r", 1, 20), car_id=0, board_time=0)])
    request = Request(10, "new", 6, 15)
    assert DirectionalDispatcher.distance(coming, request) == 4


def test_etd_does_not_mutate_cars():
    car = Car(0, capacity=4, floor=3, waiting=[Passenger(Request(0, "a", 5, 9), car_id=0)])
    before = (car.floor, car.direction, list(car.waiting), list(car.riders))
    EtdDispatcher().assign(Request(1, "b", 2, 8), [car], now=1)
    assert (car.floor, car.direction, list(car.waiting), list(car.riders)) == before
    assert car.waiting[0].board_time is None


def test_zone_keeps_lobby_trips_in_their_band():
    zone = make_dispatcher("zone", floors=21)  # floors 2..21 split across 4 cars: 5 floors each
    cars = [Car(i, 8, 1) for i in range(4)]
    picks = [zone.assign(Request(0, str(f), 1, f), cars, 0) for f in range(2, 22)]
    assert picks == [0] * 5 + [1] * 5 + [2] * 5 + [3] * 5


def test_unknown_dispatcher_rejected():
    with pytest.raises(ValueError, match="unknown dispatcher"):
        make_dispatcher("fastest", FLOORS)
