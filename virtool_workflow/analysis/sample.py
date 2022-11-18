from pathlib import Path

from pyfixtures import fixture
from virtool_workflow.analysis.utils import make_read_paths
from virtool_workflow.data_model.samples import WFSample
from virtool_workflow.api.samples import SampleProvider


@fixture
async def sample(sample_provider: SampleProvider, work_path: Path) -> WFSample:
    """
    The sample associated with the current job.

    Returns a :class:`.Sample` object.

    """
    read_path = work_path / "reads"
    read_path.mkdir()

    sample_ = await sample_provider.get()
    await sample_provider.download_reads(read_path, sample_.paired)
    sample_.reads_path = read_path
    sample_.read_paths = make_read_paths(read_path, sample_.paired)
    return sample_
