import pytest
import logging
from src.logging_monitoring import setup_logging

def test_logging_setup():
    """
    Test if logging is set up correctly.
    """
    setup_logging()
    logger = logging.getLogger("test_logger")
    logger.info("This is a test log message.")
    assert True, "Logging setup should not raise any exceptions."
