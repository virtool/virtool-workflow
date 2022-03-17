import logging
import pkg_resources
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


logger = logging.getLogger(__name__)


def sentry_init(dsn: str, dev: bool):
    """
    Initialize Sentry for log aggregation.
    """
    logger.info(f"Initializing Sentry with DSN {dsn[:20]}...")
    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            LoggingIntegration(
                level=logging.DEBUG if dev else logging.INFO,
                event_level=logging.ERROR,
            )
        ],
        release=pkg_resources.get_distribution('virtool-workflow').version,
        traces_sample_rate=0.2,
    )
