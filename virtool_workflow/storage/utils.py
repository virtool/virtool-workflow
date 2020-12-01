import asyncio
import shutil
from typing import Iterable, Tuple
from pathlib import Path
from virtool_workflow.execution.run_in_executor import FunctionExecutor


async def copy_paths(
        paths: Iterable[Tuple[Path, Path]],
        run_in_executor: FunctionExecutor
):
    """
    Copy the contents from a set of source paths to a set of destination paths concurrently.

    :param paths: An iterable containing source -> destination path pairs,
        where the first path is the source and the second is the destination.
    :param run_in_executor: A FunctionExecutor which will execute functions in
        a separate thread and return a coroutine.
    """
    coroutines = [
        run_in_executor(shutil.copytree, source, destination)
        for source, destination in paths
    ]
    await asyncio.gather(*coroutines)
