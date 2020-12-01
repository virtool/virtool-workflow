import asyncio
from concurrent import futures
from typing import Dict, Any

from .hooks import Hook
from virtool_workflow.workflow import Workflow
from virtool_workflow.fixtures.scope import WorkflowFixtureScope
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


on_success = Hook("on_success", parameters=[Workflow, Dict[str, Any]], return_type=None)
"""
Triggered when a job completes successfully.

Parameters supplied are the `Workflow` instance and the results dict.

```python
@on_success
async def perform_on_success(workflow: Workflow, results: Dict[str, Any]):
    ...
```
"""


on_failure = Hook("on_failure", parameters=[WorkflowError], return_type=None)
"""
Triggered when a job fails to complete.

```python
@on_failure
async def perform_on_failure(error: WorkflowError):
    ...
```
"""


on_finish = Hook("on_finish", parameters=[Workflow], return_type=None)
"""
Triggered when a job finishes, regardless of success or failure.

```python
@on_finish
async def perform_on_failure(error: Workflow):
    ...
```
"""


@on_success
async def _trigger_on_finish_from_on_success(workflow: Workflow, _):
    await on_finish.trigger(workflow)


@on_failure
async def _trigger_on_finish_from_on_failure(error: WorkflowError):
    await on_finish.trigger(error.workflow)


on_cancelled = Hook("on_cancelled", [Workflow, asyncio.CancelledError], None)
"""
Triggered when a job is cancelled.

```python
@on_cancelled
async def on_cancelled(workflow: Workflow, error: asyncio.CancelledError):
    ...
```
"""


@on_failure
async def _trigger_on_cancelled(error: WorkflowError):
    if isinstance(error.cause, asyncio.CancelledError) or isinstance(error.cause, futures.CancelledError):
        await on_cancelled.trigger(error.workflow, error.cause)


on_load_fixtures = Hook("on_load_fixtures", [WorkflowFixtureScope], return_type=None)
"""
Triggered after runtime fixtures have been added to the #WorkflowFixtureScope, but
before the workflow is executed.

Enables modification or injection of specific fixtures before a workflow is executed.

```python
@on_load_fixtures
async def change_fixture_values(fixtures: WorkflowFixtureScope):
    fixtures["some_fixture"] = SOME_VALUE
    await fixtures.get_or_instantiate("name_of_some_other_fixture)
    ...
```
"""

