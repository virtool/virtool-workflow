from virtool_workflow._workflow import execute, workflow
from copy import deepcopy

test_workflow = workflow.Workflow()


@test_workflow.startup
async def startup(wf, ctx):
    wf.results["start"] = True


@test_workflow.cleanup
async def cleanup(wf, ctx):
    wf.results["clean"] = True


@test_workflow.step
async def step_1(wf, ctx):
    wf.results["1"] = True
    assert ctx.current_step == 1


@test_workflow.step
async def step_2(wf, ctx):
    wf.results["2"] = True
    assert ctx.current_step == 2


async def test_execute():
    result = await execute.execute(test_workflow)
    assert result["start"]
    assert result["1"]
    assert result["2"]
    assert result["clean"]
    

async def test_respond_errors():
    wf = deepcopy(test_workflow)


    @wf.step
    async def throw_error(wf, ctx):
        raise Exception()

    
    async def handle_error(error: execute.WorkflowError):
        assert error.context.current_step == 3
        return "Step 3 skipped due to internal error"
    
    async def receive_updates(ctx, update):
        assert update == "Step 3 skipped due to internal error"
    
    await execute.execute(wf, on_error=handle_error, on_update=receive_updates)