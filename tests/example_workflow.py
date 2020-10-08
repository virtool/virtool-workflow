from virtool_workflow import Workflow

workflow = Workflow()


@workflow.startup
async def on_startup():
    return "Started up"


@workflow.step
async def step():
    return "Step"


@workflow.cleanup
async def on_cleanup():
    return "Cleaned up"
