from contextlib import suppress

import asyncio
import logging
from pathlib import Path

from virtool_workflow.data_model import Job
from virtool_workflow_runtime.cli import main
from virtool_workflow_runtime.hooks import on_init, on_docker_container_exit, on_redis_connect, on_job_processed, \
    on_start

TEST_IMAGE_MAP_JSON = Path(__file__).parent / "default_images.json"

logger = logging.getLogger(__name__)


async def test_containers_are_started_when_jobs_are_given_to_redis():
    @on_docker_container_exit(once=True)
    def job_container_exit(_, tasks):
        job_container_exit.called = True
        tasks["job_loop"].cancel()

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
    @on_docker_container_exit(once=True)
    def job_container_exit(_, tasks):
        job_container_exit.called = True
        tasks["job_loop"].cancel()

    @on_init(once=True)
    def set_job_provider(scope):
        scope["job_provider"] = lambda id_: Job(id_, {}, task="loop")

    @on_start(once=True)
    async def submit_a_job(redis, redis_job_list_name):
        await redis.lpush(redis_job_list_name, "test_job")

    @on_job_processed(once=True)
    async def submit_a_job_and_cancel(job, redis, redis_cancel_list_name):
        await asyncio.sleep(1)
        await redis.publish(redis_cancel_list_name, job._id)
        submit_a_job_and_cancel.called = True

    with suppress(asyncio.CancelledError):
        await main(workflow_to_docker_image=TEST_IMAGE_MAP_JSON)

    assert job_container_exit.called
    assert submit_a_job_and_cancel.called


async def test_runner_does_not_execute_multiple_jobs_at_once():
    test_job_processed = False
    second_test_job_processed = False

    @on_init(once=True)
    def set_job_provider(scope):
        scope["job_provider"] = lambda id_: Job(id_, {}, task="test")

    @on_start(once=True)
    async def submit_multiple_jobs(redis, redis_job_list_name):
        await redis.lpush(redis_job_list_name, "test_job")
        await redis.lpush(redis_job_list_name, "second_test_job")

    @on_job_processed
    async def check_jobs(job, tasks):
        nonlocal test_job_processed
        nonlocal second_test_job_processed
        if job._id == "test_job":
            test_job_processed = True
        elif job._id == "second_test_job":
            second_test_job_processed = True

        logger.info(f"{job} {test_job_processed}, {second_test_job_processed}")

        if test_job_processed and second_test_job_processed:
            on_job_processed.callbacks.remove(check_jobs)
            tasks["job_loop"].cancel()

    with suppress(asyncio.CancelledError):
        await main(workflow_to_docker_image=TEST_IMAGE_MAP_JSON)

    assert test_job_processed and second_test_job_processed
