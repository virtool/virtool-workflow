from pathlib import Path
from typing import Protocol


class Trimming(Protocol):
    input_path: Path

    async def run_trimming(self, output_path: Path):
        ...
