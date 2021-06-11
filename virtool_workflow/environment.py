from typing import Dict, Any

from virtool_workflow import hooks
from virtool_workflow.abc import AbstractWorkflowEnvironment
from virtool_workflow.execution.workflow_execution import WorkflowExecution
from virtool_workflow.fixtures import workflow_fixtures
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow.workflow import Workflow


class WorkflowEnvironment(AbstractWorkflowEnvironment, FixtureScope):

    def __init__(self, *providers, **instances):
        super(WorkflowEnvironment, self).__init__(
            workflow_fixtures,
            *providers,
            **instances)

    async def execute(self, workflow: Workflow = None) -> Dict[str, Any]:
        """Execute a Workflow."""
        if workflow is None:
            workflow = self["workflow"]

        return await WorkflowExecution(workflow, self)

    async def execute_function(self, func: callable):
        """Execute a function in the runtime context."""
        result = (await self.bind(func))()

        if hasattr(result, "__await__"):
            result = await result

        return result
