import asyncio

from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow_runtime.cli import init
from virtool_workflow_runtime.hooks import on_start, on_job_cancelled


async def test_watch_cancel_task_is_running():
    @on_start(once=True)
    def check_watch_cancel_is_running(tasks):
        assert not tasks["watch_cancel"].done()
        check_watch_cancel_is_running.called = True

    with FixtureScope() as fixtures:
        await init(fixtures)

    assert check_watch_cancel_is_running.called


async def test_running_jobs_get_cancelled():
    @on_start(once=True)
    async def start_a_mock_job_and_send_cancel_signal_to_redis(redis, running_jobs, redis_cancel_list_name):
        running_jobs["1"] = asyncio.create_task(asyncio.sleep(10000))

        # Allow some time for the `watch_cancel` task to prepare before publishing.
        await asyncio.sleep(0.5)

        await redis.publish(redis_cancel_list_name, "1")

        # Allow some time for redis to inform subscribers.
        await asyncio.sleep(0.5)

    @on_job_cancelled(once=True)
    def check_cancelled(job_id, running_jobs):
        assert job_id == "1"
        assert job_id not in running_jobs
        check_cancelled.called = True

    with FixtureScope() as fixtures:
        await init(fixtures)
        assert check_cancelled.called
