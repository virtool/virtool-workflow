from typing import Dict, Any

from .hooks import hook
from virtool_workflow.execution.workflow_executor import WorkflowError, State


@hook
def on_result(result: Dict[str, Any]):
    pass


@hook
def on_update(update: str):
    pass


@hook
def on_state_change(old_state: State, new_state: State):
    pass


@hook
def on_error(error: WorkflowError):
    pass


