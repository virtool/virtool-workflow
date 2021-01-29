from dataclasses import dataclass
from abc import ABC
from pathlib import Path


@dataclass(frozen=True)
class NucleotideComposition:
    a: float
    c: float
    g: float
    n: float
    t: float


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