"""Create Workflows by decorating module scope functions."""
from types import ModuleType

from virtool_workflow import Workflow


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
    Build a Workflow using the functions in a module which have been marked using a `workflow_marker`.

    Since Python 3.7 dictionaries maintain insertion order. A side effect of this is that a module's
    __dict__ attribute maintains **definition** order, since attributes are added to the dict as they
    are defined.

    The same is true in Python 3.6, however it is an implementation detail. This function may not work
    as intended in versions of python previous to 3.6 as it assumes that a module's __dict__ attribute is
    in definition order.

    :param module: A module containing functions tagged by the `workflow_marker` decorators.
    :return Workflow: A workflow build using the tagged functions.
    """

    workflow = Workflow()
    for marked in [value for value in module.__dict__.values() if hasattr(value, "__workflow_marker__")]:
        if marked.__workflow_marker__ == "startup":
            workflow.startup(marked)
        elif marked.__workflow_marker__ == "step":
            workflow.step(marked)
        elif marked.__workflow_marker__ == "cleanup":
            workflow.cleanup(marked)

    return workflow








