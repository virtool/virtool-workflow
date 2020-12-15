"""Execute workflows and manage the execution context."""
import logging
import pprint
import sys
import traceback
from enum import Enum
from typing import Optional, Callable, Coroutine, Any, Dict

from virtool_workflow.execution import hooks
from virtool_workflow.fixtures.scope import WorkflowFixtureScope
from virtool_workflow.workflow import Workflow

logger = logging.getLogger(__name__)


class WorkflowError(Exception):
    """An exception occurring during the execution of a workflow."""

    def __init__(
            self,
            cause: Exception,
            workflow: Workflow,
            context: Optional["WorkflowExecution"],
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

    def __str__(self):
        return (f"{self.cause}\n\n"
                f"Context: {self.context}\n"
                f"Workflow: {self.workflow}\n")


State = Enum("State", "WAITING STARTUP RUNNING CLEANUP FINISHED")


class WorkflowExecution:
    """An awaitable object providing access to the results of a workflow."""

    def __init__(self, workflow: Workflow, scope: WorkflowFixtureScope):
        """
        :param workflow: The Workflow to be executed
        :param scope: The WorkflowFixtureScope used to bind fixtures to the workflow.
        """
        self.workflow = workflow
        self.scope = scope
        self._updates = []
        self._state = State.WAITING
        self.current_step = 0
        self.progress = 0.0
        self.error = None

    async def send_update(self, update: str):
        """
        Send an update.

        Triggers the #virtool_workflow.hooks.on_update hook.

        :param update: A string update to send.
        """
        logger.debug(f"Sending update: {update}")
        self._updates.append(update)
        await hooks.on_update.trigger(self.scope, update)

    @property
    def state(self):
        return self._state

    async def _set_state(self, new_state: State):
        """
        Change the current state of execution.

        Triggers the #virtool_workflow.hooks.on_state_change hook.

        :param new_state: The new state that should be applied.
        """
        logger.debug(f"Changing the execution state from {self._state} to {new_state}")
        await hooks.on_state_change.trigger(self.scope, self._state, new_state)
        self._state = new_state
        return new_state

    async def _run_step(
            self,
            step: Callable[[], Coroutine[Any, Any, Optional[str]]],
    ):
        try:
            logger.info(f"Beginning step #{self.current_step}: {step.__name__}")
            return await step()
        except Exception as exception:
            self.error = exception
            error = WorkflowError(cause=exception, workflow=self.workflow, context=self)
            callback_results = await hooks.on_error.trigger(self.scope, error)

            if callback_results:
                return callback_results[0]

            raise error from exception

    async def _run_steps(self, steps, count_steps=False):
        for step in steps:
            if count_steps:
                self.current_step += 1
                self.progress = float(self.current_step) / float(len(self.workflow.steps))
            update = await self._run_step(step)
            if count_steps:
                await hooks.on_workflow_step.trigger(self.scope, update)
            if update:
                await self.send_update(update)

    async def execute(self) -> Dict[str, Any]:
        """Execute the workflow and return the result."""
        try:
            return await self._execute()
        except Exception as e:
            if not isinstance(e, WorkflowError):
                e = WorkflowError(cause=e, workflow=self.workflow, context=self)
            await hooks.on_workflow_failure.trigger(self.scope, e)
            raise e

    async def _execute(self) -> Dict[str, Any]:
        logger.info(f"Starting execution of {self.workflow}")

        self.scope["workflow"] = self.workflow
        self.scope["execution"] = self
        self.scope["results"] = {}

        bound_workflow = await self.scope.bind_to_workflow(self.workflow)

        for state, steps, count_steps in ((State.STARTUP, bound_workflow.on_startup, False),
                                          (State.RUNNING, bound_workflow.steps, True),
                                          (State.CLEANUP, bound_workflow.on_cleanup, False)):
            await self._set_state(state)
            await self._run_steps(steps, count_steps)

        await self._set_state(State.FINISHED)

        result = self.scope["results"]

        logger.info("Workflow finished")
        logger.debug(f"Result: \n{pprint.pformat(result)}")

        await hooks.on_result.trigger(self.scope)

        return result

    def __await__(self):
        return self.execute().__await__()
