from contextlib import suppress

import virtool_workflow
from virtool_workflow.abc.caches.analysis_caches import ReadsCache
from virtool_workflow.analysis import trim_parameters
from virtool_workflow.analysis.read_caching.fastqc import FastQC
from virtool_workflow.analysis.read_caching.trimming import Trimming
from virtool_workflow.caching.caches import GenericCaches
from virtool_workflow.data_model import Sample


@virtool_workflow.fixture
async def trimming(sample: Sample, number_of_processes: int, run_subprocess) -> Trimming:
    parameters = trim_parameters.trimming_parameters(
        sample.library_type,
        trim_parameters.trimming_min_length(sample.library_type, sample.quality["length"])
    )

    return Trimming(parameters, number_of_processes, run_subprocess)


@virtool_workflow.fixture
async def fastqc(work_path, run_subprocess) -> FastQC:
    return FastQC(work_path, run_subprocess)


@virtool_workflow.fixture
async def reads_cache(sample: Sample, caches: GenericCaches[ReadsCache], trimming: Trimming, fastqc) -> ReadsCache:
    cache_key = f'{sample.id}-reads-{hash(trimming)}'

    with suppress(KeyError):
        return await caches.get(cache_key)

    async with caches.create(cache_key) as cache:
        await trimming.run_trimming(output_path=cache.path)
        cache.quality = await fastqc.run(cache.path)

        for path in cache.path.iterdir():
            await cache.upload(path)

    return await caches.get(cache_key)
