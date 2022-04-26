"""
Hooks provide a way to do things when events happen during the workflow lifecycle.
"""
import asyncio
from concurrent import futures

from virtool_workflow.execution.hooks import Hook

on_result = Hook("on_result")
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

on_step_start = Hook("on_step_start")
"""
Triggered before each workflow step is executed.

The :class:`WorkflowStep` object is available via the `current_step` fixture.

.. code_block:: python

    @on_step_start
    async def use_step(current_step):
        ...
"""

on_step_finish = Hook("on_step_end")
"""
Triggered after each workflow step is executed.

The :class:`WorkflowStep` object is available via the `current_step` fixture.

@on_step_finish
async def use_step(current_step):
    ...
"""

on_workflow_start = Hook("on_workflow_start")
"""
Triggered at the start of the workflow, before any steps are executed.
"""

on_success = Hook("on_success")
"""
Triggered when a job completes successfully.

Parameters supplied are the `Workflow` instance and the results dict.

.. code-block:: python

    @on_success
    async def perform_on_success(workflow: Workflow, results: Dict[str, Any]):
        ...
"""

on_failure = Hook("on_failure")
"""
Triggered when a job fails to complete. The exception
which caused the failure will be found in the `error` fixture.

.. code-block:: python

    @on_failure
    async def perform_on_failure(error: Exception):
        ...
"""

on_finish = Hook("on_finish")
"""
Triggered when a job finishes, regardless of success or failure.

.. code-block:: python

    @on_finish
    async def perform_on_finish(workflow: Workflow):
        ...
"""


on_finalize = Hook("on_finalize")
"""
Triggered after job finishes, regardless of success or failure.

Intended for finalization actions such as closing the fixture scope.
"""


on_cancelled = Hook("on_cancelled")
"""
Triggered when a job is cancelled.

.. code-block:: python

    @on_cancelled
    async def on_cancelled(error: asyncio.CancelledError):
        ...
"""


@on_failure
async def _trigger_on_cancelled(error: Exception, scope):
    if isinstance(error, (asyncio.CancelledError, futures.CancelledError)):
        await on_cancelled.trigger(scope, error)


on_load_config = Hook("on_load_config")
"""
Triggered after the config is loaded from the CLI arguments and environment variables. A SimpleNamespace object
is provided which has an attribute (sharing the same name as the fixture) for each configuration fixture in
:mod:`virtool_workflow_runtime.config.configuration`. 

.. code-block:: python

    @on_load_config
    def use_config(dev_mode):
        if dev_mode:
            ...
"""

before_result_upload = Hook("before_result_upload")
"""Triggered after the result is ready to be uploaded, but before it is actually uploaded."""

__all__ = [
    "on_result",
    "on_success",
    "on_failure",
    "on_finalize",
    "on_finish",
    "on_load_config",
    "before_result_upload",
    "on_cancelled",
    "on_step_start",
    "on_step_finish",
    "on_workflow_start",
]
