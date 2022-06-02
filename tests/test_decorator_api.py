import sys

from virtool_workflow import step
from virtool_workflow.decorator_api import collect


@step
def step_z(results: dict):
    results["step"] = True


@step(name="Foobar")
def step_a(results: dict):
    results["step2"] = True
    assert results["step"]


async def test_decorator_api_workflow(runtime):
    workflow = collect(sys.modules[__name__])

    result = await runtime.execute(workflow)

    assert result["step"]
    assert result["step2"]


def test_step_decorator_does_set_display_name():
    workflow = collect(sys.modules[__name__])

    assert workflow.steps[1].display_name == "Foobar"
