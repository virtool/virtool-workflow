import asyncio
import datetime
from pathlib import Path

import pytest
from _pytest._py.path import LocalPath
from aioredis import Redis
from structlog.testing import LogCapture
from virtool_core.models.job import JobStatus, JobState

from virtool_workflow.pytest_plugin.data import Data
from virtool_workflow import RunSubprocess, Workflow
from virtool_workflow.errors import SubprocessFailed
from virtool_workflow.runtime.redis import CANCELLATION_CHANNEL
from virtool_workflow.runtime.run import start_runtime


@pytest.fixture
def bash(tmpdir) -> Path:
    sh = """
    echo "hello world"
    echo "foo bar"
    """

    path = Path(tmpdir / "test.sh")
    path.write_text(sh)

    return path


async def test_command_is_called(run_subprocess: RunSubprocess, tmpdir):
    """Test that the provided command is called."""
    path = tmpdir / "test.txt"
    assert not path.isfile()

    await run_subprocess(["touch", str(path)])

    assert path.isfile()


async def test_stdout_is_handled(bash: Path, run_subprocess: RunSubprocess):
    """
    Test that a function provided to ``stdout_handler`` is called with each line of
    stdout.
    """
    lines = []

    async def stdout_handler(line):
        lines.append(line)

    await run_subprocess(["bash", str(bash)], stdout_handler=stdout_handler)

    assert lines == [b"hello world\n", b"foo bar\n"]


async def test_stderr_is_handled(bash: Path, run_subprocess: RunSubprocess):
    """
    Test that a function provided to ``stderr_handler`` is called with each line of
    stderr.
    """
    lines = []

    async def stderr_handler(line):
        lines.append(line)

    with pytest.raises(SubprocessFailed):
        await run_subprocess(["bash", "/foo/bar"], stderr_handler=stderr_handler)

    assert lines == [b"bash: /foo/bar: No such file or directory\n"]


async def test_subprocess_failed(run_subprocess: RunSubprocess):
    """
    Test that a ``SubprocessFailed`` error is raised when a command fails and is not
    raised when it succeeds.
    """
    with pytest.raises(SubprocessFailed):
        await run_subprocess(["ls", "-doesnotexist"])

    await run_subprocess(["ls"])


@pytest.mark.parametrize("cancel", [True, False])
async def test_terminated_by_cancellation(
    cancel: bool,
    data: Data,
    jobs_api_connection_string: str,
    log: LogCapture,
    redis: Redis,
    redis_connection_string: str,
    static_datetime: datetime.datetime,
    work_path: Path,
    tmpdir: LocalPath,
):
    """Test that the runner exits with an appropriate status update if the job is cancelled."""
    test_txt_path = Path(tmpdir / "test.txt")

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
    async def second(logger, run_subprocess: RunSubprocess, work_path: Path):
        """Description of the second step."""

        sh_path = work_path / "script.sh"
        sh_path.write_text(
            f"""
            sleep 10
            touch {str(test_txt_path)}
            """
        )

        logger.info("work path found", work_path=work_path)

        await run_subprocess(["bash", str(sh_path)])

        await asyncio.sleep(1)

    @wf.step
    async def third(work_path: Path):
        """Description of the third step."""
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
        )
    )

    await asyncio.sleep(4)

    if cancel:
        await redis.publish(CANCELLATION_CHANNEL, data.job.id)

    await runtime_task

    last_status = data.job.status[-1]

    # This file should not have been written if the job was cancelled!
    assert test_txt_path.is_file() is not cancel

    if cancel:
        assert last_status.state == JobState.CANCELLED
        assert log.has("received cancellation signal from redis", level="info")
    else:
        assert last_status.state == JobState.COMPLETE
