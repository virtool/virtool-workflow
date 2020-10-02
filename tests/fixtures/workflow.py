import pytest
from virtool_workflow import workflow

@pytest.fixture
def test_workflow():
    _test_workflow = workflow.Workflow()


    @_test_workflow.startup
    async def startup(wf, ctx):
        wf.results["start"] = True


    @_test_workflow.cleanup
    async def cleanup(wf, ctx):
        wf.results["clean"] = True


    @_test_workflow.step
    async def step_1(wf, ctx):
        wf.results["1"] = True
        assert ctx.current_step == 1


    @_test_workflow.step
    async def step_2(wf, ctx):
        wf.results["2"] = True
        assert ctx.current_step == 2

    return _test_workflow