"""
A class and fixture for accessing Virtool HMM data for use in analysis workflows.

"""
import asyncio
from collections import UserList
from functools import cached_property
from pathlib import Path
from shutil import which
from typing import Dict, Iterable

from pyfixtures import fixture
from virtool_core.models.hmm import HMM

from virtool_workflow.api.hmm import HMMsProvider
from virtool_workflow.runtime.run_subprocess import RunSubprocess


class HMMs(UserList):
    """
    A class that exposes:

    1. A :class:`dict` the links `HMMER <http://hmmer.org/>`_ cluster IDs to Virtool annotation IDs.
    2. The path to the HMM profiles file.

    """

    def __init__(self, hmms: Iterable[HMM], path: Path):
        #: The path to the ``profiles.hmm`` file in the ``work_path`` of the running workflow.
        self.path: Path = path
        super(HMMs, self).__init__(hmms)

    @cached_property
    def cluster_annotation_map(self) -> Dict[int, str]:
        """
        A :class:`dict` that maps cluster IDs used to identify HMMs in `HMMER <http://hmmer.org/>`_ to annotation IDs
        used in Virtool.

        """
        return {hmm.cluster: hmm.id for hmm in self}


@fixture
async def hmms(
    hmms_provider: HMMsProvider, work_path: Path, run_subprocess: RunSubprocess
):
    """
    A fixture for accessing HMM data.

    The ``*.hmm`` file is copied from the data directory and ``hmmpress`` is run to create all the HMM files.

    Returns an :class:`.HMMs` object containing the path to the HMM profile file and a `dict` that maps HMM cluster numbers to
    database IDs.

    :raises: :class:`RuntimeError`: hmmpress is not installed
    :raises: :class:`RuntimeError`: hmmpress command failed

    """
    await hmms_provider.get_profiles()

    if await asyncio.to_thread(which, "hmmpress") is None:
        raise RuntimeError("hmmpress is not installed.")

    process = await run_subprocess(
        ["hmmpress", str(hmms_provider.path / "profiles.hmm")]
    )

    if process.returncode != 0:
        raise RuntimeError("hmmpress command failed")

    return HMMs(await hmms_provider.hmm_list(), hmms_provider.path)
