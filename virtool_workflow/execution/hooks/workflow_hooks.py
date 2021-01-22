from virtool_workflow.execution.hooks import FixtureHook
from virtool_workflow.execution.workflow_execution import State

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


__all__ = [
    "on_result",
    "on_update",
    "on_workflow_step",
    "on_workflow_failure",
    "on_workflow_finish",
    "on_state_change",
]
