from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.types import ASGIApp

from core.logger import log


class UserAgentMiddleware(BaseHTTPMiddleware):
    """Middleware for getting user agent."""

    def __init__(
        self,
        app: ASGIApp,
    ):
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """The dispatch method gets user's device type."""

        user_agent_header = request.headers.get("User-Agent")

        request.state.user_agent = user_agent_header
        log.info(f"\nuser_agent_header: \n{user_agent_header}\n")

        response = await call_next(request)
        return response
