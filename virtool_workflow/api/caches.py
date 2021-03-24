from pathlib import Path

from virtool_workflow.abc.caches.analysis_caches import ReadsCache
from virtool_workflow.caching.caches import GenericCacheWriter


class RemoteCacheWriter(GenericCacheWriter[ReadsCache]):
    async def open(self):
        ...

    async def upload(self, path: Path):
        pass

    async def delete(self):
        pass
