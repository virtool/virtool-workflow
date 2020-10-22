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
        "sample.id": sample_id,
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


async def fetch_raw_sample_data(
        sample_paths: Iterable[Path],
        read_paths: Iterable[Path],
        raw_path: Path,
        run_in_executor: FunctionExecutor
):
    """Copy reads to the raw_path and temp path before trimming/processing."""
    raw_read_paths = {path: raw_path/path.name for path in sample_paths}
    await copy_paths(raw_read_paths.items(), run_in_executor)

    await copy_paths(
        zip(sample_paths, read_paths),
        run_in_executor
    )


def rename_trimming_results(path: Path):
    """
    Rename Skewer output to a simple name used in Virtool.

    :param path: The path containing the results from Skewer
    """
    try:
        shutil.move(
            path/"reads_trimmed.fastq.gz",
            path/"reads_1.fq.gz",
        )
    except FileNotFoundError:
        shutil.move(
            path/"reads-trimmed-pair1.fastq.gz",
            path/"reads_1.fq.gz",
        )

        shutil.move(
            path/"reads-trimmed-pair2.fastq.gz",
            path/"reads_2.fq.gz",
        )

    shutil.move(
        path/"reads-trimmed.log",
        path/"trim.log",
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


async def create_cache_document(
        database: VirtoolDatabase,
        analysis_args: AnalysisArguments,
        trimming_parameters: Dict[str, Any]
):
    cache = await virtool_core.caches.db.create(
        database,
        analysis_args.sample_id,
        trimming_parameters,
        analysis_args.paired
    )

    await database["analyses"].update_one({"_id": analysis_args.analysis_id}, {
        "$set": {
            "cache": {
                "id": cache["id"]
            }
        }
    })

    return cache


@fixture
def cached_reads_path(cache_path: Path) -> Path:
    return cache_path/"reads"


@fixture
def cached_read_paths(cached_reads_path: Path, paired: bool) -> utils.ReadPaths:
    return utils.make_read_paths(cached_reads_path, paired)


@fixture
async def cached_reads(
        cached_read_paths,
        analysis_args: AnalysisArguments,
        run_in_executor: FunctionExecutor,
) -> utils.ReadPaths:
    await fetch_raw_sample_data(
        utils.make_read_paths(
            analysis_args.sample_path,
            analysis_args.paired,
        ),
        cached_read_paths,
        analysis_args.raw_path,
        run_in_executor,
    )

    return cached_reads_path


async def prepare_reads_and_create_cache(
        analysis_args: AnalysisArguments,
        trimming_parameters: Dict[str, Any],
        trimming_output: Path,
        cache_path: Path,
        number_of_processes: int,
        database: VirtoolDatabase,
        run_in_executor: FunctionExecutor,
) -> Dict[str, Any]:
    """Prepare read data (run skewer and fastqc) and create a new cache."""
    cache = await create_cache_document(database, analysis_args, trimming_parameters)

    trimming_output_path, _ = trimming_output

    await run_in_executor(rename_trimming_results, utils.make_read_paths(trimming_output_path))

    temp_paths = await run_cache_qc(
        cache["id"],
        analysis_args,
        number_of_processes,
        run_in_executor,
        database["caches"],
    )

    await run_in_executor(
        shutil.copytree,
        trimming_output_path,
        cache_path/cache["id"])

    await copy_paths(zip(temp_paths, analysis_args.read_paths), run_in_executor)
    return cache
