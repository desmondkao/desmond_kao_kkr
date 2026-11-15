"""Scenario generators."""

from __future__ import annotations

import pytest

from elevator_sim import Config
from elevator_sim.dispatch import RoundRobinDispatcher
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

