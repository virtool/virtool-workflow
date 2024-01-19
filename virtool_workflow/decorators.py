"""Create Workflows by decorating module scope functions."""
from types import ModuleType
from typing import Callable

from virtool_workflow.workflow import Workflow


def step(func: Callable = None, *, name: str | None = None) -> Callable:
    """Mark a function as a workflow step function.

    :param func: the workflow step function
    :param name: the display name of the workflow step. A name
        will be generated based on the function name if not provided.
    """
    if func is None:
        return lambda _f: step(_f, name=name)

    func.__workflow_marker__ = "step"
    func.__workflow_step_props__ = dict(name=name)

    return func


def collect(module: ModuleType) -> Workflow:
    """Build a :class:`.Workflow` object from a workflow module.

    :param module: A workflow module
    :return: A workflow object
    """
    workflow = Workflow()

    markers = [
        value
        for value in module.__dict__.values()
        if hasattr(value, "__workflow_marker__")
    ]

    for marked in markers:
        if marked.__workflow_marker__ == "step":
            workflow.step(marked, **marked.__workflow_step_props__)

    if len(workflow.steps) == 0:
        raise ValueError(f"No workflow steps could be found in {module}")

    return workflow
