# src/logging_monitoring.py

import logging
from typing import Dict, Any
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Response

# Initialize FastAPI app for metrics endpoint
app_metrics = FastAPI(title="AI Trading Bot Metrics")

# Configure root logger
logger = logging.getLogger("AI_Trading_Bot")
logger.setLevel(logging.DEBUG)

# Console handler with a simple formatter
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

# Metrics Setup
REQUEST_COUNT = Counter(
    "requests_total", "Total number of requests received", ["method", "endpoint"]
)
REQUEST_DURATION = Histogram(
    "request_duration_seconds", "Request duration in seconds", ["method", "endpoint"]
)
TRADE_EXECUTIONS = Counter(
    "trade_executions_total", "Total number of trade executions", ["status"]
)

def log_event(event: str, level: str = "info"):
    """
    Logs an event at the specified logging level.
    """
    if level.lower() == "debug":
        logger.debug(event)
    elif level.lower() == "warning":
        logger.warning(event)
    elif level.lower() == "error":
        logger.error(event)
    else:
        logger.info(event)

class MetricsCollector:
    """
    Collects and manages metrics for the trading bot.
    """
    def __init__(self):
        pass  # Metrics are already initialized globally

    def increment_request_count(self, method: str, endpoint: str):
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()

    def observe_request_duration(self, method: str, endpoint: str, duration: float):
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

    def increment_trade_executions(self, status: str):
        TRADE_EXECUTIONS.labels(status=status).inc()

metrics_collector = MetricsCollector()

@app_metrics.middleware("http")
async def metrics_middleware(request, call_next):
    """
    Middleware to collect metrics for each request.
    """
    method = request.method
    endpoint = request.url.path

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    metrics_collector.increment_request_count(method, endpoint)
    metrics_collector.observe_request_duration(method, endpoint, duration)

    return response

@app_metrics.get("/metrics")
async def get_metrics():
    """
    Endpoint to expose metrics for Prometheus.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

def setup_logging():
    """
    Initializes logging configurations.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )

def log_trade_execution(status: str):
    """
    Logs a trade execution event.
    """
    metrics_collector.increment_trade_executions(status)
    if status == "SUCCESS":
        logger.info("Trade executed successfully.")
    else:
        logger.error("Trade execution failed.")

# Ensure that this module does not run as a standalone script
if __name__ == "__main__":
    setup_logging()
    log_event("Logging and Monitoring Module Initialized", "info")

