from typing import Dict

from virtool_workflow.abc.db import AbstractDatabaseCollection
from virtool_workflow.abc.data_providers.indexes import AbstractIndexProvider
from virtool_workflow.data_model import Reference


class IndexDataProvider(AbstractIndexProvider):

    def __init__(self,
                 index_id: str,
                 indexes: AbstractDatabaseCollection,
                 references: AbstractDatabaseCollection):
        self.index_id = index_id
        self.indexes = indexes
        self.references = references

        self._index = None

    async def _fetch_index(self):
        if self._index:
            return self._index

        self._index = await self.indexes.get(self.index_id)

        return self._index

    async def fetch_reference(self) -> Reference:
        index = await self._fetch_index()
        ref_data = await self.references.get(index["reference"]["id"])

        return Reference(
            id=ref_data["_id"],
            name=ref_data["name"],
            description=ref_data["description"],
            data_type=ref_data["data_type"],
            organism=ref_data["organism"],
        )

    async def fetch_manifest(self) -> Dict[str, int]:
        index = await self._fetch_index()

        return index["manifest"]

    async def set_has_json(self):
        await self.indexes.set(self.index_id, has_json=True, ready=True)

