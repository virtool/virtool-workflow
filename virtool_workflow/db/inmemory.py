from typing import Any, Optional, List
from uuid import uuid1

from virtool_workflow.abc.db import AbstractDatabaseCollection
from virtool_workflow.db.db import VirtoolDatabase


class InMemoryDatabaseCollection(AbstractDatabaseCollection):
    """An in memory database collection for testing."""

    def __init__(self):
        self._db = {}

    async def get(self, id: str) -> Optional[Any]:
        if id in self._db:
            return self._db[id]

    async def find_by_projection(self, projection: List[str]) -> List[dict]:
        return [document for document in self._db if all(key in document for key in projection)]

    async def set(self, id: str, **kwargs):
        self._db[id].update(**kwargs)

    async def insert(self, value: Any) -> str:
        key = uuid1().hex
        self._db[key] = value
        return key

    async def delete(self, id: str):
        del self._db[id]


class InMemoryDatabase(VirtoolDatabase):
    """An in-memory database to use for testing."""

    def __init__(self):
        super(InMemoryDatabase, self).__init__(
            *((InMemoryDatabaseCollection(),) * 8)
        )

