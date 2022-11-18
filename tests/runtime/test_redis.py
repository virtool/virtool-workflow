import pytest
from virtool_core.redis import connect


@pytest.fixture
async def redis(redis_url):
    try:
        _redis = await connect(redis_url)
        yield _redis
        _redis.close()
        await _redis.wait_closed()
    except ConnectionRefusedError:
        pytest.skip("Redis is not available.")
