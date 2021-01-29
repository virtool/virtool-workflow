from dataclasses import dataclass
from abc import ABC
from pathlib import Path


@dataclass(frozen=True)
class NucleotideComposition:
    """The percentage composition of nucleotides in a Sample."""
    a: float
    c: float
    g: float
    n: float
    t: float

    def __post_init__(self):
        total_percentage = self.a + self.c + self.g + self.t + self.n
        if total_percentage != 1.0:
            raise ValueError("Nucleotide percentages must equal 100%")


@dataclass(frozen=True)
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
    fasta_path: Path
    bowtie2_index_path: str
