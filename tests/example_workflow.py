from virtool_workflow import Workflow

workflow = Workflow()


@workflow.startup
async def on_startup(*_):
    return "Started up"


@workflow.step
async def step(*_):
    return "Step"


@workflow.cleanup
async def on_cleanup(*_):
    return "Cleaned up"
