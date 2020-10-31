from virtool_workflow import Workflow, hooks, hook


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

    print(example_hook_without_params.callbacks)

    @example_hook_without_params.callback_until(hooks.on_result)
    def temporary_callback():
        pass

    print(hooks.on_result.callbacks)

    assert temporary_callback in example_hook_without_params.callbacks

    await hooks.on_result.trigger(Workflow(), {})

    assert "remove_callback" not in [f.__name__ for f in example_hook_without_params.callbacks]
    assert temporary_callback not in example_hook_without_params.callbacks


