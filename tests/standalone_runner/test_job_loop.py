from contextlib import suppress

import asyncio
from pathlib import Path

from virtool_workflow.data_model import Job
from virtool_workflow_runtime.cli import main
from virtool_workflow_runtime.hooks import on_init, on_docker_container_exit, on_redis_connect

TEST_IMAGE_MAP_JSON = Path(__file__).parent / "default_images.json"


@on_docker_container_exit
def job_container_exit(_, tasks):
    job_container_exit.called = True
    tasks["job_loop"].cancel()


async def test_containers_are_started_when_jobs_are_given_to_redis():
    @on_init(once=True)
    def set_job_provider(scope):
        scope["job_provider"] = lambda id_: Job(id_, {}, task="test")

    @on_redis_connect(once=True)
    async def submit_a_job(redis, redis_job_list_name):
        await redis.lpush(redis_job_list_name, "test_job")

    with suppress(asyncio.CancelledError):
        await main(workflow_to_docker_image=TEST_IMAGE_MAP_JSON)

    assert job_container_exit.called


async def test_containers_are_stopped_when_jobs_are_cancelled():
    @on_init(once=True)
    def set_job_provider(scope):
        scope["job_provider"] = lambda id_: Job(id_, {}, task="loop")

    @on_redis_connect(once=True)
    async def submit_a_job_and_cancel(redis, redis_job_list_name, redis_cancel_list_name):
        await redis.lpush(redis_job_list_name, "test_job")

        async def _wait_and_send_cancel():
            await asyncio.sleep(1)
            await redis.publish(redis_cancel_list_name, "test_job")

        asyncio.create_task(_wait_and_send_cancel())

        submit_a_job_and_cancel.called = True

    with suppress(asyncio.CancelledError):
        await main(workflow_to_docker_image=TEST_IMAGE_MAP_JSON)

    assert job_container_exit.called
    assert submit_a_job_and_cancel.called
