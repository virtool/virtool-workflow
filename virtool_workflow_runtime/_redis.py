"""Collect new Virtool Jobs from a redis list."""
import asyncio
from typing import Optional
from contextlib import asynccontextmanager

import aioredis

VIRTOOL_JOBS_CANCEL_CHANNEL = "channel:cancel"


class JobCancelledViaRedis(RuntimeError):
    """Raised when a currently executing job is cancelled via the redis cancellation queue."""


@asynccontextmanager
async def connect(address: Optional[str]) -> aioredis.Redis:
    """
    Context manager for a Redis connection

    :param address: The URL for the redis database, when not provided the value of
            the VIRTOOL_REDIS_ADDRESS environment variable is used.
    :return Iterator[aioredis.Redis]: A connection to Redis.
    """
    redis_ = await aioredis.create_redis_pool(address, loop=asyncio.get_event_loop())

    yield redis_

    redis_.close()
    await redis_.wait_closed()


async def redis_channel(redis: aioredis.Redis, channel: str):
    """Expose redis pub/sub channel as an async generator."""
    (channel_,) = await redis.subscribe(channel)
    async for message in channel_.iter(encoding="utf-8"):
        yield message


async def redis_list(redis: aioredis.Redis, list_name: str):
    """Expose redis list as async generator."""
    while True:
        message = await redis.lpop(list_name, encoding="utf-8")
        if message:
            yield message


async def monitor_cancel(redis: aioredis.Redis, current_job_id: str, task: asyncio.Task) -> asyncio.Task:
    """
    Watch the cancel channel in redis for the current job id.

    If the current job id is found, cancel the task.

    :param redis: The redis connection.
    :param current_job_id: The id of the current job.
    :param task: The asyncio task in which the job is being executed.

    :return: The asyncio task object after it has been cancelled.
    """
    async for id_ in redis_channel(redis, VIRTOOL_JOBS_CANCEL_CHANNEL):
        if id_ == current_job_id:
            task.cancel()
            return task
