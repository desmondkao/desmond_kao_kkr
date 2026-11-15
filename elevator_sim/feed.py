"""The request feed: the only object that holds future requests.

Schedulers never see it. Each tick the engine asks for requests whose time has
come, so nothing can peek ahead.
"""

from __future__ import annotations

from collections import deque

from .models import Request


class RequestFeed:
    def __init__(self, requests: list[Request]):
        self._queue = deque(sorted(requests, key=lambda r: r.time))  # stable sort: ties keep input order

    def release(self, now: int) -> list[Request]:
        out = []
        while self._queue and self._queue[0].time <= now:
            out.append(self._queue.popleft())
        return out

    @property
    def empty(self) -> bool:
        return not self._queue
