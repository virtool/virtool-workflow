from dataclasses import dataclass
from pathlib import Path
from typing import Literal


VirtoolFileFormat = Literal[
    "reference",
    "reads",
    "hmm",
    "subtraction"
]


@dataclass(frozen=True)
class FileUpload:
    name: str
    description: str
    path: Path
    format: VirtoolFileFormat
