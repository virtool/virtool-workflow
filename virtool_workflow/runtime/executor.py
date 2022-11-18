import asyncio
from asyncio import CancelledError
from contextlib import asynccontextmanager, contextmanager
from logging import getLogger

from pyfixtures import FixtureScope, fixture

from virtool_workflow import Workflow
from virtool_workflow.runtime.step import WorkflowStep
from virtool_workflow.runtime.events import Events
from virtool_workflow.runtime import states
from virtool_workflow.hooks import (
    on_cancelled,
    on_error,
    on_failure,
    on_finish,
    on_result,
    on_step_finish,
    on_step_start,
    on_success,
    on_terminated,
    on_workflow_start,
)

logger = getLogger("runtime")


async def _handle_cancel(scope: FixtureScope, events: Events):
    if events.cancelled.is_set():
        await asyncio.gather(
            on_cancelled.trigger(scope),
            on_failure.trigger(scope),
        )

        return

    if not events.terminated.is_set():
        logger.warning("Workflow cancelled for unknown reason")

    await asyncio.gather(
        on_terminated.trigger(scope),
        on_failure.trigger(scope),
    )


@asynccontextmanager
async def workflow_lifecyle(scope: FixtureScope, events: Events):
    try:
        yield
    except CancelledError:
        await _handle_cancel(scope, events)
    except Exception as error:
        scope["error"] = error
        await asyncio.gather(on_error.trigger(scope), on_failure.trigger(scope))
    else:
        if "results" in scope:
            await on_result.trigger(scope)

        await on_success.trigger(scope)
    finally:
        await on_finish.trigger(scope)


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

    async with workflow_lifecyle(scope, events):
        with update_state_in_scope(scope):
            for step in workflow.steps:
                bound_step = await scope.bind(step.function)

                async with run_step_with_hooks(scope, step):
                    logger.info(f"Running step '{step.display_name}'")
                    await bound_step()

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


@fixture
def state(scope):
    if "state" not in scope:
        scope["state"] = states.WAITING
    return scope["state"]


@fixture(scope="function")
def progress(step_number, workflow):
    return float(step_number) / float(len(workflow.steps))
