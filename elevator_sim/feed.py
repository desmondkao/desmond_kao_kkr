"""The request feed: the only thing that can see future requests.

Schedulers never touch it. The simulation asks it for requests at time `now`,
and it hands over only those whose time has come.
"""

from __future__ import annotations

from collections import deque

from .models import Request


class RequestFeed:
    def __init__(self, requests: list[Request]):
        self._queue = deque(sorted(requests, key=lambda r: r.time))  # stable: ties keep input order
        self._now = -1

    def release(self, now: int) -> list[Request]:
        if now < self._now:
            raise RuntimeError(f"time went backwards: {now} < {self._now}")
        self._now = now
        out = []
        while self._queue and self._queue[0].time <= now:
            out.append(self._queue.popleft())
        return out

    @property
    def empty(self) -> bool:
        return not self._queue
