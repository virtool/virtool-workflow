"""Calculate trimming parameters which are passed the Skewer read trimming tool."""
import json
import hashlib
from pathlib import Path
from typing import Dict, Tuple, Union
from aiohttp import ClientSession

from virtool_core.samples.utils import TRIM_PARAMETERS

from virtool_workflow.analysis.fastqc import fastqc
from virtool_workflow.analysis.library_types import LibraryType
from virtool_workflow.analysis.sample import Sample
from virtool_workflow.analysis.skewer import (calculate_trimming_min_length,
                                              skewer)
from virtool_workflow.fixtures.providers import FixtureGroup
from virtool_workflow.api.caches import RemoteReadCaches
from virtool_workflow.analysis.reads import Reads


fixtures = FixtureGroup()


@fixtures.fixture
def trimming_min_length(sample: Sample):
    return calculate_trimming_min_length(
        sample.library_type,
        sample.max_length
    )


@fixtures.fixture
def trimming_parameters(
        library_type: LibraryType,
        trimming_min_length: int
) -> Dict[str, Union[str, int]]:
    """
    Calculates trimming parameters based on the library type, and minimum allowed trim length.

    :param library_type: The LibraryType (eg. srna)
    :param trimming_min_length: The minimum length of a read before it is discarded.
    :return: the trimming parameters
    """
    if library_type == LibraryType.amplicon:
        return {
            **TRIM_PARAMETERS,
            "end_quality": 0,
            "mean_quality": 0,
            "min_length": trimming_min_length
        }

    if library_type == LibraryType.srna:
        return {
            **TRIM_PARAMETERS,
            "min_length": 20,
            "max_length": 22,
        }

    return {
        **TRIM_PARAMETERS,
        "min_length": trimming_min_length
    }


@fixtures.fixture
def trimming_cache_key(sample: Sample, trimming_parameters: dict):
    """Compute a unique cache key based on the trimming parameters"""
    trim_param_json = json.dumps({
        "id": sample.id,
        "min_length": sample.min_length,
        **trimming_parameters,
    }, sort_keys=True)

    raw_key = "reads-" + trim_param_json

    return hashlib.sha256(raw_key.encode()).hexdigest()


@fixtures.fixture
def sample_caches(
        sample: Sample,
        cache_path: Path,
        jobs_api_url: str,
        http: ClientSession,
        run_in_executor,
):
    return RemoteReadCaches(
        sample.id,
        sample.paired,
        cache_path,
        http,
        jobs_api_url,
        run_in_executor
    )


@fixtures.fixture
def reads(
    sample: Sample,
    sample_caches: RemoteReadCaches,
    trimming_min_length: int,
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
        return Reads(sample, cache.path)
    except KeyError:
        result = await skewer(
            min_length=trimming_min_length,
            **trimming_parameters
        )(sample.read_paths, run_subprocess, run_in_executor)

        quality = await fastqc(work_path, run_subprocess)(sample.read_paths)

        async with sample_caches.create(trimming_cache_key) as cache:
            for path in result.read_paths:
                await cache.upload(path)

                cache.quality = quality

        return Reads(sample, result.read_paths)
