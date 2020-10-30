import sys
import traceback
from enum import Enum
from typing import Optional, Callable, Coroutine, Any, Dict

from virtool_workflow.workflow import Workflow
from virtool_workflow.execution.hooks.hooks import create_hook
from virtool_workflow.execution.hooks.workflow_hooks import on_workflow_finish
from virtool_workflow.fixtures.scope import WorkflowFixtureScope


class WorkflowError(Exception):
    """An exception occurring during the execution of a workflow."""

    def __init__(
            self,
            cause: Exception,
            workflow: Workflow,
            context: "WorkflowExecutor",
            max_traceback_depth: int = 50
    ):
        """

        :param cause: The initial exception raised
        :param workflow: The workflow object being executed
        :param context: The execution context of the workflow being executed
        :param max_traceback_depth: The maximum depth for the traceback data
        """
        self.cause = cause
        self.workflow = workflow
        self.context = context

        exception, value, trace_info = sys.exc_info()

        self.traceback_data = {
            "type": exception.__name__,
            "traceback": traceback.format_tb(trace_info, max_traceback_depth),
            "details": [str(arg) for arg in value.args]
        }

        super().__init__(str(cause))


State = Enum("State", "WAITING STARTUP RUNNING CLEANUP FINISHED")


class WorkflowExecutor:

    def __init__(self, workflow: Workflow, scope: WorkflowFixtureScope):
        self.workflow = workflow
        self.scope = scope

        self.on_update = create_hook("on_update", str)
        self.on_state_change = create_hook("on_state_change", State, State)
        self.on_error = create_hook("on_error", WorkflowError, return_type=Optional[str])
        self.on_step = create_hook("on_step", WorkflowExecutor, str)
        self.on_result = create_hook("on_result", Dict[str, Any])

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

    async def _set_state(self, new_state: State):
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
            update = await self._run_step(step)
            await self.on_step.trigger(self, update)
            await self.send_update(*update)

    async def execute(self) -> Dict[str, Any]:

        self.scope.add_instance(self.workflow, "wf", "workflow")
        self.scope.add_instance(self, "context", "execution_context", "ctx")
        self.scope.add_instance({}, "result", "results")

        bound_workflow = await self.scope.bind_to_workflow(self.workflow)

        for state, steps in ((State.STARTUP, bound_workflow.on_startup),
                             (State.RUNNING, bound_workflow.steps),
                             (State.CLEAUP, bound_workflow.on_cleanup)):
            await self._set_state(state)
            await self._run_steps(steps)

        await self._set_state(State.FINISHED)

        result = self.scope["result"]

        await self.on_result.trigger(result)
        await on_workflow_finish.trigger(self.workflow, result)

        return self.scope["result"]

    def __await__(self):
        return self.execute().__await__()


