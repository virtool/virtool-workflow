"""Create Workflows by decorating module scope functions."""
from types import ModuleType

from virtool_workflow.workflow import Workflow


def workflow_marker(marker_name: str):
    """Create a decorator to mark a function for use within a workflow."""

    def _marker(func):
        func.__workflow_marker__ = marker_name
        return func

    return _marker


startup = workflow_marker("startup")
"""Mark a function as a workflow startup function."""
cleanup = workflow_marker("cleanup")
"""Mark a function as a workflow cleanup function."""
step = workflow_marker("step")
"""Mark a function as a workflow step function."""


def collect(module: ModuleType) -> Workflow:
    """
    Build a Workflow using marked functions from a module.

    .. warning::
        Since Python 3.7, dictionaries maintain insertion order.
        A side effect of this is that a module's __dict__ attribute
        maintains **definition** order, since attributes are added to
        the dict as they are defined. This is also the case in python 3.6,
        however it is an implementation detail and not a PEP specification.

        This function may not work as intended in older versions of python.


    :param module: A module containing functions tagged by
                   `workflow_marker` decorators.
    :return Workflow: A workflow build using the tagged functions.
    """

    workflow = Workflow()

    markers = [
        value for value
        in module.__dict__.values()
        if hasattr(value, "__workflow_marker__")
    ]

    for marked in markers:
        if marked.__workflow_marker__ == "startup":
            workflow.startup(marked)
        elif marked.__workflow_marker__ == "step":
            workflow.step(marked)
        elif marked.__workflow_marker__ == "cleanup":
            workflow.cleanup(marked)

    if (
        len(workflow.steps)
        + len(workflow.on_startup)
        + len(workflow.on_cleanup)
    ) == 0:
        raise ValueError(f"No workflow steps could be found in {module}")

    return workflow
