"""One test (or group) per rule in the brief."""

from __future__ import annotations

import random

import pytest

from elevator_sim import Config, Request, Simulation
from elevator_sim.csv_io import load_requests
from elevator_sim.feed import RequestFeed
from elevator_sim.policies import LookRouter, RoundRobinDispatcher


def make(requests, floors=10, cars=1, capacity=10, dwell=0, dispatcher=None):
    config = Config(floors, cars, capacity, dwell=dwell)
    return Simulation(config, requests, dispatcher or RoundRobinDispatcher(), LookRouter())


def run(requests, **kw):
    return make(requests, **kw).run()


def random_requests(n, floors, horizon, seed):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        source, dest = rng.sample(range(1, floors + 1), 2)
        out.append(Request(rng.randint(0, horizon), f"p{i}", source, dest))
    return out


# ---- basic correctness ----

def test_single_passenger_achieves_ideal_time():
    (p,) = run([Request(0, "a", 1, 5)]).passengers
    assert (p.wait_time, p.travel_time) == (0, 4)


def test_car_travels_to_pickup():
    (p,) = run([Request(0, "a", 4, 2)]).passengers
    assert (p.board_time, p.dropoff_time) == (3, 5)


def test_spec_example():
    result = run(load_requests("examples/spec_example.csv"), floors=60, cars=2)
    assert all(p.dropoff_time is not None for p in result.passengers)


# ---- "tick forward one time unit at a time" ----

def test_clock_ticks_through_idle_time():
    result = run([Request(50, "late", 1, 3)])
    assert len(result.positions) == result.end_time + 1
    assert result.positions[:51] == [(1,)] * 51


def test_cars_move_at_most_one_floor_per_tick():
    result = run(random_requests(200, 20, 300, seed=1), floors=20, cars=3, capacity=4)
    for prev, cur in zip(result.positions, result.positions[1:]):
        assert all(abs(a - b) <= 1 for a, b in zip(prev, cur))


# ---- "do not peek ahead" ----

def test_dispatcher_only_sees_requests_as_they_happen():
    seen = []

    class Spy(RoundRobinDispatcher):
        def assign(self, request, cars, now):
            seen.append((request.time, now))
            return super().assign(request, cars, now)

    run(random_requests(100, 10, 200, seed=2), cars=2, dispatcher=Spy())
    assert seen and all(t == now for t, now in seen)


def test_feed_cannot_go_back_in_time():
    feed = RequestFeed([Request(5, "a", 1, 2)])
    assert feed.release(4) == []
    assert [r.id for r in feed.release(5)] == ["a"]
    with pytest.raises(RuntimeError):
        feed.release(3)


# ---- constraints: capacity, direction, fixed assignment ----

def test_invariants_hold_every_tick():
    sim = make(random_requests(300, 15, 300, seed=3), floors=15, cars=3, capacity=4)
    first_car = {}
    while not sim.done:
        sim.step()
        for car in sim.cars:
            assert len(car.riders) <= car.capacity
            assert len({p.direction for p in car.riders}) <= 1  # riders all go one way
            for p in car.riders + car.waiting:
                assert first_car.setdefault(p.req.id, car.id) == car.id  # assignment never changes


def test_riders_never_move_the_wrong_way():
    result = run(random_requests(300, 15, 400, seed=4), floors=15, cars=3, capacity=5)
    for p in result.passengers:
        path = [floors[p.car_id] for floors in result.positions[p.board_time:p.dropoff_time + 1]]
        assert all((b - a) * p.direction >= 0 for a, b in zip(path, path[1:])), p.req.id


def test_full_car_comes_back_for_the_rest():
    # Capacity 3, seven people at floor 1 going to 10: trips of 3, 3, then 1.
    result = run([Request(0, f"p{i}", 1, 10) for i in range(7)], capacity=3)
    assert sorted(p.wait_time for p in result.passengers) == [0, 0, 0, 18, 18, 18, 36]


# ---- "serve all requests eventually" ----

@pytest.mark.parametrize("seed", range(5))
def test_everyone_delivered_under_overload(seed):
    result = run(random_requests(500, 25, 200, seed), floors=25, cars=2, capacity=4)
    assert all(p.dropoff_time is not None for p in result.passengers)


# ---- input validation ----

@pytest.mark.parametrize("requests", [
    [Request(0, "x", 0, 5)],                          # floor below 1
    [Request(0, "x", 1, 11)],                         # floor above top
    [Request(0, "x", 3, 3)],                          # source == dest
    [Request(-1, "x", 1, 2)],                         # negative time
    [Request(0, "x", 1, 2), Request(1, "x", 2, 3)],   # duplicate id
])
def test_invalid_input_rejected(requests):
    with pytest.raises(ValueError):
        run(requests)


# ---- configuration ----

def test_dwell_adds_ticks_per_stop():
    (p,) = run([Request(0, "a", 1, 5)], dwell=1).passengers
    assert (p.wait_time, p.travel_time) == (0, 5)


def test_runs_are_deterministic():
    requests = random_requests(200, 20, 200, seed=5)
    assert run(requests, floors=20, cars=3).positions == run(requests, floors=20, cars=3).positions
