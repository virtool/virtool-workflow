import asyncio
from concurrent import futures
from virtool_workflow import Hook, Workflow, WorkflowError, WorkflowFixtureScope
from typing import Dict, Any

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







