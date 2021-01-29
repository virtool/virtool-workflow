from dataclasses import dataclass

from typing import Optional, List

from virtool_workflow.data_model.references import Reference
from virtool_workflow.data_model.samples import Sample
from virtool_workflow.data_model.subtractions import Subtraction
from virtool_workflow.data_model.indexes import Index


@dataclass(frozen=True)
class Analysis:
    _id: str
    cache: dict
    index: Index
    reference: Reference
    sample: Sample
    subtractions: List[Subtraction]
    read_count: Optional[int] = None
    subtracted_count: Optional[int] = None

