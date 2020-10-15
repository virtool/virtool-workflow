import asyncio
import shutil
from typing import Dict, Any, Optional
from pathlib import Path

from virtool_workflow import fixture
from virtool_workflow.execute import FunctionExecutor
from virtool_workflow_runtime.db.fixtures import caches, Collection
from .trim_parameters import trimming_parameters
from .analysis_info import sample_id
from virtool_core.caches.db import calculate_cache_hash

TRIMMING_PROGRAM = "skewer-0.2.2"


@fixture
async def cache_document(
        trimming_parameters: Dict[str, Any],
        sample_id: str,
        caches: Collection,
) -> Optional[Dict[str, Any]]:
    cache_document = caches.find_one({
        "hash": calculate_cache_hash(trimming_parameters),
        "missing": False,
        "program": TRIMMING_PROGRAM,
        "sample.id": sample_id
    })

    return cache_document


async def fetch_cache(
        cache_document: Dict[str, Any],
        cache_path: Path,
        reads_path: Path,
        run_in_executor: FunctionExecutor
):
    cached_read_dir_path = cache_path/cache_document["_id"]
    cached_read_paths = [cached_read_dir_path/"reads_1.fq.gz"]

    if cache_document["paired"]:
        cached_read_paths.append(
            cached_read_dir_path/"reads_2.fq.gz"
        )

    await asyncio.gather(*[
        run_in_executor(shutil.copy, path, reads_path/path.name)
        for path in cached_read_paths
    ])



