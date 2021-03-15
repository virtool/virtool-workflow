import virtool_workflow
from virtool_workflow.abc.caches.analysis_caches import ReadsCache
from virtool_workflow.abc.caches.cache import AbstractCaches
from virtool_workflow.data_model import Sample


@virtool_workflow.fixture
def reads_cache(sample: Sample, caches: AbstractCaches, trimming) -> ReadsCache:
    cache_key = f'{sample.id}-reads-{hash(trimming)}'
    try:
        return await caches.get(cache_key)
    except KeyError:
        cache_writer = caches.create(cache_key)
