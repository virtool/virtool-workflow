from pathlib import Path

import aiohttp

from tests.virtool_workflow.api.mocks.mock_sample_routes import TEST_SAMPLE_ID
from virtool_workflow.abc.caches.analysis_caches import ReadsCache
from virtool_workflow.analysis.read_caching.reads_cache import reads_cache
from virtool_workflow.analysis.reads import Reads, reads
from virtool_workflow.analysis.utils import make_read_paths
from virtool_workflow.api.samples import SampleProvider
from virtool_workflow.caching.local import LocalCacheWriter, LocalCaches


async def test_get_reads_from_existing_cache(tmpdir, run_in_executor):
    tmpdir = Path(tmpdir)
    reads_path = tmpdir / "reads"
    reads_path.mkdir()
    reads_cache_writer = LocalCacheWriter[ReadsCache]("read_cache", reads_path, run_in_executor)

    mock_reads_file = tmpdir / "work/reads.fq.gz"
    mock_reads_file.parent.mkdir()
    mock_reads_file.touch()

    async with reads_cache_writer:
        await reads_cache_writer.upload(mock_reads_file)
        reads_cache_writer.quality = {
            "length": [0, 100],
            "count": 10
        }

    _reads = await reads(reads_cache=reads_cache_writer.cache, paired=False)

    assert isinstance(_reads, Reads)

    assert _reads.paired is False
    assert _reads.count == 10
    assert (_reads.min_length, _reads.max_length) == (0, 100)
    assert _reads.paths == make_read_paths(reads_path, False)


async def test_reads_fixture_without_existing_cache(runtime, http: aiohttp.ClientSession,
                                                    jobs_api_url: str, tmpdir, run_in_executor):
    runtime["caches"] = LocalCaches[ReadsCache](Path(tmpdir), run_in_executor)
    runtime["number_of_processes"] = 3
    runtime["sample_provider"] = SampleProvider(TEST_SAMPLE_ID, http, jobs_api_url)
    runtime["work_path"] = Path(tmpdir)

    cache = await runtime.instantiate(reads_cache)

    await cache
