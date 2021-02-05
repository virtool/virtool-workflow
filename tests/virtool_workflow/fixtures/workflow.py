import pytest
from virtool_workflow import workflow


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
    async def step_1(execution, results):
        results["1"] = True
        assert execution.current_step == 1
        return "Step 1 complete"

    @_test_workflow.step
    async def step_2(execution, results):
        results["2"] = True
        assert execution.current_step == 2
        return "Step 2 complete"

    return _test_workflow
