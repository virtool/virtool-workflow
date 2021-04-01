from collections import UserList
from functools import cached_property
from pathlib import Path
from typing import Iterable
from shutil import which

from virtool_workflow.abc.data_providers.hmms import AbstractHMMsProvider
from virtool_workflow.data_model import HMM
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
async def hmms(hmms_provider: AbstractHMMsProvider, work_path: Path, run_subprocess: RunSubprocess):
    """
    A fixture for accessing HMM data.

    The *.hmm file is copied from the data directory and `hmmpress` is run to create all the HMM files.

    Returns a data object containing the path to the HMM profile file and a `dict` that maps HMM cluster numbers to
    database IDs.
    """
    await hmms_provider.get_profiles()

    if which("hmmpress") is None:
        raise RuntimeError("hmmpress is not installed.")

    await run_subprocess(["hmmpress", str(hmms_provider.path)])

    return HMMs(await hmms_provider.hmm_list(), hmms_provider.path)
