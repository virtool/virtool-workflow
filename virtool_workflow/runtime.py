from typing import Dict, Any

from virtool_workflow.abc import AbstractWorkflowEnvironment
from virtool_workflow.data_model import Job
from virtool_workflow.execution.workflow_executor import WorkflowExecution
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow.workflow import Workflow
from virtool_workflow_runtime.config.configuration import config_fixtures
from virtool_workflow.fixtures.workflow_fixture import workflow_fixtures


class WorkflowEnvironment(AbstractWorkflowEnvironment, FixtureScope):

    def __init__(self, job: Job, *providers, **instances):
        self.load_plugins(
            "virtool_workflow.execution.fixtures",
            "virtool_workflow.storage.paths",
            "virtool_workflow_runtime.config.configuration"
        )

        self.job = job

        super(WorkflowEnvironment, self).__init__(
            workflow_fixtures,
            config_fixtures,
            *providers,
            **instances)

        self["job_args"] = job.args

    async def execute(self, workflow: Workflow) -> Dict[str, Any]:
        """Execute a Workflow."""
        return await WorkflowExecution(workflow, self)

    async def execute_function(self, func: callable):
        """Execute a function in the runtime context."""
        result = (await self.bind(func))()

        if hasattr(result, "__await__"):
            result = await result

        return result


