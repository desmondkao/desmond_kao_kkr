"""One test (or group) per rule in the brief."""

from __future__ import annotations

import pytest

from elevator_sim import Config, Request, Simulation, simulate
from elevator_sim.dispatch import RoundRobinDispatcher
from helpers import random_requests


def run(requests, floors=10, cars=1, capacity=10, **options):
    return simulate(requests, floors, cars, capacity, dispatcher="round-robin", **options)


# Basic correctness

def test_single_passenger_achieves_ideal_time():
    (p,) = run([(0, "a", 1, 5)]).passengers
    assert (p.wait_time, p.travel_time) == (0, 4)


def test_car_travels_to_pickup():
    (p,) = run([(0, "a", 4, 2)]).passengers
    assert (p.board_time, p.dropoff_time) == (3, 5)


def test_no_requests_is_fine():
    assert run([]).positions == [(1,)]


# "tick forward one time unit at a time"

def test_clock_ticks_through_idle_time():
    result = run([(50, "late", 1, 3)])
    assert len(result.positions) == result.end_time + 1
    assert result.positions[:51] == [(1,)] * 51


def test_cars_move_at_most_one_floor_per_tick():
    result = run(random_requests(200, 20, 300, seed=1), floors=20, cars=3, capacity=4)
    for prev, cur in zip(result.positions, result.positions[1:]):
        assert all(abs(a - b) <= 1 for a, b in zip(prev, cur))


# "do not peek ahead"

def test_dispatcher_only_sees_requests_as_they_happen():
    seen = []

    class Spy(RoundRobinDispatcher):
        def assign(self, request, cars, now):
            seen.append((request.time, now))
            return super().assign(request, cars, now)

    Simulation(Config(10, 2, 10), random_requests(100, 10, 200, seed=2), Spy()).run()
    assert seen and all(t == now for t, now in seen)


# Constraints: capacity, direction, fixed assignment

def test_invariants_hold_every_tick():
    sim = Simulation(Config(15, 3, 4), random_requests(300, 15, 300, seed=3), RoundRobinDispatcher())
    first_car = {}
    while not sim.done:
        sim.step()
        for car in sim.cars:
            assert len(car.riders) <= car.capacity
            assert len({p.direction for p in car.riders}) <= 1  # riders all go one way
            for p in car.riders + car.waiting:
                assert first_car.setdefault(p.request.id, car.id) == car.id  # assignment never changes


def test_full_car_comes_back_for_the_rest():
    # Capacity 3, seven people at floor 1 going to 10: trips of 3, 3, then 1.
    result = run([(0, f"p{i}", 1, 10) for i in range(7)], capacity=3)
    assert sorted(p.wait_time for p in result.passengers) == [0, 0, 0, 18, 18, 18, 36]


# "serve all requests eventually"

@pytest.mark.parametrize("seed", range(5))
def test_everyone_delivered_under_overload(seed):
    result = run(random_requests(500, 25, 200, seed), floors=25, cars=2, capacity=4)
    assert all(p.dropoff_time is not None for p in result.passengers)


def starvation_case(n_later):
    # One full car keeps getting new riders at the lobby, so it never stops for P at floor 5.
    return [(0, "P", 5, 15)] + [(10 * i, f"q{i}", 1, 10) for i in range(n_later)]


def test_without_a_guard_a_passenger_can_wait_without_limit():
    waits = [next(p.wait_time for p in run(starvation_case(n), floors=20, capacity=1, max_wait=10**6).passengers
                  if p.request.id == "P") for n in (10, 20, 40)]
    assert waits[0] < waits[1] < waits[2]  # grows with the number of later arrivals


@pytest.mark.parametrize("n_later", [10, 40, 80])
def test_overdue_passenger_is_served_within_a_bound(n_later):
    floors, max_wait = 20, 30
    result = run(starvation_case(n_later), floors=floors, capacity=1, max_wait=max_wait)
    p = next(p for p in result.passengers if p.request.id == "P")
    # Once overdue, P has a reserved seat and is the car's target: reached within 3 sweeps.
    assert p.wait_time <= max_wait + 3 * (floors - 1)


# Input validation

@pytest.mark.parametrize("requests", [
    [(0, "x", 0, 5)],                  # floor below 1
    [(0, "x", 1, 11)],                 # floor above top
    [(0, "x", 3, 3)],                  # source == dest
    [(-1, "x", 1, 2)],                 # negative time
    [(0, "x", 1, 2), (1, "x", 2, 3)],  # duplicate id
])
def test_invalid_input_rejected(requests):
    with pytest.raises(ValueError):
        run(requests)


# Configuration

def test_dwell_adds_ticks_per_stop():
    (p,) = run([(0, "a", 1, 5)], dwell=1).passengers
    assert (p.wait_time, p.travel_time) == (0, 5)


def test_runs_are_deterministic():
    requests = random_requests(200, 20, 200, seed=5)
    assert run(requests, floors=20, cars=3).positions == run(requests, floors=20, cars=3).positions
