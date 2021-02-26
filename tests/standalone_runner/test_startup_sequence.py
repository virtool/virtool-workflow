from typing import AsyncGenerator

from aioredis import Redis

from virtool_workflow.data_model import Job
from virtool_workflow_runtime.hooks import on_redis_connect, on_exit, on_init, on_start, on_docker_connect


@on_init
def set_job_provider(scope):
    scope["job_provider"] = lambda id_: Job(id_, {})


async def test_startup_sequence(loopless_main):
    @on_redis_connect(once=True)
    async def check_redis_connection(redis):
        assert isinstance(redis, Redis)
        await redis.ping()
        check_redis_connection.called = True

    @on_exit(once=True)
    async def check_redis_closed(redis):
        assert redis.closed
        check_redis_closed.called = True

    await loopless_main()

    assert check_redis_connection.called
    assert check_redis_closed.called


async def test_jobs_generator_is_instantiated(loopless_main):
    @on_start
    async def push_to_jobs_list(redis: Redis, redis_job_list_name: str, jobs: AsyncGenerator[Job, None]):
        await redis.lpush(redis_job_list_name, "1")

        job = await jobs.__anext__()

        assert isinstance(job, Job)
        assert job.id == "1"

        push_to_jobs_list.called = True

    await loopless_main()

    assert push_to_jobs_list.called


async def test_docker_client_available(loopless_main):
    @on_docker_connect(once=True)
    async def check_docker_client(docker):
        assert docker
        assert docker.ping()

        check_docker_client.called = True

    await loopless_main()

    assert check_docker_client.called
