import time
from datetime import timedelta

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Rate limitter middleware."""

    def __init__(
        self,
        app: ASGIApp,
        max_requests_per_window_size: int = 60_000,
        window_size_in_seconds: int = 60,
    ):
        super().__init__(app)
        self.max_requests_per_window_size = max_requests_per_window_size
        self.window_size_in_seconds = window_size_in_seconds
        self.requests: dict[str, int] = {}
        self.last_reset_time = 0

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """The dispatch method for counting requests from the hosts."""

        remote_address = request.client.host
        now = self.current_timestamp()

        if now - self.last_reset_time > self.window_size_in_seconds:
            self.reset_counters(now)

        self.update_counter(remote_address, now)

        if self.is_limit_exceeded(remote_address):
            return Response(status_code=429, content="Too many requests")

        response = await call_next(request)
        return response

    def reset_counters(self, now: int) -> None:
        """Reset counters of the requests."""

        self.requests.clear()
        self.last_reset_time = now

    def update_counter(self, ip: str, now: int) -> None:
        """Update counters for the hosts."""

        if ip in self.requests:
            self.requests[ip] += 1
        else:
            self.requests[ip] = 1

    def is_limit_exceeded(self, ip: str) -> bool:
        """Checking for exceeding the limit."""

        return (
            ip in self.requests
            and self.requests[ip] > self.max_requests_per_window_size
        )

    @staticmethod
    def current_timestamp() -> int:
        """Returns current timestamp."""
        return int(timedelta(seconds=time.monotonic()).total_seconds())
