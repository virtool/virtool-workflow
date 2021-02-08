import asyncio
from aioredis import Redis
from typing import AsyncGenerator
from typing import Dict

from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow_runtime._redis import redis_channel
from virtool_workflow_runtime.hooks import on_redis_connect, on_init, on_exit


@on_init
def create_running_jobs_list(scope: FixtureScope):
    scope["tasks"] = {}
    scope["running_jobs"] = {}


async def watch_cancel(cancel_channel: AsyncGenerator, running_jobs: Dict[str, asyncio.Task]):
    async for job_id in cancel_channel:
        if job_id in running_jobs:
            running_jobs[job_id].cancel(f"This job ({job_id}) has been cancelled via Redis.")


@on_redis_connect
def start_cancellation_watcher(redis: Redis, redis_cancel_list_name: str,
                               tasks: dict, running_jobs: Dict[str, asyncio.Task]):
    cancel_channel = redis_channel(redis, redis_cancel_list_name)
    tasks["watch_cancel"] = asyncio.create_task(watch_cancel(cancel_channel, running_jobs))


@on_exit
def cancel_cancellation_watcher(tasks: Dict[str, asyncio.Task]):
    tasks["watch_cancel"].cancel()
