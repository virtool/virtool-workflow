import os
import shutil
from asyncio.subprocess import Process
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from virtool_workflow.analysis.library_types import LibraryType
from virtool_workflow.analysis.utils import ReadPaths


@dataclass
class SkewerResult:
    """Represents the result of running Skewer to trim a paired or unpaired FASTQ dataset."""
    #: The paths to the trimmed reads.
    read_paths: ReadPaths
    #: The process running Skewer.
    process: Process
    #: The command used to run Skewer.
    command: List[str]

    @property
    def left(self) -> Path:
        """
        The path to one of:
            - the FASTQ trimming result for an unpaired Illumina dataset
            - the FASTA trimming result for the left reads of a paired Illumina dataset

        :type: :class:`.Path`

        """
        return self.read_paths[0]

    @property
    def right(self) -> Optional[Path]:
        """
        The path to the rights reads of a paired Illumina dataset.

        ``None`` if the dataset in unpaired.

        :type: :class:`.Path`

        """
        try:
            return self.read_paths[1]
        except IndexError:
            return None


def skewer(
        min_length: int,
        mode: str = "pe",
        max_error_rate: float = 0.1,
        max_indel_rate: float = 0.03,
        end_quality: int = 0,
        mean_quality: int = 0,
        number_of_processes: int = 1,
        quiet: bool = True,
        other_options: Iterable[str] = ("-n", "-z"),
        **kwargs
):
    """Create a coroutine function that will run skewer with the given parameters."""
    if shutil.which("skewer") is None:
        raise RuntimeError("skewer is not installed.")

    command = [
        "skewer",
        "-r", str(max_error_rate),
        "-d", str(max_indel_rate),
        "-m", str(mode),
        "-l", str(min_length),
        "-q", str(end_quality),
        "-Q", str(mean_quality),
        "-t", str(number_of_processes),
        *other_options
    ]

    if quiet:
        command.append("--quiet")

    async def run_skewer(read_paths, run_subprocess, run_in_executor):
        nonlocal command
        command += [str(read_path) for read_path in read_paths]
        command += ["-o", "reads"]

        env = dict(os.environ, LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu")

        reads_path = read_paths[0].parent

        process = await run_subprocess(command, env=env, cwd=reads_path)

        read_paths = await run_in_executor(rename_trimming_results, reads_path)

        return SkewerResult(read_paths, process, command)

    return run_skewer


def rename_trimming_results(path: Path):
    """
    Rename Skewer output to a simple name used in Virtool.

    :param path: The path containing the results from Skewer
    """
    shutil.move(
        path / "reads-trimmed.log",
        path / "trim.log",
    )

    try:
        return (shutil.move(
            path / "reads-trimmed.fastq.gz",
            path / "reads_1.fq.gz",
        ),)
    except FileNotFoundError:
        return (
            shutil.move(
                path / "reads-trimmed-pair1.fastq.gz",
                path / "reads_1.fq.gz",
            ),
            shutil.move(
                path / "reads-trimmed-pair2.fastq.gz",
                path / "reads_2.fq.gz",
            )
        )


def calculate_trimming_min_length(library_type: LibraryType, sample_read_length: int) -> int:
    """
    The minimum length of a read.

    This takes into account the library type (eg. srna)
    and the maximum observed read length in the sample.

    :param library_type: the sample library type
    :param sample_read_length: the maximum read length observed in the sample
    :return: the minimum allowed trimmed read length
    """
    if library_type == LibraryType.amplicon:
        return round(0.95 * sample_read_length)

    if sample_read_length < 80:
        return 35

    if sample_read_length < 160:
        return 100

    return 160
