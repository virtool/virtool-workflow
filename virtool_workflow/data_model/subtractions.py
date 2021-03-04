from abc import ABC
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NucleotideComposition:
    a: float = 0.0
    c: float = 0.0
    g: float = 0.0
    n: float = 0.0
    t: float = 0.0


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
