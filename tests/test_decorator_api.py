import sys

from virtool_workflow import step
from virtool_workflow.decorator_api import collect


@step
def step_z(results: dict):
    results["step"] = True


@step
def step_a(results: dict):
    results["step2"] = True
    assert results["step"]


async def test_decorator_api_workflow(runtime):
    workflow = collect(sys.modules[__name__])

    result = await runtime.execute(workflow)

    assert result["step"]
    assert result["step2"]
