import asyncio
import signal
import logging
from typing import Any, Coroutine
from contextlib import suppress

from virtool_workflow.workflow import Workflow


sigterm_received = False
logger = logging.getLogger(__name__)


async def shutdown():
    logger.info("received SIGTERM.. shutting down")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    logger.info(f"Cancelling {len(tasks)} remaining tasks")

    for t in tasks:
        t.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)


def configure_signal_handling():
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(
        signal.SIGTERM, 
        lambda *_: asyncio.create_task(shutdown())
    )
