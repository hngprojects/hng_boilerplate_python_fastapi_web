import time
from typing import Dict
from collections import defaultdict
from fastapi import status, HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from api.core import responses
from api.utils.json_response import JsonResponseDict


RATE_LIMIT = 10  # Number of allowed requests
TIME_WINDOW = 60  # Time window in seconds for rate limiting

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit: int = 1, time_window: int = 1):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.rate_limit_records: Dict[str, float] = defaultdict(float)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        time_since_last_request = current_time - self.rate_limit_records[client_ip]

        # Check if the request is within the rate limit time window
        if time_since_last_request < self.time_window / self.rate_limit:
            return JsonResponseDict(
                message=responses.TOO_MANY_REQUEST, 
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        self.rate_limit_records[client_ip] = current_time
        response = await call_next(request)
        return response