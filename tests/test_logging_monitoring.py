import pytest
import os
import logging
from src.logging_monitoring import setup_logging, log_event, monitor_metrics

@pytest.fixture
def mock_log_file():
    """
    Fixture to create a temporary log file for testing.
    """
    log_file = "test_log.log"
    yield log_file
    if os.path.exists(log_file):
        os.remove(log_file)

def test_setup_logging(mock_log_file):
    """
    Test setting up the logging configuration.
    """
    setup_logging(log_file=mock_log_file)
    logger = logging.getLogger("trading_bot")
    assert logger.level == logging.INFO, "Logger should be set to INFO level"
    assert os.path.exists(mock_log_file), "Log file should be created"

def test_log_event(mock_log_file):
    """
    Test logging events to the log file.
    """
    setup_logging(log_file=mock_log_file)
    log_event("info", "This is a test info message")
    log_event("error", "This is a test error message")

    with open(mock_log_file, "r") as f:
        logs = f.read()
    assert "INFO:trading_bot:This is a test info message" in logs, "Info log should be written to the log file"
    assert "ERROR:trading_bot:This is a test error message" in logs, "Error log should be written to the log file"

def test_log_event_invalid_level(mock_log_file):
    """
    Test handling invalid log levels.
    """
    setup_logging(log_file=mock_log_file)
    with pytest.raises(ValueError):
        log_event("invalid_level", "This is a test message")

def test_monitor_metrics():
    """
    Test the monitoring metrics function.
    """
    metrics = {
        "total_trades": 100,
        "successful_trades": 90,
        "profit_percentage": 12.5,
    }
    monitor_output = monitor_metrics(metrics)

    assert "Total Trades: 100" in monitor_output, "Output should contain total trades"
    assert "Successful Trades: 90" in monitor_output, "Output should contain successful trades"
    assert "Profit Percentage: 12.5%" in monitor_output, "Output should contain profit percentage"
