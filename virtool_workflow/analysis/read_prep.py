"""Perform read prep before accessing Virtool reads."""
import logging
from pathlib import Path

from virtool_workflow import fixture
from virtool_workflow.abc.caches.analysis_caches import ReadsCache
from virtool_workflow.analysis.reads import Reads
from virtool_workflow.execution.run_in_executor import FunctionExecutor

logger = logging.getLogger(__name__)


@fixture
async def reads(
        reads_path: Path,
        run_in_executor: FunctionExecutor,
        paired: bool,
        reads_cache: ReadsCache = None,
):
    """A fixture for accessing trimmed reads for the current sample."""
    return Reads.from_quality(reads_cache.quality, paired, reads_cache.path)
