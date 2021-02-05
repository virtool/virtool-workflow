import pytest
from virtool_workflow.db.inmemory import InMemoryDatabaseCollection


@pytest.fixture
def db():
    return InMemoryDatabaseCollection()


async def test_insert_and_get(db):
    id_ = await db.insert(dict(foo="bar"))
    item = await db.get(id_)

    assert item["foo"] == "bar"


async def test_set_and_delete(db):
    id_ = await db.insert(dict(foo="bar"))

    await db.set(id_, foo="cat", bar="dog")

    item = await db.get(id_)

    assert item["foo"] == "cat" and item["bar"] == "dog"

    await db.delete(id_)

    assert await db.get(id_) is None



