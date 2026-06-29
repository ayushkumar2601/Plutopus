import time
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Define core observability metrics
API_REQUESTS_TOTAL = Counter(
    "api_requests_total",
    "Total count of incoming API HTTP requests.",
    ["method", "endpoint", "status"]
)

API_REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds",
    "Distribution of API response processing durations.",
    ["method", "endpoint"]
)

PREDICTION_JOBS_TOTAL = Counter(
    "prediction_jobs_total",
    "Telemetry forecasting and anomaly job triggers.",
    ["status"]
)

COPILOT_QUERIES_TOTAL = Counter(
    "copilot_queries_total",
    "AI NOC Copilot user dialogue requests.",
    ["status"]
)

INCIDENTS_GENERATED_TOTAL = Counter(
    "incidents_generated_total",
    "Incident objects created by the correlation engine.",
    ["severity"]
)

WEBHOOK_DELIVERY_TOTAL = Counter(
    "webhook_delivery_total",
    "Outbound incident webhook status tracking.",
    ["status"]
)

async def prometheus_metrics_middleware(request: Request, call_next):
    """
    Middleware registering API requests counters and latency values.
    """
    start_time = time.time()
    endpoint = request.url.path
    method = request.method
    
    response: Response = await call_next(request)
    
    latency = time.time() - start_time
    status = str(response.status_code)
    
    API_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status).inc()
    API_REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
    
    return response

def get_metrics_report() -> Response:
    """
    Renders current Prometheus registry metrics in text exposition format.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
