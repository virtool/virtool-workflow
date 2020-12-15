from virtool_workflow import fixture
from virtool_workflow.db import db
from typing import Dict, Any


@fixture
def sample(job_args: Dict[str, Any]):
    """The sample document for the current job."""
    return db.fetch_document_by_id(job_args["sample_id"], "samples")
