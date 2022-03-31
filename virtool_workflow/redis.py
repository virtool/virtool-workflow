import asyncio
import logging
import aioredis
from typing import AsyncGenerator
from aioredis import Redis
from virtool_core.redis import periodically_ping_redis
from contextlib import asynccontextmanager, suppress
from virtool_workflow._graceful_exit import shutdown


logger = logging.getLogger(__name__)


@asynccontextmanager
async def configure_redis(url: str, timeout=1) -> AsyncGenerator[Redis, None]:
    """Prepare a redis connection."""
    redis = None
    ping_task = None

    try:
        logger.info(f"attempting Redis connection at {url}")
        redis = await aioredis.create_redis_pool(url, timeout=timeout)
        ping_task = asyncio.create_task(periodically_ping_redis(redis))
        logger.info(f"connected to Redis at {url}")
        yield redis
    finally:
        if ping_task is not None and redis is not None:
            logger.info("disconnecting from Redis")
            ping_task.cancel()

            with suppress(asyncio.CancelledError):
                await ping_task

            redis.close()
            await redis.wait_closed()


async def get_next_job(list_name: str, redis: Redis, timeout: int = None) -> str:
    logger.info(f"waiting for a job; {timeout=}")
    try:
        return await asyncio.wait_for(_get_next_job(list_name, redis), timeout)
    except asyncio.TimeoutError:
        await shutdown(exit_code=124, message=f"failed to find a job within timeout")


async def _get_next_job(list_name: str, redis: Redis) -> str:
    result = await redis.blpop(list_name)

    if result is not None:
        return str(result[1], encoding="utf-8")
