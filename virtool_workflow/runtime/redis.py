from .runtime import run_workflow, prepare_workflow
from aioredis import create_redis


async def run_jobs_from_redis(
    list_name: str,
    redis_url: str,
    **config,
):
    """Run jobs from a redis list."""
    redis = await create_redis(redis_url)

    async with prepare_workflow(**config) as workflow:
        while True:
            config["job_id"] = await redis.blpop(list_name, encoding="utf-8")
            await run_workflow(workflow, config)
