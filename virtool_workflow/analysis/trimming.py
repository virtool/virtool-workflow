"""Calculate trimming parameters which are passed the Skewer read trimming tool."""
import hashlib
import json
from typing import Dict, Union
from pyfixtures import fixture
from virtool_core.models.enums import LibraryType

from virtool_workflow.analysis.sample import WFSample
from virtool_workflow.analysis.skewer import calculate_trimming_min_length


TRIM_PARAMETERS = {
    "end_quality": "20",
    "mode": "pe",
    "max_error_rate": "0.1",
    "max_indel_rate": "0.03",
    "max_length": None,
    "mean_quality": "25",
    "min_length": "20",
}


@fixture
def trimming_min_length(sample: WFSample):
    return calculate_trimming_min_length(sample.library_type, sample.max_length)


@fixture
def trimming_parameters(
    sample: WFSample, trimming_min_length: int
) -> Dict[str, Union[str, int]]:
    """
    Calculates trimming parameters based on the library type, and minimum allowed trim length.

    :param sample: The sample being trimmed.
    :param trimming_min_length: The minimum length of a read before it is discarded.
    :return: the trimming parameters
    """
    if sample.library_type == LibraryType.amplicon:
        return {
            **TRIM_PARAMETERS,
            "end_quality": 0,
            "mean_quality": 0,
            "min_length": trimming_min_length,
        }

    if sample.library_type == LibraryType.srna:
        return {
            **TRIM_PARAMETERS,
            "min_length": 20,
            "max_length": 22,
        }

    return {**TRIM_PARAMETERS, "min_length": trimming_min_length}


@fixture
def trimming_cache_key(sample: WFSample, trimming_parameters: dict):
    """Compute a unique cache key based on the trimming parameters"""
    trim_param_json = json.dumps(
        {
            "id": sample.id,
            "min_length": sample.min_length,
            **trimming_parameters,
        },
        sort_keys=True,
    )

    raw_key = "reads-" + trim_param_json

    return hashlib.sha256(raw_key.encode()).hexdigest()
