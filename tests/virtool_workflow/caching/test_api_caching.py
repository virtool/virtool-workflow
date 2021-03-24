from pathlib import Path

from tests.virtool_workflow.api.mocks.mock_sample_routes import TEST_CACHE, TEST_SAMPLE_ID
from virtool_workflow.api.caches import RemoteReadsCacheWriter


async def test_api_caching(tmpdir, http, jobs_api_url, run_in_executor):
    tmpdir = Path(tmpdir)
    cache_dir = tmpdir / "cache"
    cache_dir.mkdir()

    writer = RemoteReadsCacheWriter(TEST_CACHE["key"],
                                    cache_dir,
                                    TEST_SAMPLE_ID,
                                    http,
                                    jobs_api_url,
                                    run_in_executor)

    read_1 = tmpdir / "reads_1.fq.gz"
    read_2 = tmpdir / "reads_2.fq.gz"

    read_1.touch()
    read_2.touch()

    quality = {"length": [0, 100]}

    async with writer:
        writer.quality = quality
        await writer.upload(read_1)
        await writer.upload(read_2)

    cache = writer.cache

    assert cache.quality == quality
    assert cache.path.exists()
    assert (cache.path / "reads_1.fq.gz").exists()
    assert (cache.path / "reads_2.fq.gz").exists()

    assert TEST_CACHE["ready"] is True
