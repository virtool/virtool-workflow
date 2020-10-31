from typing import Dict, Any

from .hooks import hook
from virtool_workflow.workflow import Workflow
from virtool_workflow.execution.workflow_executor import WorkflowError, State, WorkflowExecution


@hook
def on_result(workflow: Workflow, result: Dict[str, Any]):
    pass


@hook
def on_update(workflow: WorkflowExecution, update: str):
    pass


@hook
def on_workflow_step(executor: WorkflowExecution):
    pass


@hook
def on_state_change(old_state: State, new_state: State):
    pass


@hook
def on_error(error: WorkflowError):
    pass



