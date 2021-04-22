"""Execute workflows and manage the execution context."""
import logging
import pprint
from typing import Any, Dict
from contextlib import asynccontextmanager

from virtool_workflow import hooks
from virtool_workflow.fixtures.scope import FixtureScope
from virtool_workflow.execution import states
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

    @asynccontextmanager
    async def startup_and_cleanup(self):
        """Run the startup and cleanup operations of the workflow."""
        workflow = await self.scope.bind_to_workflow(self.workflow)

        for startup_step in workflow.on_startup:
            logger.info(f"Running startup step '{startup_step.__name__}'")
            await startup_step()

        self.state = states.RUNNING

        yield workflow

        self.state = states.CLEANUP

        for cleanup_step in workflow.on_cleanup:
            logger.info(f"Running cleanup step '{cleanup_step.__name__}'")
            await cleanup_step()

        self.state = states.FINISHED

    async def _execute(self) -> Dict[str, Any]:
        self.scope["workflow"] = self.workflow
        self.scope["execution"] = self
        self.scope["current_step"] = self.current_step

        async with self.startup_and_cleanup() as workflow:

            for step in workflow.steps:
                self.current_step += 1

                self.progress = (float(self.current_step) /
                                 float(len(workflow.steps)))

                logger.info(
                    f"Running step #{self.current_step}: {step.__name__}")

                update = await step()
                await self.send_update(update)

        result = self.scope["results"]

        logger.info("Workflow finished")
        logger.debug(f"Result: \n{pprint.pformat(result)}")

        return result

    def __await__(self):
        return self.execute().__await__()
