"""Collect new Virtool Jobs from a redis list."""

import aioredis
import asyncio

from virtool_workflow.execution.hooks import on_load_config
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow_runtime.hooks import on_redis_connect


@on_load_config
async def connect_to_redis(redis_connection_string: str, scope: FixtureScope):
    scope["redis"] = await aioredis.create_redis_pool(redis_connection_string)
    await on_redis_connect.trigger(scope)


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
