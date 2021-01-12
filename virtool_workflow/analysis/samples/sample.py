from typing import Dict, Any

from virtool_workflow import fixture
from virtool_workflow.analysis.library_types import LibraryType
from virtool_workflow.abc.db import AbstractDatabase


@fixture
async def sample(job_args: Dict[str, Any], database: AbstractDatabase) -> Dict[str, Any]:
    """The sample document for the current job."""
    return await database.fetch_document_by_id(job_args["sample_id"], "samples")


@fixture
def paired(sample: Dict[str, Any]) -> bool:
    """A boolean indicating that the sample data for the current job is paired."""
    return sample["paired"]


@fixture
def library_type(sample: Dict[str, Any]) -> LibraryType:
    """The library type for the sample being analyzed."""
    return sample["library_type"]
