"""Calculate trimming parameters which are passed the Skewer read trimming tool."""
import hashlib
import json

from virtool_core.models.enums import LibraryType

from virtool_workflow.data.samples import WFSample


def calculate_trimming_cache_key(
    sample_id: str, trimming_parameters: dict, program: str = "skewer"
):
    """
    Compute a unique cache key.

    **This is not currently used.**

    :param sample_id: The ID of the sample being trimmed.
    :param trimming_parameters: The trimming parameters.
    :param program: The name of the trimming program.
    :return: A unique cache key.

    """

    raw_key = "reads-" + json.dumps(
        {
            "id": sample_id,
            "parameters": trimming_parameters,
            "program": program,
        },
        sort_keys=True,
    )

    return hashlib.sha256(raw_key.encode()).hexdigest()


def calculate_trimming_min_length(sample: WFSample) -> int:
    """
    Calculate the minimum trimming length that should be used for the passed sample.

    This takes into account the library type (:class:`.LibraryType`) and the maximum
    observed read length in the sample.

    :param sample: the sample
    :return: the minimum allowed trimmed read length
    """
    if sample.library_type == LibraryType.amplicon:
        return round(0.95 * sample.max_length)

    if sample.max_length < 80:
        return 35

    if sample.max_length < 160:
        return 100

    return 160
