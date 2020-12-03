import shutil
from dataclasses import dataclass
from os import makedirs
from pathlib import Path
from typing import Dict

from virtool_workflow import fixture
from virtool_workflow.execution.run_in_executor import FunctionExecutor
from virtool_workflow.execution.run_subprocess import RunSubprocess
from virtool_workflow_runtime.db import VirtoolDatabase


@dataclass
class HMMs:
    cluster_annotation_map: Dict[int, str]
    path: Path


@fixture
async def cluster_annotation_map(database: VirtoolDatabase) -> Dict[int, str]:
    cursor = database.hmm.find({}, ["cluster"])
    return {int(document["cluster"]): document["_id"] async for document in cursor}


@fixture
async def hmms(
    cluster_annotation_map: Dict[int, str],
    data_path: Path,
    temp_analysis_path: Path,
    run_in_executor: FunctionExecutor,
    run_subprocess: RunSubprocess,
) -> HMMs:
    """
    A fixture for accessing HMM data.

    The *.hmm file is copied from the data directory and `hmmpress` is run to create all the HMM files.

    Returns a data object containing the path to the HMM profile file and a `dict` that maps HMM cluster numbers to
    database IDs.

    """
    hmms_path = temp_analysis_path / "hmms"

    await run_in_executor(makedirs, hmms_path)

    await run_in_executor(shutil.copy, data_path / "hmm" / "profiles.hmm", hmms_path)

    profiles_path = hmms_path / "profiles.hmm"

    await run_subprocess(["hmmpress", str(profiles_path)])

    return HMMs(cluster_annotation_map, profiles_path)
