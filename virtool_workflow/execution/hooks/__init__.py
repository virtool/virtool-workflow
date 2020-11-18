from typing import Dict, Any

from .hooks import Hook
from virtool_workflow.workflow import Workflow
from virtool_workflow.execution.workflow_executor import WorkflowError, State, WorkflowExecution


on_result = Hook("on_result", [Workflow, Dict[str, Any]], None)
"""
Triggered when a workflow has completed and a result is available.

```python
@on_result
async def use_result(workflow: Workflow, result: Dict[str, Any]):
    ...
```

This Hook is triggered before the result of the workflow is stored. As 
such the result can be mutated within the callback and that change will be 
reflected in the final result. 
"""

on_update = Hook("on_update", [WorkflowExecution, str], None)
"""
Triggered when an update is sent from a Workflow. 

This occurs both when a (*str*) value is returned from a workflow step and when
#WorkflowExecution.send_update() is invoked directly. 

```python
@on_update
async def use_updates(execution: WorkflowExecution, update: str):
    ...
```
"""

on_workflow_step = Hook("on_workflow_step", [WorkflowExecution], None)
"""
Triggered on each workflow step.

```python
@on_workflow_step
async def do_something_on_step(execution: WorkflowExecution):
    ...
```
"""

on_state_change = Hook("on_state_change", [State, State], None)
"""
Triggered on a change of state during workflow execution.

```python
@on_workflow_step
async def do_something_on_state_change(old_state, new_state):
    ...
```
"""

on_error = Hook("on_error", [WorkflowError], None)
"""
Triggered when an exception occurs during a workflow.

```python
@on_error
async def perform_on_error(error: WorkflowError):
    ...
```
"""

on_workflow_failure = Hook("on_workflow_finish", [Exception, WorkflowExecution], None)
"""
Triggered when a workflow fails to complete.

```python
async def perform_on_failure(cause: Exception, execution: WorkflowExecution):
    ...
```
"""

on_workflow_finish = Hook("on_workflow_finish", [Workflow], None)
"""
Triggered when a workflow finishes, regardless of it's success.

```python
@on_workflow_finish
async def perform_on_success(workflow: Workflow):
    ...
```
"""


@on_workflow_failure
async def _trigger_finish_from_failure(_, execution):
    await on_workflow_finish.trigger(execution.workflow)


@on_result
async def _trigger_finish_from_success(workflow, _):
    await on_workflow_finish.trigger(workflow)



