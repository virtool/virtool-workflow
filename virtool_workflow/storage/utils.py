import asyncio
import shutil
from typing import Iterable
from pathlib import Path
from virtool_workflow.execute import FunctionExecutor


async def copy_paths(
        sources: Iterable[Path],
        destinations: Iterable[Path],
        run_in_executor: FunctionExecutor):
    coroutines = [
        run_in_executor(shutil.copy, source, destination)
        for source, destination in zip(sources, destinations)
    ]
    await asyncio.gather(*coroutines)
