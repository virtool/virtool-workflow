from virtool_workflow.execution.hooks.fixture_hooks import FixtureHook

on_result = FixtureHook("on_result")
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

on_update = FixtureHook("on_update")
"""
Triggered when an update is sent from a Workflow

This occurs both when a (*str*) value is returned from a workflow step and when
:func:`virtool_workflow.WorkflowExecution.send_update()` is invoked directly.

.. code-block:: python

    @on_update
    async def use_updates(execution: WorkflowExecution, update: str):
        ...
"""

__all__ = [
    "on_result",
    "on_update",
]
