import logging
from itertools import chain
from contextlib import asynccontextmanager, contextmanager

from fixtures import FixtureScope, fixture
from virtool_workflow import Workflow
from virtool_workflow.hooks import (on_failure, on_finish, on_result,
                                    on_step_finish, on_step_start, on_success)
from virtool_workflow.execution import states

logger = logging.getLogger(__name__)


async def execute(
    workflow: Workflow,
    scope: FixtureScope,
) -> FixtureScope:
    """
    Execute a workflow.

    :param workflow: The workflow to execute
    :param scope: The :class:`FixtureScope` to use for fixture injection
    """
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
        scope["state"] = states.FINISHED


@asynccontextmanager
async def step_setup(scope, step):
    scope["current_step"] = step
    await on_step_start.trigger(scope)

    try:
        yield 
    except:
        raise
    else:
        await on_step_finish.trigger(scope)
    finally:
        del scope["current_step"]


async def _execute(
    workflow: Workflow,
    scope: FixtureScope,
):
    scope["workflow"] = workflow

    steps = chain(workflow.on_startup, workflow.steps, workflow.on_cleanup)


    for step in steps:
        async with step_setup(scope, step):
            logger.info(f"Running step '{step.display_name}'")
            run_step = await scope.bind(step.call)
            await run_step()

    scope["state"] = states.FINISHED


@on_step_start
async def update_step_number(scope):
    if "step_number" not in scope:
        scope["step_number"] = 0
    else:
        scope["step_number"] += 1

    return scope["step_number"]


@fixture(scope="function")
def progress(step_number, workflow):
    return float(step_number) / float(len(workflow.steps))

    
    
