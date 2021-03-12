import shutil
from pathlib import Path

from virtool_workflow.abc.caches.cache import AbstractCacheWriter, AbstractCaches
from virtool_workflow.execution.run_in_executor import FunctionExecutor


class LocalCache(AbstractCacheWriter):
    """A cache stored in the local filesystem."""

    def __init__(self, key: str, path: Path, run_in_executor: FunctionExecutor):
        self.key = key
        self.path = path
        self.run_in_executor = run_in_executor
        self.closed = False

        path.mkdir(parents=True, exist_ok=True)

    async def open(self) -> "AbstractCacheWriter":
        self.closed = False
        return self

    async def upload(self, path: Path):
        await self.run_in_executor(shutil.copyfile, path, self.path / path.name)

    async def close(self):
        self.closed = True

    async def delete(self):
        await self.run_in_executor(shutil.rmtree, self.path)


class LocalCaches(AbstractCaches):

    def __init__(self, path: Path, run_in_executor: FunctionExecutor):
        self.path = path
        path.mkdir(parents=True, exist_ok=True)

        self.run_in_executor = run_in_executor
        self._caches = {}

    async def get(self, key: str) -> AbstractCacheWriter:
        return self._caches[key]

    async def create(self, key: str) -> AbstractCacheWriter:
        self._caches = LocalCache(key, self.path / key, self.run_in_executor)
        return self._caches[key]

    def __contains__(self, key: str):
        return key in self._caches
