"""Functional API for workflow execution."""
from . import workflow_executor
from ..workflow import Workflow
from ..fixtures.scope import WorkflowFixtureScope
from typing import Dict, Any


async def execute(workflow: Workflow, scope: WorkflowFixtureScope = None) -> Dict[str, Any]:
    """Execute a workflow."""
    if not scope:
        scope = WorkflowFixtureScope()
    with scope as fixtures:
        return await workflow_executor.WorkflowExecution(workflow, fixtures)

