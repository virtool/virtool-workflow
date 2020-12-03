import asyncio
import asyncio.subprocess
from logging import getLogger
from typing import Optional, Callable, Awaitable, List, Coroutine

from virtool_workflow import fixture, hooks

logger = getLogger(__name__)

RunSubprocessHandler = Callable[[str], Awaitable[None]]
RunSubprocess = Callable[
    [List[str],
     Optional[RunSubprocessHandler],
     Optional[RunSubprocessHandler],
     Optional[dict],
     Optional[str],
     Optional[bool]],
    Awaitable[asyncio.subprocess.Process]
]


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
    """Watch both stderr and stdout using #watch_pipe."""
    coros = [
        watch_pipe(process.stderr, stderr_handler)
    ]

    if stdout_handler:
        coros.append(watch_pipe(process.stdout, stdout_handler))

    await asyncio.gather(*coros)


@fixture
def run_subprocess() -> RunSubprocess:
    """Fixture to run subprocesses and handle stdin and stderr output line-by-line."""

    async def _run_subprocess(
            command: List[str],
            stdout_handler: Optional[RunSubprocessHandler] = None,
            stderr_handler: Optional[Callable[[str], Coroutine]] = None,
            env: Optional[dict] = None,
            cwd: Optional[str] = None,
            wait: bool = True,
    ):
        """
        Run a command as a subprocess and handle stdin and stderr output line-by-line.

        :param command: The command to run as a subprocess.
        :param stdout_handler: A function to handle stdout lines.
        :param stderr_handler: A function to handle stderr lines.
        :param env: Environment variables to set for the subprocess.
        :param cwd: Current working directory for the subprocess.
        :param wait: Flag indicating to wait for the subprocess to finish before returning.

        :return
        """
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

        _watch_subprocess = asyncio.create_task(watch_subprocess(process, stdout_handler, _stderr_handler))

        @hooks.on_failure
        def _terminate_process():
            if process.returncode is None:
                process.terminate()
            _watch_subprocess.cancel()

        if wait:
            await process.wait()

        return process

    return _run_subprocess
