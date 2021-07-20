from pathlib import Path

import pytest

from tests.api.mocks.mock_sample_routes import TEST_SAMPLE_ID
from virtool_workflow.analysis import reads
from virtool_workflow.caching.local import LocalCaches
from virtool_workflow.caching.caches import ReadsCache
from virtool_workflow.data_model import Job


@pytest.fixture
def scope(runtime):
    runtime["job"] = Job(
        id=test_get_reads_from_existing_cache.__name__,
        args={
            "sample_id": TEST_SAMPLE_ID,
        }
    )

    return runtime


async def test_get_reads_from_existing_cache(
        scope,
        tmpdir,
        run_in_executor,
        analysis_files,
):

    read_files = (analysis_files/"reads_1.fq.gz",
                  analysis_files/"reads_2.fq.gz")
    cache_path = Path(tmpdir)

    caches = LocalCaches[ReadsCache](
        path=cache_path,
        run_in_executor=run_in_executor
    )

    cache_key = await scope.get_or_instantiate("trimming_cache_key")

    async with caches.create(cache_key) as cache:
        await cache.upload(read_files[0])
        await cache.upload(read_files[1])

        cache.quality = {}

    scope["sample_caches"] = caches

    trimmed_reads = await scope.instantiate(reads.reads)

    assert trimmed_reads.sample.id == "hl5v0i0y"
    assert trimmed_reads.quality == {}
    assert trimmed_reads.left == cache_path/"reads_1.fq.gz"
    assert trimmed_reads.right == cache_path/"reads_2.fq.gz"
