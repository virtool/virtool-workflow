import pytest
from virtool_core.redis import connect


@pytest.fixture
async def redis(redis_service):
    _redis = await connect(redis_service)
    try:
        yield _redis
    finally:
        _redis.close()
        await _redis.wait_closed()
