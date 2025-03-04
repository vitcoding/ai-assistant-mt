import uuid
from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware

from api import router
from core.config import settings
from core.jaeger import tracer
from core.logger import log
from db import elastic, redis


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Подключение к базам при старте сервера
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    elastic.es = AsyncElasticsearch(
        hosts=[
            f"{settings.elastic_schema}{settings.elastic_host}:"
            f"{settings.elastic_port}"
        ]
    )
    yield
    # Отключение от баз при выключении сервера
    await redis.redis.close()
    await elastic.es.close()


# Конфигурация приложения
app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.add_middleware(TracingMiddleware)
FastAPIInstrumentor.instrument_app(app)


# @app.middleware("http")
# async def before_request(request: Request, call_next):
#     response = await call_next(request)
#     request_id = request.headers.get("X-Request-Id")
#     if not request_id:
#         return ORJSONResponse(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             content={"detail": "X-Request-Id is required"},
#         )
#     return response


# Подключение роутера к серверу
app.include_router(router, prefix="/api")
