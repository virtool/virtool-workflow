from dataclasses import dataclass
from virtool_workflow.analysis.utils import ReadPaths


@dataclass
class Reads:
    """Dataclass representing prepared reads for an analysis workflow."""
    paired: bool
    min_length: int
    max_length: int
    count: int
    paths: ReadPaths
