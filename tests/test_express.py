"""Express cars: they stop only at their floors, and only get passengers they can serve."""

from __future__ import annotations

import pytest

from elevator_sim import Config, Request, Simulation
from elevator_sim.__main__ import parse_express
from elevator_sim.dispatch import EtdDispatcher, RoundRobinDispatcher
from elevator_sim.scenarios import generate

EXPRESS = {2: frozenset({1, *range(16, 31)}), 3: frozenset({1, *range(16, 31)})}


def test_parse_express():
    assert parse_express("2,3:1,16-30") == EXPRESS
    assert parse_express("0:1-3,5") == {0: frozenset({1, 2, 3, 5})}


@pytest.mark.parametrize("dispatcher", [RoundRobinDispatcher, EtdDispatcher])
def test_express_cars_only_serve_their_floors(dispatcher):
    config = Config(30, 4, 10, express=EXPRESS)
    result = Simulation(config, generate("lunch", 30, 0.6, 400, seed=0), dispatcher()).run()
    express_riders = [p for p in result.passengers if p.car_id in EXPRESS]
    assert express_riders  # they do get used
    for p in express_riders:
        assert {p.source, p.dest} <= EXPRESS[p.car_id]
    assert all(p.dropoff_time is not None for p in result.passengers)


def test_unservable_request_rejected():
    config = Config(10, 1, 4, express={0: frozenset({1, 10})})
    with pytest.raises(ValueError, match="no car serves"):
        Simulation(config, [Request(0, "a", 1, 5)], EtdDispatcher())


def test_invalid_express_config_rejected():
    with pytest.raises(ValueError):
        Config(10, 2, 4, express={5: frozenset({1})})       # no car 5
    with pytest.raises(ValueError):
        Config(10, 2, 4, express={0: frozenset({1, 11})})   # no floor 11
