from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

from core.config import settings
from core.logger import log


def configure_tracer(
    service_name: str, jaeger_host: str | None, jaeger_port: int | None
) -> trace:
    """Configures the tracer using OpenTelemetry."""

    resource = Resource.create({"service.name": service_name})
    tracer_provider = TracerProvider(resource=resource)
    jaeger_exporter = JaegerExporter(
        agent_host_name=jaeger_host, agent_port=jaeger_port
    )
    span_processor = BatchSpanProcessor(jaeger_exporter)
    tracer_provider.add_span_processor(span_processor)

    console_exporter = ConsoleSpanExporter()
    tracer_provider.add_span_processor(BatchSpanProcessor(console_exporter))

    trace.set_tracer_provider(tracer_provider)
    log.info("Tracing is configured successfully.")
    return trace.get_tracer(__name__)


tracer = configure_tracer(
    "search-service", settings.jaeger_host, int(settings.jaeger_port)
)
