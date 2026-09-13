import asyncio
import time
from typing import Dict

class AsyncTokenThrottle:
    """Async token bucket / interval throttler to prevent spamming upstream providers."""
    def __init__(self, min_interval: float = 1.0):
        self.min_interval = min_interval
        self.last_called: float = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_called
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
            self.last_called = time.monotonic()

class SyncThrottle:
    """Synchronous throttle for thread-based provider requests."""
    def __init__(self, min_interval: float = 1.0):
        self.min_interval = min_interval
        self.last_called: float = 0.0

    def acquire(self):
        now = time.monotonic()
        elapsed = now - self.last_called
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_called = time.monotonic()
