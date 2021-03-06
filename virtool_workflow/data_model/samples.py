from dataclasses import dataclass, field
from typing import List

from virtool_workflow.analysis.library_types import LibraryType
from virtool_workflow.data_model.files import VirtoolFile


@dataclass(frozen=True)
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
    files: List[VirtoolFile] = field(default_factory=lambda: [])
