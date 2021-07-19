import asyncio
import asyncio.subprocess
from contextlib import suppress
from logging import getLogger
from typing import Awaitable, Callable, Coroutine, List, Optional, Protocol

from fixtures import fixture
from virtool_workflow import hooks

logger = getLogger(__name__)


class LineOutputHandler(Protocol):
    async def __Call__(self, line: str):
        """
        Handle input from stdin, or stderr, line by line.

        :param line: A line of output from the stream.
        :type line: str
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
    ) -> asyncio.subprocess.Process:
        """
        Run a shell command in a subprocess.

        :param command: A shell command, as a list of strings including the program name and arguments
        :type command: List[str]
        :param stdout_handler: A function to handle stdout output line by line
        :type stdout_handler: Optional[LineOutputHandler], optional
        :param stderr_handler: A function to handle stderr output line by line
        :type stderr_handler: Optional[LineOutputHandler], optional
        :param env: environment variables which should be available to the subprocess
        :type env: Optional[dict], optional
        :param cwd: The current working directory for the subprocess
        :type cwd: Optional[str], optional

        :return: An :class:`asyncio.subprocess.Process` instance
        :rtype: asyncio.subprocess.Process
        """
        raise NotImplementedError()


async def watch_pipe(stream: asyncio.StreamReader, handler: Callable[[bytes], Awaitable[None]]):
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


async def watch_subprocess(process, stdout_handler, stderr_handler):
    """
    Watch both stderr and stdout using :func:`.watch_pipe`.

    :param process: the process to watch
    :param stdout_handler: a handler function to call with each line received from stdout
    :param stdout_handler: a handler function to call with each line received from stderr

    """
    coros = [
        watch_pipe(process.stderr, stderr_handler)
    ]

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

    # Ensure the asyncio child watcher has a reference to the running loop, prevents `process.wait` from hanging.
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
        cwd=cwd
    )

    _watch_subprocess = asyncio.create_task(
        watch_subprocess(process, stdout_handler, _stderr_handler))

    @hooks.on_failure
    def _terminate_process():
        if process.returncode is None:
            process.terminate()
        _watch_subprocess.cancel()

    with suppress(asyncio.CancelledError):
        await _watch_subprocess

    await process.wait()

    return process


@fixture(protocol=RunSubprocess)
def run_subprocess() -> RunSubprocess:
    """Fixture to run subprocesses and handle stdin and stderr output line-by-line."""
    return _run_subprocess
