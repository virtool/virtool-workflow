import asyncio
import signal
import logging

from virtool_workflow._graceful_exit import shutdown


logger = logging.getLogger(__name__)


def configure_signal_handling():
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(
        signal.SIGTERM, 
        lambda *_: asyncio.create_task(shutdown(signal.SIGTERM))
    )
