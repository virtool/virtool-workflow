import asyncio
import shutil
import virtool_workflow
import virtool_core.caches.db
from typing import Dict, Any, List
from pathlib import Path
from .analysis_info import AnalysisArguments, sample_path, sample
from .cache import cache_document, fetch_cache, create_cache
from .trim_parameters import trimming_parameters
from virtool_workflow.execute import run_in_executor, FunctionExecutor
from virtool_workflow.storage.paths import cache_path
from virtool_workflow.storage.utils import copy_paths
from virtool_workflow_runtime.db import VirtoolDatabase


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
        run_in_executor: FunctionExecutor
) -> Path:
    """The analysis reads path with caches fetched if they exist"""
    if cache_document:
        await fetch_cache(cache_document,
                          cache_path,
                          analysis_args.reads_path,
                          run_in_executor)

    elif not all(f["raw"] for f in analysis_args.sample["files"]):
        legacy_paths = [analysis_args.sample_path/"reads_1.fastq"]
        if analysis_args.sample["paired"]:
            legacy_paths.append(analysis_args.sample_path/"reads_2.fastq")

        await copy_paths(legacy_paths,
                         [reads_path/path.name for path in legacy_paths],
                         run_in_executor)
    else:
        await create_cache(analysis_args.sample_id, analysis_args.analysis_id,
                           analysis_args.paired, trimming_parameters, database)

    return analysis_args.reads_path














