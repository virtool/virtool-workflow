from dataclasses import dataclass
from datetime import date
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


@dataclass
class VirtoolFile:
    id: int
    name: str
    size: int
    format: VirtoolFileFormat
    name_on_disk: str = None
    uploaded_at: date = None
