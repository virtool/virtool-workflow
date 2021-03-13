"""Perform read prep before accessing Virtool reads."""
import logging
import shutil
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
    if reads_cache:
        await run_in_executor(shutil.copytree, reads_cache.path, reads_path)
        return Reads.from_quality(reads_cache.quality, paired, reads_path)
    else:
        raise NotImplementedError()
