"""Perform read prep before accessing Virtool reads_path."""
# pylint: disable=redefined-outer-name
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Any, Tuple

import virtool_workflow
from virtool_workflow.analysis import utils, fastqc
from virtool_workflow.analysis.analysis_info import AnalysisArguments
from virtool_workflow.analysis.cache import fetch_cache, create_cache
from virtool_workflow.execution.run_in_executor import FunctionExecutor
from virtool_workflow.execution.run_subprocess import RunSubprocess
from virtool_workflow.storage.utils import copy_paths
from virtool_workflow.fixtures.scope import WorkflowFixtureScope
from virtool_workflow_runtime.db import VirtoolDatabase
from virtool_workflow import hooks
from virtool_workflow.analysis.cache import delete_cache_if_not_ready, delete_analysis
from virtool_workflow.analysis.reads import Reads

logger = logging.getLogger(__name__)


def rename_trimming_results(path: Path):
    """
    Rename Skewer output to a simple name used in Virtool.

    :param path: The path containing the results from Skewer
    """
    try:
        shutil.move(
            path/"reads-trimmed.fastq.gz",
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


@virtool_workflow.fixture
async def parsed_fastqc(
        run_subprocess: RunSubprocess,
        trimming_output: Path,
        analysis_args: AnalysisArguments,
        number_of_processes: int,
) -> Dict[str, Any]:
    """
    The parsed output from fastqc.

    To be executed after the reads have been trimmed.
    """
    trimming_output_path = trimming_output

    rename_trimming_results(trimming_output_path)

    read_paths = utils.make_read_paths(trimming_output_path, analysis_args.paired)

    fastqc_path = analysis_args.temp_cache_path/"fastqc"
    fastqc_path.mkdir()

    command = [
        "fastqc",
        "-f", "fastq",
        "-o", str(fastqc_path),
        "-t", str(number_of_processes),
        "--extract",
        *[str(path) for path in read_paths]
    ]

    await run_subprocess(command)

    return fastqc.parse_fastqc(fastqc_path, analysis_args.sample_path)


async def fetch_legacy_paths(
        paths: List[Path],
        reads_path: Path,
        run_in_executor: FunctionExecutor
):
    """Copy legacy style reads to the reads_path."""
    return await copy_paths({path: reads_path/path.name for path in paths}.items(), run_in_executor)


@virtool_workflow.fixture
async def prepared_reads_and_fastqc(
        analysis_args: AnalysisArguments,
        trimming_output: Path,
        parsed_fastqc: Dict[str, Any],
) -> Tuple[Path, Dict[str, Any]]:
    """
    The reads_path and parsed fastqc output for the sample being analyzed.

    The raw reads are trimmed and moved to the reads path before returning.

    :param analysis_args: The AnalysisArguments for the current job.
    :param trimming_output: The trimmed reads. See #virtool_workflow.analysis.trimming.trimming_output.
    """
    shutil.copytree(trimming_output, analysis_args.reads_path)

    return analysis_args.reads_path, parsed_fastqc


@virtool_workflow.fixture
def unprepared_reads(analysis_args: AnalysisArguments):
    """The unprepared reads for the current analysis job."""
    min_length, max_length = analysis_args.sample["quality"]["length"]

    return Reads(paired=analysis_args.paired,
                 min_length=min_length,
                 max_length=max_length,
                 count=analysis_args.sample["quality"]["count"],
                 paths=analysis_args.read_paths)


@virtool_workflow.fixture
async def reads(
        scope: WorkflowFixtureScope,
        analysis_args: AnalysisArguments,
        cache_path: Path,
        cache_document: Dict[str, Any],
        database: VirtoolDatabase,
        trimming_parameters: Dict[str, Any],
        trimming_output_path: Path,
        run_in_executor: FunctionExecutor,
        unprepared_reads: Reads
) -> Reads:
    """
    The prepared reads for the current job.

    The trimming and fastqc check for the sample is completed before returning.
    """
    analysis_args.reads_path.mkdir(parents=True, exist_ok=True)

    if cache_document:
        await fetch_cache(cache_document,
                          cache_path,
                          analysis_args.reads_path,
                          run_in_executor)

    elif not all(f["raw"] for f in analysis_args.sample["files"]):
        legacy_paths = utils.make_legacy_read_paths(analysis_args.sample_path, analysis_args.paired)

        paths_to_copy = {path: analysis_args.reads_path/path.name
                         for path in legacy_paths}

        await copy_paths(paths_to_copy.items(), run_in_executor)
    else:
        hooks.on_workflow_failure(delete_cache_if_not_ready, once=True)
        hooks.on_workflow_failure(delete_analysis, once=True)

        _, fq = await scope.instantiate(prepared_reads_and_fastqc)
        await create_cache(fq, database, analysis_args, trimming_parameters, trimming_output_path, cache_path)

    hooks.on_result(VirtoolDatabase.store_result_callback(analysis_args.analysis_id,
                                                          database["analyses"],
                                                          analysis_args.path), once=True)

    return unprepared_reads

