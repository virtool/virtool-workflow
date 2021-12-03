from asyncio import create_task

from aioredis import Redis
from virtool_core.redis import connect_to_redis, periodically_ping_redis

from .runtime import prepare_workflow, run_workflow


async def redis_jobs(list_name: str, redis: Redis) -> str:
    """An async generator yielding redis job IDs."""
    while True:
        _, _id = await redis.blpop(list_name)
        yield str(_id, encoding="utf-8")


async def run_jobs_from_redis(
    list_name: str,
    redis_url: str,
    **config,
):
    """Run jobs from a redis list."""
    redis = await connect_to_redis(redis_url)
    ping_task = create_task(periodically_ping_redis(redis))

    async with prepare_workflow(**config) as workflow:
        async for job_id in redis_jobs(list_name, redis):
            config["job_id"] = job_id
            await run_workflow(workflow, config)

    ping_task.cancel()
    await ping_task
