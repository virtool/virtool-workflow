from typing import Dict, Any

from virtool_workflow import fixture
from virtool_workflow.db import db


@fixture
def sample(job_args: Dict[str, Any]):
    """The sample document for the current job."""
    return db.fetch_document_by_id(job_args["sample_id"], "samples")


@fixture
def paired(sample) -> bool:
    return sample["paired"]
