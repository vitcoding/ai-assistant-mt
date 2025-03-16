from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis

from api import router
from core.config import settings
from db import redis
from middleware.rate_limiter import RateLimiterMiddleware
from middleware.tracing import TracingMiddleware
from middleware.user_agent import UserAgentMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    yield
    await redis.redis.close()


# App configuration
app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.add_middleware(UserAgentMiddleware)

app.add_middleware(TracingMiddleware)

if settings.enable_tracer:
    FastAPIInstrumentor.instrument_app(app)

app.add_middleware(
    RateLimiterMiddleware,
    max_requests_per_window_size=60_000,
    window_size_in_seconds=60,
)

# Router connection to the server
app.include_router(router, prefix="/api")
