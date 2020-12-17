from typing import Callable, Dict, Any

import pytest

from virtool_workflow import WorkflowExecution, WorkflowFixtureScope, Workflow
from virtool_workflow_runtime.abc.runtime import AbstractRuntime
from virtool_workflow_runtime.runtime import runtime_scope


class TestRuntime(AbstractRuntime):
    """Testing harness for Virtool Workflows."""

    def __init__(self):
        self._execution = None
        self.job_args = {}

    async def execute_function(self, func: Callable):
        """Bind runtime fixtures to a function and execute it."""
        return (await self.scope.bind(func))()

    async def execute(self, workflow: Workflow) -> Dict[str, Any]:
        self._execution = WorkflowExecution(workflow, self.scope)
        return await self.execution.execute()

    @property
    def scope(self) -> WorkflowFixtureScope:
        return runtime_scope

    @property
    def execution(self) -> WorkflowExecution:
        return self._execution

    @execution.setter
    def execution(self, _execution: WorkflowExecution):
        self._execution = _execution


@pytest.yield_fixture()
def runtime():
    """The WorkflowFixtureScope which would be used by the runtime."""
    test_environment = TestRuntime()

    with test_environment.scope:
        return test_environment
