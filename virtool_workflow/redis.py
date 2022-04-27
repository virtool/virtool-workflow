import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from typing import AsyncGenerator

import aioredis
from aioredis import Redis
from virtool_core.redis import periodically_ping_redis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def configure_redis(url: str, timeout=1) -> AsyncGenerator[Redis, None]:
    """Prepare a redis connection."""
    redis = None
    ping_task = None

    try:
        logger.info(f"Attempting Redis connection at {url}")
        redis = await aioredis.create_redis_pool(url, timeout=timeout)
        ping_task = asyncio.create_task(periodically_ping_redis(redis))
        logger.info(f"Connected to Redis at {url}")
        yield redis
    finally:
        if ping_task is not None and redis is not None:
            logger.info("Disconnecting from Redis")
            ping_task.cancel()

            with suppress(asyncio.CancelledError):
                await ping_task

            redis.close()
            await redis.wait_closed()


async def get_next_job_with_timeout(
    list_name: str, redis: Redis, timeout: int = None
) -> str:
    """
    Get the next job ID from a Redis list and raise a  :class:``Timeout`` error if one
    is not found in ``timeout`` seconds.

    :param list_name: the name of the list to pop from
    :param redis: the Redis client
    :param timeout: seconds to wait before raising :class:``Timeout``
    :return: the next job ID

    """
    logger.info(f"Waiting for a job for {timeout if timeout else 'infinity'} seconds")
    return await asyncio.wait_for(get_next_job(list_name, redis), timeout)


async def get_next_job(list_name: str, redis: Redis) -> str:
    """
    Get the next job ID from a Redis list.

    :param list_name: the name of the list to pop from
    :param redis: the Redis client
    :return: the next job ID

    """
    if result := await redis.blpop(list_name) is not None:
        return str(result[1], encoding="utf-8")
