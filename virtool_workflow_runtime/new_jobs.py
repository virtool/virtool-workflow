from aioredis import Redis

from virtool_workflow.abc.data_providers.jobs import JobProviderProtocol
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow_runtime._redis import redis_list
from virtool_workflow_runtime.hooks import on_redis_connect

_job_watcher_task = None


@on_redis_connect
async def create_job_generator(
        redis: Redis,
        redis_job_list_name: str,
        job_provider: JobProviderProtocol,
        scope: FixtureScope,
):
    """Create a :class:`AsyncGenerator` which provides access to incoming jobs."""
    scope["jobs"] = (job_provider(id_) async for id_ in redis_list(redis, redis_job_list_name))
