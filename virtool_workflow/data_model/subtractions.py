from abc import ABC
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NucleotideComposition:
    a: float
    c: float
    g: float
    n: float
    t: float


@dataclass
class Subtraction(ABC):
    """A dataclass representing a subtraction in Virtool."""
    id: str
    name: str
    nickname: str
    count: int
    deleted: bool
    gc: NucleotideComposition
    is_host: bool
    path: Path

    def __post_init__(self):
        self.fasta_path = self.path / "subtraction.fa.gz"
        self.bowtie2_index_path = str(self.path) + "/reference"
