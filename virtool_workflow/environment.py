from typing import Dict, Any

from virtool_workflow.abc import AbstractWorkflowEnvironment
from virtool_workflow.data_model import Job
from virtool_workflow.execution.workflow_execution import WorkflowExecution
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow.fixtures.workflow_fixture import workflow_fixtures
from virtool_workflow.workflow import Workflow


class WorkflowEnvironment(AbstractWorkflowEnvironment, FixtureScope):

    def __init__(self, job: Job, *providers, **instances):
        self.load_plugins(
            "virtool_workflow.execution.fixtures",
            "virtool_workflow.storage.paths",
            "virtool_workflow.config.configuration"
        )

        self.job = self["job"] = job

        super(WorkflowEnvironment, self).__init__(
            workflow_fixtures,
            *providers,
            **instances)

        self.override("job_args", lambda: job.args)

    async def execute(self, workflow: Workflow) -> Dict[str, Any]:
        """Execute a Workflow."""
        return await WorkflowExecution(workflow, self)

    async def execute_function(self, func: callable):
        """Execute a function in the runtime context."""
        result = (await self.bind(func))()

        if hasattr(result, "__await__"):
            result = await result

        return result
