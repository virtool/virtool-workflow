import pytest
from aioredis import create_pool, Redis
from virtool_workflow.runtime.redis import redis_jobs


@pytest.fixture
async def redis(redis_url):
    try:
        redis = await create_pool(redis_url)
        yield redis
        redis.close()
    except ConnectionRefusedError:
        pytest.skip("Redis is not available.")


@pytest.mark.asyncio
async def test_redis_jobs_collected(redis: Redis):
    redis_list = "test_jobs_collected"

    target_ids = [str(i) for i in range(10)]

    await redis.lpush(redis_list, *target_ids)

    lst = []
    async for _id in redis_jobs(redis_list, redis):
        lst.append(_id)
        if int(_id) == 0:
            break

    assert lst == list(reversed(target_ids))
