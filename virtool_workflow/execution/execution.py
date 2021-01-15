"""Functional API for workflow execution."""
from . import workflow_executor
from ..workflow import Workflow
from ..fixtures.scope import FixtureScope
from ..fixtures.workflow_fixture import workflow_fixtures
from virtool_workflow_runtime.config.configuration import config_fixtures
from virtool_workflow_runtime.runtime import runtime_scope
from typing import Dict, Any


async def execute(workflow: Workflow, scope: FixtureScope = None) -> Dict[str, Any]:
    """Execute a workflow."""
    if not scope:
        scope = runtime_scope
    with scope as fixtures:
        return await workflow_executor.WorkflowExecution(workflow, fixtures)

