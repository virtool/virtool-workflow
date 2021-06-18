from dataclasses import dataclass
from virtool_workflow.data_model.samples import Sample
from pathlib import Path


@dataclass
class Reads:
    """The prepared reads for an analysis workflow."""
    sample: Sample
    path: Path

    @property
    def left(self):
        return self.path / "reads_1.fq.gz"

    @property
    def right(self):
        return self.path / "reads_2.fq.gz"
