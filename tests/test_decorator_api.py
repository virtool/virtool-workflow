import sys

from virtool_workflow import startup, cleanup, step
from virtool_workflow.decorator_api import collect
from virtool_workflow.execution.execution import execute


@startup
def first(results: dict):
    results["startup"] = True


@step
def step_z(results: dict):
    results["step"] = True


@step
def step_a(results: dict):
    results["step2"] = True
    assert results["step"]


@cleanup
def last(results: dict):
    results["cleanup"] = True


async def test_decorator_api_workflow():
    workflow = collect(sys.modules[__name__])

    result = await execute(workflow)

    assert result["startup"]
    assert result["step"]
    assert result["step2"]
    assert result["cleanup"]



