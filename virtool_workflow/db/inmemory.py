from typing import Any, Optional
from uuid import uuid1

from virtool_workflow.abc.db import AbstractDatabaseCollection


class InMemoryDatabaseCollection(AbstractDatabaseCollection):
    """An in memory database collection for testing."""

    def __init__(self):
        self._db = {}

    async def get(self, id: str) -> Optional[Any]:
        return self._db[id]

    async def set(self, id: str, **kwargs):
        self._db[id].update(**kwargs)

    async def insert(self, value: Any) -> str:
        key = uuid1().hex
        self._db[key] = value
        return key

    async def delete(self, id: str):
        del self._db[id]
