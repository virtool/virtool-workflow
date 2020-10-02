import pytest
from virtool_workflow import execute, workflow

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


async def test_execute(test_workflow):
    result = await execute.execute(test_workflow)
    assert result["start"]
    assert result["1"]
    assert result["2"]
    assert result["clean"]
    

async def test_respond_errors(test_workflow):

    @test_workflow.step
    async def throw_error(wf, ctx):
        raise Exception()

    async def raise_exception(error: execute.WorkflowError):
        assert error.context.current_step == 3
        return "Step 3 skipped due to internal error"

    updates = []
    
    async def receive_updates(ctx, update):
        updates.append(update)


    await execute.execute(test_workflow, on_error=raise_exception, on_update=receive_updates)
    assert "Step 3 skipped due to internal error" in updates


async def test_correct_traceback_data(test_workflow):
    
    @test_workflow.step
    async def raise_exception(_, __):
        raise ValueError("Fake Error", "Other Argument")


    try:
        await execute.execute(test_workflow)
    except execute.WorkflowError as error:
        tb = error.traceback_data
        assert tb["type"] == "ValueError"
        assert len(tb["traceback"]) >= 1
        assert "Other Argument", "Fake Error" in tb["details"]

