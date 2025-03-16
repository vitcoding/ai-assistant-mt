import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.jaeger import tracer
from core.logger import log


class TracingMiddleware(BaseHTTPMiddleware):
    """Tracing middleware."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """The tracing middleware dispatch method."""

        log.info("\nMiddleware begining.\n")

        x_request_id = request.headers.get("X-Request-Id")

        if not x_request_id:
            x_request_id = str(uuid.uuid4())

        request.state.request_id = x_request_id

        with tracer.start_as_current_span(
            f"{request.method} {request.url}"
        ) as span:
            span.set_attribute("component", "fastapi")
            response = await call_next(request)

            response.headers["X-Request-Id"] = x_request_id

            log.info("\nMiddleware ending.\n")
            return response
