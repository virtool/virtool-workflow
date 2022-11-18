import asyncio
from asyncio import CancelledError
from logging import getLogger
from typing import Callable

from aioredis import Redis

logger = getLogger("redis")

CANCELLATION_CHANNEL = "channel:cancel"


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
    result = await redis.blpop(list_name)

    if result is not None:
        job_id = str(result[1], encoding="utf-8")
        logger.info(f"Pulled job from Redis id={job_id}")
        return job_id


async def wait_for_cancellation(redis, job_id: str, func: Callable):
    (channel,) = await redis.subscribe(CANCELLATION_CHANNEL)

    try:
        async for cancelled_job_id in channel.iter():
            if cancelled_job_id.decode() == job_id:
                return func()
    except CancelledError:
        ...
