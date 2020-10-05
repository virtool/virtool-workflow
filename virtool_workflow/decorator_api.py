"""Provide a static interface to workflow development using a backing global variable."""
from .workflow import Workflow
from .execute import execute

# Create a new workflow only if `workflow` is undefined (the first time the module is imported)
try:
    workflow
except NameError:
    workflow = Workflow()

step = workflow.step
startup = workflow.startup
cleanup = workflow.cleanup

async def execute_workflow(**kwargs):
    return await execute(workflow, **kwargs)




