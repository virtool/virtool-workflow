"""Provide a static interface to workflow development using a backing global variable."""
from .workflow import Workflow
from .execute import execute

# Create a new workflow only if `workflow` is undefined (the first time the module is imported)
try:
    _workflow
except NameError:
    _workflow = Workflow()

step = _workflow.step
startup = _workflow.startup
cleanup = _workflow.cleanup

async def execute_workflow(**kwargs):
    return await execute(_workflow, **kwargs)




