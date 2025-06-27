"""Tests for utility functions."""

import structlog

from virtool_workflow.utils import configure_logs


def test_configure_logs_handles_exception_level():
    """Test that configure_logs properly handles the EXCEPTION log level."""
    configure_logs(use_sentry=False)
    logger = structlog.get_logger("test_logger")

    try:
        raise ValueError("Test error")
    except Exception:
        logger.exception()


def test_logger_reconfiguration_after_configure_logs():
    """Test that existing loggers work properly after configure_logs is called."""
    # Create logger before configure_logs (simulating the original issue)
    structlog.get_logger("runtime")

    # Configure logs
    configure_logs(use_sentry=False)

    # Recreate logger after configure_logs (simulating the fix)
    logger_after = structlog.get_logger("runtime")

    # Test that exception logging works without raising ValueError
    try:
        raise ValueError("Test error")
    except Exception:
        logger_after.exception("Test exception logging")
