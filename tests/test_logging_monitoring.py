# tests/test_logging_monitoring.py

import pytest
import logging
from src.logging_monitoring import setup_logging, log_event, monitor_metrics, metrics, log_performance
import time
import threading

def test_setup_logging(caplog):
    """
    Test if logging is set up correctly.
    """
    setup_logging()
    log_event("Test event")
    assert "Test event" in caplog.text, "Log should contain the test event"

def test_log_event(caplog):
    """
    Test if log_event correctly logs an event.
    """
    setup_logging()
    with caplog.at_level(logging.INFO):
        log_event("Sample log event")
    assert "Sample log event" in caplog.text, "Log should contain the sample event"

def test_log_performance(caplog):
    """
    Test if log_performance correctly logs the event duration.
    """
    setup_logging()
    with caplog.at_level(logging.INFO):
        start_time = time.time()
        time.sleep(0.1)  # Simulate some processing
        log_performance("test_event", start_time)
    assert "Event 'test_event' took" in caplog.text, "Performance log should be present"

def test_monitor_metrics():
    """
    Test the monitor_metrics function runs without errors.
    Since it's a placeholder, ensure it doesn't raise exceptions.
    """
    try:
        # Run monitor_metrics in a separate thread to prevent blocking
        thread = threading.Thread(target=monitor_metrics, daemon=True)
        thread.start()
        time.sleep(1)  # Allow some time for the thread to run
    except Exception as e:
        pytest.fail(f"monitor_metrics failed with exception: {e}")

