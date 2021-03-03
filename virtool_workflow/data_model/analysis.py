from dataclasses import dataclass
from typing import Sequence

from virtool_workflow.data_model.files import VirtoolFile
from virtool_workflow.data_model.indexes import Index
from virtool_workflow.data_model.samples import Sample
from virtool_workflow.data_model.subtractions import Subtraction


@dataclass
class Analysis:
    id: str
    files: Sequence[VirtoolFile]
    sample: Sample = None
    index: Index = None
    subtractions: Sequence[Subtraction] = None
    ready: bool = False
