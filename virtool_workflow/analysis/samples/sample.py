from virtool_workflow import fixture
from virtool_workflow.abc.data_providers import AbstractSampleProvider
from virtool_workflow.analysis.library_types import LibraryType
from virtool_workflow.data_model.samples import Sample


@fixture
async def sample(sample_provider: AbstractSampleProvider) -> Sample:
    """The sample document for the current job."""
    return await sample_provider


@fixture
def paired(sample: Sample) -> bool:
    """A boolean indicating that the sample data for the current job is paired."""
    return sample.paired


@fixture
def library_type(sample: Sample) -> LibraryType:
    """The library type for the sample being analyzed."""
    return sample.library_type
