import asyncio

from virtool_workflow_runtime.hooks import on_start, on_job_cancelled, on_init


@on_init
def set_job_provider(scope):
    scope["job_provider"] = lambda id_: Job(id_, {})


async def test_watch_cancel_task_is_running(loopless_main):
    @on_start(once=True)
    def check_watch_cancel_is_running(tasks):
        assert not tasks["watch_cancel"].done()
        check_watch_cancel_is_running.called = True

    await loopless_main()

    assert check_watch_cancel_is_running.called


async def test_running_jobs_get_cancelled(loopless_main):
    @on_start(once=True)
    async def start_a_mock_job_and_send_cancel_signal_to_redis(redis, redis_cancel_list_name):
        # Allow some time for the `watch_cancel` task to prepare before publishing.
        await asyncio.sleep(0.5)

        await redis.publish(redis_cancel_list_name, "1")

        # Allow some time for redis to inform subscribers.
        await asyncio.sleep(0.5)

    @on_job_cancelled(once=True)
    def check_cancelled(_id):
        assert _id == "1"
        check_cancelled.called = True

    await loopless_main()

    assert check_cancelled.called
