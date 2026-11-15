"""Shared test helpers."""

from __future__ import annotations

import random

from elevator_sim import Request


def random_requests(n: int, floors: int, horizon: int, seed: int) -> list[Request]:
    """n trips between random distinct floors, at random times in [0, horizon]."""
    rng = random.Random(seed)
    out = []
    for i in range(n):
        source, dest = rng.sample(range(1, floors + 1), 2)
        out.append(Request(rng.randint(0, horizon), f"p{i}", source, dest))
    return out
