"""An SDK for defining Virtool workflows."""
from virtool_workflow.execution import hooks
from virtool_workflow.execution.hooks.hooks import hook, Hook
from virtool_workflow.execution.workflow_executor import WorkflowExecution, State, WorkflowError
from virtool_workflow.fixtures.scope import \
    WorkflowFixtureScope, \
    WorkflowFixtureMultipleYield, \
    WorkflowFixtureNotAvailable
from virtool_workflow.fixtures.workflow_fixture import WorkflowFixture, fixture
from virtool_workflow.workflow import Workflow
from virtool_workflow.decorator_api import step, cleanup, startup

__fixtures__ = [
    "virtool_workflow.storage.paths"
]

__all__ = [
    "hooks",
    "hook",
    "Hook",
    "WorkflowExecution",
    "WorkflowError",
    "State",
    "WorkflowFixtureScope",
    "WorkflowFixtureNotAvailable",
    "WorkflowFixtureMultipleYield",
    "WorkflowFixture",
    "fixture",
    "Workflow",
    "step",
    "cleanup",
    "startup",
]
