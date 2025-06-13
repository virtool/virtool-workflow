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
