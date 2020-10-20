import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Iterable

import virtool_core.caches.db
from virtool_workflow_runtime.db import VirtoolDatabase
from virtool_workflow_runtime.db.fixtures import Collection
from . import fastqc
from . import utils
from .analysis_info import AnalysisArguments
from .. import fixture
from ..execute import FunctionExecutor
from ..execute import run_shell_command
from ..storage.utils import copy_paths

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
    raw_read_paths = [raw_path/path.name for path in read_paths]

    await copy_paths(zip(read_paths, raw_read_paths), run_in_executor)


def compose_trimming_command(
        cache_path: Path,
        trimming_parameters: Dict[str, Any],
        number_of_processes: int,
        read_paths: Iterable[Path]
):
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
        temp_cache_path: Path,
        paired: bool,
        sample_path: Path,
        number_of_processes: int,
        run_in_executor: FunctionExecutor,
        caches: Collection
):
    fastqc_path = temp_cache_path/"fastqc"
    fastqc_path.mkdir()

    read_paths = utils.make_read_paths(temp_cache_path, paired)

    await fastqc.run_fastqc(number_of_processes, read_paths, fastqc_path)

    qc = await run_in_executor(fastqc.parse_fastqc, fastqc_path, sample_path)

    await caches.update_one({"_id": cache_id}, {
        "$set": {
            "quality": qc
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
    return compose_trimming_command(cache_path,
                                    trimming_parameters,
                                    number_of_processes,
                                    read_paths)


async def create_cache(
        analysis_args: AnalysisArguments,
        trimming_parameters: Dict[str, Any],
        trimming_command: List[str],
        cache_path: Path,
        number_of_processes: int,
        database: VirtoolDatabase,
        run_in_executor: FunctionExecutor,
) -> Dict[str, Any]:
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
        analysis_args.temp_cache_path,
        analysis_args.paired,
        analysis_args.sample_path,
        number_of_processes,
        run_in_executor,
        database["caches"]
    )

    await run_in_executor(
        shutil.copytree,
        str(analysis_args.temp_cache_path),
        cache_path/cache["id"])

    await copy_paths(zip(temp_paths, analysis_args.read_paths), run_in_executor)
    return cache
