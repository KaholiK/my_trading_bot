# src/logging_monitoring.py

import logging
from prometheus_client import start_http_server, Summary

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

def setup_prometheus(port: int = 8001):
    """
    Starts a Prometheus metrics server.
    
    :param port: Port to serve metrics on.
    """
    start_http_server(port)
    logging.info(f"Prometheus metrics server started on port {port}")

# Set up logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    return logger
    
