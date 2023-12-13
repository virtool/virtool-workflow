import pytest
from aioredis import Redis
from virtool_core.redis import configure_redis


@pytest.fixture
async def push_job_id_to_redis(redis: Redis):
    """
    Push a job ID to the Redis list for the workflow.
    """

    async def func(redis_list_name: str, job_id: str):
        await redis.rpush(redis_list_name, job_id)

    return func


@pytest.fixture
async def redis(redis_connection_string: str):
    """
    Push a job ID to the Redis list for the workflow.
    """
    async with configure_redis(redis_connection_string) as redis:
        yield redis


@pytest.fixture
async def redis_connection_string(request) -> str:
    """The connection string to the Redis test database."""
    base_connection_string = request.config.getoption("redis_connection_string")

    connection_string = f"{base_connection_string}/0"

    async with configure_redis(connection_string) as _redis:
        await _redis.flushdb()

    return connection_string
