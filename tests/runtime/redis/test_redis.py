import asyncio
import pytest
import concurrent.futures._base

from virtool_workflow import WorkflowError
from virtool_workflow_runtime._redis import \
    connect, \
    redis_list, \
    monitor_cancel, \
    VIRTOOL_JOBS_CANCEL_CHANNEL
from virtool_workflow_runtime.config.configuration import redis_connection_string, \
    redis_job_list_name, \
    db_name, \
    db_connection_string
from virtool_workflow_runtime.runtime import execute_from_redis,\
    execute_while_watching_for_cancellation
from virtool_workflow import hooks
from virtool_workflow_runtime.db import VirtoolDatabase


@pytest.fixture()
async def job_ids():
    _job_ids = [str(n) for n in range(3)]

    jobs = VirtoolDatabase(db_name(), db_connection_string())["jobs"]

    for id_ in _job_ids:
        await jobs.insert_one(dict(_id=id_, args=dict()))

    return _job_ids


async def assert_correct_job_ids(job_ids):
    async with connect(redis_connection_string()) as redis:
        queue = redis_list(redis, redis_job_list_name())
        for id_ in job_ids:
            _id = await queue.__anext__()
            assert _id == id_


async def publish_job_ids(job_ids):
    async with connect(redis_connection_string()) as redis:
        name = redis_job_list_name()
        for id_ in job_ids:
            await redis.lpush(name, id_)


async def run_workflows_from_redis(test_workflow, job_ids):
    exec_ = execute_from_redis(workflow=test_workflow)
    for _ in job_ids:
        result = await exec_.__anext__()
        assert result["start"] and result["clean"]
        assert result["1"] and result["2"]


async def test_job_id_queue(job_ids):
    asyncio.create_task(publish_job_ids(job_ids))
    await assert_correct_job_ids(job_ids)


async def test_execute_from_redis(test_workflow, job_ids):
    asyncio.create_task(publish_job_ids(job_ids))
    await run_workflows_from_redis(test_workflow, job_ids)


async def test_cancellation_monitoring(test_workflow):

    async with connect(redis_connection_string()) as redis:
        wait = asyncio.create_task(asyncio.sleep(10000))
        wait_for_cancel = asyncio.create_task(monitor_cancel(redis, "1", wait))

        # Give monitor_cancel routine enough time to get started.
        await asyncio.sleep(0.1)

        await redis.publish(VIRTOOL_JOBS_CANCEL_CHANNEL, "1")

        cancelled = await wait_for_cancel

        assert cancelled.cancelled()


async def test_execute_from_redis_with_cancellation(test_workflow):
    @test_workflow.step
    async def _step():
        await asyncio.sleep(1000)

    @hooks.on_failure
    def failure():
        failure.called = True

    @hooks.on_cancelled
    def cancelled():
        cancelled.called = True

    async with connect(redis_connection_string()) as redis:
        running = asyncio.create_task(execute_while_watching_for_cancellation("1", test_workflow, redis))

        # give monitor_cancel routine enough time to get started
        await asyncio.sleep(0.1)

        await redis.publish(VIRTOOL_JOBS_CANCEL_CHANNEL, "1")

        try:
            await running
        except (asyncio.CancelledError, concurrent.futures._base.CancelledError, WorkflowError) as e:
            if isinstance(e, WorkflowError):
                if not isinstance(e.cause, asyncio.CancelledError):
                    assert isinstance(e.cause, concurrent.futures._base.CancelledError)

            assert failure.called
            assert cancelled.called
            return

        assert False









