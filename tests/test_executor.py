from asyncio import CancelledError

import pytest
from pytest_mock import MockerFixture
from virtool_workflow import Workflow, hooks
from virtool_workflow.runtime.executor import execute
from virtool_workflow.events import Events
from virtool_workflow.execution.states import COMPLETE, ERROR, RUNNING, WAITING

from pyfixtures import FixtureScope


@pytest.fixture
def success_workflow():
    def dummy_step():
        ...

    workflow = Workflow()

    for _ in range(3):
        workflow.step(dummy_step)

    return workflow


@pytest.fixture
def failure_workflow():
    workflow = Workflow()

    @workflow.step
    async def fail():
        raise ValueError()

    return workflow


async def test_execute_does_trigger_success_hooks(
    success_workflow: Workflow, empty_scope: FixtureScope, mocker: MockerFixture
):
    mocks = {
        hook.name: mocker.patch.object(hook, "trigger", autospec=True)
        for hook in (
            hooks.on_finish,
            hooks.on_success,
            hooks.on_workflow_start,
            hooks.on_result,
        )
    }

    # add a result so that `on_result` hook does trigger
    empty_scope["results"] = {}

    await execute(success_workflow, empty_scope, Events())

    for name, mock in mocks.items():
        try:
            mock.assert_called_once()
        except AssertionError as e:
            raise AssertionError(f"{name} was not triggered") from e


async def test_execute_does_trigger_step_hooks(
    success_workflow: Workflow, empty_scope: FixtureScope, mocker: MockerFixture
):
    on_start = mocker.patch.object(hooks.on_step_start, "trigger", autospec=True)
    on_finish = mocker.patch.object(hooks.on_step_finish, "trigger", autospec=True)

    await execute(success_workflow, empty_scope, Events())

    assert on_start.call_count == len(success_workflow.steps)
    assert on_finish.call_count == len(success_workflow.steps)


async def test_execute_does_trigger_failure_hooks(
    failure_workflow, empty_scope: FixtureScope, mocker: MockerFixture
):
    on_failure = mocker.patch.object(hooks.on_failure, "trigger", autospec=True)
    on_finish = mocker.patch.object(hooks.on_finish, "trigger", autospec=True)
    on_error = mocker.patch.object(hooks.on_error, "trigger", autospec=True)

    await execute(failure_workflow, empty_scope, Events())

    on_failure.assert_called_once()
    on_finish.assert_called_once()
    on_error.assert_called_once()

    assert isinstance(empty_scope["error"], ValueError)
    assert empty_scope["state"] == ERROR


async def test_execute_does_trigger_on_cancelled_hook_after_cancelled_event(
    empty_scope: FixtureScope, mocker: MockerFixture
):
    workflow = Workflow()

    @workflow.step
    async def simulate_cancel():
        raise CancelledError()

    on_cancel = mocker.patch.object(hooks.on_cancelled, "trigger", autospec=True)

    events = Events()
    events.cancelled.set()

    await execute(workflow, empty_scope, events)

    on_cancel.assert_called_once()


async def test_execute_does_update_state_fixture(
    empty_scope: FixtureScope, mocker: MockerFixture
):
    state = await empty_scope.get_or_instantiate("state")
    assert state == WAITING

    workflow = Workflow()

    @workflow.step
    def running(state):
        assert state == RUNNING

    @hooks.on_finish(once=True)
    def check_complete(state):
        assert state == COMPLETE

    await execute(workflow, empty_scope, Events())

    assert empty_scope["error"] is None
    assert empty_scope["state"] == COMPLETE
