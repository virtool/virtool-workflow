from virtool_workflow.abc.data_providers.cache import AbstractCaches, AbstractCache


class MockCaches(AbstractCaches):

    async def get(self, key: str) -> AbstractCache:
        pass

    async def create(self, key: str) -> AbstractCache:
        pass


MockCaches(AbstractCaches)


async def test_reads_caching():
