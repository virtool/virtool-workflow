"""
Hooks provide a way to do things when events happen during the workflow lifecycle.
"""

from virtool_workflow.runtime.hook import Hook

on_result = Hook("on_result")
"""
Triggered when a workflow has completed and a result is available.

.. code-block:: python

    @on_result
    async def use_result(workflow: Workflow, results: Dict[str, Any]):
        ...
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
async def handle_step_finish(current_step):
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

on_cancelled = Hook("on_cancelled")
"""
Triggered when a job is cancelled.

.. code-block:: python

    @on_cancelled
    async def handle_cancellation(error: asyncio.CancelledError):
        ...
"""

on_error = Hook("on_error")
"""
Triggered when a job encounters an exception while running.

The exception can be found in the ``error`` fixture.

.. code-block:: python

    @on_error
    async def handle_error(error: Exception):
        ...
"""

on_terminated = Hook("on_terminated")
"""
Triggered when the workflow process receives a SIGTERM.

.. code-block:: python

    @on_terminated
    def handle_termination():
        ...
"""

on_failure = Hook("on_failure")
"""
Triggered when a job fails to complete.

Failure to complete can be caused by: user cancellation, termination by the host, or
an error during workflow execution.

.. code-block:: python

    @on_failure
    async def handle_failure(error: Exception):
        ...
"""

on_finish = Hook("on_finish")
"""
Triggered when a job completes, success or failure.

.. code-block:: python

    @on_finish
    async def do_something_on_finish(workflow: Workflow):
        ...
"""

__all__ = [
    "on_cancelled",
    "on_error",
    "on_failure",
    "on_finish",
    "on_result",
    "on_step_finish",
    "on_step_start",
    "on_success",
    "on_terminated",
    "on_workflow_start",
]
