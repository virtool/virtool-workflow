import aioredis
from .runtime import run_workflow, prepare_workflow


async def redis_jobs(list_name: str, redis: aioredis.Redis) -> str:
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
    redis = await aioredis.create_redis_pool(redis_url)

    async with prepare_workflow(**config) as workflow:
        async for job_id in redis_jobs(list_name, redis):
            config["job_id"] = job_id
            await run_workflow(workflow, config)
