import shutil
from pathlib import Path

from virtool_workflow.abc.caches.cache import AbstractCacheWriter, AbstractCaches, Cache, CacheExists
from virtool_workflow.caching.caches import GenericCacheWriter
from virtool_workflow.execution.run_in_executor import FunctionExecutor


class LocalCacheWriter(GenericCacheWriter):
    """A cache stored in the local filesystem."""

    def __init__(self, key: str, path: Path, run_in_executor: FunctionExecutor):
        self.key = key
        self.path = path
        self.run_in_executor = run_in_executor

        super(LocalCacheWriter, self).__init__()

        self._attributes["key"] = key
        self._attributes["path"] = path

    async def upload(self, path: Path):
        await self.run_in_executor(shutil.copyfile, path, self.path / path.name)

    async def delete(self):
        await self.run_in_executor(shutil.rmtree, self.path)


class LocalCaches(AbstractCaches):
    cache_class = Cache

    def __init__(self, path: Path, run_in_executor: FunctionExecutor):
        self.path = path
        path.mkdir(parents=True, exist_ok=True)

        self.run_in_executor = run_in_executor
        self._caches = {}

    async def get(self, key: str) -> AbstractCacheWriter:
        try:
            return self._caches[key].cache
        except AttributeError:
            del self._caches[key]
            raise KeyError(key)

    def create(self, key: str) -> AbstractCacheWriter:
        if key in self._caches:
            raise CacheExists(key)
        self._caches[key] = LocalCacheWriter[self.cache_class](key, self.path, self.run_in_executor)
        return self._caches[key]

    def __contains__(self, key: str):
        return key in self._caches

    def __class_getitem__(cls, item):
        cls.cache_class = item
        return cls
