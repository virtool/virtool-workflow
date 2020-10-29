from virtool_workflow.execution.hooks import hook, trigger_hook


@hook
async def example_hook_without_params():
    pass


async def test_hook():

    @example_hook_without_params.callback
    async def example_callback():
        example_callback.called = True

    example_callback.called = False

    await trigger_hook(example_hook_without_params)

    assert example_callback.called
