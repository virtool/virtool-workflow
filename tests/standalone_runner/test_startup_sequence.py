from aioredis import Redis

from virtool_workflow_runtime.cli import main
from virtool_workflow_runtime.hooks import on_redis_connect


async def test_startup_sequence():
    @on_redis_connect
    async def check_redis_connection(redis):
        assert isinstance(redis, Redis)
        await redis.ping()
        check_redis_connection.called = True

    await main()

    assert check_redis_connection.called
