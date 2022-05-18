"""Create Workflows by decorating module scope functions."""
from types import ModuleType
from typing import Callable

from virtool_workflow.workflow import Workflow


def step(func: Callable):
    """Mark a function as a workflow step function."""
    func.__workflow_marker__ = "step"
    return func


def collect(module: ModuleType) -> Workflow:
    """
    Build a Workflow object from a workflow module.

    .. warning::
        Since Python 3.7, dictionaries maintain insertion order.
        A side effect of this is that a module's __dict__ attribute
        maintains **definition** order, since attributes are added to
        the dict as they are defined. This is also the case in python 3.6,
        however it is an implementation detail and not a PEP specification.

        This function may not work as intended in older versions of python.


    :param module: A workflow module
    :return Workflow: A workflow object
    """

    workflow = Workflow()

    markers = [
        value
        for value in module.__dict__.values()
        if hasattr(value, "__workflow_marker__")
    ]

    for marked in markers:
        if marked.__workflow_marker__ == "step":
            workflow.step(marked)

    if len(workflow.steps) == 0:
        raise ValueError(f"No workflow steps could be found in {module}")

    return workflow
