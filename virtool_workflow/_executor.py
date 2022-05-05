import asyncio
import logging
from asyncio import CancelledError
from contextlib import asynccontextmanager, contextmanager
from itertools import chain

from fixtures import FixtureScope, fixture
from virtool_workflow import Workflow
from virtool_workflow._steps import WorkflowStep
from virtool_workflow.events import Events
from virtool_workflow.execution import states
from virtool_workflow.hooks import (
    on_failure,
    on_finish,
    on_result,
    on_step_finish,
    on_step_start,
    on_success,
    on_workflow_start,
    on_terminated,
    on_cancelled,
    on_error,
)

logger = logging.getLogger(__name__)


async def execute(
    workflow: Workflow, scope: FixtureScope, events: Events
) -> FixtureScope:
    """
    Execute a workflow.

    :param workflow: The workflow to execute
    :param scope: The :class:`FixtureScope` to use for fixture injection
    """
    scope["step_number"] = 0
    scope["error"] = None
    scope["logger"] = logger
    scope["workflow"] = workflow
    scope["current_step"] = None

    await on_workflow_start.trigger(scope)

    try:
        with update_state_in_scope(scope):
            for step in chain(workflow.on_startup, workflow.steps, workflow.on_cleanup):
                bound_step = await scope.bind(step.function)

                async with run_step_with_hooks(scope, step):
                    logger.info(f"Running step '{step.display_name}'")
                    await bound_step()
    except CancelledError:
        if events.cancelled.is_set():
            await asyncio.gather(
                on_cancelled.trigger(scope),
                on_failure.trigger(scope),
            )
        else:
            if not events.terminated.is_set():
                logger.warning("Workflow cancelled for unknown reason")

            await asyncio.gather(
                on_terminated.trigger(scope),
                on_failure.trigger(scope),
            )
    except Exception as error:
        scope["error"] = error
        await asyncio.gather(on_error.trigger(scope), on_failure.trigger(scope))
    else:
        if "results" in scope:
            await on_result.trigger(scope)

        await on_success.trigger(scope)
    finally:
        await on_finish.trigger(scope)

    return scope


@contextmanager
def update_state_in_scope(scope: FixtureScope):
    """
    Update the scope state value as the enclosed workflow execution proceeds.

    :param scope: the workflow fixture scope
    """
    scope["state"] = states.RUNNING

    try:
        yield
    except Exception:
        scope["state"] = states.ERROR
        raise
    else:
        scope["state"] = states.COMPLETE


@asynccontextmanager
async def run_step_with_hooks(scope: FixtureScope, step: WorkflowStep):
    """
    Run the passed ``step`` while updating the ``scope`` and triggering hooks.

    :param scope: the scope to update and use for triggering hooks
    :param step: the workflow step
    """
    scope["current_step"] = step
    scope["step_number"] += 1

    try:
        await on_step_start.trigger(scope)
        yield
        await on_step_finish.trigger(scope)
    finally:
        scope["current_step"] = None


@fixture(scope="function")
def progress(step_number, workflow):
    return float(step_number) / float(len(workflow.steps))
