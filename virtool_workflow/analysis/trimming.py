"""Calculate trimming parameters which are passed the Skewer read trimming tool."""
from typing import Dict, Union

from virtool_core.samples.utils import TRIM_PARAMETERS

from virtool_workflow.analysis.library_types import LibraryType


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
