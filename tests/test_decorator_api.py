import sys

from virtool_workflow import startup, cleanup, step
from virtool_workflow.decorator_api import collect
from virtool_workflow.execution.execution import execute


@startup
def first(result: dict):
    result["startup"] = True


@step
def step_z(result: dict):
    result["step"] = True


@step
def step_a(result: dict):
    result["step2"] = True
    assert result["step"]


@cleanup
def last(result: dict):
    result["cleanup"] = True


async def test_decorator_api_workflow():
    workflow = collect(sys.modules[__name__])

    result = await execute(workflow)

    assert result["startup"]
    assert result["step"]
    assert result["step2"]
    assert result["cleanup"]



