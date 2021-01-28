import pytest
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from virtool_workflow.db.mongo import MongoDatabaseCollection
from virtool_workflow_runtime.config.configuration import db_name, db_connection_string


@pytest.fixture
def db_factory():
    # Cannot instantiate db in fixture since each test is executed with a different event loop instance.
    def _db_factory():
        client = AsyncIOMotorClient(db_connection_string())
        db = client[db_name()]

        collection: AsyncIOMotorCollection = db["test_collection"]

        return MongoDatabaseCollection(collection)

    return _db_factory


async def test_insert_and_get(db_factory):
    db = db_factory()

    _id = await db.insert({"attr": "foo"})

    assert _id

    document = await db.get(_id)

    assert document["attr"] == "foo"


async def test_update(db_factory):
    db = db_factory()

    _id = await db.insert({"foo": "bar"})

    async with db.update(_id) as document:
        document.set("foo", "cat")
        document.set("attr", "value")

    document = await db.get(_id)

    assert document["foo"] == "cat"
    assert document["attr"] == "value"


async def test_delete(db_factory):
    db = db_factory()

    _id = await db.insert(dict(foo="bar"))

    document = await db.get(_id)

    assert document

    await db.delete(_id)

    document = await db.get(_id)

    assert not document


