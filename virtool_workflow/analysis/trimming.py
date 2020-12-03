import os
from pathlib import Path
from typing import Dict, Any, Iterable, List

from virtool_workflow.analysis import utils, analysis_info
from virtool_workflow.execution.run_in_executor import FunctionExecutor
from virtool_workflow.fixtures.workflow_fixture import fixture
from virtool_workflow.storage.utils import copy_paths


@fixture
def trimming_output_path(cache_path: Path):
    """
    The output path for the trimming command.

    A directory will be created at the Path if one does not already exist.
    """
    path = cache_path/"reads"
    path.mkdir(exist_ok=True, parents=True)
    return path


@fixture
async def trimming_input_paths(analysis_args: analysis_info.AnalysisArguments,
                               run_in_executor: FunctionExecutor) -> utils.ReadPaths:
    """
    The input path for the trimming command.

    Sample data will be copied to the raw_path and read_paths before returning.
    """
    sample_paths = utils.make_read_paths(analysis_args.sample_path, analysis_args.paired)
    raw_read_paths = {path: analysis_args.raw_path / path.name for path in sample_paths}
    await copy_paths(raw_read_paths.items(), run_in_executor)

    await copy_paths(
        zip(sample_paths, analysis_args.read_paths),
        run_in_executor
    )

    return analysis_args.read_paths


def compose_trimming_command(
        output_path: Path,
        trimming_parameters: Dict[str, Any],
        number_of_processes: int,
        input_paths: Iterable[Path]
) -> List[str]:
    """
    Compose a shell command to run skewer on the read data located by the `input_paths`.

    :param output_path: The Path to a directory where the output from skewer should be stored
    :param trimming_parameters: The trimming parameters
        (see virtool_workflow.analysis.trimming_parameters)
    :param number_of_processes: The number of allowable processes to be used by skewer
    :param input_paths: The paths to the un-trimmed read data
    :return: The trimming command.
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
        "-o", str(output_path/"reads"),
        "-n",
        "-z",
        "--quiet",
    ]

    if trimming_parameters["max_length"]:
        command += [
            "-L", str(trimming_parameters["max_length"]),
            "-e"
        ]

    command += [str(path) for path in input_paths]

    return command


@fixture
def trimming_command(
        trimming_output_path: Path,
        trimming_parameters: Dict[str, Any],
        number_of_processes: int,
        trimming_input_paths: utils.ReadPaths
) -> List[str]:
    """The trimming command for the current analysis."""
    return compose_trimming_command(trimming_output_path,
                                    trimming_parameters,
                                    number_of_processes,
                                    trimming_input_paths)


@fixture
async def trimming_output(
        run_subprocess,
        trimming_command: List[str],
        trimming_input_paths: utils.ReadPaths,
        trimming_output_path: Path

) -> Path:
    """
    The `trimming_output_path` provided  along with the shell output from the trimming command.

    :param trimming_command: The trimming command.
    :param trimming_input_paths: The input paths locating the un-trimmed reads.
    :param trimming_output_path: The output path where the trimmed reads should be stored.
    """
    env = dict(os.environ, LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu")

    await run_subprocess(trimming_command, env=env)

    return trimming_output_path
