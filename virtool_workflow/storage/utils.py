import asyncio
import shutil
from typing import List
from pathlib import Path
from virtool_workflow.execute import FunctionExecutor


async def copy_paths(
        sources: List[Path],
        destinations: List[Path],
        run_in_executor: FunctionExecutor):
    coroutines = [
        run_in_executor(shutil.copy, source, destination)
        for source, destination in zip(sources, destinations)
    ]
    await asyncio.gather(*coroutines)