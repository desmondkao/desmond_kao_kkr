"""Routing: the rollout router must be safe and never worse than LOOK on known passengers."""

from __future__ import annotations

import pytest

from elevator_sim import Config, Request, Simulation
from elevator_sim.policies import LookRouter, RolloutRouter, RoundRobinDispatcher
from elevator_sim.rules import forecast
from test_engine import random_requests


def run(requests, router, floors=20, cars=1, capacity=6):
    return Simulation(Config(floors, cars, capacity), requests, RoundRobinDispatcher(), router).run()


def total_cost(result, cost=float):
    return sum(cost(p.total_time) for p in result.passengers)


def squared(t):
    return t * t


@pytest.mark.parametrize("cost", [float, squared])
@pytest.mark.parametrize("seed", range(30))
def test_rollout_never_worse_than_look_when_all_requests_known(seed, cost):
    # With every request known up front, rollout's guarantee applies exactly.
    requests = [Request(0, r.id, r.source, r.dest) for r in random_requests(15, 20, 0, seed)]
    look = total_cost(run(requests, LookRouter()), cost)
    rollout = total_cost(run(requests, RolloutRouter(cost=cost)), cost)
    assert rollout <= look


def test_rollout_beats_look_on_a_lopsided_choice():
    # Car rests at 10 after a drop-off. One person at 11 going up, six at 9 going down.
    # LOOK keeps heading up for the one; rollout serves the six first.
    warmup = [Request(0, "w", 1, 10)]
    crowd = [Request(9, f"d{i}", 9, 1) for i in range(6)] + [Request(9, "u", 11, 20)]
    look = total_cost(run(warmup + crowd, LookRouter()))
    rollout = total_cost(run(warmup + crowd, RolloutRouter()))
    assert rollout < look


def test_backstop_zero_means_plain_look():
    requests = random_requests(200, 20, 300, seed=7)
    look = run(requests, LookRouter(), cars=2)
    capped = run(requests, RolloutRouter(max_wait=0), cars=2)
    assert look.positions == capped.positions


def test_forecast_matches_real_run_when_no_new_arrivals():
    # The forecast and the engine share rules.py, so with no surprises they must agree.
    requests = [Request(0, r.id, r.source, r.dest) for r in random_requests(10, 15, 0, seed=3)]
    sim = Simulation(Config(15, 1, 4), requests, RoundRobinDispatcher(), LookRouter())
    sim.step()  # tick 0: assign, service, move
    car = sim.cars[0]
    predicted = {p.req.id: p.dropoff_time for p in forecast(car, sim.now, LookRouter().decide, dwell=0)}
    actual = {p.req.id: p.dropoff_time for p in sim.run().passengers}
    assert {k: actual[k] for k in predicted} == predicted
