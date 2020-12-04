from virtool_workflow import hooks, hook
from virtool_workflow.execution.hooks.hooks import IncompatibleCallback


@hook
async def example_hook_without_params():
    pass


async def test_hook():

    @example_hook_without_params.callback
    async def callback():
        callback.called = True

    await example_hook_without_params.trigger()

    assert callback.called


async def test_temporary_callback(empty_scope):

    @example_hook_without_params.callback(until=hooks.on_result)
    def temporary_callback():
        pass

    assert temporary_callback in example_hook_without_params.callbacks

    await hooks.on_result.trigger(empty_scope)

    assert "remove_callback" not in [f.__name__ for f in example_hook_without_params.callbacks]
    assert temporary_callback not in example_hook_without_params.callbacks


async def test_return_type_hint_checking_error_raised():

    @hook
    def hook_with_return_hint() -> str:
        pass

    thrown = False

    try:
        @hook_with_return_hint.callback
        def callback_with_return_type_hint() -> int:
            return 1
    except IncompatibleCallback:
        thrown = True

    assert thrown


async def test_return_type_hint_checking():

    @hook
    def hook_with_return_hint() -> str:
        pass

    @hook_with_return_hint.callback
    def no_hints():
        return ""

    @hook_with_return_hint.callback
    def correct_hint() -> str:
        return ""

