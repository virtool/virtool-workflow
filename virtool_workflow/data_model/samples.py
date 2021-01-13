from dataclasses import dataclass
from typing import List
from virtool_workflow.uploads.files import DownloadableFileUpload
from virtool_workflow.analysis.library_types import LibraryType


@dataclass(frozen=True)
class Sample:
    name: str
    host: str
    isolate: str
    locale: str
    library_type: LibraryType
    paired: bool
    nuvs: bool
    pathoscope: bool
    quality: dict
    files: List[DownloadableFileUpload]