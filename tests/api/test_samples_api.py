import gzip
from pathlib import Path

import pytest

from tests.api.mocks.mock_sample_routes import TEST_SAMPLE_ID
from virtool_workflow.api.errors import AlreadyFinalized
from virtool_workflow.api.samples import SampleProvider

QUALITY = {
    "bases": [
        [30, 31, 31, 31, 31, 31],
        [30, 31, 31, 31, 31, 32],
    ],
    "composition": [
        [32, 14, 4, 40],
        [22, 12, 34, 25],
    ],
    "count": 998822,
    "encoding": "Sanger / Illumina 1.8",
    "gc": 43,
    "length": [0, 52],
    "sequences": [
        0,
        0,
        3512,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ],
}


@pytest.fixture
def sample_api(http, jobs_api_connection_string: str):
    return SampleProvider(TEST_SAMPLE_ID, http, jobs_api_connection_string)


async def test_get(sample_api, snapshot):
    assert await sample_api.get() == snapshot


async def test_finalize(sample_api, snapshot):
    sample = await sample_api.finalize(QUALITY)

    assert sample.quality == QUALITY
    assert sample == snapshot


async def test_delete(sample_api):
    await sample_api.delete()


async def test_delete_after_finalize(sample_api):
    sample_api.id = "finalized"

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


async def test_download(sample_api, tmpdir, file_regression):
    tmpdir = Path(tmpdir)

    read_files = await sample_api.download_reads(tmpdir, paired=True)

    for read_file in read_files:
        with gzip.open(read_file) as f:
            file_regression.check(f.read(), basename=read_file.name, binary=True)

    assert (
        read_files == read_files == (tmpdir / "reads_1.fq.gz", tmpdir / "reads_2.fq.gz")
    )

    await sample_api.download_artifact("artifact.json", tmpdir)

    assert (tmpdir / "artifact.json").exists()
