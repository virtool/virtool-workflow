import os
import shutil
from typing import Dict, Any, Optional, List
from pathlib import Path

import virtool_core.caches.db
from virtool_workflow import fixture
from virtool_workflow.execute import FunctionExecutor
from virtool_workflow_runtime.db.fixtures import caches, Collection
from virtool_workflow_runtime.db import VirtoolDatabase
from virtool_workflow.storage.utils import copy_paths
from virtool_workflow.execute import run_subprocess
from . import fastqc
from .trim_parameters import trimming_parameters

TRIMMING_PROGRAM = "skewer-0.2.2"


@fixture
async def cache_document(
        trimming_parameters: Dict[str, Any],
        sample_id: str,
        caches: Collection,
) -> Optional[Dict[str, Any]]:
    cache_document = caches.find_one({
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
    cached_read_dir_path = cache_path/cache_document["_id"]
    cached_read_paths = [cached_read_dir_path/"reads_1.fq.gz"]

    if cache_document["paired"]:
        cached_read_paths.append(
            cached_read_dir_path/"reads_2.fq.gz"
        )

    await copy_paths(
        cached_read_paths,
        [reads_path/path.name for path in cached_read_paths],
        run_in_executor
    )


async def fetch_raw(
        read_paths: List[Path],
        raw_path: Path,
        run_in_executor: FunctionExecutor
):
    raw_read_paths = [raw_path/path.name for path in read_paths]

    await copy_paths(read_paths, raw_read_paths, run_in_executor)


def compose_trimming_command(
        cache_path: Path,
        trimming_parameters: Dict[str, Any],
        number_of_processes: int,
        read_paths: List[Path]
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


def rename_trimming_results(path):
    """
    Rename Skewer output to a simple name used in Virtool.

    :param path:

    """
    try:
        shutil.move(
            os.path.join(path, f"reads-trimmed.fastq.gz"),
            os.path.join(path, f"reads_1.fq.gz")
        )
    except FileNotFoundError:
        shutil.move(
            os.path.join(path, f"reads-trimmed-pair1.fastq.gz"),
            os.path.join(path, f"reads_1.fq.gz")
        )

        shutil.move(
            os.path.join(path, f"reads-trimmed-pair2.fastq.gz"),
            os.path.join(path, f"reads_2.fq.gz")
        )

    shutil.move(
        os.path.join(path, "reads-trimmed.log"),
        os.path.join(path, "trim.log")
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

    read_paths = [temp_cache_path/"reads_1.fq.gz"]

    if paired:
        read_paths.append(temp_cache_path/"reads_2.fq.gz")

    await fastqc.run_fastqc(number_of_processes, read_paths, fastqc_path)

    qc = await run_in_executor(fastqc.parse_fastqc, fastqc_path, sample_path)

    await caches.update_one({"_id": cache_id}, {
        "$set": {
            "quality": qc
        }
    })

    return read_paths


async def create_cache(
        sample_id: str,
        analysis_id: str,
        paired: bool,
        trimming_parameters: Dict[str, Any],
        read_paths: List[Path],
        raw_path: Path,
        sample_path: Path,
        proc: int,
        cache_path: Path,
        temp_cache_path: Path,
        database: VirtoolDatabase,
        run_in_executor: FunctionExecutor,
) -> Dict[str, Any]:
    cache = await virtool_core.caches.db.create(
        database, sample_id, trimming_parameters, paired)

    await database.analyses.update_one({"_id": analysis_id}, {
        "$set": {
            "cache": {
                "id": cache["id"]
            }
        }
    })

    await fetch_raw(read_paths, raw_path, run_in_executor)

    trimming_command = compose_trimming_command(cache_path,
                                                trimming_parameters,
                                                proc,
                                                read_paths)

    env = dict(os.environ, LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu")

    await run_subprocess(trimming_command, env=env)

    await run_in_executor(rename_trimming_results, temp_cache_path)

    temp_paths = await run_cache_qc(
        cache["id"],
        temp_cache_path,
        paired,
        sample_path,
        2,
        run_in_executor,
        database["caches"]
    )

    await run_in_executor(shutil.copytree, str(temp_cache_path), cache_path/cache["id"])

    await copy_paths(temp_paths, read_paths)

    await run_in_executor(shutil.rmtree, str(temp_cache_path))

    return cache

