"""Functional API for workflow execution."""
from . import workflow_executor
from ..workflow import Workflow
from ..fixtures.scope import FixtureScope
from typing import Dict, Any


async def execute(workflow: Workflow, scope: FixtureScope = None) -> Dict[str, Any]:
    """Execute a workflow."""
    if not scope:
        scope = FixtureScope()
    with scope as fixtures:
        return await workflow_executor.WorkflowExecution(workflow, fixtures)

