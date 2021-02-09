import asyncio
import logging
from aioredis import Redis
from typing import AsyncGenerator
from typing import Dict

from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow_runtime._redis import redis_channel
from virtool_workflow_runtime.hooks import on_redis_connect, on_exit, on_job_cancelled

logger = logging.getLogger(__name__)


async def watch_cancel(cancel_channel: AsyncGenerator, running_jobs: Dict[str, asyncio.Task], scope: FixtureScope):
    logger.debug("Starting `watch_cancel` task.")
    async for job_id in cancel_channel:
        if job_id in running_jobs:
            running_jobs[job_id].cancel(f"This job ({job_id}) has been cancelled via Redis.")
            del running_jobs[job_id]
            logger.info(f"Cancelling job {job_id}.")
            await on_job_cancelled.trigger(scope, job_id)


@on_redis_connect
def start_cancellation_watcher(redis: Redis, redis_cancel_list_name: str,
                               tasks: dict, running_jobs: Dict[str, asyncio.Task],
                               scope: FixtureScope):
    cancel_channel = redis_channel(redis, redis_cancel_list_name)
    logger.debug("Creating watch_cancel task.")
    tasks["watch_cancel"] = asyncio.create_task(watch_cancel(cancel_channel, running_jobs, scope))


@on_exit
def cancel_cancellation_watcher(tasks: Dict[str, asyncio.Task]):
    tasks["watch_cancel"].cancel()
    del tasks["watch_cancel"]
