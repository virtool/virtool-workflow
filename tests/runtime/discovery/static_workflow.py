from virtool_workflow.decorator_api import *

@step
async def _step(wf, ctx):
    wf.results["step"] = True



@startup
async def _startup(wf, ctx):
    wf.results["start"] = True


@cleanup
async def _cleanup(wf, ctx):
    wf.results["clean"] = True


