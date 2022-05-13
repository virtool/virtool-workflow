import pytest
from virtool_workflow import workflow

from fixtures import FixtureScope


@pytest.fixture
async def empty_scope():
    async with FixtureScope() as scope:
        yield scope


@pytest.fixture
def test_workflow():
    _test_workflow = workflow.Workflow()

    @_test_workflow.startup
    async def startup(results):
        results["start"] = True
        return "Startup complete"

    @_test_workflow.cleanup
    async def cleanup(results):
        results["clean"] = True
        return "Cleanup complete"

    @_test_workflow.step
    async def step_1(step_number, results):
        results["1"] = True
        assert step_number == 1
        return "Step 1 complete"

    @_test_workflow.step
    async def step_2(step_number, results):
        results["2"] = True
        assert step_number == 2
        return "Step 2 complete"

    return _test_workflow
