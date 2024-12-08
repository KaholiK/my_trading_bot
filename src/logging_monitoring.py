# src/logging_monitoring.py

import logging
from typing import Dict, Any
import time

# Configure root logger
logger = logging.getLogger("AI_Trading_Bot")
logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels

# Console handler with a simple formatter
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)  # Set to INFO for general logs
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

# File handler for detailed logs
fh = logging.FileHandler("logs/trading_bot.log")
fh.setLevel(logging.DEBUG)  # Detailed logs in file
fh.setFormatter(formatter)
logger.addHandler(fh)

class MetricsCollector:
    """
    Collects and stores metrics.
    """
    def __init__(self):
        self.metrics: Dict[str, float] = {}

    def increment(self, name: str, amount: float = 1.0):
        if name not in self.metrics:
            self.metrics[name] = 0.0
        self.metrics[name] += amount
        logger.debug(f"Incremented metric {name} by {amount}, total: {self.metrics[name]}")

    def set_metric(self, name: str, value: float):
        self.metrics[name] = value
        logger.debug(f"Set metric {name} to {value}")

    def get_metric(self, name: str) -> float:
        return self.metrics.get(name, 0.0)

    def report_metrics(self) -> Dict[str, float]:
        logger.info(f"Reporting Metrics: {self.metrics}")
        return dict(self.metrics)

metrics = MetricsCollector()

def log_performance(event_name: str, start_time: float):
    """
    Logs the performance of a specific event.
    """
    elapsed = time.time() - start_time
    logger.info(f"Event '{event_name}' took {elapsed:.4f} seconds")
    metrics.set_metric(f"event_{event_name}_time", elapsed)

def setup_logging():
    """
    Additional logging setup if needed.
    Currently, logging is configured at the module level.
    This function can be expanded for more handlers or formatters.
    """
    pass  # Placeholder for future enhancements

def log_event(event: str):
    """
    Logs a generic event with INFO level.
    """
    logger.info(event)

def monitor_metrics():
    """
    Placeholder for real-time monitoring logic.
    In the future, integrate with Prometheus or other monitoring tools.
    """
    # Example: Periodically report metrics
    while True:
        time.sleep(60)  # Report every 60 seconds
        metrics.report_metrics()

__all__ = ["setup_logging", "log_event", "monitor_metrics", "metrics", "log_performance"]
