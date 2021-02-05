import json
import pytest
from pathlib import Path

from virtool_workflow.db.data_providers.sample_data_provider import SampleDataProvider
from virtool_workflow.db.inmemory import InMemoryDatabaseCollection
from virtool_workflow.uploads.files import FileUpload

TEST_SAMPLE = json.loads((Path(__file__).parent / "sample.json").read_text())


@pytest.fixture
async def analyses():
    return InMemoryDatabaseCollection()


@pytest.fixture
async def samples():
    return InMemoryDatabaseCollection()


@pytest.fixture
async def provider(analyses, samples) -> SampleDataProvider:
    sample_id = await samples.insert(TEST_SAMPLE)

    return SampleDataProvider(sample_id, samples, analyses)


async def test_fetch_sample(provider):
    sample = await provider.fetch_sample()

    assert sample.name == TEST_SAMPLE["name"]
    assert sample.host == TEST_SAMPLE["host"]


async def test_set_quality(provider, samples):
    await provider.set_quality(None)

    document = await samples.get(provider.sample_id)

    assert document["quality"] is None


async def test_delete_sample(provider: SampleDataProvider, samples: InMemoryDatabaseCollection):
    await provider.delete_sample()
    assert await samples.get(provider.sample_id) is None


async def test_set_files(provider: SampleDataProvider, samples: InMemoryDatabaseCollection):
    file = Path("foo")
    file.touch()

    await provider.set_files([(FileUpload(file.name, "", file, "unknown"), file)])

    file.unlink()

    document = await samples.get(provider.sample_id)

    assert document["files"][0]["name"] == "foo"


async def test_set_prune(provider: SampleDataProvider, samples: InMemoryDatabaseCollection):
    await provider.set_prune(True)

    assert (await samples.get(provider.sample_id))["prune"]


async def test_delete_files(provider: SampleDataProvider, samples: InMemoryDatabaseCollection):
    await provider.delete_files()

    assert (await samples.get(provider.sample_id))["files"] is None
