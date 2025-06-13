import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from structlog import get_logger

from virtool_workflow.utils import get_virtool_workflow_version

logger = get_logger("runtime")


def configure_sentry(dsn: str | None) -> None:
    """Initialize Sentry for log aggregation."""
    if dsn:
        logger.info("initializing sentry", dsn=f"{dsn[:15]}...")

        sentry_sdk.init(
            dsn=dsn,
            integrations=[
                LoggingIntegration(
                    event_level=logging.WARNING,
                ),
            ],
            release=get_virtool_workflow_version(),
            traces_sample_rate=0.2,
        )
    else:
        logger.info("sentry disabled because no dsn was provided")


def set_workflow_context(
    workflow_name: str,
    job_id: str,
    workflow_version: str | None = None,
):
    """Set workflow context for Sentry reporting."""
    sentry_sdk.set_context(
        "workflow",
        {
            "workflow_name": workflow_name,
            "workflow_version": workflow_version,
            "virtool_workflow_version": get_virtool_workflow_version(),
            "job_id": job_id,
        },
    )
