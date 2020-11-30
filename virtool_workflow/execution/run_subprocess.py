import asyncio
import asyncio.subprocess
from logging import getLogger
from typing import Optional, Callable, Awaitable, List

from virtool_workflow import fixture, hooks

logger = getLogger(__name__)


async def watch_pipe(stream: asyncio.StreamReader, handler: Callable[[bytes], Awaitable[None]]):
    """
    Watch stdout and stderr streams and pass lines to the #`handler` callback function.

    :param stream: a stdout or stderr file object
    :param handler: a handler coroutine for output lines

    """
    while True:
        line = await stream.readline()

        if not line:
            return

        await handler(line)


async def watch_subprocess(process, stdout_handler, stderr_handler):
    coros = [
        watch_pipe(process.stderr, stderr_handler)
    ]

    if stdout_handler:
        coros.append(watch_pipe(process.stdout, stdout_handler))

    await asyncio.gather(*coros)


@fixture
def run_subprocess():
    async def _run_subprocess(
            command: List[str],
            stdout_handler: Optional[Callable] = None,
            stderr_handler=None,
            env: Optional[dict] = None,
            cwd: Optional[str] = None
    ):
        logger.info(f"Running command in subprocess: {' '.join(command)}")

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

        @hooks.on_workflow_failure(until=hooks.on_f)
        def terminate_subprocess():
            process.terminate()

        await watch_subprocess(process, stdout_handler, _stderr_handler)

        await process.wait()

        return process

    return _run_subprocess
