"""Collect new Virtool Jobs from a redis list."""
import asyncio
import contextlib
from os import getenv
from typing import Optional

import aioredis

VIRTOOL_JOBS_CHANNEL = "channel:dispatch"

VIRTOOL_REDIS_ADDRESS_ENV = "VIRTOOL_REDIS_ADDRESS"
VIRTOOL_REDIS_ADDRESS_DEFAULT = "redis://localhost:6379/1"


@contextlib.asynccontextmanager
async def connect(address: Optional[str] = None) -> aioredis.Redis:
    """
    Context manager for a Redis connection

    :param address: The URL for the redis database, when not provided the value of
            the VIRTOOL_REDIS_ADDRESS environment variable is used.
    :return Iterator[aioredis.Redis]: A connection to Redis
    """
    if not address:
        address = getenv(VIRTOOL_REDIS_ADDRESS_ENV, default=VIRTOOL_REDIS_ADDRESS_DEFAULT)

    redis_ = await aioredis.create_redis_pool(address, loop=asyncio.get_event_loop())

    yield redis_

    redis_.close()
    await redis_.wait_closed()


async def job_id_queue(redis_connection: Optional[str] = None,
                       channel: Optional[str] = VIRTOOL_JOBS_CHANNEL):
    """
    Exposes the redis jobs channel for Virtool Jobs as an async generator

    :param redis_connection: The URL address of the redis database, if none provided
        the value of the environment variable VIRTOOL_REDIS_ADDRESS is used
    :param channel: The redis channel to which job id's are published
    :return Iterator[str]: The database (mongo) id's for each job to be executed
    :raise ConnectionRefusedError: When redis is not available at the given URL
    """
    async with connect(redis_connection) as redis:
        (job_ids,) = await redis.subscribe(channel)
        async for message in job_ids.iter():
            yield str(message, encoding="utf-8")
