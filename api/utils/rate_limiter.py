from fastapi import HTTPException, Request
from starlette.requests import Request
import time
from functools import wraps


class RateLimiter:
    def __init__(self, max_calls, time_frame):
        self.max_calls = max_calls
        self.time_frame = time_frame
        self.calls = {}

    def is_allowed(self, key):
        current_time = time.time()
        if key in self.calls:
            call_history = self.calls[key]
            while call_history and call_history[-1] <= current_time - self.time_frame:
                call_history.pop()
            if len(call_history) >= self.max_calls:
                return False
        else:
            self.calls[key] = []
        self.calls[key].append(current_time)
        return True


rate_limiter = RateLimiter(max_calls=5, time_frame=60)


def rate_limit(max_calls: int, time_frame: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            key = f"{request.client.host}:{func.__name__}"
            if not rate_limiter.is_allowed(key):
                raise HTTPException(
                    status_code=429, detail="Too many requests")
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
