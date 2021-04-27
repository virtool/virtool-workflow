from contextlib import suppress

from virtool_workflow import hooks, Workflow


async def test_on_finish_triggered(runtime):
    success_called = False
    finish_called = False

    @hooks.on_success(once=True)
    def success_callback():
        nonlocal success_called
        success_called = True

    @hooks.on_finish(once=True)
    def finish_callback():
        nonlocal finish_called
        finish_called = True

    await runtime.execute(Workflow())

    assert success_called
    assert finish_called


async def test_on_failure_triggered(runtime):
    failure_called = False

    @hooks.on_failure(once=True)
    def failure_callback():
        nonlocal failure_called
        failure_called = True

    workflow = Workflow()

    @workflow.step
    def step():
        raise ValueError("test error")

    with suppress(Exception):
        await runtime.execute(workflow)

    assert failure_called


async def test_on_failure_not_triggered_when_successful(runtime):
    @hooks.on_success(once=True)
    def success_callback(results):
        results["SUCCESS"] = True

    @hooks.on_failure(once=True)
    def failure_callback():
        raise RuntimeError("Failure hook incorrectly triggered.")

    result = await runtime.execute(Workflow())

    assert result["SUCCESS"] is True
