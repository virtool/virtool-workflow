"""Create Workflows by decorating module scope functions."""
from types import ModuleType
from typing import Callable

from virtool_workflow.workflow import Workflow


def step(f: Callable = None, *, name: str = None):
    """
    Mark a function as a workflow step function.

    :param f: the workflow step function
    :param name: the display name of the workflow step. A name
        will be generated based on the function name if not provided.
    """
    if f is None:
        return lambda _f: step(_f, name=name)

    f.__workflow_marker__ = "step"
    f.__workflow_step_props__ = dict(name=name)

    return f


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
            workflow.step(marked, **marked.__workflow_step_props__)

    if len(workflow.steps) == 0:
        raise ValueError(f"No workflow steps could be found in {module}")

    return workflow
