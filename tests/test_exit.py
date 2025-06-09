import asyncio
import datetime
import multiprocessing
from pathlib import Path

from pytest_structlog import StructuredLogCapture
from structlog.testing import LogCapture
from virtool.jobs.models import JobState, JobStatus
from virtool.redis import Redis

from virtool_workflow import Workflow
from virtool_workflow.pytest_plugin.data import Data
from virtool_workflow.runtime.redis import CANCELLATION_CHANNEL
from virtool_workflow.runtime.run import start_runtime


async def test_cancellation(
    data: Data,
    jobs_api_connection_string: str,
    log: LogCapture,
    redis: Redis,
    redis_connection_string: str,
    static_datetime: datetime.datetime,
    work_path: Path,
):
    """Test that the runner exits with an appropriate status update if the job is cancelled."""
    data.job.workflow = "aodp"
    data.job.status = [
        JobStatus(
            progress=0,
            state=JobState.WAITING,
            timestamp=static_datetime,
        ),
    ]

    redis_list_name = "jobs_aodp"

    await redis.rpush(redis_list_name, data.job.id)

    wf = Workflow()

    @wf.step
    async def first():
        """Description of the first step."""
        await asyncio.sleep(2)

    @wf.step
    async def second():
        """Description of the second step."""
        await asyncio.sleep(3)

    @wf.step
    async def third():
        """Description of the third step."""
        await asyncio.sleep(4)

    @wf.step
    async def third():
        """Description of the fourth step."""
        await asyncio.sleep(5)

    runtime_task = asyncio.create_task(
        start_runtime(
            False,
            jobs_api_connection_string,
            4,
            2,
            redis_connection_string,
            redis_list_name,
            "",
            5,
            work_path,
            workflow_loader=lambda: wf,
        ),
    )

    await asyncio.sleep(5)

    await redis.publish(CANCELLATION_CHANNEL, data.job.id)

    await runtime_task

    state_and_progress = [(update.state, update.progress) for update in data.job.status]

    assert state_and_progress[0] == (JobState.WAITING, 0)
    assert state_and_progress[1] == (JobState.PREPARING, 0)
    assert state_and_progress[2] == (JobState.RUNNING, 0)
    assert state_and_progress[-1] == (JobState.CANCELLED, state_and_progress[-2][1])

    assert log.has("received cancellation signal from redis", level="info")


async def test_timeout(
    log,
    jobs_api_connection_string: str,
    redis_connection_string: str,
    work_path: Path,
):
    """Test that the runner exits if no job ID can be pulled from Redis before the timeout.

    This situation does not involve a status update being sent to the server.
    """
    redis_list_name = "jobs_termination"

    wf = Workflow()

    @wf.step
    async def first():
        """Description of First."""
        await asyncio.sleep(1)

    @wf.step
    async def second():
        """Description of Second."""
        await asyncio.sleep(2)

    await start_runtime(
        False,
        jobs_api_connection_string,
        8,
        2,
        redis_connection_string,
        redis_list_name,
        "",
        5,
        work_path,
        workflow_loader=lambda: wf,
    )

    assert log.has("timed out while waiting for job id", level="warning")


async def test_sigterm(
    data,
    jobs_api_connection_string: str,
    redis: Redis,
    redis_connection_string: str,
    static_datetime: datetime.datetime,
    work_path: Path,
    log: StructuredLogCapture,
):
    data.job.workflow = "aodp"
    data.job.status = [
        JobStatus(
            progress=0,
            state=JobState.WAITING,
            timestamp=static_datetime,
        ),
    ]

    def start_runtime_sync():
        wf = Workflow()

        @wf.step
        async def first():
            """Description of First."""
            await asyncio.sleep(1)

        @wf.step
        async def second():
            """Description of Second."""
            await asyncio.sleep(2)

        asyncio.run(
            start_runtime(
                False,
                jobs_api_connection_string,
                8,
                2,
                redis_connection_string,
                "jobs_aodp",
                "",
                5,
                work_path,
                workflow_loader=lambda: wf,
            ),
        )

    # We need to use multiprocessing here because the signal handler is set up in the
    # main thread.
    p = multiprocessing.Process(target=start_runtime_sync)
    p.start()

    await redis.rpush("jobs_aodp", data.job.id)

    # Let the jobs be acquired and started.
    await asyncio.sleep(3)

    p.terminate()
    p.join(3)

    # Sleep so that status update can be committed.
    await asyncio.sleep(1)

    assert [(update.state, update.progress) for update in data.job.status] == [
        (JobState.WAITING, 0),
        (JobState.PREPARING, 0),
        (JobState.RUNNING, 0),
        (JobState.RUNNING, 50),
        (JobState.TERMINATED, 50),
    ]
