"""Create caches of read-prep steps for Virtool analysis workflows"""
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Iterable

import virtool_core.caches.db
from virtool_workflow import fixture
from virtool_workflow.analysis import fastqc, utils
from virtool_workflow.analysis.analysis_info import AnalysisArguments
from virtool_workflow.execute import FunctionExecutor, run_shell_command
from virtool_workflow.storage.utils import copy_paths
from virtool_workflow_runtime.db import VirtoolDatabase
from virtool_workflow_runtime.db.fixtures import Collection

TRIMMING_PROGRAM = "skewer-0.2.2"


@fixture
async def cache_document(
        trimming_parameters: Dict[str, Any],
        sample_id: str,
        caches: Collection,
) -> Optional[Dict[str, Any]]:
    """Fetch the cache document for a given sample if it exists."""
    cache_document = await caches.find_one({
        "hash": virtool_core.caches.db.calculate_cache_hash(trimming_parameters),
        "missing": False,
        "program": TRIMMING_PROGRAM,
        "sample.id": sample_id
    })

    return cache_document


async def fetch_cache(
        cache_document: Dict[str, Any],
        cache_path: Path,
        reads_path: Path,
        run_in_executor: FunctionExecutor
):
    """Copy cached read files to the reads_path."""
    cached_read_paths = utils.make_read_paths(
        reads_dir_path=cache_path/cache_document["_id"],
        paired=cache_document["paired"]
    )

    await copy_paths(
        {path: reads_path/path.name for path in cached_read_paths}.items(),
        run_in_executor
    )


async def fetch_raw(
        read_paths: Iterable[Path],
        raw_path: Path,
        run_in_executor: FunctionExecutor
):
    """Copy reads to the raw_path before trimming/processing."""
    raw_read_paths = {path: raw_path/path.name for path in read_paths}
    await copy_paths(raw_read_paths.items(), run_in_executor)


def compose_trimming_command(
        cache_path: Path,
        trimming_parameters: Dict[str, Any],
        number_of_processes: int,
        read_paths: Iterable[Path]
):
    """
    Compose a shell command to run skewer on the reads located by read_paths.

    :param cache_path: The Path to a directory where the output from skewer should be stored
    :param trimming_parameters: The trimming parameters
        (see virtool_workflow.analysis.trimming_parameters)
    :param number_of_processes: The number of allowable processes to be used by skewer
    :param read_paths: The paths to the reads data
        (see virtool_workflow.analysis.reads_path)
    """
    command = [
        "skewer",
        "-r", str(trimming_parameters["max_error_rate"]),
        "-d", str(trimming_parameters["max_indel_rate"]),
        "-m", str(trimming_parameters["mode"]),
        "-l", str(trimming_parameters["min_length"]),
        "-q", str(trimming_parameters["end_quality"]),
        "-Q", str(trimming_parameters["mean_quality"]),
        "-t", str(number_of_processes),
        "-o", str(cache_path/"reads"),
        "-n",
        "-z",
        "--quiet"
    ]

    if trimming_parameters["max_length"]:
        command += [
            "-L", str(trimming_parameters["max_length"]),
            "-e"
        ]

    command += [str(path) for path in read_paths]

    return command


def rename_trimming_results(path: Path):
    """
    Rename Skewer output to a simple name used in Virtool.

    :param path: The path containing the results from Skewer
    """
    try:
        shutil.move(
            str(path/"reads_trimmed-pair1.fastq.gz"),
            str(path/"reads_1.fq.gz"),
        )
    except FileNotFoundError:
        shutil.move(
            str(path/"reads-trimmed-pair1.fastq.gz"),
            str(path/"reads_1.fq.gz"),
        )

        shutil.move(
            str(path/"reads-trimmed-pair2.fastq.gz"),
            str(path/"reads_2.fq.gz"),
        )

    shutil.move(
        str(path/"reads-trimmed.log"),
        str(path/"trim.log"),
    )


async def run_cache_qc(
        cache_id: str,
        analysis_args: AnalysisArguments,
        number_of_processes: int,
        run_in_executor: FunctionExecutor,
        caches: Collection
):
    """
    Run fastqc on the trimmed read files.

    Expected to be ran after the :func:`trimming_command` has been executed.
    """
    fastqc_path = analysis_args.temp_cache_path/"fastqc"
    fastqc_path.mkdir()

    read_paths = utils.make_read_paths(analysis_args.temp_cache_path, analysis_args.paired)

    await fastqc.run_fastqc(number_of_processes, read_paths, fastqc_path)

    quality = await run_in_executor(fastqc.parse_fastqc, fastqc_path, analysis_args.sample_path)

    await caches.update_one({"_id": cache_id}, {
        "$set": {
            "quality": quality
        }
    })

    return read_paths


@fixture
def trimming_command(
        trimming_parameters: Dict[str, Any],
        cache_path: Path,
        number_of_processes: int,
        read_paths: utils.PairedPaths
) -> List[str]:
    """A fixture for the skewer trimming command."""
    return compose_trimming_command(cache_path,
                                    trimming_parameters,
                                    number_of_processes,
                                    read_paths)


async def prepare_reads_and_create_cache(
        analysis_args: AnalysisArguments,
        trimming_parameters: Dict[str, Any],
        trimming_command: List[str],
        cache_path: Path,
        number_of_processes: int,
        database: VirtoolDatabase,
        run_in_executor: FunctionExecutor,
) -> Dict[str, Any]:
    """Prepare read data (run skewer and fastqc) and create a new cache."""
    cache = await virtool_core.caches.db.create(
        database, analysis_args.sample_id, trimming_parameters, analysis_args.paired)

    await database["analyses"].update_one({"_id": analysis_args.analysis_id}, {
        "$set": {
            "cache": {
                "id": cache["id"]
            }
        }
    })

    await fetch_raw(
        utils.make_read_paths(
            analysis_args.sample_path,
            analysis_args.paired
        ),
        analysis_args.raw_path,
        run_in_executor,
    )

    env = dict(os.environ, LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu")

    _, err = await run_shell_command(trimming_command, env=env)

    if err:
        raise RuntimeError("trimming command failed", err, trimming_command)

    await run_in_executor(rename_trimming_results, analysis_args.temp_cache_path)

    temp_paths = await run_cache_qc(
        cache["id"],
        analysis_args,
        number_of_processes,
        run_in_executor,
        database["caches"],
    )

    await run_in_executor(
        shutil.copytree,
        str(analysis_args.temp_cache_path),
        cache_path/cache["id"])

    await copy_paths(zip(temp_paths, analysis_args.read_paths), run_in_executor)
    return cache
