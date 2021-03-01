from dataclasses import dataclass
from typing import Sequence

from virtool_workflow.data_model import Sample, Index, Subtraction
from virtool_workflow.data_model.files import AnalysisFile


@dataclass
class Analysis:
    id: str
    files: Sequence[AnalysisFile]
    sample: Sample = None
    index: Index = None
    subtractions: Sequence[Subtraction] = None
    ready: bool = False
