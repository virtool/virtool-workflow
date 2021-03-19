from pathlib import Path

from virtool_workflow import fixture
from virtool_workflow.abc.data_providers import AbstractSampleProvider
from virtool_workflow.analysis.library_types import LibraryType
from virtool_workflow.data_model.samples import Sample


@fixture
async def sample(sample_provider: AbstractSampleProvider, work_path: Path) -> Sample:
    """The sample document for the current job."""
    read_path = work_path / "reads"
    read_path.mkdir()
    sample_ = await sample_provider.get()
    read_paths = await sample_provider.download_reads(read_path, sample_.paired)

    sample_.reads_path = read_path
    sample_.read_paths = read_paths
   
    return sample_


@fixture
def paired(sample: Sample) -> bool:
    """A boolean indicating that the sample data for the current job is paired."""
    return sample.paired


@fixture
def library_type(sample: Sample) -> LibraryType:
    """The library type for the sample being analyzed."""
    return sample.library_type
