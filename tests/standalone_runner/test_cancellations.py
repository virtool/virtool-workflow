from contextlib import suppress

from virtool_workflow_runtime.cli import main
from virtool_workflow_runtime.hooks import on_start


async def test_watch_cancel_task_is_running():
    @on_start(once=True)
    def check_watch_cancel_is_running(tasks):
        assert not tasks["watch_cancel"].done()
        check_watch_cancel_is_running.called = True

    with suppress(Exception):
        await main()

    assert check_watch_cancel_is_running.called
