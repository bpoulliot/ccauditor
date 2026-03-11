import random
import threading
import time


class CanvasRateLimiter:
    """
    Token bucket rate limiter designed for Canvas API workloads.

    Prevents:
    • request bursts
    • DNS exhaustion
    • connection pool starvation
    """

    def __init__(
        self,
        rate=8,          # requests per second
        burst=12,        # burst allowance
        min_sleep=0.02,  # baseline jitter
        max_sleep=0.15,
    ):
        self.rate = rate
        self.capacity = burst
        self.tokens = burst
        self.last_refill = time.time()
        self.lock = threading.Lock()

        self.min_sleep = min_sleep
        self.max_sleep = max_sleep

    def acquire(self):
        """
        Block until a request token is available.
        """

        while True:

            with self.lock:

                now = time.time()
                elapsed = now - self.last_refill

                # refill tokens
                refill = elapsed * self.rate

                if refill > 0:
                    self.tokens = min(self.capacity, self.tokens + refill)
                    self.last_refill = now

                if self.tokens >= 1:
                    self.tokens -= 1
                    return

            # sleep with jitter outside lock
            time.sleep(random.uniform(self.min_sleep, self.max_sleep))


canvas_rate_limiter = CanvasRateLimiter()