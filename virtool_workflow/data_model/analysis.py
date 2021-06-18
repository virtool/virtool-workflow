from dataclasses import dataclass
from typing import List

from virtool_workflow.data_model.files import VirtoolFile
from virtool_workflow.data_model.indexes import Index
from virtool_workflow.data_model.samples import Sample
from virtool_workflow.data_model.subtractions import Subtraction


@dataclass
class Analysis:
    """
    A data model for Virtool analyses.

    """
    #: The analysis' unique database ID.
    id: str
    #: A list of files associated with the analysis
    files: List[VirtoolFile]
    #: The parent sample of the analysis
    sample: Sample = None
    #: The reference index being used in the analysis.
    index: Index = None
    #: The subtractions being used in the analysis.
    subtractions: List[Subtraction] = None
    #: Flag indicating if the analysis has been finalized.
    ready: bool = False
