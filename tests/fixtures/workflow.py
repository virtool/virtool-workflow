import pytest
from virtool_workflow import workflow, WorkflowExecutionContext


@pytest.fixture
def test_workflow():
    _test_workflow = workflow.Workflow()

    @_test_workflow.startup
    async def startup(ctx, results):
        results["start"] = True
        assert isinstance(ctx, WorkflowExecutionContext)
        ctx.important_variable = "IMPORTANT"

    @_test_workflow.cleanup
    async def cleanup(ctx, result):
        result["clean"] = True
        assert ctx.important_variable == "IMPORTANT"

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
