from contextlib import suppress

import asyncio

from virtool_workflow import hooks
from virtool_workflow.execution.hooks.hooks import Hook

example_hook = Hook("example_hook")


async def test_hook():
    @example_hook.callback
    async def callback():
        callback.called = True

    await example_hook.trigger()

    assert callback.called


async def test_temporary_callback(runtime):
    @example_hook(until=hooks.on_result)
    def temporary_callback():
        pass

    assert temporary_callback in example_hook.callbacks

    await hooks.on_result.trigger(runtime)

    assert "remove_callback" not in [f.__name__ for f in example_hook.callbacks]
    assert temporary_callback not in example_hook.callbacks


async def test_failure_behaviour(runtime):
    class SpecificError(Exception):
        ...

    @example_hook
    def raise_error():
        raise SpecificError()

    @example_hook
    async def fine():
        await asyncio.sleep(1)
        print("fine")

    with suppress(SpecificError):
        await example_hook.trigger()
