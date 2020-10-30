from virtool_workflow.execution.hooks import hook
from virtool_workflow import Workflow, WorkflowExecutionContext
from virtool_workflow.execution.execution_hooks import on_error


@hook
async def example_hook_without_params():
    pass


async def test_hook():

    @example_hook_without_params.callback
    async def callback():
        callback.called = True

    await example_hook_without_params.trigger()

    assert callback.called


async def test_on_error():

    @on_error.callback
    def error_callback(error: Exception, workflow: Workflow, context: WorkflowExecutionContext):
        pass

    await on_error.trigger(ValueError(), Workflow(), WorkflowExecutionContext())






