from dataclasses import dataclass

from virtool_workflow import fixture
from virtool_workflow.abc.caches.analysis_caches import ReadsCache
from virtool_workflow.analysis.utils import ReadPaths, make_read_paths


@dataclass
class Reads:
    """The prepared reads for an analysis workflow."""
    paired: bool
    min_length: int
    max_length: int
    count: int
    paths: ReadPaths


@fixture
async def reads(
        paired: bool,
        reads_cache: ReadsCache = None,
):
    """A fixture for accessing trimmed reads for the current sample."""
    min_length, max_length = reads_cache.quality["length"]

    return Reads(
        paired,
        min_length,
        max_length,
        reads_cache.quality["count"],
        make_read_paths(reads_cache.path, paired)
    )
