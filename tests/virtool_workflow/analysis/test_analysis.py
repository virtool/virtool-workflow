from pathlib import Path

from virtool_workflow.abc.caches.analysis_caches import AbstractReadsCache
from virtool_workflow.caching.local import LocalCache
from virtool_workflow.execution.run_in_executor import FunctionExecutor, run_in_executor, thread_pool_executor


class MockReadsCache(AbstractReadsCache, LocalCache):

    def __init__(self, path: Path, run_in_executor: FunctionExecutor):
        super(MockReadsCache, self).__init__("test_analysis_cache", path, run_in_executor)
        self._quality = None

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


async def test_reads_caching(tmpdir):
    read_cache = MockReadsCache(Path(tmpdir), run_in_executor(thread_pool_executor()))

    reads(read_cache)
