from concurrent import futures

import asyncio
from types import SimpleNamespace

from virtool_workflow.execution.workflow_executor import WorkflowError, State
from virtool_workflow.fixtures.scope import FixtureScope
from .hooks import Hook
from .fixture_hooks import FixtureHook

on_result = FixtureHook("on_result", [], None)
"""
Triggered when a workflow has completed and a result is available.

.. code-block:: python

    @on_result
    async def use_result(workflow: Workflow, results: Dict[str, Any]):
        ...

This Hook is triggered before the result of the workflow is stored. As 
such the result can be mutated within the callback and that change will be 
reflected in the final result. 
"""

on_update = FixtureHook("on_update", [str], None)
"""
Triggered when an update is sent from a Workflow. 

This occurs both when a (*str*) value is returned from a workflow step and when
:func:`virtool_workflow.WorkflowExecution.send_update()` is invoked directly. 

.. code-block:: python

    @on_update
    async def use_updates(execution: WorkflowExecution, update: str):
        ...
"""

on_workflow_step = FixtureHook("on_workflow_step", [], None)
"""
Triggered on each workflow step.

.. code-block:: python

    @on_workflow_step
    async def do_something_on_step(execution: WorkflowExecution):
        ...
"""

on_state_change = FixtureHook("on_state_change", [State, State], None)
"""
Triggered on a change of state during workflow execution.

.. code-block:: python

    @on_workflow_step
    async def do_something_on_state_change(old_state, new_state):
        ...
"""

on_error = FixtureHook("on_error", [WorkflowError], None)
"""
Triggered when an exception occurs during a workflow.

.. code-block:: python

    @on_error
    async def perform_on_error(error: WorkflowError):
        ...
"""

on_workflow_failure = FixtureHook("on_workflow_finish", [Exception], None)
"""
Triggered when a workflow fails to complete.

.. code-block:: python

    @on_on_workflow_failure
    async def perform_on_failure(cause: Exception, execution: WorkflowExecution):
        ...
"""

on_workflow_finish = FixtureHook("on_workflow_finish", [], None)
"""
Triggered when a workflow finishes, regardless of it's success.

.. code-block:: python

    @on_workflow_finish
    async def perform_on_success(workflow: Workflow):
        ...
"""


@on_workflow_failure
async def _trigger_finish_from_failure(_, scope):
    await on_workflow_finish.trigger(scope)


@on_result
async def _trigger_finish_from_success(scope):
    await on_workflow_finish.trigger(scope)


on_success = FixtureHook("on_success", parameters=[], return_type=None)
"""
Triggered when a job completes successfully.

Parameters supplied are the `Workflow` instance and the results dict.

.. code-block:: python

    @on_success
    async def perform_on_success(workflow: Workflow, results: Dict[str, Any]):
        ...
"""


on_failure = FixtureHook("on_failure", parameters=[WorkflowError], return_type=None)
"""
Triggered when a job fails to complete.

.. code-block:: python

    @on_failure
    async def perform_on_failure(error: WorkflowError):
        ...
"""


on_finish = FixtureHook("on_finish", parameters=[], return_type=None)
"""
Triggered when a job finishes, regardless of success or failure.

.. code-block:: python

    @on_finish
    async def perform_on_finish(workflow: Workflow):
        ...
"""


@on_success
async def _trigger_on_finish_from_on_success(scope: FixtureScope):
    await on_finish.trigger(scope)


@on_failure
async def _trigger_on_finish_from_on_failure(error: WorkflowError, scope: FixtureScope):
    await on_finish.trigger(scope, error.workflow)


on_cancelled = FixtureHook("on_cancelled", [asyncio.CancelledError], None)
"""
Triggered when a job is cancelled.

.. code-block:: python

    @on_cancelled
    async def on_cancelled(error: asyncio.CancelledError):
        ...
"""


@on_failure
async def _trigger_on_cancelled(error: WorkflowError, scope: FixtureScope):
    if isinstance(error.cause, asyncio.CancelledError) or isinstance(error.cause, futures.CancelledError):
        await on_cancelled.trigger(scope, error.cause)


on_load_fixtures = FixtureHook("on_load_fixtures", [FixtureScope], return_type=None)
"""
Triggered after runtime fixtures have been added to the #WorkflowFixtureScope, but
before the workflow is executed.

Enables modification or injection of specific fixtures before a workflow is executed.

.. code-block:: python

    @on_load_fixtures
    async def change_fixture_values(fixtures: WorkflowFixtureScope):
        fixtures["some_fixture"] = SOME_VALUE
        await fixtures.get_or_instantiate("name_of_some_other_fixture)
        ...
"""

on_load_config = Hook("on_load_config", [SimpleNamespace], None)
"""
Triggered after the config is loaded from the CLI arguments and environment variables. A SimpleNamespace object
is provided which has an attribute (sharing the same name as the fixture) for each configuration fixture in
:mod:`virtool_workflow_runtime.config.configuration`. 

.. code-block:: python

    @on_load_config
    def use_config(config: SimpleNamespace):
        if config.dev_mode:
            ...
"""

before_result_upload = FixtureHook("before_result_upload", [], None)
"""Triggered after the result is ready to be uploaded, but before it is actually uploaded."""

__all__ = [
    "on_result",
    "on_update",
    "on_workflow_step",
    "on_success",
    "on_failure",
    "on_workflow_failure",
    "on_workflow_finish",
    "on_finish",
    "on_load_config",
    "on_load_fixtures",
    "before_result_upload",
    "on_cancelled",
    "on_state_change",
    "Hook",
    "FixtureHook",
]
