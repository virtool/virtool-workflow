from virtool_workflow.workflow import Workflow
from virtool_workflow.execution import hooks
from virtool_workflow.execution.hooks.hooks import hook
from virtool_workflow.execution.hooks.workflow_hooks import workflow_hook, on_workflow_finish


@hook
async def example_hook_without_params():
    pass


async def test_hook():

    @example_hook_without_params.callback
    async def callback():
        callback.called = True

    await example_hook_without_params.trigger()

    assert callback.called


async def test_temporary_callback():

    @example_hook_without_params.temporary_callback(on_workflow_finish)
    def temporary_callback():
        pass

    assert temporary_callback in example_hook_without_params.callbacks

    await on_workflow_finish.trigger(Workflow(), {})

    assert temporary_callback not in example_hook_without_params.callbacks
    assert "remove_callback" not in [f.__name__ for f in example_hook_without_params.callbacks]


