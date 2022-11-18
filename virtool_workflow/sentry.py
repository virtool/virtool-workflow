import logging
from logging import getLogger
from typing import Optional

import pkg_resources
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

logger = getLogger("runtime")


def configure_sentry(dsn: Optional[str], event_level: int = logging.ERROR):
    """
    Initialize Sentry for log aggregation.
    """
    if dsn is None:
        return

    logger.info(f"Initializing Sentry dsn='{dsn[:15]}...'")

    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            LoggingIntegration(
                event_level=event_level,
            )
        ],
        release=pkg_resources.get_distribution("virtool-workflow").version,
        traces_sample_rate=0.2,
    )
