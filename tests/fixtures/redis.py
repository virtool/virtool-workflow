import pytest

from virtool_core.redis import Redis


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
    redis = Redis(redis_connection_string)
    yield redis


@pytest.fixture
async def redis_connection_string(request) -> str:
    """The connection string to the Redis test database."""
    base_connection_string = request.config.getoption("redis_connection_string")

    connection_string = f"{base_connection_string}/0"

    redis = Redis(connection_string)
    await redis.flushdb()

    return connection_string
