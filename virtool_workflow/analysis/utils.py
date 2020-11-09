from pathlib import Path
from typing import Tuple, Callable, Union

ReadPaths = Union[Tuple[Path], Tuple[Path, Path]]


def _make_paired_paths(
        dir_path: Path,
        paired: bool,
        mkstr: Callable[[int], str]
) -> ReadPaths:
    path1 = dir_path/mkstr(1)
    return (path1, dir_path/mkstr(2)) if paired else (path1,)


def make_read_paths(
        reads_dir_path: Path,
        paired: bool
) -> ReadPaths:
    return _make_paired_paths(reads_dir_path, paired, lambda n: f"reads_{n}.fq.gz")


def make_legacy_read_paths(
        reads_dir_path: Path,
        paired: bool
) -> ReadPaths:
    return _make_paired_paths(reads_dir_path, paired, lambda n: f"reads_{n}.fastq")

