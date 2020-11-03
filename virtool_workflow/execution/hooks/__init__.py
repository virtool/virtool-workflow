from typing import Dict, Any

from .hooks import Hook
from virtool_workflow.workflow import Workflow
from virtool_workflow.execution.workflow_executor import WorkflowError, State, WorkflowExecution
from virtool_workflow_runtime.hooks import on_failure, on_success, on_finish, on_load_fixtures


on_result = Hook("on_result", [Workflow, Dict[str, Any]], None)
on_update = Hook("on_update", [WorkflowExecution, str], None)
on_workflow_step = Hook("on_workflow_step", [WorkflowExecution], None)
on_state_change = Hook("on_state_change", [State, State], None)
on_error = Hook("on_error", [WorkflowError], None)
on_workflow_failure = Hook("on_workflow_finish", [Exception, WorkflowExecution], None)
on_workflow_finish = Hook("on_workflow_finish", [Workflow], None)


@on_workflow_failure
async def _trigger_finish_from_failure(_, execution):
    await on_workflow_finish.trigger(execution.workflow)


@on_result
async def _trigger_finish_from_success(workflow, _):
    await on_workflow_finish.trigger(workflow)



