"""Collect new Virtool Jobs from a redis list."""

import aioredis

from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow_runtime.hooks import on_redis_connect, on_exit, on_load_config


@on_load_config
async def connect_to_redis(redis_connection_string: str, scope: FixtureScope):
    scope["redis"] = await aioredis.create_redis_pool(redis_connection_string)
    await scope["redis"].ping()
    await on_redis_connect.trigger(scope)


@on_exit
async def close_redis_connection(redis: aioredis.Redis):
    redis.close()
    await redis.wait_closed()


async def redis_channel(redis: aioredis.Redis, channel: str):
    """Expose redis pub/sub channel as an async generator."""
    (channel_,) = await redis.subscribe(channel)
    async for message in channel_.iter(encoding="utf-8"):
        yield message


async def redis_list(redis: aioredis.Redis, list_name: str):
    """Expose redis list as async generator."""
    while True:
        _, message = await redis.blpop(list_name, encoding="utf-8")
        if message:
            yield message
