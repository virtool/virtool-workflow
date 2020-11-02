from typing import Dict, Any

from .hooks import Hook
from virtool_workflow.workflow import Workflow
from virtool_workflow.execution.workflow_executor import WorkflowError, State, WorkflowExecution


on_result = Hook("on_result", [Workflow], Dict[str, Any])
on_update = Hook("on_update", [WorkflowExecution, str], None)
on_workflow_step = Hook("on_workflow_step", [WorkflowExecution], None)
on_state_change = Hook("on_state_change", [State, State], None)
on_error = Hook("on_error", [WorkflowError], None)
