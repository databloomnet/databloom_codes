# rate_limiter.py

from collections import deque 
import time
"""
offers rate limiters - in this case used for genai calls
usage:
    rate_limiter = RateLimiter(max_request=5, interval_sec = 5)
    if not rate_limiter.allow():
        print("sorry, rate limited")
    print(rate_limiter.status())

uses a double ended queue
"""

RATE_LIMITER_DEFAULT_MAX_REQUESTS = 10
RATE_LIMITER_DEFAULT_INTERVAL_SECONDS = 120



class RateLimiter:
    def __init__(self, max_requests = RATE_LIMITER_DEFAULT_MAX_REQUESTS, interval_sec = RATE_LIMITER_DEFAULT_INTERVAL_SECONDS):
        self.max_requests = max_requests
        self.interval = interval_sec
        self.timestamps = deque() # double ended queue 

    def allow(self):
        now = time.time()
        while self.timestamps and now - self.timestamps[0] > self.interval:
            # while 1+ timestamps and the oldest timestamp is greater than interval seconds ago... pop it off
            self.timestamps.popleft()

        # room for another request?
        if len(self.timestamps) < self.max_requests:
            self.timestamps.append(now)
            return True
        
        # throttle
        return False

    def status(self, verbose=False):
        # delete old timestamps
        now = time.time()
        while self.timestamps and now - self.timestamps[0] > self.interval:
            self.timestamps.popleft()

        #if not verbose:
        return f"{len(self.timestamps)} of {self.max_requests} over {self.interval} seconds"
        # else:
        #     queue = str(self.timestamps)
        #     print("queue", len(self.timestamps))
        #     return f"{len(queue)}...{len(self.timestamps)} of {self.max_requests} over {self.interval} seconds"

