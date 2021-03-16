from pathlib import Path

import aiohttp
import pytest

from tests.virtool_workflow.api.mocks.mock_sample_routes import TEST_SAMPLE_ID, TEST_SAMPLE
from virtool_workflow.api.errors import AlreadyFinalized
from virtool_workflow.api.samples import SampleProvider
from virtool_workflow.data_model import Sample


@pytest.fixture
def sample_api(http: aiohttp.ClientSession, jobs_api_url: str):
    if "ready" in TEST_SAMPLE:
        del TEST_SAMPLE["ready"]
    return SampleProvider(TEST_SAMPLE_ID, http, jobs_api_url)


async def test_get(sample_api):
    sample = await sample_api.get()

    assert isinstance(sample, Sample)
    assert sample.id == sample_api.id

    for key in ["name", "id", "host", "isolate", "locale",
                "paired", "quality", "nuvs", "pathoscope"]:
        assert getattr(sample, key) == TEST_SAMPLE[key]

    for actual, expected in zip(sample.files, TEST_SAMPLE["files"]):
        assert actual == expected


async def test_finalize(sample_api):
    mock_quality = {"quality": True}
    sample = await sample_api.finalize(mock_quality)

    assert isinstance(sample, Sample)
    assert sample.quality == mock_quality


async def test_delete(sample_api):
    await sample_api.delete()


async def test_delete_after_finalize(sample_api):
    await sample_api.finalize({})

    with pytest.raises(AlreadyFinalized):
        await sample_api.delete()


async def test_upload(sample_api, tmpdir):
    tmpdir = Path(tmpdir)

    reads_1 = tmpdir / "reads_1.fq.gz"
    artifact = tmpdir / "artifact.json"

    reads_1.touch()
    artifact.touch()

    await sample_api.upload(reads_1)
    await sample_api.upload(artifact)


async def test_download(sample_api, tmpdir):
    tmpdir = Path(tmpdir)

    read_files = await sample_api.download_reads(tmpdir)

    assert read_files == (tmpdir / "reads_1.fq.gz",)

    await sample_api.download_artifact("artifact.json", tmpdir)

    assert (tmpdir / "artifact.json").exists()
