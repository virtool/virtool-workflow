import logging
from contextlib import asynccontextmanager, contextmanager
from itertools import chain

from fixtures import FixtureScope, fixture
from virtool_workflow import Workflow
from virtool_workflow.execution import states
from virtool_workflow.hooks import (on_failure, on_finish, on_result,
                                    on_step_finish, on_step_start, on_success,
                                    on_workflow_start)

logger = logging.getLogger(__name__)

@on_workflow_start
async def initialize_scope(scope):
    scope["step_number"] = 0
    scope["error"] = None
    scope["logger"] = logger


async def execute(
    workflow: Workflow,
    scope: FixtureScope,
) -> FixtureScope:
    """
    Execute a workflow.

    :param workflow: The workflow to execute
    :param scope: The :class:`FixtureScope` to use for fixture injection
    """
    await on_workflow_start.trigger(scope)
    try:
        with workflow_state_management(scope):
            await _execute(workflow, scope)
    except Exception as error:
        scope["error"] = error
        await on_failure.trigger(scope)
        raise error
    else:
        if "results" in scope:
            await on_result.trigger(scope)

        await on_success.trigger(scope)
    finally:
        await on_finish.trigger(scope)

    return scope


@contextmanager
def workflow_state_management(scope):
    scope["state"] = states.RUNNING
    try:
        yield
    except:
        scope["state"] = states.ERROR
        raise
    else:
        scope["state"] = states.COMPLETE


@asynccontextmanager
async def step_setup(scope, step):
    scope["current_step"] = step

    try:
        await on_step_start.trigger(scope)
        yield 
        await on_step_finish.trigger(scope)
    finally:
        scope["current_step"] = None


async def _execute(
    workflow: Workflow,
    scope: FixtureScope,
):
    scope["workflow"] = workflow

    steps = chain(workflow.on_startup, workflow.steps, workflow.on_cleanup)

    for step in steps:
        run_step = await scope.bind(step.function)
        async with step_setup(scope, step=step):
            logger.info(f"Running step '{step.display_name}'")
            await run_step()

    scope["state"] = states.COMPLETE


@on_step_start
async def update_step_number(scope):
    scope["step_number"] += 1
    return scope["step_number"]


@fixture(scope="function")
def progress(step_number, workflow):
    return float(step_number) / float(len(workflow.steps))

    
    
