from . import workflow_executor
from ..workflow import Workflow
from ..fixtures.scope import WorkflowFixtureScope


async def execute(workflow: Workflow):
    with WorkflowFixtureScope() as fixtures:
        return await workflow_executor.WorkflowExecution(workflow, fixtures)

