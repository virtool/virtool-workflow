import asyncio
import shutil
from pathlib import Path
from typing import List, Dict, Any

import virtool_workflow
from virtool_workflow_runtime.db import VirtoolDatabase
from . import utils
from .analysis_info import AnalysisArguments
from .cache import fetch_cache, prepare_reads_and_create_cache
from ..execute import FunctionExecutor
from ..storage.utils import copy_paths


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
    """The analysis reads path with caches fetched if they exist."""
    analysis_args.reads_path.mkdir(parents=True, exist_ok=True)

    if cache_document:
        await fetch_cache(cache_document,
                          cache_path,
                          analysis_args.reads_path,
                          run_in_executor)

    elif not all(f["raw"] for f in analysis_args.sample["files"]):
        legacy_paths = utils.make_legacy_read_paths(analysis_args.sample_path, analysis_args.paired)

        paths_to_copy = {path: reads_path/path.name
                         for path in legacy_paths}

        await copy_paths(paths_to_copy.items(), run_in_executor)
    else:
        await prepare_reads_and_create_cache(analysis_args,
                                             trimming_parameters,
                                             trimming_command,
                                             cache_path,
                                             number_of_processes,
                                             database,
                                             run_in_executor)

    return analysis_args.reads_path














