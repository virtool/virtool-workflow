from typing import List
from pathlib import Path


def make_read_paths(reads_dir_path: Path, paired: bool) -> List[Path]:
    read_paths = [reads_dir_path / "reads_1.fq.gz"]

    if paired:
        read_paths.append(
            reads_dir_path / "reads_2.fq.gz"
        )

    return read_paths