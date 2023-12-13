import logging

import pkg_resources
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from structlog import get_logger

logger = get_logger("runtime")


def configure_sentry(dsn: str):
    """
    Initialize Sentry for log aggregation.
    """
    if dsn:
        logger.info("initializing sentry", dsn=f"{dsn[:15]}...")

        sentry_sdk.init(
            dsn=dsn,
            integrations=[
                LoggingIntegration(
                    event_level=logging.WARNING,
                )
            ],
            release=pkg_resources.get_distribution("virtool-workflow").version,
            traces_sample_rate=0.2,
        )
    else:
        logger.info("sentry disabled because no dsn was provided")
