from collections import UserList
from os import makedirs

import shutil
from functools import cached_property
from pathlib import Path
from typing import Iterable

from virtool_workflow.abc.data_providers.hmms import AbstractHmmsProvider
from virtool_workflow.data_model import HMM
from virtool_workflow.execution.run_in_executor import FunctionExecutor
from virtool_workflow.execution.run_subprocess import RunSubprocess
from virtool_workflow.fixtures import fixture


class HMMs(UserList):
    """A list of :class:`virtool_workflow.data_model.HMM` instances, along with a path to the HMM profiles file."""
    path: Path

    def __init__(self, hmms: Iterable[HMM], path: Path):
        self.path = path
        super(HMMs, self).__init__(hmms)

    @cached_property
    def cluster_annotation_map(self):
        return {hmm.cluster: hmm.id for hmm in self}


@fixture
async def hmms(hmms_provider: AbstractHmmsProvider, work_path: Path, data_path: Path,
               run_in_executor: FunctionExecutor, run_subprocess: RunSubprocess):
    """
    A fixture for accessing HMM data.

    The *.hmm file is copied from the data directory and `hmmpress` is run to create all the HMM files.

    Returns a data object containing the path to the HMM profile file and a `dict` that maps HMM cluster numbers to
    database IDs.
    """
    hmms_path = work_path / "hmms"

    await run_in_executor(makedirs, hmms_path)
    await run_in_executor(shutil.copy, data_path / "hmm" / "profiles.hmm", hmms_path)

    profiles_path = hmms_path / "profiles.hmm"
    await run_subprocess(["hmmpress", str(profiles_path)])

    return HMMs(hmms_provider.hmm_list, profiles_path)
