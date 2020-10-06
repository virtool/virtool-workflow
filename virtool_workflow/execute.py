import asyncio
from asyncio.subprocess import PIPE, Process
from typing import Union, IO, Tuple


async def subprocess(command: Union[str, list], **kwargs) -> Process:
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

    return await asyncio.create_subprocess_exec(*command, **args)


async def shell(
        command: Union[str, list],
        stdin: Union[str, IO] = "",
        **kwargs,
) -> Tuple[str, str]:
    """Execute a shell command as a subprocess and return stdout & stderr output.

    :param command: Either a string or a list representing the shell command and it's arguments.
    :param stdin: Either a string or file-like object to be used as stdin for the command.
    :param kwargs: Any other parameters are passed directly to :func:`subprocess.Popen`
    :return
    """
    stdin_is_str = isinstance(stdin, str)

    proc = await (subprocess(command, **kwargs) if stdin_is_str else subprocess(command, stdin=stdin, **kwargs))
    input_ = bytes(stdin, encoding="utf-8") if stdin_is_str else None

    out, err = await proc.communicate(input=input_)

    return str(out, encoding="utf-8"), str(err, encoding="utf-8")




