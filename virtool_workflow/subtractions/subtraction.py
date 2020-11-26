from dataclasses import dataclass
from typing import Dict
from pathlib import Path


@dataclass
class Subtraction:
    name: str
    nickname: str
    path: Path
    gc: Dict[str, float]
    count: int
