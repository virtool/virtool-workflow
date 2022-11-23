import asyncio
from asyncio.subprocess import Process
from contextlib import suppress
from logging import getLogger
from subprocess import SubprocessError
from typing import Awaitable, Callable, Coroutine, List, Optional, Protocol

from pyfixtures import fixture
from virtool_workflow import hooks

logger = getLogger("subproc")


class SubprocessFailed(SubprocessError):
    """Subprocess exited with non-zero status during a workflow."""


class LineOutputHandler(Protocol):
    async def __call__(self, line: str):
        """
        Handle input from stdin, or stderr, line by line.

        :param line: A line of output from the stream.
        """
        raise NotImplementedError()


class RunSubprocess(Protocol):
    async def __call__(
        self,
        command: List[str],
        stdout_handler: LineOutputHandler = None,
        stderr_handler: LineOutputHandler = None,
        env: dict = None,
        cwd: str = None,
    ) -> Process:
        """
        Run a shell command in a subprocess.

        :param command: A shell command
        :param stdout_handler: A function to handle stdout output line by line
        :param stderr_handler: A function to handle stderr output line by line
        :param env: environment variables which should be available to the subprocess
        :param cwd: The current working directory for the subprocess
        :raise SubprocessFailed: The subprocess has exited with a non-zero exit code
        :return: An :class:`.Process` instance
        """
        raise NotImplementedError()


async def watch_pipe(
    stream: asyncio.StreamReader, handler: Callable[[bytes], Awaitable[None]]
):
    """
    Watch the stdout or stderr stream and pass lines to the `handler` callback function.

    :param stream: a stdout or stderr file object
    :param handler: a handler coroutine for output lines

    """
    while True:
        line = await stream.readline()

        if not line:
            return

        await handler(line)


async def watch_subprocess(
    process: Process, stdout_handler: Callable, stderr_handler: Callable
):
    """
    Watch both stderr and stdout using :func:`.watch_pipe`.

    :param process: the process to watch
    :param stdout_handler: a function to call with each stdout line
    :param stderr_handler: a function to call with each stderr line

    """
    coros = [watch_pipe(process.stderr, stderr_handler)]

    if stdout_handler:
        coros.append(watch_pipe(process.stdout, stdout_handler))

    await asyncio.gather(*coros)


async def _run_subprocess(
    command: List[str],
    stdout_handler: Optional[LineOutputHandler] = None,
    stderr_handler: Optional[Callable[[str], Coroutine]] = None,
    env: Optional[dict] = None,
    cwd: Optional[str] = None,
) -> asyncio.subprocess.Process:
    """An implementation of :class:`RunSubprocess` using `asyncio.subprocess`."""
    logger.info(f"Running command in subprocess: {' '.join(command)}")

    # Ensure the asyncio child watcher has a reference to the running loop, prevents
    # `process.wait` from hanging.
    asyncio.get_child_watcher().attach_loop(asyncio.get_running_loop())

    stdout = asyncio.subprocess.PIPE if stdout_handler else asyncio.subprocess.DEVNULL

    if stderr_handler:

        async def _stderr_handler(line):
            await stderr_handler(line)
            logger.info(f"STDERR: {line.rstrip()}")

    else:

        async def _stderr_handler(line):
            logger.info(f"STDERR: {line.rstrip()}")

    process = await asyncio.create_subprocess_exec(
        *(str(arg) for arg in command),
        stdout=stdout,
        stderr=asyncio.subprocess.PIPE,
        env=env,
        cwd=cwd,
    )

    _watch_subprocess = asyncio.create_task(
        watch_subprocess(process, stdout_handler, _stderr_handler)
    )

    @hooks.on_failure
    def _terminate_process():
        if process.returncode is None:
            process.terminate()
        _watch_subprocess.cancel()

    with suppress(asyncio.CancelledError):
        await _watch_subprocess

    exit_code = await process.wait()

    # Exit code 15 indicates that the process was terminated. This is expected
    # when the workflow fails for some other reason, hence not an exception
    if exit_code not in [0, 15, -15]:
        raise SubprocessFailed(
            f"{command[0]} failed with exit code {exit_code}\n"
            f"Arguments: {command}\n"
        )

    return process


@fixture(protocol=RunSubprocess)
def run_subprocess() -> RunSubprocess:
    """Fixture to run subprocesses and handle stdin and stderr output line-by-line."""
    return _run_subprocess
