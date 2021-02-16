"""Create caches of read-prep steps for Virtool analysis workflows."""
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from virtool_workflow import fixture
from virtool_workflow.abc.data_providers import AbstractCacheProvider
from virtool_workflow.abc.data_providers.cache import CacheEntry
from virtool_workflow.analysis import utils
from virtool_workflow.execution.run_in_executor import FunctionExecutor
from virtool_workflow.storage.utils import copy_paths

logger = logging.getLogger(__name__)

TRIMMING_PROGRAM = "skewer-0.2.2"


@fixture
async def cache_entry(
        cache_provider: AbstractCacheProvider,
        trimming_parameters: Dict[str, Any],
        sample_id: str,
) -> Optional[CacheEntry]:
    """
    The cache document for the current analysis.

    If no cache exists (ie. the current analysis job is not a re-try) then None is returned.
    """
    return await cache_provider.find(trimming_parameters, TRIMMING_PROGRAM)


async def fetch_cache(
        cache_entry: CacheEntry,
        paired: bool,
        cache_path: Path,
        reads_path: Path,
        run_in_executor: FunctionExecutor
):
    """Copy cached read files to the reads_path."""
    cached_read_paths = utils.make_read_paths(
        reads_dir_path=cache_path / cache_entry.id,
        paired=paired
    )

    await copy_paths(
        {path: reads_path / path.name for path in cached_read_paths}.items(),
        run_in_executor
    )


async def create_cache(
        cache_provider: AbstractCacheProvider,
        job_args: Dict[str, Any],
        paired: bool,
        fastqc: Dict[str, Any],
        trimming_parameters: Dict[str, Any],
        trimming_output_path: Path,
        cache_path: Path,
):
    """Cache the trimmed reads and parsed fastqc data."""
    cache = await cache_provider.create(trimming_parameters, paired, fastqc)

    shutil.copytree(trimming_output_path, cache_path / cache["id"])
