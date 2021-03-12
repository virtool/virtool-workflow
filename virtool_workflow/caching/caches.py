from virtool_workflow.abc.caches.cache import AbstractCaches, AbstractCacheWriter


class Caches(AbstractCaches):
    async def get(self, key: str) -> AbstractCacheWriter:
        pass

    async def create(self, key: str) -> AbstractCacheWriter:
        pass

    def __contains__(self, item: str):
        pass
