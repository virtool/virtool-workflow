from virtool_workflow import hooks
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

    await runtime.execute(Workflow(), runtime.DirectDatabaseAccessRuntime("1"))

    assert success_called
    assert finish_called


async def test_on_failure_triggered():

    failure_called = False

    @hooks.on_failure(once=True)
    def failure_callback(error):
        nonlocal failure_called
        failure_called = True

        assert isinstance(error.cause, ValueError)

    workflow = Workflow()

    @workflow.step
    def step():
        raise ValueError("test error")

    try:
        await runtime.execute(workflow, runtime.DirectDatabaseAccessRuntime("1"))
    except Exception:
        pass

    assert failure_called


async def test_on_failure_not_triggered_when_successful():

    @hooks.on_success
    def success_callback(results):
        results["SUCCESS"] = True

    @hooks.on_failure
    def failure_callback():
        raise RuntimeError("Failure hook incorrectly triggered.")

    workflow = Workflow()

    result = await runtime.execute(workflow, runtime.DirectDatabaseAccessRuntime("1"))

    assert result["SUCCESS"]

    hooks.on_failure.callbacks.remove(failure_callback)



