"""An example workflow."""
import asyncio
from pathlib import Path

from virtool_workflow import step
from virtool_workflow.analysis.fastqc import FastQCRunner
from virtool_workflow.data.samples import WFNewSample


@step
async def step_1():
    """A basic step that doesn't actually do anything."""
    await asyncio.sleep(1)


@step
async def try_fastqc(fastqc: FastQCRunner, new_sample: WFNewSample, work_path: Path):
    paths = [u.path for u in new_sample.uploads]
    await fastqc(paths, work_path / "reads")
