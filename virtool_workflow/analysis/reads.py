from dataclasses import dataclass
from importlib import import_module
from pathlib import Path

from fixtures import fixture
from virtool_workflow.analysis.fastqc import fastqc
from virtool_workflow.analysis.skewer import skewer
from virtool_workflow.data_model.samples import Sample

import_module(__package__ + ".trimming")


@dataclass
class Reads:
    """
    Dataclass storing the trimmed reads for a sample.

    :param sample: The target sample.
    :param quality: The fastqc results for the trimmed reads.
    :param path: The path to the directory containing the trimmed read files.
    """
    sample: Sample
    quality: dict
    path: Path

    @property
    def left(self):
        return self.path / "reads_1.fq.gz"

    @property
    def right(self):
        return self.path / "reads_2.fq.gz"


@fixture
async def reads(
    sample: Sample,
    trimming_parameters: dict,
    work_path: Path,
    run_subprocess,
    run_in_executor,
):
    """
    The trimmed sample reads.

    If a cache exists it will be used, otherwise a new cache will be created.
    """
    result = await skewer(
        **trimming_parameters
    )(sample.read_paths, run_subprocess, run_in_executor)

    quality = await fastqc(work_path, run_subprocess)(sample.read_paths)

    return Reads(sample=sample, quality=quality, path=result.left.parent)
