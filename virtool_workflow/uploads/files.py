from dataclasses import dataclass
from pathlib import Path
from typing import Literal


VirtoolFileFormat = Literal[
    "sam",
    "bam",
    "fasta",
    "fastq",
    "csv",
    "tsv",
    "json",
    "unknown",
]


@dataclass(frozen=True)
class FileUpload:
    name: str
    description: str
    path: Path
    format: VirtoolFileFormat
