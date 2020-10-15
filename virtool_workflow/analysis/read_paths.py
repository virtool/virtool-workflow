import virtool_workflow
from typing import Dict, Any, List
from pathlib import Path
from .analysis_info import AnalysisArguments
from .cache import cache_document, fetch_cache
from virtool_workflow.execute import run_in_executor, FunctionExecutor
from virtool_workflow.storage.paths import cache_path


@virtool_workflow.fixture
async def reads_path(
        analysis_args: AnalysisArguments,
        cache_path: Path,
        cache_document: Dict[str, Any],
        run_in_executor: FunctionExecutor
) -> Path:
    """The analysis reads path with caches fetched if they exist"""
    if cache_document:
        await fetch_cache(cache_document, cache_path,
                          analysis_args.reads_path, run_in_executor)
    return analysis_args.reads_path









