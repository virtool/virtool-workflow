from virtool_workflow.execution.hooks.fixture_hooks import FixtureHook
from virtool_workflow.fixtures.scope import FixtureScope

test_hook = FixtureHook("test_hook", [str, str], None)


async def test_trigger():

    hook_triggered = False

    @test_hook
    def use_test_hook(item1, item2, some_fixture):
        nonlocal hook_triggered
        hook_triggered = True
        assert item1 == "item1"
        assert item2 == "item2"
        assert some_fixture == "some_fixture"

    with FixtureScope() as scope:
        scope["some_fixture"] = "some_fixture"

        await test_hook.trigger(scope, "item1", "item2")

    assert hook_triggered


