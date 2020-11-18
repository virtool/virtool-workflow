"""Calculate trimming parameters (parameters to skewer)."""
from typing import Dict, Union

from virtool_core.samples.utils import TRIM_PARAMETERS
from .library_types import LibraryType
from .. import fixture


@fixture
def trimming_min_length(library_type: LibraryType, sample_read_length: int):
    """
    The minimum length of a read.

    This takes into account the library type (eg. srna)
    and the maximum observed read length in the sample.

    :param library_type: the sample library type
    :param sample_read_length: the maximum read length observed in the sample
    :return: the minimum allowed trimmed read length
    """
    if library_type == LibraryType.amplicon:
        return round(0.95 * sample_read_length)

    if sample_read_length < 80:
        return 35

    if sample_read_length < 160:
        return 100

    return 160


@fixture
def trimming_parameters(
        library_type: LibraryType,
        trimming_min_length: int
) -> Dict[str, Union[str, int]]:
    """
    The trimming parameters based on the library type, and minimum allowed trim length.

    :param library_type: The LibraryType (eg. srna)
    :param trimming_min_length: The minimum length of a read
        before it is discarded.
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
