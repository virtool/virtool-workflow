import os
import shutil
from pathlib import Path
from typing import Iterable


def skewer(
        max_error_rate: float,
        max_indel_rate: float,
        mode: str,
        min_length: int,
        end_quality: int = 0,
        mean_quality: int = 0,
        number_of_processes: int = 1,
        other_options: Iterable[str] = ("-n", "-z", "--quiet"),
):
    """Create a coroutine function that will run skewer with the given parameters."""
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

    async def run_skewer(output_path, run_subprocess, run_in_executor):
        nonlocal command
        command += ["-o", str(output_path)]
        env = dict(os.environ, LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu")

        await run_subprocess(command, env=env)

        await run_in_executor(rename_trimming_results, output_path)

    return run_skewer


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
