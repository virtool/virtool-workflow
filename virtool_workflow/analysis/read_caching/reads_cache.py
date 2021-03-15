from contextlib import suppress

import virtool_workflow
from virtool_workflow.abc.caches.analysis_caches import ReadsCache
from virtool_workflow.caching.caches import GenericCaches
from virtool_workflow.data_model import Sample


@virtool_workflow.fixture
async def reads_cache(sample: Sample, caches: GenericCaches[ReadsCache], trimming, fastqc) -> ReadsCache:
    cache_key = f'{sample.id}-reads-{hash(trimming)}'

    with suppress(KeyError):
        return await caches.get(cache_key)

    async with caches.create(cache_key) as cache:
        for path in await trimming.run_trimming(output_path=cache.path):
            await cache.upload(path)
            cache.quality = await fastqc.run(cache.path)

    return await caches.get(cache_key)
