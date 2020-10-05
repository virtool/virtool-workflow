import virtool_workflow.decorator_api
from virtool_workflow.decorator_api import *

async def test_steps_added():

    @step
    async def _step(wf, ctx):
        wf.results["param"] = True

    assert virtool_workflow.decorator_api.workflow.steps[0] == _step
    assert "param" in await execute_workflow()


async def test_statup_added():

    @startup
    async def _startup(wf, ctx):
        wf.results["start"] = True

    assert virtool_workflow.decorator_api.workflow.on_startup[0] == _startup
    assert "start", "param" in await execute_workflow()

async def test_cleaup_added():

    @cleanup
    async def _cleanup(wf, ctx):
        wf.results["clean"] = True

    assert virtool_workflow.decorator_api.workflow.on_cleanup[0] == _cleanup
    assert "start", "clean" in await execute_workflow()
