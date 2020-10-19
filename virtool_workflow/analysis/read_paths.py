import asyncio
import shutil
import virtool_workflow
from typing import Dict, Any, List
from pathlib import Path
from virtool_workflow_runtime.db import VirtoolDatabase

from ..config.fixtures import number_of_processes
from ..storage.paths import cache_path
from ..execute import run_in_executor, FunctionExecutor
from ..storage.utils import copy_paths

from .trim_parameters import trimming_parameters
from .analysis_info import AnalysisArguments
from .cache import cache_document, fetch_cache, create_cache, trimming_command
from . import utils


async def fetch_legacy_paths(
        paths: List[Path],
        reads_path: Path,
        run_in_executor: FunctionExecutor
):
    coroutines = [
        run_in_executor(shutil.copy, path, reads_path/path.name)
        for path in paths
    ]

    await asyncio.gather(*coroutines)


@virtool_workflow.fixture
async def reads_path(
        analysis_args: AnalysisArguments,
        cache_path: Path,
        cache_document: Dict[str, Any],
        database: VirtoolDatabase,
        trimming_parameters: Dict[str, Any],
        trimming_command: List[str],
        number_of_processes: int,
        run_in_executor: FunctionExecutor
) -> Path:
    """The analysis reads path with caches fetched if they exist"""

    analysis_args.reads_path.mkdir(parents=True, exist_ok=True)

    if cache_document:
        await fetch_cache(cache_document,
                          cache_path,
                          analysis_args.reads_path,
                          run_in_executor)

    elif not all(f["raw"] for f in analysis_args.sample["files"]):
        legacy_paths = utils.make_legacy_read_paths(analysis_args.sample_path)

        paths_to_copy = {path: reads_path/path.name
                         for path in legacy_paths}

        await copy_paths(paths_to_copy.items(), run_in_executor)
    else:
        await create_cache(analysis_args,
                           trimming_parameters,
                           trimming_command,
                           cache_path,
                           number_of_processes,
                           database,
                           run_in_executor)

    return analysis_args.reads_path














