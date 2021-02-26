from dataclasses import dataclass
from pathlib import Path

from virtool_workflow.data_model.files import VirtoolFileFormat


@dataclass(frozen=True)
class FileUpload:
    name: str
    description: str
    path: Path
    format: VirtoolFileFormat


@dataclass(frozen=True)
class DownloadableFileUpload(FileUpload):
    download_url: str
