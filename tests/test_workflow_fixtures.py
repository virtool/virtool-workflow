import inspect
from typing import Dict

from virtool_workflow.execution.execution import execute
from virtool_workflow.fixtures.workflow_fixture import fixture, workflow_fixtures
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow.fixtures.errors import FixtureNotAvailable


@fixture
def my_fixture():
    return "FIXTURE"


def test_workflow_fixture_is_registered():
    assert my_fixture.__name__ in workflow_fixtures


async def test_workflow_fixture_injection():
    def uses_fixture(my_fixture: str):
        assert my_fixture == "FIXTURE"
        uses_fixture.called = True

    with FixtureScope(workflow_fixtures) as scope:
        (await scope.bind(uses_fixture))()

    assert uses_fixture.called


async def test_workflow_fixture_injection_on_async_function():
    async def uses_fixture(my_fixture: str):
        assert my_fixture == "FIXTURE"
        uses_fixture.called = True

    with FixtureScope(workflow_fixtures) as fixtures:
        await (await fixtures.bind(uses_fixture))()

    assert uses_fixture.called


async def test_fixtures_used_by_fixtures():

    @fixture
    def fixture_using_fixture(my_fixture: str):
        return f"FIXTURE_USING_{my_fixture}"

    def use_fixture_using_fixture(fixture_using_fixture: str):
        assert fixture_using_fixture == "FIXTURE_USING_FIXTURE"
        use_fixture_using_fixture.called = True

    with FixtureScope(workflow_fixtures) as scope:
        (await scope.bind(use_fixture_using_fixture))()

    assert use_fixture_using_fixture.called


async def test_same_instance_is_used():

    @fixture
    def dictionary():
        return {}

    with FixtureScope(workflow_fixtures) as scope:

        def func1(dictionary: Dict[str, str]):
            dictionary["item"] = "item"

        def func2(dictionary: Dict[str, str]):
            assert dictionary["item"] == "item"
            dictionary["item"] = "different item"

        func1 = await scope.bind(func1)
        func2 = await scope.bind(func2)

        func1()
        func2()

        assert scope["dictionary"]["item"] == "different item"


async def test_generator_fixtures_cleanup():

    cleanup_executed = False

    @fixture
    def generator_fixture():
        yield "FIXTURE"
        nonlocal cleanup_executed
        cleanup_executed = True

    with FixtureScope(workflow_fixtures) as scope:

        def use_generator_fixture(generator_fixture):
            assert generator_fixture == "FIXTURE"

        await scope.bind(use_generator_fixture)

        assert len(scope._generators) == 1

    assert cleanup_executed


async def test_workflow_using_fixtures(workflow_with_fixtures):
    result = await execute(workflow_with_fixtures)

    assert result["start"] and result["clean"] and result["step"]


async def test_exception_is_raised_when_fixture_not_available():

    async def non_resolvable_fixture_function(fixture_that_doesnt_exist):
        pass

    with FixtureScope(workflow_fixtures) as scope:
        try:
            await scope.bind(non_resolvable_fixture_function)
            assert False
        except FixtureNotAvailable as not_available:
            assert not_available.param_name == "fixture_that_doesnt_exist"
            assert inspect.signature(non_resolvable_fixture_function) == not_available.signature

