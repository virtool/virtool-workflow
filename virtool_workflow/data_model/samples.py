from dataclasses import dataclass, field
from typing import List
from virtool_workflow.uploads.files import DownloadableFileUpload
from virtool_workflow.analysis.library_types import LibraryType


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
    files: List[DownloadableFileUpload] = field(default_factory=lambda: [])
