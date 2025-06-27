import asyncio
from contextlib import suppress

import pytest
from structlog import get_logger

from virtool_workflow.pytest_plugin.data import Data
from virtool_workflow import hooks, Workflow
from virtool_workflow.runtime.config import RunConfig
from virtool_workflow.runtime.events import Events
from virtool_workflow.runtime.run import run_workflow


@pytest.fixture
def success_workflow():
    def dummy_step(): ...

    workflow = Workflow()

    for _ in range(3):
        workflow.step(dummy_step)

    return workflow


async def test_success(clear_hooks, data: Data, run_config: RunConfig):
    """
    Test that the on_success and on_finish hooks are triggered when a workflow succeeds.
    """
    wf = Workflow()

    @wf.step
    async def first():
        """Description of the first step."""
        await asyncio.sleep(2)

    success_called = False
    error_called = False
    finish_called = False

    @hooks.on_error(once=True)
    def success_callback():
        nonlocal success_called
        success_called = True

    @hooks.on_success(once=True)
    def success_callback():
        nonlocal success_called
        success_called = True

    @hooks.on_finish(once=True)
    def finish_callback():
        nonlocal finish_called
        finish_called = True

    await run_workflow(run_config, data.job.id, wf, Events(), get_logger("test"))

    assert success_called
    assert not error_called
    assert finish_called


async def test_error(clear_hooks, data: Data, run_config: RunConfig):
    """
    Test that the on_failure and on_finish hooks are triggered when a workflow fails
    due to an error.
    """
    failure_called = False
    finish_called = False

    @hooks.on_failure(once=True)
    def failure_callback():
        nonlocal failure_called
        failure_called = True

    @hooks.on_finish(once=True)
    def finish_callback():
        nonlocal finish_called
        finish_called = True

    wf = Workflow()

    @wf.step
    async def first():
        """Description of the first step."""
        await asyncio.sleep(1)
        raise ValueError("test error")

    with suppress(Exception):
        await run_workflow(run_config, data.job.id, wf, Events(), get_logger("test"))

    assert failure_called
    assert finish_called
