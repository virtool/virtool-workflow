import asyncio
import concurrent.futures._base

from virtool_workflow import WorkflowError
from virtool_workflow_runtime._redis import \
    connect, \
    redis_list, \
    monitor_cancel, \
    VIRTOOL_JOBS_CANCEL_CHANNEL
from virtool_workflow_runtime.config.configuration import redis_connection_string, redis_job_list_name
from virtool_workflow_runtime.runtime import execute_from_redis, hooks, \
    execute_while_watching_for_cancellation

JOB_IDs = [str(n) for n in range(3)]


async def assert_correct_job_ids():
    async with connect(redis_connection_string()) as redis:
        queue = redis_list(redis, redis_job_list_name())
        for id_ in JOB_IDs:
            _id = await queue.__anext__()
            assert _id == id_


async def publish_job_ids():
    async with connect(redis_connection_string()) as redis:
        name = redis_job_list_name()
        for id_ in JOB_IDs:
            await redis.lpush(name, id_)


async def run_workflows_from_redis(test_workflow):
    exec_ = execute_from_redis(workflow=test_workflow)
    for _ in JOB_IDs:
        result = await exec_.__anext__()
        assert result["start"] and result["clean"]
        assert result["1"] and result["2"]


async def test_job_id_queue():
    asyncio.create_task(publish_job_ids())
    await assert_correct_job_ids()


async def test_execute_from_redis(test_workflow):
    asyncio.create_task(publish_job_ids())
    await run_workflows_from_redis(test_workflow)


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









