from pytest import fixture
from virtool_workflow.db.data_providers.index_data_provider import IndexDataProvider
from virtool_workflow.db.inmemory import InMemoryDatabaseCollection

MOCK_INDEX = {
    "_id": "1",
    "version": 11,
    "created_at": {
        "$date": "2018-09-25T18:44:51.658Z"
    },
    "manifest": {
        "10798798": 0,
        "10857991": 0,
        "13053251": 0,
        "16174395": 2,
        "16699571": 0,
        "1984998": 0,
        "20603017": 2
    },
    "ready": False,
    "has_files": False,
    "job": {
        "id": "fbaya08n"
    },
    "reference": {
        "id": "original"
    },
    "user": {
        "id": "igboyes"
    }
}


@fixture
async def indexes():
    collection = InMemoryDatabaseCollection()
    await collection.insert(MOCK_INDEX, _id="1")

    return collection


MOCK_REFERENCE = {
    "_id": "original",
    "created_at": {
        "$date": "2019-10-04T17:17:48.935Z"
    },
    "data_type": "genome",
    "description": "",
    "name": "Clone of Banana Viruses",
    "organism": "virus",
    "source_types": [
        "isolate",
        "strain"
    ],
    "groups": [

    ],
    "cloned_from": {
        "id": "9mciizg6",
        "name": "Banana Viruses"
    },
}


@fixture
async def references():
    collection = InMemoryDatabaseCollection()

    await collection.insert(MOCK_REFERENCE, _id="original")

    return collection


@fixture
def provider(indexes, references):
    return IndexDataProvider("1", indexes, references)


async def test_fetch_reference(provider):
    reference = await provider.fetch_reference()

    assert reference.name == MOCK_REFERENCE["name"]
    assert reference.organism == MOCK_REFERENCE["organism"]
    assert reference.description == MOCK_REFERENCE["description"]
    assert reference.id == MOCK_REFERENCE["_id"]


async def test_fetch_manifest(provider):
    manifest = await provider.fetch_manifest()

    assert manifest == MOCK_INDEX["manifest"]


async def test_set_has_json(provider, indexes):
    await provider.set_has_json()

    index = await indexes.get("1")
    assert index["has_json"] and index["ready"]
