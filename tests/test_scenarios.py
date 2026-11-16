"""Scenario generators and the benchmark harness."""

from __future__ import annotations

import pytest

from elevator_sim import Config
from elevator_sim.benchmark import EXPERIMENTS, Experiment, run, to_markdown
from elevator_sim.capacity import handling_capacity, keeps_up
from elevator_sim.dispatch import RoundRobinDispatcher, make_dispatcher
from elevator_sim.engine import Simulation
from elevator_sim.scenarios import LOBBY, SCENARIOS, generate


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_generated_requests_are_valid_and_reproducible(scenario):
    requests = generate(scenario, floors=20, rate=0.5, duration=400, seed=1)
    Simulation(Config(20, 1, 1), requests, RoundRobinDispatcher())  # raises on invalid input
    assert all(0 <= r.time < 400 for r in requests)
    assert [r.time for r in requests] == sorted(r.time for r in requests)
    assert requests == generate(scenario, floors=20, rate=0.5, duration=400, seed=1)


def test_rate_is_respected():
    requests = generate("interfloor", floors=20, rate=0.5, duration=2000, seed=0)
    assert 900 < len(requests) < 1100  # expected 1000


def test_up_peak_is_mostly_from_the_lobby():
    requests = generate("up-peak", floors=20, rate=1.0, duration=1000, seed=0)
    share = sum(r.source == LOBBY for r in requests) / len(requests)
    assert 0.8 < share < 0.9  # configured at 85%


def test_benchmark_smoke():
    exp = Experiment("smoke", {"small": Config(10, 2, 4)}, ("round-robin", "etd"), scenarios=("lunch",), rates=(0.2,))
    rows = run(exp, seeds=2, duration=50)
    assert len(rows) == 2  # one per dispatcher, averaged over seeds
    assert all(row["vs_ideal"] >= 1 for row in rows)  # nobody beats the lower bound
    assert to_markdown(rows).count("\n") == len(rows) + 1


def test_experiments_use_known_names():
    for exp in EXPERIMENTS.values():
        for name in exp.dispatchers:
            make_dispatcher(name, 30)


def test_capacity_search_finds_where_the_queue_starts_growing():
    config = Config(10, 2, 4)
    rate = handling_capacity(config, "lunch", "round-robin", seeds=2, duration=1200, steps=2)
    assert keeps_up(config, "lunch", "round-robin", rate / 2, seeds=2, duration=1200)
    assert not keeps_up(config, "lunch", "round-robin", rate * 2, seeds=2, duration=1200)
