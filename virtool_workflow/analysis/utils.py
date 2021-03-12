import shutil
from pathlib import Path
from typing import Tuple, Callable, Union

ReadPaths = Union[Tuple[Path], Tuple[Path, Path]]


def _make_paired_paths(
        dir_path: Path,
        paired: bool,
        mkstr: Callable[[int], str]
) -> ReadPaths:
    path1 = dir_path / mkstr(1)
    return (path1, dir_path / mkstr(2)) if paired else (path1,)


def make_read_paths(
        reads_dir_path: Path,
        paired: bool
) -> ReadPaths:
    """
    Get the path(s) locating the compressed fastq files containing the read data.

    :param reads_dir_path: The directory containing the fastq file(s).
    :param paired: A boolean indicating if the sequence is paired (two fastq files).
    :return: A :class:`Tuple[Path]` if :obj:`paired` is `False`, else a :class:`Tuple[Path, Path]`.
    """
    return _make_paired_paths(reads_dir_path, paired, lambda n: f"reads_{n}.fq.gz")


def make_legacy_read_paths(
        reads_dir_path: Path,
        paired: bool
) -> ReadPaths:
    return _make_paired_paths(reads_dir_path, paired, lambda n: f"reads_{n}.fastq")


def rename_trimming_results(path: Path):
    """
    Rename Skewer output to a simple name used in Virtool.

    :param path: The path containing the results from Skewer
    """
    try:
        shutil.move(
            path / "reads-trimmed.fastq.gz",
            path / "reads_1.fq.gz",
        )
    except FileNotFoundError:
        shutil.move(
            path / "reads-trimmed-pair1.fastq.gz",
            path / "reads_1.fq.gz",
        )

        shutil.move(
            path / "reads-trimmed-pair2.fastq.gz",
            path / "reads_2.fq.gz",
        )

    shutil.move(
        path / "reads-trimmed.log",
        path / "trim.log",
    )
