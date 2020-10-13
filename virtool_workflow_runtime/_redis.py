"""Collect new Virtool Jobs from a redis list"""
import aioredis
import contextlib

VIRTOOL_JOBS_CHANNEL = "channel:dispatch"


@contextlib.asynccontextmanager
async def connect(address: str):
    redis_ = await aioredis.create_redis_pool(address)
    yield redis_
    redis_.close()
    await redis_.wait_closed()


async def job_id_queue(redis_connection: str, channel: str = VIRTOOL_JOBS_CHANNEL):
    """
    Exposes the redis jobs channel for Virtool Jobs as an async generator

    :param redis_connection: The URL address of the redis database
    :param channel: The redis channel to which job id's are published
    :yields str: The database (mongo) id's for each job to be executed
    :raise ConnectionRefusedError: When redis is not available at the given URL
    """
    async with connect(redis_connection) as redis:
        async for message in redis.subscribe(channel).iter():
            yield message
