import asyncio
from aioredis import Redis
from typing import AsyncGenerator

from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow_runtime._redis import redis_channel
from virtool_workflow_runtime.hooks import on_redis_connect, on_init


@on_init
def create_running_jobs_list(scope: FixtureScope):
    scope["tasks"] = {}
    scope["running_jobs"] = {}


async def watch_cancel(cancel_channel: AsyncGenerator, running_jobs: dict):
    ...


@on_redis_connect
def start_cancellation_watcher(redis: Redis, redis_cancel_list_name: str, tasks: dict, running_jobs: dict):
    cancel_channel = redis_channel(redis, redis_cancel_list_name)

    tasks["watch_cancel"] = asyncio.create_task(watch_cancel(cancel_channel, running_jobs))
