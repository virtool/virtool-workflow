from motor.motor_asyncio import AsyncIOMotorCollection

from virtool_workflow.abc.db import AbstractDatabaseCollection, DocumentUpdater


class MongoDocumentUpdater(DocumentUpdater):
    """A :class:`DocumentUpdater` for MongoDB documents."""

    def __init__(self, id: str, db: AsyncIOMotorCollection):
        self.id = id
        self.attrs = {}
        self._db = db

    def set(self, key, value):
        self.attrs[key] = value

    async def update(self):
        return await self._db.update_one(dict(_id=self.id), {
            "$set": self.attrs
        })


class MongoDatabaseCollection(AbstractDatabaseCollection):
    """A MongoDB database collection."""

    def __init__(self, _db: AsyncIOMotorCollection):
        self._db = _db

    async def get(self, id: str) -> dict:
        return await self._db.find_one(dict(_id=id))

    async def insert(self, value: dict) -> str:
        insert_result = await self._db.insert_one(value)
        return insert_result.inserted_id

    def update(self, id: str) -> MongoDocumentUpdater:
        return MongoDocumentUpdater(id, self._db)

    async def delete(self, id: str):
        await self._db.delete_one(dict(_id=id))
