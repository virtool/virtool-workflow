"""Functional API for workflow execution."""
from typing import Dict, Any

from virtool_workflow_runtime.runtime import runtime_scope
from . import workflow_executor
from ..fixtures.scope import FixtureScope
from ..workflow import Workflow


async def execute(workflow: Workflow, scope: FixtureScope = None) -> Dict[str, Any]:
    """Execute a workflow."""
    if not scope:
        scope = runtime_scope
    with scope as fixtures:
        return await workflow_executor.WorkflowExecution(workflow, fixtures)

