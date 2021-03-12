from pathlib import Path

from virtool_workflow.abc.caches.analysis_caches import AbstractReadsCache
from virtool_workflow.analysis.read_prep import reads
from virtool_workflow.analysis.reads import Reads
from virtool_workflow.analysis.utils import make_read_paths
from virtool_workflow.caching.local import LocalCache
from virtool_workflow.execution.run_in_executor import FunctionExecutor


class MockReadsCache(AbstractReadsCache, LocalCache):

    def __init__(self, path: Path, run_in_executor: FunctionExecutor):
        super(MockReadsCache, self).__init__("test_analysis_cache", path, run_in_executor)
        self._quality = None
        self.finalized = False

    @property
    def quality(self):
        return self._quality

    @quality.setter
    def quality(self, qc: dict):
        self._quality = qc

    async def open(self) -> "MockReadsCache":
        return self

    async def close(self):
        await AbstractReadsCache.close(self)
        self.finalized = True


async def test_get_reads_from_existing_cache(tmpdir, run_in_executor):
    tmpdir = Path(tmpdir)
    read_cache = MockReadsCache(tmpdir, run_in_executor)

    mock_reads_file = tmpdir / "work/reads.fq.gz"
    mock_reads_file.parent.mkdir()
    mock_reads_file.touch()

    async with read_cache:
        await read_cache.upload(mock_reads_file)
        read_cache.quality = {
            "length": [0, 100],
            "count": 10
        }

    assert read_cache.finalized

    _reads = await reads(read_cache, tmpdir / "reads", run_in_executor, False)

    assert isinstance(_reads, Reads)

    assert _reads.paired is False
    assert _reads.count == 10
    assert (_reads.min_length, _reads.max_length) == (0, 100)
    assert _reads.paths == make_read_paths(tmpdir / "reads", False)
