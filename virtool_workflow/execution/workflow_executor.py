from virtool_workflow import Workflow
from virtool_workflow.execution.execute_workflow import WorkflowError
from virtool_workflow.execution.hooks import create_hook
from virtool_workflow.fixtures.scope import WorkflowFixtureScope
from typing import Optional, Callable, Coroutine, Any
from enum import Enum

State = Enum("State", "WAITING STARTUP RUNNING CLEANUP FINISHED")


class WorkflowExecutor:

    def __init__(self, workflow: Workflow, scope: WorkflowFixtureScope):
        self.workflow = workflow
        self.scope = scope

        self.on_update = create_hook("on_update", str)
        self.on_state_change = create_hook("on_state_change", State, State)
        self.on_error = create_hook("on_error", WorkflowError, return_type=Optional[str])
        self.on_step = create_hook("on_step", WorkflowExecutor)

        self._updates = []
        self._state = State.WAITING
        self.current_step = 0
        self.progress = 0.0

    async def send_update(self, update: str):
        """
        Send an update.

        All functions registered by :func:`on_update` will be called.

        :param update: A string update to send.
        """
        for update_ in update:
            if update:
                self._updates.append(update_)
                await self.on_update.trigger(self, update_)

    @property
    def state(self):
        return self._state

    async def set_state(self, new_state: State):
        await self.on_state_change.trigger(self._state, new_state)
        self._state = new_state
        return new_state

    async def _run_step(
            self,
            step: Callable[[], Coroutine[Any, Any, Optional[str]]],
    ):
        try:
            return [await step()]
        except Exception as exception:
            error = WorkflowError(cause=exception, workflow=self.workflow, context=self)
            callback_results = await self.on_error.trigger(error)

            if callback_results:
                return callback_results

            raise error from exception

    async def _run_steps(self, steps):
        for step in steps:
            update = await _run_step(step, workflow, ctx)
            await self.on_step.trigger(workflow, ctx)
            await ctx.send_update(*update)

    def execute(self):


