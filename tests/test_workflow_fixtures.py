from virtool_workflow.workflow_fixture import *
from inspect import signature


@workflow_fixture
def my_fixture():
    return "FIXTURE"


def test_workflow_fixture_is_registered():
    assert my_fixture.__name__ in WorkflowFixture.types()
    assert my_fixture in WorkflowFixture.types().values()


def test_workflow_fixture_injection():
    def uses_fixture(my_fixture: str):
        assert my_fixture == "FIXTURE"
        uses_fixture.called = True

    with_fixtures_injected = WorkflowFixture.inject(uses_fixture)
    with_fixtures_injected()
    assert uses_fixture.called


async def test_workflow_fixture_injection_on_async_function():
    async def uses_fixture(my_fixture: str):
        assert my_fixture == "FIXTURE"
        uses_fixture.called = True

    with_fixtures_injected = WorkflowFixture.inject(uses_fixture)
    await with_fixtures_injected()
    assert uses_fixture.called
