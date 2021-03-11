from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass(frozen=True)
class HMM:
    """A Virtool HMM (Hidden Markov Model)."""
    id: str
    cluster: int
    count: int
    entries: List[dict]
    families: Dict[str, int]
    genera: Dict[str, int]
    hidden: bool
    length: int
    mean_entropy: float
    total_entropy: float
    names: Tuple[str, str, str]
