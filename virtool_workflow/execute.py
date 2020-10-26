"""Helper functions for threading and running subprocesses within Virtool Workflows."""
from concurrent.futures import ThreadPoolExecutor
from subprocess import PIPE, Popen
from typing import Union, IO, Tuple, Callable, Any, Coroutine

from virtool_workflow.fixtures.workflow_fixture import fixture


async def run_subprocess(command: Union[str, list], **kwargs) -> Popen:
    """
    Execute a shell command as a subprocess

    :param command: The command to be executed
    :param kwargs: Keyword arguments are passed to :func:`asyncio.create_subprocess_exec`
    :return: A :class:`asyncio.subprocess.Process` instance
    """
    if isinstance(command, str):
        command = command.split(" ")

    args = dict(
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
    )

    args.update(kwargs)

    return Popen(command, **args)


async def run_shell_command(
        command: Union[str, list],
        stdin: Union[str, IO] = "",
        **kwargs,
) -> Tuple[str, str]:
    """
    Execute a shell command as a subprocess and return stdout & stderr output.

    :param command: Either a string or a list representing the shell command and it's arguments.
    :param stdin: Either a string or file-like object to be used as stdin for the command.
    :param kwargs: Any other parameters are passed directly to :func:`subprocess.Popen`
    :return
    """
    stdin_is_str = isinstance(stdin, str)

    proc = await (run_subprocess(command, **kwargs) if stdin_is_str
                  else run_subprocess(command, stdin=stdin, **kwargs))
    input_ = bytes(stdin, encoding="utf-8") if stdin_is_str else None

    out, err = proc.communicate(input=input_)

    return str(out, encoding="utf-8"), str(err, encoding="utf-8")


@fixture
def thread_pool_executor() -> ThreadPoolExecutor:
    """A fixture for a :class:`ThreadPoolExecutor` to be used by :func:`run_in_executor`."""
    return ThreadPoolExecutor()


FunctionExecutor = Callable[..., Coroutine[Any, Any, Any]]
"""A function which accepts a Callable and it's arguments as parameters and returns a coroutine"""


@fixture
def run_in_executor(thread_pool_executor: ThreadPoolExecutor) -> FunctionExecutor:
    """
    Fixture to execute functions in a ThreadPoolExecutor.

    Wraps :func:`ThreadPoolExecutor.submit` as an async function.
    """
    async def _run_in_executor(func, *args, **kwargs):
        future = thread_pool_executor.submit(func, *args, **kwargs)
        return future.result()

    return _run_in_executor