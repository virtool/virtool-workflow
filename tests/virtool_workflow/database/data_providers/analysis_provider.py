import pytest
from virtool_workflow.db.data_providers.analysis_data_provider import AnalysisDataProvider
from virtool_workflow.db.inmemory import InMemoryDatabaseCollection
from virtool_workflow.uploads.files import FileUpload
from pathlib import Path


@pytest.fixture
async def provider_and_db():
    db = InMemoryDatabaseCollection()
    id_ = await db.insert({})

    return AnalysisDataProvider(analysis_id=id_, db=db), db


async def test_store_result(provider_and_db):
    provider, db = provider_and_db

    await provider.store_result(dict(foo=True))

    document = await db.get(provider.analysis_id)
    assert document["results"]["foo"]


async def test_set_files(provider_and_db):
    provider, db = provider_and_db

    foo = Path("foo")

    foo.touch()

    files = [(FileUpload(name=foo.name, description="", path=foo, format="unknown"), foo)]
    await provider.store_files(files)

    foo.unlink()

    document = await db.get(provider.analysis_id)

    assert document["files"][0]["id"] == "foo"


async def test_delete(provider_and_db):
    provider, db = provider_and_db

    assert await db.get(provider.analysis_id) is not None

    await provider.delete()

    assert await db.get(provider.analysis_id) is None


