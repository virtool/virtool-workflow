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

on_step_start = FixtureHook("on_step_start")
"""
Triggered before each workflow step is executed.

The :class:`WorkflowStep` object is available via the `current_step` fixture.

.. code_block:: python
    
    @on_step_start
    async def use_step(current_step):
        ...
"""


on_step_finish = FixtureHook("on_step_end")
"""
Triggered after each workflow step is executed.

The :class:`WorkflowStep` object is available via the `current_step` fixture.

@on_step_finish
async def use_step(current_step):
    ...
"""


on_workflow_start = FixtureHook("on_workflow_start")
"""
Triggered at the start of the workflow, before any steps are executed.
"""


__all__ = [
    "on_result",
    "on_step_finish",
    "on_step_start",
    "on_workflow_start",
]
