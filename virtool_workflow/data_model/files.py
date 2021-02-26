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
class AnalysisFile:
    id: int
    name: str
    name_on_disk: str
    size: int
    uploaded_at: date
    format: VirtoolFileFormat
