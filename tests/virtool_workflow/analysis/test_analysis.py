import shutil
from pathlib import Path

from virtool_workflow.abc.data_providers.cache import AbstractCaches, AbstractCache


class MockCache(AbstractCache):

    def __init__(self, key, path):
        self.key = key
        self.path = path
        self.open = False

    async def open(self) -> "AbstractCache":
        self.open = True
        return self

    async def upload(self, path: Path):
        shutil.copyfile(path, self.path / path.name)

    async def close(self):
        self.open = False

    async def delete(self):
        shutil.rmtree(self.path)


class MockCaches(AbstractCaches):

    async def get(self, key: str) -> AbstractCache:
        pass

    async def create(self, key: str) -> AbstractCache:
        pass


MockCaches(AbstractCaches)


async def test_reads_caching():
