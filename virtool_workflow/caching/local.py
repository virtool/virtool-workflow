import shutil
from pathlib import Path

from virtool_workflow.caching.caches import CacheWriter, Caches, Cache, CacheNotFinalized, CacheExists
from virtool_workflow.execution.run_in_executor import FunctionExecutor


class LocalCacheWriter(CacheWriter):
    """A cache stored in the local filesystem."""

    def __init__(self, key: str, path: Path, run_in_executor: FunctionExecutor):
        self.run_in_executor = run_in_executor
        super(LocalCacheWriter, self).__init__(key, path)

    async def upload(self, path: Path):
        await self.run_in_executor(shutil.copyfile, path, self.path / path.name)

    async def delete(self):
        await self.run_in_executor(shutil.rmtree, self.path)


class LocalCaches(Caches):
    """Access and create local caches."""

    def __init__(self, path: Path, run_in_executor: FunctionExecutor):
        self.path = path
        path.mkdir(parents=True, exist_ok=True)

        self.run_in_executor = run_in_executor
        self._caches = {}

    async def get(self, key: str) -> Cache:
        """Get a cache if one exists."""
        try:
            return self._caches[key].cache
        except (AttributeError, CacheNotFinalized):
            del self._caches[key]
            raise KeyError(key)

    def create(self, key: str) -> LocalCacheWriter:
        """Create a new cache."""
        if key in self._caches:
            raise CacheExists(key)
        self._caches[key] = LocalCacheWriter[self.cache_class](
            key, self.path, self.run_in_executor)
        return self._caches[key]

    def __contains__(self, key: str):
        return key in self._caches
