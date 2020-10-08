from typing import Dict

from virtool_workflow.execute_workflow import execute
from virtool_workflow.workflow_fixture import workflow_fixture, WorkflowFixture, WorkflowFixtureScope
from .workflow_with_fixtures import workflow_with_fixtures


@workflow_fixture
def my_fixture():
    return "FIXTURE"


def test_workflow_fixture_is_registered():
    assert my_fixture.__class__.__name__ in WorkflowFixture.types()
    assert my_fixture.__class__ in WorkflowFixture.types().values()


def test_workflow_fixture_injection():
    def uses_fixture(my_fixture: str):
        assert my_fixture == "FIXTURE"
        uses_fixture.called = True

    with WorkflowFixtureScope() as scope:
        scope.bind(uses_fixture)()

    assert uses_fixture.called


async def test_workflow_fixture_injection_on_async_function():
    async def uses_fixture(my_fixture: str):
        assert my_fixture == "FIXTURE"
        uses_fixture.called = True

    with WorkflowFixtureScope() as fixtures:
        await fixtures.bind(uses_fixture)()

    assert uses_fixture.called


async def test_fixtures_used_by_fixtures():

    @workflow_fixture
    def fixture_using_fixture(my_fixture: str):
        return f"FIXTURE_USING_{my_fixture}"

    def use_fixture_using_fixture(fixture_using_fixture: str):
        assert fixture_using_fixture == "FIXTURE_USING_FIXTURE"
        use_fixture_using_fixture.called = True

    with WorkflowFixtureScope() as scope:
        scope.bind(use_fixture_using_fixture)()

    assert use_fixture_using_fixture.called


async def test_preservation_and_injection_of_non_fixture_arguments():

    def use_fixture_and_other_args(arg1: str, my_fixture: str, kwarg=None, other_param=None):
        assert arg1 == "arg1"
        assert kwarg is None
        assert my_fixture == "FIXTURE"
        assert other_param is not None

    with WorkflowFixtureScope() as scope:
        injected = scope.bind(use_fixture_and_other_args, arg1="arg1", other_param="param")
        injected()
        injected(kwarg=None, other_param="stuff")

        injected = scope.bind(use_fixture_and_other_args)

        injected(arg1="arg1", other_param="param")
        injected("arg1", other_param="param")


async def test_same_instance_is_used():

    @workflow_fixture
    def dictionary():
        return {}

    with WorkflowFixtureScope() as scope:

        @scope.bind
        def func1(dictionary: Dict[str, str]):
            dictionary["item"] = "item"

        @scope.bind
        def func2(dictionary: Dict[str, str]):
            assert dictionary["item"] == "item"
            dictionary["item"] = "different item"

        func1()
        func2()

        assert scope._instances["dictionary"]["item"] == "different item"


def test_generator_fixtures_cleanup():

    cleanup_executed = False

    @workflow_fixture
    def generator_fixture():
        yield "FIXTURE"
        nonlocal cleanup_executed
        cleanup_executed = True

    with WorkflowFixtureScope() as scope:

        @scope.bind
        def use_generator_fixture(generator_fixture):
            assert generator_fixture == "FIXTURE"

        assert len(scope._generators) == 1

    assert cleanup_executed


async def test_workflow_using_fixtures(workflow_with_fixtures):
    result = await execute(workflow_with_fixtures)

    assert result["start"] and result["clean"] and result["step"]

