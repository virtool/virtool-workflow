from virtool_workflow.execution.hooks.fixture_hooks import FixtureHook
from fixtures import FixtureScope

test_hook = FixtureHook("test_hook")


async def test_trigger():
    hook_triggered = False

    @test_hook
    async def use_test_hook(item1, item2, some_fixture):
        nonlocal hook_triggered
        hook_triggered = True
        assert item1 == "item1"
        assert item2 == "item2"
        assert some_fixture == "some_fixture"

    async with FixtureScope() as scope:
        scope["some_fixture"] = "some_fixture"

        await test_hook.trigger(scope, item1="item1", item2="item2")

    assert hook_triggered
