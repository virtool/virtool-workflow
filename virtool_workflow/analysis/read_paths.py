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
from .cache import cache_document, fetch_cache, create_cache
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
        number_of_processes: int,
        run_in_executor: FunctionExecutor
) -> Path:
    """The analysis reads path with caches fetched if they exist"""
    if cache_document:
        await fetch_cache(cache_document,
                          cache_path,
                          analysis_args.reads_path,
                          run_in_executor)

    elif not all(f["raw"] for f in analysis_args.sample["files"]):
        legacy_paths = utils.make_legacy_read_paths(analysis_args.sample_path)

        await copy_paths(legacy_paths,
                         [reads_path/path.name for path in legacy_paths],
                         run_in_executor)
    else:
        await create_cache(analysis_args,
                           trimming_parameters,
                           cache_path,
                           number_of_processes,
                           database,
                           run_in_executor)

    return analysis_args.reads_path














