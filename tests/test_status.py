import asyncio
from datetime import datetime

from syrupy import SnapshotAssertion
from syrupy.filters import props
from virtool_core.models.job import JobState, JobStatus

from virtool_workflow.pytest_plugin.data import Data
from virtool_workflow import Workflow, hooks
from virtool_workflow.runtime.config import RunConfig
from virtool_workflow.runtime.events import Events
from virtool_workflow.runtime.run import run_workflow


async def test_ok(data: Data, run_config: RunConfig, snapshot: SnapshotAssertion):
    """Test that status is reported normally in a successful workflow run."""
    wf = Workflow()

    data.job.status = [
        JobStatus(
            progress=0,
            state=JobState.PREPARING,
            timestamp=datetime.now(),
        )
    ]

    @wf.step
    async def first():
        """Description of First."""
        assert data.job.status[-1].state == JobState.RUNNING
        assert data.job.status[-1].step_name == "First"
        assert data.job.status[-1].step_description == "Description of First."

        await asyncio.sleep(1)

    @wf.step
    async def second():
        """Description of Second."""
        assert data.job.status[-1].state == JobState.RUNNING
        assert data.job.status[-1].step_name == "Second"
        assert data.job.status[-1].step_description == "Description of Second."

        await asyncio.sleep(2)

    on_success_called = False

    @hooks.on_success(once=True)
    async def check_success_status():
        nonlocal on_success_called
        on_success_called = True

        # Wait for status to be received at Virtool server
        await asyncio.sleep(0.1)

        assert data.job.status[-1].state == JobState.COMPLETE

    await run_workflow(run_config, data.job.id, wf, Events())

    assert on_success_called is True

    assert [s.dict() for s in data.job.status] == snapshot(
        name="status", exclude=props("timestamp")
    )


async def test_error(data: Data, run_config: RunConfig, snapshot: SnapshotAssertion):
    """Test that an error raised in workflow step is reported."""
    data.job.status = [
        JobStatus(
            progress=0,
            state=JobState.PREPARING,
            timestamp=datetime.now(),
        )
    ]

    wf = Workflow()

    error = ValueError()

    @wf.step
    def raise_error():
        raise error

    error_hook_called = False

    @hooks.on_error(once=True)
    async def check_error_update_sent():
        nonlocal error_hook_called

        # Wait for status to be received at Virtool server.
        await asyncio.sleep(0.1)

        last_status = data.job.status[-1]

        assert last_status.state == JobState.ERROR
        assert last_status.error.type == "ValueError"

        error_hook_called = True

    failure_hook_called = False

    @hooks.on_failure(once=True)
    async def check_failure_hook_called():
        nonlocal failure_hook_called
        failure_hook_called = True

    await run_workflow(
        run_config,
        data.job.id,
        wf,
        Events(),
    )

    assert error_hook_called is True
    assert failure_hook_called is True

    assert [s.dict() for s in data.job.status] == snapshot(
        name="status", exclude=props("timestamp", "traceback")
    )
