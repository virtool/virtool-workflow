import logging
from typing import Optional
import pkg_resources
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


logger = logging.getLogger(__name__)


def configure_sentry(
    dsn: Optional[str], log_level: int, event_level: int = logging.ERROR
):
    """
    Initialize Sentry for log aggregation.
    """
    if dsn is None:
        return

    logger.info(f"Initializing Sentry with DSN {dsn[:20]}...")
    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            LoggingIntegration(
                level=log_level,
                event_level=event_level,
            )
        ],
        release=pkg_resources.get_distribution("virtool-workflow").version,
        traces_sample_rate=0.2,
    )
