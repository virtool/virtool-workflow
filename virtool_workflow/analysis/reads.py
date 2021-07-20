from dataclasses import dataclass
from pathlib import Path

from aiohttp import ClientSession

from fixtures import fixture

from virtool_workflow.analysis.fastqc import fastqc
from virtool_workflow.analysis.skewer import skewer
from virtool_workflow.analysis.trimming import (trimming_cache_key,
                                                trimming_min_length,
                                                trimming_parameters)
from virtool_workflow.api.caches import RemoteReadCaches
from virtool_workflow.data_model.samples import Sample
from virtool_workflow.caching.caches import GenericCaches
from virtool_workflow.abc.caches.analysis_caches import ReadsCache

__depends_on__ = (
    trimming_min_length,
    trimming_cache_key,
    trimming_parameters
)


@dataclass
class Reads:
    """
    Dataclass storing the trimmed reads for a sample.

    :param sample: The target sample.
    :param quality: The fastqc results for the trimmed reads.
    :param path: The path to the directory containing the trimmed read files.
    """
    sample: Sample
    quality: dict
    path: Path

    @property
    def left(self):
        return self.path / "reads_1.fq.gz"

    @property
    def right(self):
        return self.path / "reads_2.fq.gz"


@fixture
def sample_caches(
        sample: Sample,
        work_path: Path,
        jobs_api_url: str,
        http: ClientSession,
        run_in_executor,
):
    cache_path = work_path / "caches" / sample.id
    cache_path.mkdir(parents=True)
    return RemoteReadCaches(
        sample.id,
        sample.paired,
        cache_path,
        http,
        jobs_api_url,
        run_in_executor
    )


@fixture
async def reads(
    sample: Sample,
    sample_caches: GenericCaches[ReadsCache],
    trimming_parameters: dict,
    trimming_cache_key: str,
    work_path: Path,
    run_subprocess,
    run_in_executor
):
    """
    The trimmed sample reads.

    If a cache exists it will be used, otherwise a new cache will be created.
    """

    try:
        cache = await sample_caches.get(trimming_cache_key)
        return Reads(sample, quality=cache.quality, path=cache.path)
    except KeyError:
        result = await skewer(
            **trimming_parameters
        )(sample.read_paths, run_subprocess, run_in_executor)

        quality = await fastqc(work_path, run_subprocess)(sample.read_paths)

        async with sample_caches.create(trimming_cache_key) as cache:
            for path in result.read_paths:
                await cache.upload(path)

                cache.quality = quality

        return Reads(sample=sample, quality=quality, path=result.left.parent)
