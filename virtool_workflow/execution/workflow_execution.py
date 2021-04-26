"""Execute workflows and manage the execution context."""
import logging
import pprint
from typing import Any, Callable, Coroutine, Dict

from virtool_workflow import hooks
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow.workflow import Workflow

logger = logging.getLogger(__name__)


class WorkflowExecution:
    """An awaitable object providing access to the results of a workflow."""

    def __init__(self, workflow: Workflow, scope: FixtureScope):
        """
        :param workflow: The Workflow to be executed
        :param scope: The :class:`FixtureScope` instance
        """
        self.current_step = 0
        self.error = None
        self.progress = 0.0
        self.scope = scope
        self.state = states.WAITING
        self.workflow = workflow

        self._updates = []

    async def send_update(self, update: str):
        """
        Send an update.

        Triggers the :obj:`virtool_workflow.hooks.on_update` hook.

        :param update: A string update to send
        """
        self._updates.append(update)
        self.scope["update"] = update
        await hooks.on_update.trigger(self.scope)

    async def _run_steps(self, steps, count_steps=False):
        for step in steps:
            if count_steps:
                self.current_step += 1
                self.progress = float(self.current_step) / float(
                    len(self.workflow.steps))
            logger.debug(
                f"Beginning step #{self.current_step}: {step.__name__}")
            update = await step()

            if count_steps:
                await hooks.on_workflow_step.trigger(self.scope, update)
            if update:
                await self.send_update(update)

    async def execute(self) -> Dict[str, Any]:
        """Execute the workflow and return the result."""
        try:
            result = await self._execute()
        except Exception as e:
            self.scope["error"] = e
            await hooks.on_failure.trigger(self.scope)
            raise e

        await hooks.on_result.trigger(self.scope)
        await hooks.on_success.trigger(self.scope)

        return result

    async def _execute(self) -> Dict[str, Any]:
        logger.debug(f"Starting execution of {self.workflow}")

        self.scope["workflow"] = self.workflow
        self.scope["execution"] = self
        self.scope["results"] = {}

        bound_workflow = await self.scope.bind_to_workflow(self.workflow)

        for state, steps, count_steps in (
            (states.STARTUP, bound_workflow.on_startup, False),
            (states.RUNNING, bound_workflow.steps, True),
            (states.CLEANUP, bound_workflow.on_cleanup, False),
        ):
            self.state = state
            await self._run_steps(steps, count_steps)

        self.state = states.FINISHED

        result = self.scope["results"]

        logger.debug("Workflow finished")
        logger.debug(f"Result: \n{pprint.pformat(result)}")

        return result

    def __await__(self):
        return self.execute().__await__()
