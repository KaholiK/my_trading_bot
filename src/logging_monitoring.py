# src/logging_monitoring.py

import logging
from prometheus_client import start_http_server, Summary, Counter, Gauge

# Metrics
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
TRADE_EXECUTED = Counter('trade_executed_total', 'Total number of trades executed')
TRADE_FAILED = Counter('trade_failed_total', 'Total number of trades failed')
PORTFOLIO_VALUE = Gauge('portfolio_value', 'Current portfolio value')

def setup_prometheus(port: int = 8001):
    """
    Starts a Prometheus metrics server.
    
    :param port: Port to serve metrics on.
    """
    start_http_server(port)
    logging.info(f"Prometheus metrics server started on port {port}")

def setup_logging():
    """
    Configures logging for the application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    return logger
