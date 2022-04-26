import pytest
from virtool_core.redis import connect_to_redis


@pytest.fixture
async def redis(redis_service):
    _redis = await connect_to_redis(redis_service)
    try:
        yield _redis
    finally:
        _redis.close()
        await _redis.wait_closed()
