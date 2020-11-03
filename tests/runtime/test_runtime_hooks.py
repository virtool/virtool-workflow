from virtool_workflow_runtime import hooks
from virtool_workflow_runtime import runtime
from virtool_workflow import Workflow


async def test_on_finish_triggered():

    success_called = False
    finish_called = False

    @hooks.on_success
    def success_callback():
        nonlocal success_called
        success_called = True

    @hooks.on_finish
    def finish_callback():
        nonlocal finish_called
        finish_called = True

    await runtime.execute("1", Workflow())

    assert success_called
    assert finish_called


async def test_on_failure_triggered():

    failure_called = False

    @hooks.on_failure
    def failure_callback(error):
        nonlocal failure_called
        failure_called = True

        assert isinstance(error.cause, ValueError)

    workflow = Workflow()

    @workflow.step
    def step():
        raise ValueError("test error")

    try:
        await runtime.execute("1", workflow)
    except Exception:
        pass

    assert failure_called


async def test_on_failure_not_triggered_when_successful():

    @hooks.on_success
    def success_callback(_, results):
        results["SUCCESS"] = True

    @hooks.on_failure
    def failure_callback(_):
        raise RuntimeError("Failure hook incorrectly triggered.")

    workflow = Workflow()

    result = await runtime.execute("1", workflow)

    assert result["SUCCESS"]



