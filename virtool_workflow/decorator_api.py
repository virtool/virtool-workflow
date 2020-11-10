from types import ModuleType

from virtool_workflow import Workflow


def startup(func):
    func._is_workflow_startup_function = True
    return func


def cleanup(func):
    func._is_workflow_cleanup_function = True
    return func


def step(func):
    func._is_workflow_step_function = True
    return func


def collect(module: ModuleType) -> Workflow:

    # From python 3.7+ dictionary order is guaranteed to be insertion order.
    # So, for a module, __dict__ is in definition order.

    workflow = Workflow()
    for value in module.__dict__.values():
        if hasattr(value, "_is_workflow_startup_function"):
            workflow.startup(value)
        elif hasattr(value, "_is_workflow_step_function"):
            workflow.step(value)
        elif hasattr(value, "_is_workflow_cleanup_function"):
            workflow.cleanup(value)

    return workflow








