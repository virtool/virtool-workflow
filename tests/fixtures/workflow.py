import pytest
from virtool_workflow import workflow


@pytest.fixture
def test_workflow():
    _test_workflow = workflow.Workflow()

    @_test_workflow.startup
    async def startup(results):
        results["start"] = True

    @_test_workflow.cleanup
    async def cleanup(result):
        result["clean"] = True

    @_test_workflow.step
    async def step_1(ctx, results):
        results["1"] = True
        print(ctx.current_step)
        print(ctx.state)
        assert ctx.current_step == 1

    @_test_workflow.step
    async def step_2(ctx, results):
        results["2"] = True
        assert ctx.current_step == 2

    return _test_workflow
