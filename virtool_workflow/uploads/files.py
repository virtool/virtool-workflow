from dataclasses import dataclass
from pathlib import Path


VirtoolFileFormat = str


@dataclass(frozen=True)
class FileUpload:
    name: str
    description: str
    path: Path
    format: VirtoolFileFormat
