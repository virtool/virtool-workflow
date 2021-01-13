from dataclasses import dataclass
from abc import ABC


@dataclass(frozen=True)
class NucleotideComposition:
    a: float
    c: float
    g: float
    n: float
    t: float


@dataclass(frozen=True)
class Subtraction(ABC):
    name: str
    nickname: str
    count: int
    deleted: bool
    gc: NucleotideComposition
    is_host: bool