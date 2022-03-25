import asyncio
import logging
from typing import AsyncGenerator
from aioredis import Redis
from virtool_core.redis import connect_to_redis, periodically_ping_redis
from contextlib import asynccontextmanager, suppress
from virtool_workflow.signals import sigterm_received


logger = logging.getLogger(__name__)


@asynccontextmanager
async def configure_redis(url: str) -> AsyncGenerator[Redis, None]:
    """Prepare a redis connection."""
    try:
        redis = await connect_to_redis(url)
    except OSError as e:
        raise ConnectionError(f"Could not connect to Redis at {url}") from e

    ping_task = asyncio.create_task(periodically_ping_redis(redis))

    try:
        yield redis
    finally:
        logger.info("disconnecting from Redis")
        ping_task.cancel()

        with suppress(asyncio.CancelledError):
            await ping_task

        redis.close()
        await redis.wait_closed()


async def get_next_job(list_name: str, redis: Redis, timeout: int = 1) -> str:
    while True:
        if sigterm_received is True:
            raise InterruptedError("SIGTERM signal received")

        result = await redis.blpop(list_name, timeout=timeout)

        if result is not None:
            return str(result[1], encoding="utf-8")
