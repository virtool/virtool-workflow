from virtool_workflow import Workflow
from virtool_workflow.fixtures.errors import FixtureNotAvailable
from virtool_workflow.fixtures.workflow_fixture import fixture


@fixture
def my_fixture():
    return True


def test_workflow_fixture_is_registered(runtime):
    assert my_fixture.__name__ in runtime.available


async def test_workflow_fixture_injection(runtime):
    assert await runtime.execute_function(lambda my_fixture: my_fixture)


async def test_workflow_fixture_injection_on_async_function(runtime):
    async def uses_fixture(my_fixture: str):
        return my_fixture

    assert await runtime.execute_function(uses_fixture)


async def test_fixtures_used_by_fixtures(runtime):
    @fixture
    def fixture_using_fixture(my_fixture: str):
        return my_fixture

    assert await runtime.execute_function(lambda fixture_using_fixture: fixture_using_fixture)


async def test_same_instance_is_used(runtime):
    @fixture
    def dictionary():
        return {}

    def func1(dictionary):
        return dictionary

    def func2(dictionary):
        return dictionary

    d1 = await runtime.execute_function(func1)
    d2 = await runtime.execute_function(func2)

    assert isinstance(d1, dict) and isinstance(d2, dict)
    assert id(d1) == id(d2)


async def test_generator_fixtures_cleanup(runtime):
    cleanup_executed = False

    def generator_fixture():
        yield True
        nonlocal cleanup_executed
        cleanup_executed = True

    await runtime.instantiate(generator_fixture)

    assert runtime["generator_fixture"]

    assert not cleanup_executed
    runtime.close()
    assert cleanup_executed


async def test_workflow_using_fixtures(runtime):
    workflow = Workflow()

    @workflow.step
    def startup(results, my_fixture):
        results["fixture"] = my_fixture

    results = await runtime.execute(workflow)

    assert results["fixture"] and runtime["results"]["fixture"]


async def test_exception_is_raised_when_fixture_not_available(runtime):
    try:
        assert await runtime.execute_function(lambda non_existent_fixture: False)
    except FixtureNotAvailable as not_available:
        assert not_available.param_name == "non_existent_fixture"


async def test_fixture_override(runtime):
    assert await runtime.instantiate(my_fixture)

    runtime.override("my_fixture", lambda: False)

    assert not await runtime.get_or_instantiate('my_fixture')
    assert not await runtime.execute_function(lambda my_fixture: my_fixture)

