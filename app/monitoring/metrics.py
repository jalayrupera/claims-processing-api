from prometheus_client import Counter, Gauge, Histogram
from prometheus_fastapi_instrumentator import Instrumentator, metrics

http_requests_total = Counter(
    "http_requests_total",
    "Total count of HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

active_requests = Gauge("active_requests", "Number of active HTTP requests")

claim_processing_total = Counter(
    "claim_processing_total", "Total number of claims processed", ["status"]
)


def setup_metrics(app):
    instrumentator = Instrumentator()

    instrumentator.add(metrics.latency())
    instrumentator.add(metrics.requests())

    instrumentator.instrument(app).expose(app, include_in_schema=True, should_gzip=True)

    return instrumentator
