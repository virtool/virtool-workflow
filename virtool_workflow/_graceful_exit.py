import sys
import logging 
import asyncio
from contextlib import suppress

logger = logging.getLogger(__name__)

async def shutdown(exit_code=1, message=None, level=logging.CRITICAL):
    if message:
        logger.log(level, message)

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    logger.info(f"cancelling {len(tasks)} remaining tasks")

    for t in tasks:
        t.cancel()

    with suppress(asyncio.CancelledError):
        await asyncio.gather(*tasks, return_exceptions=True)

    logger.info(f"process finished with exit code {exit_code}")

    sys.stdout.flush()
    sys.stderr.flush()

    sys.exit(exit_code)


    


