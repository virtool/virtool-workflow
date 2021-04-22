from dataclasses import dataclass, field
from typing import List

from virtool_workflow.analysis.library_types import LibraryType


@dataclass
class Sample:
    """A Virtool Sample."""
    id: str
    name: str
    host: str
    isolate: str
    locale: str
    library_type: LibraryType
    paired: bool
    quality: dict
    nuvs: bool = False
    pathoscope: bool = False
    files: List[dict] = field(default_factory=lambda: [])

    def __post_init__(self):
        self.reads_path = None
        self.read_paths = None

    @property
    def min_length(self):
        return self.quality["length"][0] if self.quality else None

    @property
    def max_length(self):
        return self.quality["length"][1] if self.quality else None
