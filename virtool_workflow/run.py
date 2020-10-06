import subprocess
from typing import Union, IO


def sh(command: Union[str, list], stdin: Union[str, IO] = "", **kwargs):
    if isinstance(command, str):
        command = command.split(" ")

    is_str = isinstance(stdin, str)

    args = dict(
        args=command,
        stdin=subprocess.PIPE if is_str else stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    args.update(kwargs)

    proc = subprocess.Popen(**args)

    input_ = bytes(stdin, encoding="utf-8") if is_str else None

    return proc.communicate(input=input_)
