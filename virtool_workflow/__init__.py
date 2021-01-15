"""An SDK for defining Virtool workflows."""
from virtool_workflow.execution import hooks
from virtool_workflow.execution.hooks.hooks import hook, Hook
from virtool_workflow.execution.workflow_executor import WorkflowExecution, State, WorkflowError
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow.fixtures.workflow_fixture import fixture
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
    "FixtureScope",
    "fixture",
    "Workflow",
    "step",
    "cleanup",
    "startup",
]
